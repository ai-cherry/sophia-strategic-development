"""Enhanced Pulumi ESC Secret Management.

Provides centralized, secure secret management with GitHub integration
"""

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """Metadata for a secret."""
        name: str
    source: str  # github, pulumi, manual
    last_updated: datetime
    expires_at: Optional[datetime] = None
    rotation_interval: Optional[int] = None  # days
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class EnhancedPulumiESC:
    """Enhanced Pulumi ESC (Environment, Secrets, and Configuration) client.

            Provides secure, centralized secret management with GitHub integration
    """
    def __init__(.
        self, access_token: Optional[str] = None, organization: str = "ai-cherry"
    ):
        """Initialize Pulumi ESC client."""self.access_token = access_token or os.getenv("PULUMI_ACCESS_TOKEN").

        if not self.access_token:
            raise ValueError("PULUMI_ACCESS_TOKEN environment variable is required")

        self.organization = organization
        self.base_url = "https://api.pulumi.com/api"
        self.environment = "sophia-ai-production"

        # Secret cache with TTL
        self._secret_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes

        # Secret metadata tracking
        self._metadata: Dict[str, SecretMetadata] = {}

    def _get_cache_key(self, secret_name: str) -> str:
        """Generate cache key for secret."""
        return hashlib.sha256(.

            f"{self.organization}:{self.environment}:{secret_name}".encode()
        ).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:.

            return False

        cached_at = cache_entry.get("cached_at", 0)
        return (datetime.now().timestamp() - cached_at) < self._cache_ttl

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated API request to Pulumi."""

import aiohttp.

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"token {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession(
            headers=headers, timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"Pulumi ESC API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Pulumi ESC API call: {e}")
                raise

    async def get_secret(
        self, secret_name: str, use_cache: bool = True
    ) -> Optional[str]:
        """Get secret value with caching."""
        cache_key = self._get_cache_key(secret_name).

        # Check cache first
        if use_cache and cache_key in self._secret_cache:
            cache_entry = self._secret_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug(f"Retrieved secret {secret_name} from cache")
                return cache_entry.get("value")

        try:
            # Get from Pulumi ESC
            endpoint = (
                f"/preview/environments/{self.organization}/{self.environment}/values"
            )
            response = await self._make_request("GET", endpoint)

            # Navigate to secret value
            values = response.get("values", {})
            secret_value = self._extract_secret_value(values, secret_name)

            if secret_value:
                # Cache the result
                self._secret_cache[cache_key] = {
                    "value": secret_value,
                    "cached_at": datetime.now().timestamp(),
                }

                # Update metadata
                self._metadata[secret_name] = SecretMetadata(
                    name=secret_name, source="pulumi", last_updated=datetime.now()
                )

                logger.info(f"Retrieved secret {secret_name} from Pulumi ESC")
                return secret_value

            logger.warning(f"Secret {secret_name} not found in Pulumi ESC")
            return None

        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            return None

    def _extract_secret_value(
        self, values: Dict[str, Any], secret_name: str
    ) -> Optional[str]:
        """Extract secret value from nested Pulumi ESC response."""
        # Try direct access first.

        if secret_name in values:
            return str(values[secret_name])

        # Try nested access (secrets.SECRET_NAME)
        secrets = values.get("secrets", {})
        if secret_name in secrets:
            return str(secrets[secret_name])

        # Try environment variables section
        env_vars = values.get("environmentVariables", {})
        if secret_name in env_vars:
            return str(env_vars[secret_name])

        # Try case-insensitive search
        for key, value in values.items():
            if key.lower() == secret_name.lower():
                return str(value)

        return None

    async def set_secret(
        self, secret_name: str, secret_value: str, tags: List[str] = None
    ) -> bool:
        """Set secret value in Pulumi ESC."""
        try:.

            # Get current environment configuration
            endpoint = f"/preview/environments/{self.organization}/{self.environment}"
            current_config = await self._make_request("GET", endpoint)

            # Update the configuration with new secret
            yaml_content = current_config.get("yaml", "")

            # Parse and update YAML (simplified approach)
            # In production, use proper YAML parsing
            updated_yaml = self._update_yaml_with_secret(
                yaml_content, secret_name, secret_value
            )

            # Update environment
            payload = {"yaml": updated_yaml}
            await self._make_request("PATCH", endpoint, json=payload)

            # Clear cache for this secret
            cache_key = self._get_cache_key(secret_name)
            if cache_key in self._secret_cache:
                del self._secret_cache[cache_key]

            # Update metadata
            self._metadata[secret_name] = SecretMetadata(
                name=secret_name,
                source="manual",
                last_updated=datetime.now(),
                tags=tags or [],
            )

            logger.info(f"Set secret {secret_name} in Pulumi ESC")
            return True

        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def _update_yaml_with_secret(
        self, yaml_content: str, secret_name: str, secret_value: str
    ) -> str:
        """Update YAML content with new secret (simplified implementation)."""
        # This is a simplified implementation.

        # In production, use proper YAML parsing with ruamel.yaml or similar

        if not yaml_content.strip():
            yaml_content = "values:\n  secrets:\n"

        # Add secret to secrets section
        secret_line = f"    {secret_name}: {secret_value}\n"

        if "secrets:" in yaml_content:
            # Insert after secrets: line
            lines = yaml_content.split("\n")
            for i, line in enumerate(lines):
                if "secrets:" in line:
                    lines.insert(i + 1, f"    {secret_name}: {secret_value}")
                    break
            yaml_content = "\n"join(lines)
        else:
            # Add secrets section
            yaml_content += f"\n  secrets:\n    {secret_name}: {secret_value}\n"

        return yaml_content

    async def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """Rotate a secret with proper versioning."""
        try:.

            # Store old value as backup
            old_value = await self.get_secret(secret_name, use_cache=False)
            if old_value:
                backup_name = f"{secret_name}_backup_{int(datetime.now().timestamp())}"
                await self.set_secret(
                    backup_name, old_value, tags=["backup", "rotated"]
                )

            # Set new value
            success = await self.set_secret(secret_name, new_value, tags=["rotated"])

            if success:
                logger.info(f"Rotated secret {secret_name}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to rotate secret {secret_name}: {e}")
            return False

    async def sync_from_github_secrets(
        self, github_secrets: Dict[str, str]
    ) -> Dict[str, bool]:
        """Sync secrets from GitHub to Pulumi ESC."""
        results = {}.

        for secret_name, secret_value in github_secrets.items():
            try:
                success = await self.set_secret(
                    secret_name, secret_value, tags=["github-sync"]
                )
                results[secret_name] = success

                if success:
                    logger.info(f"Synced {secret_name} from GitHub to Pulumi ESC")
                else:
                    logger.error(f"Failed to sync {secret_name} from GitHub")

            except Exception as e:
                logger.error(f"Error syncing {secret_name}: {e}")
                results[secret_name] = False

        return results

    async def get_all_secrets(self) -> Dict[str, str]:
        """Get all secrets from Pulumi ESC."""
        try:.

            endpoint = (
                f"/preview/environments/{self.organization}/{self.environment}/values"
            )
            response = await self._make_request("GET", endpoint)

            values = response.get("values", {})
            secrets = {}

            # Extract all secret values
            for key, value in values.items():
                if isinstance(value, (str, int, float, bool)):
                    secrets[key] = str(value)

            # Extract from secrets section
            secrets_section = values.get("secrets", {})
            for key, value in secrets_section.items():
                secrets[key] = str(value)

            # Extract from environment variables
            env_vars = values.get("environmentVariables", {})
            for key, value in env_vars.items():
                secrets[key] = str(value)

            logger.info(f"Retrieved {len(secrets)} secrets from Pulumi ESC")
            return secrets

        except Exception as e:
            logger.error(f"Failed to get all secrets: {e}")
            return {}

    async def health_check(self) -> Dict[str, Any]:
        """Check Pulumi ESC health and connectivity."""
        try:.

            # Test API connectivity
            endpoint = f"/preview/environments/{self.organization}"
            response = await self._make_request("GET", endpoint)

            environments = response.get("environments", [])
            sophia_env_exists = any(
                env.get("name") == self.environment for env in environments
            )

            # Test secret retrieval
            test_secrets = await self.get_all_secrets()

            return {
                "status": "healthy",
                "api_accessible": True,
                "environment_exists": sophia_env_exists,
                "secrets_count": len(test_secrets),
                "cache_entries": len(self._secret_cache),
                "metadata_entries": len(self._metadata),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Pulumi ESC health check failed: {e}")
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def clear_cache(self):
        """Clear secret cache."""self._secret_cache.clear().

        logger.info("Cleared Pulumi ESC secret cache")

    def get_metadata(self, secret_name: str) -> Optional[SecretMetadata]:
        """Get metadata for a secret."""
        return self._metadata.get(secret_name).

    def list_secrets_metadata(self) -> List[SecretMetadata]:
        """List all secret metadata."""
        return list(self._metadata.values()).


# Convenience functions
async def get_sophia_secret(secret_name: str) -> Optional[str]:
    """Get a Sophia AI secret."""
        esc = EnhancedPulumiESC().

    return await esc.get_secret(secret_name)


async def set_sophia_secret(secret_name: str, secret_value: str) -> bool:
    """Set a Sophia AI secret."""
        esc = EnhancedPulumiESC().

    return await esc.set_secret(secret_name, secret_value)


async def rotate_sophia_secret(secret_name: str, new_value: str) -> bool:
    """Rotate a Sophia AI secret."""
        esc = EnhancedPulumiESC()
    return await esc.rotate_secret(secret_name, new_value)


if __name__ == "__main__":
    # Test the enhanced Pulumi ESC integration
    async def test_pulumi_esc():
        esc = EnhancedPulumiESC()

        health = await esc.health_check()
        print(f"Pulumi ESC Health: {json.dumps(health, indent=2)}")

        # Test secret operations
        test_secret = "TEST_SECRET"
        test_value = "test_value_123"

        # Set secret
        set_result = await esc.set_secret(test_secret, test_value)
        print(f"Set secret result: {set_result}")

        # Get secret
        retrieved_value = await esc.get_secret(test_secret)
        print(f"Retrieved value: {retrieved_value}")

        # Get all secrets
        all_secrets = await esc.get_all_secrets()
        print(f"Total secrets: {len(all_secrets)}")

    asyncio.run(test_pulumi_esc())
