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
        print("🔍 Searching for Lambda Labs API key...")

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
                print(f"✅ Found API key in environment variable: {key}")
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
                    print(f"✅ Found API key in Pulumi ESC: {key}")
                    return value

        except Exception as e:
            print(f"⚠️ Could not check Pulumi ESC: {e}")

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
                                print(f"✅ Found API key in config file: {config_file}")
                                return config["api_key"]
                        else:
                            # Plain text file
                            content = f.read().strip()
                            if len(content) > 10:
                                print(f"✅ Found API key in config file: {config_file}")
                                return content
                except Exception as e:
                    print(f"⚠️ Could not read {config_file}: {e}")

        print("❌ Lambda Labs API key not found in any source")
        return None

    def initialize(self) -> bool:
        """Initialize Lambda Labs connection"""
        print("🚀 Initializing Lambda Labs connection...")

        self.api_key = self.get_api_key()
        if not self.api_key:
            print("❌ Cannot initialize without API key")
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
            if response.status_code == 200:
                print("✅ Lambda Labs connection successful")
                return True
            else:
                print(
                    f"❌ Lambda Labs connection failed: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            print(f"❌ Lambda Labs connection error: {e}")
            return False


def main():
    """Main execution function"""
    print("🚀 LAMBDA LABS ACCESS & CONFIGURATION OPTIMIZER")
    print("=" * 70)

    # Initialize Lambda Labs manager
    manager = LambdaLabsManager()

    if not manager.initialize():
        print("\n❌ LAMBDA LABS ACCESS FAILED")
        print("Please ensure you have a valid Lambda Labs API key configured.")
        print("\nOptions to configure API key:")
        print("1. Set environment variable: export LAMBDA_API_KEY=" "")
        print("2. Add to Pulumi ESC under 'lambda_labs_api_key'")
        print("3. Create ~/.lambda/config file with API key")
        print("4. Add to project config/lambda_config.json")
        return False

    print("✅ Lambda Labs access successful!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
