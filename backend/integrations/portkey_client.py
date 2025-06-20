"""Portkey LLM Router Client for Sophia AI
Centralized LLM routing with guardrails and fallback logic
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class PortkeyConfig:
    """Configuration for Portkey routing"""

    api_key: str
    default_provider: str = "openrouter"
    virtual_key: str = "sophia-ai-key"
    base_url: str = "https://api.portkey.ai/v1"
    routing_rules: List[Dict[str, Any]] = None
    guardrails: Dict[str, Any] = None
    fallback_providers: List[str] = None


class PortkeyClient:
    """Portkey client for centralized LLM routing
    - Config-driven routing rules
    - Guardrails for input/output validation
    - Automatic fallback on errors
    """

    def __init__(self, config_path: str = "config/portkey.json"):
        self.config = self._load_config(config_path)
        self.session = None
        self._initialize_routing_rules()

    def _load_config(self, config_path: str) -> PortkeyConfig:
        """Load Portkey configuration from file or environment"""
        config_data = {
            "api_key": os.getenv("PORTKEY_API_KEY", ""),
            "default_provider": "openrouter",
            "virtual_key": "sophia-ai-key",
            "base_url": "https://api.portkey.ai/v1",
        }

        # Try to load from config file
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                file_config = json.load(f)
                config_data.update(file_config)

        # Default routing rules if not specified
        if "routing_rules" not in config_data:
            config_data["routing_rules"] = [
                {"temperature": ">0.7", "route_to": "openrouter/mixtral"},
                {"temperature": "<=0.3", "route_to": "claude-3-opus"},
                {"task": "code_review", "route_to": "claude-3-opus"},
                {"task": "creative", "route_to": "openrouter/mixtral"},
            ]

        # Default guardrails if not specified
        if "guardrails" not in config_data:
            config_data["guardrails"] = {
                "input_checks": ["length < 10000"],
                "output_checks": ["no_pii", "professional_tone"],
            }

        # Default fallback providers
        if "fallback_providers" not in config_data:
            config_data["fallback_providers"] = [
                "claude-3-opus",
                "gpt-4",
                "openrouter/mixtral",
            ]

        return PortkeyConfig(**config_data)

    def _initialize_routing_rules(self):
        """Initialize routing rules for quick access"""
        self.routing_cache = {}
        for rule in self.config.routing_rules:
            # Cache rules by key for faster lookup
            if "task" in rule:
                self.routing_cache[f"task:{rule['task']}"] = rule["route_to"]
            if "temperature" in rule:
                # Parse temperature rules
                temp_str = rule["temperature"]
                if temp_str.startswith(">"):
                    self.routing_cache[f"temp_gt:{temp_str[1:]}"] = rule["route_to"]
                elif temp_str.startswith("<="):
                    self.routing_cache[f"temp_lte:{temp_str[2:]}"] = rule["route_to"]

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        task: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send chat completion request through Portkey
        Handles routing, guardrails, and fallback
        """
        start_time = datetime.utcnow()

        # Determine model based on routing rules
        if not model:
            model = self._determine_model(temperature, task)

        # Apply input guardrails
        validation_result = self._validate_input(messages)
        if not validation_result["valid"]:
            return {
                "error": f"Input validation failed: {validation_result['reason']}",
                "status": "error",
            }

        # Prepare request
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "x-portkey-virtual-key": self.config.virtual_key,
            "Content-Type": "application/json",
        }

        # Try primary model with fallback logic
        providers_to_try = [model] + self.config.fallback_providers
        last_error = None

        for provider in providers_to_try:
            try:
                request_data["model"] = provider

                if not self.session:
                    self.session = aiohttp.ClientSession()

                async with self.session.post(
                    f"{self.config.base_url}/chat/completions",
                    json=request_data,
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()

                        # Apply output guardrails
                        output_validation = self._validate_output(result)
                        if not output_validation["valid"]:
                            logger.warning(
                                f"Output validation failed: {output_validation['reason']}"
                            )
                            # Continue to next provider
                            continue

                        # Log successful request
                        logger.info(f"LLM request successful via {provider}")

                        return {
                            "choices": result.get("choices", []),
                            "usage": result.get("usage", {}),
                            "model": provider,
                            "execution_time": (
                                datetime.utcnow() - start_time
                            ).total_seconds(),
                            "status": "success",
                        }
                    else:
                        error_text = await response.text()
                        last_error = f"Provider {provider} failed: {response.status} - {error_text}"
                        logger.warning(last_error)

            except Exception as e:
                last_error = f"Provider {provider} error: {str(e)}"
                logger.error(last_error)
                continue

        # All providers failed
        return {
            "error": f"All providers failed. Last error: {last_error}",
            "status": "error",
            "providers_tried": providers_to_try,
        }

    def _determine_model(self, temperature: float, task: Optional[str]) -> str:
        """Determine which model to use based on routing rules"""
        # Check task-based routing first
        if task and f"task:{task}" in self.routing_cache:
            return self.routing_cache[f"task:{task}"]

        # Check temperature-based routing
        for key, model in self.routing_cache.items():
            if key.startswith("temp_gt:"):
                threshold = float(key.split(":")[1])
                if temperature > threshold:
                    return model
            elif key.startswith("temp_lte:"):
                threshold = float(key.split(":")[1])
                if temperature <= threshold:
                    return model

        # Default to configured default provider
        return self.config.default_provider

    def _validate_input(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Apply input guardrails"""
        # Check message length
        total_length = sum(len(msg.get("content", "")) for msg in messages)

        for check in self.config.guardrails.get("input_checks", []):
            if "length <" in check:
                max_length = int(check.split("<")[1].strip())
                if total_length >= max_length:
                    return {
                        "valid": False,
                        "reason": f"Input too long: {total_length} chars",
                    }

        return {"valid": True}

    def _validate_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply output guardrails"""
        # Extract content from response
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return {"valid": False, "reason": "Invalid response format"}

        for check in self.config.guardrails.get("output_checks", []):
            if check == "no_pii":
                # Simple PII check (can be enhanced)
                pii_patterns = ["ssn:", "credit card:", "password:"]
                if any(pattern in content.lower() for pattern in pii_patterns):
                    return {"valid": False, "reason": "Output contains potential PII"}

            elif check == "professional_tone":
                # Simple profanity check (can be enhanced)
                inappropriate_words = ["damn", "hell"]  # Simplified for example
                if any(word in content.lower() for word in inappropriate_words):
                    return {
                        "valid": False,
                        "reason": "Output contains inappropriate language",
                    }

        return {"valid": True}

    async def update_routing_rules(self, new_rules: List[Dict[str, Any]]):
        """Update routing rules dynamically"""
        self.config.routing_rules = new_rules
        self._initialize_routing_rules()
        logger.info("Routing rules updated")

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            "default_provider": self.config.default_provider,
            "routing_rules": self.config.routing_rules,
            "guardrails": self.config.guardrails,
            "fallback_providers": self.config.fallback_providers,
        }


# Global Portkey client instance
portkey_client = PortkeyClient()
