#!/usr/bin/env python3
"""
Lambda Labs Access & Server Configuration Optimizer for Sophia AI
Comprehensive script to access Lambda Labs, audit server configurations, and optimize for current state
"""

import json
import os
import sys
from dataclasses import dataclass

import requests

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


@dataclass
class ServerConfig:
    """Lambda Labs server configuration"""

    instance_type: str
    gpu_count: int
    gpu_type: str
    vcpus: int
    ram_gb: int
    storage_gb: int
    price_per_hour: float
    region: str
    availability: str


@dataclass
class OptimizationRecommendation:
    """Server optimization recommendation"""

    current_config: str
    recommended_config: str
    reason: str
    cost_impact: str
    performance_impact: str


class LambdaLabsManager:
    """Lambda Labs API manager and configuration optimizer"""

    def __init__(self):
        self.api_key = None
        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.headers = {}
        self.current_instances = []
        self.available_instance_types = []

    def get_api_key(self) -> str:
        """Get Lambda Labs API key from various sources"""

        # Try environment variables
        env_keys = [
            "LAMBDA_API_KEY",
            "LAMBDA_LABS_API_KEY",
            "LAMBDALABS_API_KEY",
            "LAMBDA_CLOUD_API_KEY",
        ]

        for key in env_keys:
            value = os.getenv(key)
            if value:
                return value

        # Try Pulumi ESC
        try:
            from backend.core.auto_esc_config import get_config_value

            esc_keys = [
                "lambda_api_key",
                "lambda_labs_api_key",
                "lambda_labs.api_key",
                "infrastructure.lambda_labs.api_key",
                "lambdalabs_api_key",
            ]

            for key in esc_keys:
                value = get_config_value(key)
                if value and value != "None" and len(value) > 10:
                    return value

        except Exception:
            pass

        # Try reading from common config files
        config_files = [
            os.path.expanduser("~/.lambda/config"),
            os.path.expanduser("~/.config/lambda/config"),
            "./config/lambda_config.json",
            "./infrastructure/lambda_config.json",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file) as f:
                        if config_file.endswith(".json"):
                            config = json.load(f)
                            if "api_key" in config:
                                return config["api_key"]
                        else:
                            # Plain text file
                            content = f.read().strip()
                            if len(content) > 10:
                                return content
                except Exception:
                    pass

        return None

    def initialize(self) -> bool:
        """Initialize Lambda Labs connection"""

        self.api_key = self.get_api_key()
        if not self.api_key:
            return False

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Test connection
        try:
            response = requests.get(
                f"{self.base_url}/instance-types", headers=self.headers, timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False


def main():
    """Main execution function"""

    # Initialize Lambda Labs manager
    manager = LambdaLabsManager()

    return manager.initialize()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
