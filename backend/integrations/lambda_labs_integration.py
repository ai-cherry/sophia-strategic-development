"""Lambda Labs Integration for Sophia AI
Provides secure API client for Lambda Labs cloud compute services
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class LambdaLabsInstance:
    """Lambda Labs instance representation"""

    id: str
    name: str
    instance_type: str
    region: str
    status: str
    ip: Optional[str] = None
    ssh_key_names: List[str] = None
    created_at: Optional[datetime] = None


class LambdaLabsIntegration:
    """Lambda Labs API Integration
    Provides secure access to Lambda Labs cloud compute services
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Lambda Labs integration"""
        self.api_key = api_key or os.getenv("LAMBDA_LABS_API_KEY")
        if not self.api_key:
            raise ValueError("LAMBDA_LABS_API_KEY environment variable is required")

        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.session = None

        # Default configuration
        self.default_instance_type = os.getenv(
            "LAMBDA_LABS_INSTANCE_TYPE", "gpu_1x_a100_sxm4"
        )
        self.default_ssh_key = os.getenv("LAMBDA_LABS_SSH_KEY_NAME", "sophia-ai-key")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Lambda Labs API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Lambda Labs API call: {e}")
            raise

    async def get_instance_types(self) -> List[Dict[str, Any]]:
        """Get available instance types"""
        try:
            response = await self._make_request("GET", "/instance-types")
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get instance types: {e}")
            return []

    async def list_instances(self) -> List[LambdaLabsInstance]:
        """List all instances"""
        try:
            response = await self._make_request("GET", "/instances")
            instances = []

            for instance_data in response.get("data", []):
                instance = LambdaLabsInstance(
                    id=instance_data.get("id"),
                    name=instance_data.get("name"),
                    instance_type=instance_data.get("instance_type", {}).get("name"),
                    region=instance_data.get("region", {}).get("name"),
                    status=instance_data.get("status"),
                    ip=instance_data.get("ip"),
                    ssh_key_names=instance_data.get("ssh_key_names", []),
                )
                instances.append(instance)

            return instances
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            return []

    async def create_instance(
        self,
        name: str,
        instance_type: Optional[str] = None,
        region: str = "us-west-1",
        ssh_key_names: Optional[List[str]] = None,
    ) -> Optional[LambdaLabsInstance]:
        """Create a new instance"""
        instance_type = instance_type or self.default_instance_type
        ssh_key_names = ssh_key_names or [self.default_ssh_key]

        payload = {
            "region_name": region,
            "instance_type_name": instance_type,
            "ssh_key_names": ssh_key_names,
            "name": name,
        }

        try:
            response = await self._make_request(
                "POST", "/instance-operations/launch", json=payload
            )
            instance_data = response.get("data", {}).get("instance_ids", [])

            if instance_data:
                # Get instance details
                instances = await self.list_instances()
                for instance in instances:
                    if instance.id in instance_data:
                        logger.info(
                            f"Created Lambda Labs instance: {instance.name} ({instance.id})"
                        )
                        return instance

            return None
        except Exception as e:
            logger.error(f"Failed to create instance: {e}")
            return None

    async def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an instance"""
        payload = {"instance_ids": [instance_id]}

        try:
            await self._make_request(
                "POST", "/instance-operations/terminate", json=payload
            )
            logger.info(f"Terminated Lambda Labs instance: {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate instance {instance_id}: {e}")
            return False

    async def restart_instance(self, instance_id: str) -> bool:
        """Restart an instance"""
        payload = {"instance_ids": [instance_id]}

        try:
            await self._make_request(
                "POST", "/instance-operations/restart", json=payload
            )
            logger.info(f"Restarted Lambda Labs instance: {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restart instance {instance_id}: {e}")
            return False

    async def get_ssh_keys(self) -> List[Dict[str, Any]]:
        """Get SSH keys"""
        try:
            response = await self._make_request("GET", "/ssh-keys")
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get SSH keys: {e}")
            return []

    async def add_ssh_key(self, name: str, public_key: str) -> bool:
        """Add SSH key"""
        payload = {"name": name, "public_key": public_key}

        try:
            await self._make_request("POST", "/ssh-keys", json=payload)
            logger.info(f"Added SSH key: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add SSH key {name}: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check Lambda Labs API health"""
        try:
            # Test API connectivity by getting instance types
            instance_types = await self.get_instance_types()
            instances = await self.list_instances()

            return {
                "status": "healthy",
                "api_accessible": True,
                "instance_types_count": len(instance_types),
                "active_instances": len([i for i in instances if i.status == "active"]),
                "total_instances": len(instances),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Lambda Labs health check failed: {e}")
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


# Convenience functions for common operations
async def create_sophia_instance(
    name: str = "sophia-ai-compute",
) -> Optional[LambdaLabsInstance]:
    """Create a Sophia AI compute instance"""
    async with LambdaLabsIntegration() as lambda_client:
        return await lambda_client.create_instance(name)


async def list_sophia_instances() -> List[LambdaLabsInstance]:
    """List all Sophia AI instances"""
    async with LambdaLabsIntegration() as lambda_client:
        return await lambda_client.list_instances()


async def cleanup_instances() -> int:
    """Cleanup all instances (use with caution)"""
    async with LambdaLabsIntegration() as lambda_client:
        instances = await lambda_client.list_instances()
        terminated = 0

        for instance in instances:
            if await lambda_client.terminate_instance(instance.id):
                terminated += 1

        return terminated


if __name__ == "__main__":
    # Test the integration
    async def test_lambda_labs():
        async with LambdaLabsIntegration() as client:
            health = await client.health_check()
            print(f"Lambda Labs Health: {json.dumps(health, indent=2)}")

            instance_types = await client.get_instance_types()
            print(f"Available instance types: {len(instance_types)}")

            instances = await client.list_instances()
            print(f"Current instances: {len(instances)}")

            for instance in instances:
                print(f"  - {instance.name} ({instance.status})")

    asyncio.run(test_lambda_labs())
