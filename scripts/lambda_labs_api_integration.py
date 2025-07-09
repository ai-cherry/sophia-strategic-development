#!/usr/bin/env python3
"""
Lambda Labs API Integration Module
Handles both Inference API and Cloud API with proper authentication
"""

import logging
import os
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class LambdaLabsAPIClient:
    """Unified client for Lambda Labs APIs"""

    def __init__(self):
        # Get API keys from environment
        self.inference_api_key = os.getenv("LAMBDA_API_KEY")
        self.cloud_api_key = os.getenv("LAMBDA_CLOUD_API_KEY")

        # API endpoints
        self.inference_base_url = "https://api.lambda.ai/v1"
        self.cloud_base_url = "https://cloud.lambda.ai/api/v1"

        # Validate keys
        if not self.inference_api_key:
            logger.warning("LAMBDA_API_KEY not set - inference API calls will fail")
        if not self.cloud_api_key:
            logger.warning("LAMBDA_CLOUD_API_KEY not set - cloud API calls will fail")

    # ========== INFERENCE API METHODS ==========

    def inference_completion(self, model: str, prompt: str, **kwargs) -> dict[str, Any]:
        """
        Make an inference API call for LLM completion
        Uses Basic Auth with API key as username and empty password
        """
        if not self.inference_api_key:
            raise ValueError("LAMBDA_API_KEY not configured")

        endpoint = f"{self.inference_base_url}/inference"

        payload = {
            "model": model,
            "prompt": prompt,
            **kwargs,  # max_tokens, temperature, etc.
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(
                    self.inference_api_key, ""
                ),  # Basic auth with empty password
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Inference API error: {e}")
            raise

    def list_inference_models(self) -> list[str]:
        """List available inference models"""
        if not self.inference_api_key:
            raise ValueError("LAMBDA_API_KEY not configured")

        endpoint = f"{self.inference_base_url}/models"

        try:
            response = requests.get(
                endpoint, auth=HTTPBasicAuth(self.inference_api_key, ""), timeout=10
            )
            response.raise_for_status()
            return response.json().get("models", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            raise

    # ========== CLOUD API METHODS ==========

    def list_instances(self) -> list[dict[str, Any]]:
        """
        List all Lambda Labs cloud instances
        Uses Bearer token authentication
        """
        if not self.cloud_api_key:
            raise ValueError("LAMBDA_CLOUD_API_KEY not configured")

        endpoint = f"{self.cloud_base_url}/instances"

        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.cloud_api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json().get("data", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud API error: {e}")
            raise

    def get_instance(self, instance_id: str) -> dict[str, Any]:
        """Get details of a specific instance"""
        if not self.cloud_api_key:
            raise ValueError("LAMBDA_CLOUD_API_KEY not configured")

        endpoint = f"{self.cloud_base_url}/instances/{instance_id}"

        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.cloud_api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json().get("data", {})

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get instance {instance_id}: {e}")
            raise

    def create_instance(
        self, name: str, instance_type: str, region: str = "us-west-1"
    ) -> dict[str, Any]:
        """Create a new Lambda Labs instance"""
        if not self.cloud_api_key:
            raise ValueError("LAMBDA_CLOUD_API_KEY not configured")

        endpoint = f"{self.cloud_base_url}/instances"

        payload = {
            "name": name,
            "instance_type": instance_type,
            "region": region,
            "ssh_key_names": [],  # Add your SSH key names here
            "file_system_names": [],
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.cloud_api_key}"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("data", {})

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create instance: {e}")
            raise

    def terminate_instance(self, instance_id: str) -> bool:
        """Terminate a Lambda Labs instance"""
        if not self.cloud_api_key:
            raise ValueError("LAMBDA_CLOUD_API_KEY not configured")

        endpoint = f"{self.cloud_base_url}/instances/{instance_id}/terminate"

        try:
            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {self.cloud_api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to terminate instance {instance_id}: {e}")
            return False

    def get_ssh_keys(self) -> list[dict[str, Any]]:
        """List SSH keys in Lambda Labs account"""
        if not self.cloud_api_key:
            raise ValueError("LAMBDA_CLOUD_API_KEY not configured")

        endpoint = f"{self.cloud_base_url}/ssh-keys"

        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.cloud_api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json().get("data", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list SSH keys: {e}")
            raise

    # ========== HYBRID ARCHITECTURE METHODS ==========

    def route_inference_request(
        self, model: str, prompt: str, **kwargs
    ) -> dict[str, Any]:
        """
        Route inference request based on 80/20 serverless/dedicated split
        """
        import random

        # 80% chance to use serverless
        use_serverless = random.random() < 0.8

        if use_serverless:
            logger.info(f"Routing to serverless inference for model: {model}")
            return self.inference_completion(model, prompt, **kwargs)
        else:
            logger.info(f"Routing to dedicated GPU for model: {model}")
            # In production, this would route to your dedicated GPU instance
            # For now, we'll use serverless as fallback
            return self.inference_completion(model, prompt, **kwargs)

    def get_instance_by_name(self, name: str) -> dict[str, Any] | None:
        """Find an instance by name"""
        instances = self.list_instances()
        for instance in instances:
            if instance.get("name") == name:
                return instance
        return None

    def get_running_instances(self) -> list[dict[str, Any]]:
        """Get all running instances"""
        instances = self.list_instances()
        return [i for i in instances if i.get("status") == "running"]


# ========== UTILITY FUNCTIONS ==========


def test_inference_api():
    """Test the inference API with a simple prompt"""
    client = LambdaLabsAPIClient()

    try:
        result = client.inference_completion(
            model="llama3.1-8b",
            prompt="What is the capital of France? Answer in one word.",
            max_tokens=10,
        )
        print("✅ Inference API test successful:")
        print(f"Response: {result}")
        return True
    except Exception as e:
        print(f"❌ Inference API test failed: {e}")
        return False


def test_cloud_api():
    """Test the cloud API by listing instances"""
    client = LambdaLabsAPIClient()

    try:
        instances = client.list_instances()
        print(f"✅ Cloud API test successful. Found {len(instances)} instances:")
        for instance in instances:
            print(
                f"  - {instance.get('name')} ({instance.get('status')}): {instance.get('ip_address')}"
            )
        return True
    except Exception as e:
        print(f"❌ Cloud API test failed: {e}")
        return False


def get_instance_ssh_command(instance_name: str) -> str | None:
    """Get SSH command for connecting to an instance"""
    client = LambdaLabsAPIClient()

    instance = client.get_instance_by_name(instance_name)
    if instance and instance.get("status") == "running":
        ip = instance.get("ip_address")
        return f"ssh -i ~/.ssh/sophia2025.pem ubuntu@{ip}"
    return None


if __name__ == "__main__":
    # Test both APIs
    print("🧪 Testing Lambda Labs API Integration")
    print("=" * 50)

    print("\n1. Testing Inference API...")
    inference_ok = test_inference_api()

    print("\n2. Testing Cloud API...")
    cloud_ok = test_cloud_api()

    print("\n" + "=" * 50)
    if inference_ok and cloud_ok:
        print("✅ All API tests passed!")
    else:
        print("❌ Some API tests failed. Check your API keys.")
        print("   - LAMBDA_API_KEY for inference API")
        print("   - LAMBDA_CLOUD_API_KEY for cloud API")
