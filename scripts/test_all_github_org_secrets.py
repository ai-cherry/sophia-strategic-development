#!/usr/bin/env python3
"""Sophia AI - Comprehensive GitHub Organization Secret Tester.

Test access to all secrets from Pulumi ESC and optionally test API connectivity.
"""

import argparse
import asyncio
import logging
import os
from typing import Any, Dict

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set Pulumi organization
os.environ["PULUMI_ORG"] = "scoobyjava-org"

# Import config after setting the org
try:
    from backend.core.auto_esc_config import config
except (ImportError, ModuleNotFoundError):
    logger.error(
        "Could not import auto_esc_config. Make sure backend is in PYTHONPATH."
    )
    logger.error("Try running `export PYTHONPATH=$PYTHONPATH:$(pwd)`")
    config = None

# Mappings for API tests
API_TEST_CONFIG = {
    "agno": {
        "key_attr": "agno_api_key",
        "url": "https://api.agno.ai/v1/models",  # Hypothetical
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
    },
    "arize": {
        "key_attr": "arize_api_key",
        "space_id_attr": "arize_space_id",
        "url": lambda space_id: f"https://app.arize.com/v1/spaces/{space_id}/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
    },
    "openai": {
        "key_attr": "openai_api_key",
        "url": "https://api.openai.com/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
    },
    "anthropic": {
        "key_attr": "anthropic_api_key",
        "url": "https://api.anthropic.com/v1/messages",  # just checking headers
        "headers": lambda key: {"x-api-key": key, "anthropic-version": "2023-06-01"},
        "method": "post",
        "payload": {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "test"}],
        },
        "expected_status": 400,  # Will fail on payload, but 401/403 means auth issue. 400 means auth is ok.
    },
    "gong": {
        "key_attr": "gong_access_key",
        "url": "https://api.gong.io/v2/calls",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
    },
}


class SecretTester:
    def __init__(self):
        if not config:
            raise RuntimeError("Pulumi ESC config is not loaded.")
        self.config = config
        self.results: Dict[str, Any] = {}

    def check_secret_presence(self, key_attr: str) -> str:
        """Check if a secret is present in the config."""
        value = getattr(self.config, key_attr, None)
        if value:
            if "PLACEHOLDER" in str(value):
                return "Placeholder"
            return "Available"
        return "Not found"

    async def test_api_connectivity(self, service: str) -> str:
        """Test connectivity to a specific API."""
        service_config = API_TEST_CONFIG[service]
        key_attr = service_config["key_attr"]
        api_key = getattr(self.config, key_attr, None)

        if not api_key or "PLACEHOLDER" in str(api_key):
            return "Skipped (key not available)"

        url = service_config["url"]
        if callable(url):
            space_id_attr = service_config.get("space_id_attr")
            if not space_id_attr:
                return f"Skipped (missing config for callable url: {space_id_attr})"
            space_id = getattr(self.config, space_id_attr, None)
            if not space_id or "PLACEHOLDER" in str(space_id):
                return "Skipped (dependent key not available)"
            url = url(space_id)

        headers = service_config["headers"](api_key)
        method = service_config.get("method", "get")
        payload = service_config.get("payload")
        expected_status = service_config.get("expected_status", 200)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=payload, timeout=10
                ) as response:
                    if response.status == expected_status:
                        return f"Success (Status: {response.status})"
                    elif method == "get" and response.status in [400, 404]:
                        return f"Success (likely) (Status: {response.status})"
                    else:
                        return f"Failed (Status: {response.status}, Body: {await response.text()})"
        except aiohttp.ClientConnectorError as e:
            return f"Failed (Connection Error: {e})"
        except Exception as e:
            return f"Failed (Error: {e})"

    async def run_tests(self, check_arize: bool, check_agno: bool, test_apis: bool):
        logger.info("Starting secret tests...")

        services_to_test = []
        if check_arize:
            services_to_test.append("arize")
        if check_agno:
            services_to_test.append("agno")
        if test_apis:
            services_to_test = list(API_TEST_CONFIG.keys())

        services_to_test = sorted(list(set(services_to_test)))

        for service in services_to_test:
            key_attr = API_TEST_CONFIG[service]["key_attr"]
            presence_status = self.check_secret_presence(key_attr)
            self.results[f"{key_attr}_presence"] = presence_status

            if test_apis:
                api_status = await self.test_api_connectivity(service)
                self.results[f"{service}_api_connectivity"] = api_status

        self.print_results()

    def print_results(self):
        print("\n--- Secret Test Results ---")
        for test_name, result in sorted(self.results.items()):
            status_emoji = (
                "✅" if "Success" in result or "Available" in result else "❌"
            )
            if "Placeholder" in result or "Skipped" in result:
                status_emoji = "⚠️"
            print(f"{status_emoji} {test_name}: {result}")
        print("-------------------------\n")


async def main():
    parser = argparse.ArgumentParser(
        description="Test Sophia AI secrets from Pulumi ESC."
    )
    parser.add_argument(
        "--check-arize", action="store_true", help="Check for Arize keys."
    )
    parser.add_argument(
        "--check-agno", action="store_true", help="Check for Agno keys."
    )
    parser.add_argument(
        "--test-apis",
        action="store_true",
        help="Test connectivity to all configured APIs.",
    )
    args = parser.parse_args()

    if not config:
        return

    tester = SecretTester()
    await tester.run_tests(args.check_arize, args.check_agno, args.test_apis)


if __name__ == "__main__":
    asyncio.run(main())
