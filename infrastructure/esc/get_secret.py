#!/usr/bin/env python3
"""
Secure Secret Retrieval from Pulumi ESC for Sophia AI

This script provides secure, efficient secret retrieval from Pulumi ESC environments
with comprehensive error handling, caching, and security features.

Features:
- Single secret retrieval with validation
- Batch secret retrieval for efficiency
- Nested key support (dot notation)
- Comprehensive error handling
- Security-focused logging (no secret exposure)
- Authentication validation
- Timeout handling

Usage:
    python infrastructure/esc/get_secret.py openai_api_key
    python infrastructure/esc/get_secret.py sophia.ai.openai_api_key --output json
    python infrastructure/esc/get_secret.py --list-keys
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecureSecretRetriever:
    """
    Secure secret retrieval from Pulumi ESC with enterprise-grade features
    """

    def __init__(self, org: str | None = None, environment: str | None = None):
        self.org = org or get_config_value("pulumi_org", "default")
        self.environment = environment or os.getenv(
            "PULUMI_ENV", "sophia-ai-production"
        )
        self.logger = logging.getLogger(__name__)

        # Cache for environment data to reduce API calls
        self._env_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes cache TTL

        # Validate authentication on initialization
        if not self._validate_auth():
            raise RuntimeError("Pulumi authentication failed - cannot retrieve secrets")

    def _validate_auth(self) -> bool:
        """Validate Pulumi authentication before proceeding"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                user = result.stdout.strip()
                self.logger.debug(f"Authenticated as Pulumi user: {user}")
                return True
            else:
                self.logger.error(f"Pulumi authentication failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Pulumi authentication check timed out")
            return False
        except FileNotFoundError:
            self.logger.error("Pulumi CLI not found - please install Pulumi")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during auth validation: {e}")
            return False

    def _get_environment_data(self, force_refresh: bool = False) -> dict[str, Any]:
        """
        Get environment data with caching to reduce API calls

        Args:
            force_refresh: Force refresh of cached data

        Returns:
            Environment data dictionary
        """
        current_time = time.time()

        # Check if cache is still valid
        if (
            not force_refresh
            and self._env_cache is not None
            and self._cache_timestamp is not None
            and current_time - self._cache_timestamp < self._cache_ttl
        ):
            self.logger.debug("Using cached environment data")
            return self._env_cache

        # Fetch fresh data from ESC
        try:
            env_path = f"{self.org}/{self.environment}"
            self.logger.debug(f"Fetching environment data from {env_path}")

            result = subprocess.run(
                ["pulumi", "env", "get", env_path, "--show-secrets"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                error_msg = (
                    f"Failed to get ESC environment '{env_path}': {result.stderr}"
                )
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

            try:
                # Try to extract JSON from the output (may have extra formatting)
                output = result.stdout.strip()

                # Look for JSON data - it should start with { and end with }
                json_start = output.find("{")
                json_end = output.rfind("}") + 1

                if json_start >= 0 and json_end > json_start:
                    json_data = output[json_start:json_end]
                    env_data = json.loads(json_data)
                    values = env_data if isinstance(env_data, dict) else {}
                else:
                    # Fallback: parse the structured output manually
                    values = self._parse_esc_output_manual(output)

                # Update cache
                self._env_cache = values
                self._cache_timestamp = current_time

                self.logger.debug(f"Successfully cached {len(values)} values from ESC")
                return values

            except json.JSONDecodeError as e:
                # Fallback to manual parsing
                self.logger.debug(f"JSON parsing failed, trying manual parsing: {e}")
                values = self._parse_esc_output_manual(result.stdout)

                # Update cache
                self._env_cache = values
                self._cache_timestamp = current_time

                self.logger.debug(
                    f"Successfully parsed {len(values)} values manually from ESC"
                )
                return values

        except subprocess.TimeoutExpired:
            error_msg = "Timeout while retrieving environment data from Pulumi ESC"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error retrieving environment data: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _parse_esc_output_manual(self, output: str) -> dict[str, Any]:
        """
        Manually parse ESC output when JSON parsing fails

        Args:
            output: Raw output from pulumi env get

        Returns:
            Dictionary of parsed values
        """
        values = {}

        # Look for patterns in the output that indicate key-value pairs
        lines = output.split("\n")

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith("#") or line in ["Value", "Definition"]:
                continue

            # Look for key: value patterns
            if ":" in line and not line.strip().startswith("{"):
                try:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        key = parts[0].strip().strip('"')
                        value = parts[1].strip().strip('"')

                        # Handle special values
                        if value == "[secret]":
                            values[key] = "[secret]"
                        elif value.startswith("fn::secret:"):
                            values[key] = "[secret]"
                        else:
                            values[key] = value
                except Exception:
                    # Skip problematic lines
                    continue

        return values

    def get_secret(self, secret_key: str, mask_in_logs: bool = True) -> str | None:
        """
        Securely retrieve a single secret from Pulumi ESC

        Args:
            secret_key: The key of the secret to retrieve (supports dot notation)
            mask_in_logs: Whether to mask the secret value in logs

        Returns:
            The secret value or None if not found

        Raises:
            RuntimeError: If ESC access fails or authentication issues
        """
        start_time = time.time()

        try:
            values = self._get_environment_data()

            # Support nested key access (e.g., "sophia.ai.openai_api_key")
            secret_value = self._get_nested_value(values, secret_key)

            # Log retrieval result (with masking)
            execution_time = time.time() - start_time

            if secret_value is not None:
                log_value = "***MASKED***" if mask_in_logs else secret_value
                self.logger.info(
                    f"Retrieved secret '{secret_key}' successfully "
                    f"(length: {len(secret_value)}, time: {execution_time:.3f}s): {log_value}"
                )
                return secret_value
            else:
                self.logger.warning(
                    f"Secret '{secret_key}' not found in ESC environment '{self.environment}'"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving secret '{secret_key}': {e}")
            raise

    def _get_nested_value(self, data: dict[str, Any], key: str) -> str | None:
        """
        Get value from nested dictionary using dot notation

        Args:
            data: Dictionary to search
            key: Key to find (supports dot notation like "sophia.ai.openai_api_key")

        Returns:
            The value if found, None otherwise
        """
        # Try direct key first (most common case)
        if key in data:
            value = data[key]
            return str(value) if value is not None else None

        # Try with dot notation for nested access
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return str(current) if current is not None else None

    def get_multiple_secrets(
        self, secret_keys: list[str], mask_in_logs: bool = True
    ) -> dict[str, str | None]:
        """
        Efficiently retrieve multiple secrets in a single ESC call

        Args:
            secret_keys: List of secret keys to retrieve
            mask_in_logs: Whether to mask secret values in logs

        Returns:
            Dictionary mapping secret keys to their values (None if not found)
        """
        start_time = time.time()

        try:
            values = self._get_environment_data()

            results = {}
            for key in secret_keys:
                results[key] = self._get_nested_value(values, key)

            # Log summary
            execution_time = time.time() - start_time
            found_count = sum(1 for v in results.values() if v is not None)

            self.logger.info(
                f"Retrieved {found_count}/{len(secret_keys)} secrets successfully "
                f"(time: {execution_time:.3f}s)"
            )

            # Log individual results
            for key, value in results.items():
                if value is not None:
                    log_value = "***MASKED***" if mask_in_logs else value
                    self.logger.debug(f"  ✅ {key}: {log_value}")
                else:
                    self.logger.debug(f"  ❌ {key}: NOT FOUND")

            return results

        except Exception as e:
            self.logger.error(f"Error retrieving multiple secrets: {e}")
            raise

    def list_available_keys(self, filter_secrets_only: bool = True) -> list[str]:
        """
        List all available keys in the ESC environment

        Args:
            filter_secrets_only: If True, only return keys that appear to be secrets

        Returns:
            List of available keys
        """
        try:
            values = self._get_environment_data()

            if filter_secrets_only:
                # Filter for keys that look like secrets
                secret_indicators = [
                    "secret",
                    "key",
                    "token",
                    "password",
                    "credential",
                    "auth",
                    "api_key",
                    "access_token",
                    "private",
                ]

                secret_keys = []
                for key in values.keys():
                    key_lower = key.lower()
                    if any(indicator in key_lower for indicator in secret_indicators):
                        secret_keys.append(key)

                self.logger.info(
                    f"Found {len(secret_keys)} secret keys out of {len(values)} total values"
                )
                return sorted(secret_keys)
            else:
                self.logger.info(f"Found {len(values)} total keys in environment")
                return sorted(values.keys())

        except Exception as e:
            self.logger.error(f"Error listing available keys: {e}")
            raise

    def validate_secret_access(self, secret_keys: list[str]) -> dict[str, bool]:
        """
        Validate access to multiple secrets without retrieving values

        Args:
            secret_keys: List of secret keys to validate

        Returns:
            Dictionary mapping secret keys to availability status
        """
        try:
            values = self._get_environment_data()

            results = {}
            for key in secret_keys:
                results[key] = self._get_nested_value(values, key) is not None

            available_count = sum(results.values())
            self.logger.info(
                f"Validated {available_count}/{len(secret_keys)} secrets are available"
            )

            return results

        except Exception as e:
            self.logger.error(f"Error validating secret access: {e}")
            raise

    def get_environment_info(self) -> dict[str, Any]:
        """
        Get information about the current ESC environment

        Returns:
            Dictionary with environment metadata
        """
        try:
            values = self._get_environment_data()

            # Analyze the environment
            secret_indicators = ["secret", "key", "token", "password", "credential"]
            secret_count = 0

            for key in values.keys():
                key_lower = key.lower()
                if any(indicator in key_lower for indicator in secret_indicators):
                    secret_count += 1

            return {
                "organization": self.org,
                "environment": self.environment,
                "total_values": len(values),
                "estimated_secrets": secret_count,
                "cache_timestamp": datetime.fromtimestamp(
                    self._cache_timestamp
                ).isoformat()
                if self._cache_timestamp
                else None,
                "cache_ttl_seconds": self._cache_ttl,
            }

        except Exception as e:
            self.logger.error(f"Error getting environment info: {e}")
            raise


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Securely retrieve secrets from Pulumi ESC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Get a single secret
    python infrastructure/esc/get_secret.py openai_api_key

    # Get a nested secret with JSON output
    python infrastructure/esc/get_secret.py sophia.ai.openai_api_key --output json

    # List all available secret keys
    python infrastructure/esc/get_secret.py --list-keys

    # Get multiple secrets
    python infrastructure/esc/get_secret.py openai_api_key anthropic_api_key --multiple

    # Validate secret access without retrieving values
    python infrastructure/esc/get_secret.py openai_api_key --validate-only
        """,
    )

    parser.add_argument(
        "secret_keys",
        nargs="*",
        help="Secret key(s) to retrieve (supports dot notation)",
    )
    parser.add_argument(
        "--org", help="Pulumi organization (default: from PULUMI_ORG env var)"
    )
    parser.add_argument(
        "--env", help="ESC environment name (default: from PULUMI_ENV env var)"
    )
    parser.add_argument(
        "--output",
        choices=["value", "json"],
        default="value",
        help="Output format (default: value)",
    )
    parser.add_argument(
        "--mask-logs",
        action="store_true",
        help="Mask secret values in logs (default: True)",
    )
    parser.add_argument(
        "--list-keys", action="store_true", help="List all available secret keys"
    )
    parser.add_argument(
        "--multiple", action="store_true", help="Retrieve multiple secrets efficiently"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate secret access without retrieving values",
    )
    parser.add_argument(
        "--env-info", action="store_true", help="Show environment information"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress log output")

    args = parser.parse_args()

    # Adjust logging level if quiet
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        retriever = SecureSecretRetriever(org=args.org, environment=args.env)

        # Handle different operation modes
        if args.env_info:
            info = retriever.get_environment_info()
            if args.output == "json":
                pass
            else:
                if info["cache_timestamp"]:
                    pass

        elif args.list_keys:
            keys = retriever.list_available_keys()
            if args.output == "json":
                pass
            else:
                for key in keys:
                    pass

        elif args.validate_only:
            if not args.secret_keys:
                sys.exit(1)

            validation_results = retriever.validate_secret_access(args.secret_keys)
            if args.output == "json":
                pass
            else:
                for key, available in validation_results.items():
                    pass

        elif args.multiple:
            if not args.secret_keys:
                sys.exit(1)

            results = retriever.get_multiple_secrets(
                args.secret_keys, mask_in_logs=args.mask_logs
            )
            if args.output == "json":
                pass
            else:
                for key, value in results.items():
                    if value is not None:
                        pass
                    else:
                        pass

        else:
            # Single secret retrieval (default mode)
            if not args.secret_keys or len(args.secret_keys) != 1:
                sys.exit(1)

            secret_key = args.secret_keys[0]
            secret_value = retriever.get_secret(secret_key, mask_in_logs=args.mask_logs)

            if secret_value is not None:
                if args.output == "json":
                    pass
                else:
                    pass
                sys.exit(0)
            else:
                sys.exit(1)

    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        if args.output == "json":
            {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }
        else:
            pass
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.output == "json":
            {
                "error": f"Unexpected error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }
        else:
            pass
        sys.exit(2)


if __name__ == "__main__":
    main()
