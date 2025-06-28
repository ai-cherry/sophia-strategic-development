#!/usr/bin/env python3
from backend.core.auto_esc_config import get_config_value

"""
Deploy Estuary Foundation for Sophia AI
Complete deployment of Estuary Flow captures and materializations
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.integrations.estuary_flow_manager import (
    EstuaryFlowManager,
    EstuaryCredentials,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EstuaryFoundationDeployment:
    """Deploy complete Estuary Flow foundation for Sophia AI"""

    def __init__(self):
        # Set up credentials
        self.access_token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlhaYXZsWHkrajczYUxwYlEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2V5cmNubXV6enlyaXlwZGFqd2RrLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJkNDRmMDBhNC05NmE1LTQyMWItYTkxZS02ODVmN2I3NDg5ZTMiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzUxMDYxMTk4LCJpYXQiOjE3NTEwNTc1OTgsImVtYWlsIjoibXVzaWxseW5uQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ2l0aHViIiwicHJvdmlkZXJzIjpbImdpdGh1YiJdfSwidXNlcl9tZXRhZGF0YSI6eyJhdmF0YXJfdXJsIjoiaHR0cHM6Ly9hdmF0YXJzLmdpdGh1YnVzZXJjb250ZW50LmNvbS91LzEyNDQxODk1Mz92PTQiLCJlbWFpbCI6Im11c2lsbHlubkBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiTHlubiBNdXNpbCIsImlzcyI6Imh0dHBzOi8vYXBpLmdpdGh1Yi5jb20iLCJuYW1lIjoiTHlubiBNdXNpbCIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoic2Nvb2J5amF2YSIsInByb3ZpZGVyX2lkIjoiMTI0NDE4OTUzIiwic3ViIjoiMTI0NDE4OTUzIiwidXNlcl9uYW1lIjoic2Nvb2J5amF2YSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6Im9hdXRoIiwidGltZXN0YW1wIjoxNzUxMDU3NTk4fV0sInNlc3Npb25faWQiOiIwNWZkMTY4OC0xNWJlLTRjYWUtYjYyNS1lYWViODRlZWI2MGUiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.CW9TX5chVAepKLVvAh7tiom8MCMRz9wmq0rtfYO0Z-Y"
        self.refresh_token = "eyJpZCI6IjExOjk1OmRmOjEyOjFiOjQ1OjE4OjAwIiwic2VjcmV0IjoiNThkMmNkNTktMjNhZC00ZWJlLTk0YzAtNjY4MzQ2OGQzOWQ4In0="

        # Set environment variables
        os.environ["ESTUARY_ACCESS_TOKEN"] = self.access_token
        os.environ["ESTUARY_REFRESH_TOKEN"] = self.refresh_token

        # Initialize Estuary Flow Manager
        credentials = EstuaryCredentials(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            tenant="Pay_Ready",
        )

        self.manager = EstuaryFlowManager(credentials)

        # Snowflake configuration
        self.snowflake_config = {
            "account": "UHDECNO-CVB64222",
            "user": "SCOOBYJAVA15",
            "password": get_config_value("snowflake_password"),
            "role": "ACCOUNTADMIN",
            "warehouse": "CORTEX_COMPUTE_WH",
            "database": "SOPHIA_AI",
            "schema": "ESTUARY_STAGING",
        }

    def create_snowflake_materialization_config(self):
        """Create optimized Snowflake materialization configuration"""
        logger.info("📊 Creating Snowflake materialization configuration...")

        # Create materialization with bindings for all expected collections
        materialization_config = {
            "materializations": {
                "Pay_Ready/snowflake-sophia-ai": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/materialize-snowflake:dev",
                            "config": {
                                "host": f"{self.snowflake_config['account']}.snowflakecomputing.com",
                                "account": self.snowflake_config["account"],
                                "user": self.snowflake_config["user"],
                                "password": self.snowflake_config["password"],
                                "role": self.snowflake_config["role"],
                                "warehouse": self.snowflake_config["warehouse"],
                                "database": self.snowflake_config["database"],
                                "schema": self.snowflake_config["schema"],
                                "advanced": {
                                    "updateDelay": "0s",  # Real-time processing
                                    "deltaUpdates": True,
                                },
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {"table": "GITHUB_COMMITS"},
                            "source": "Pay_Ready/github-commits",
                        },
                        {
                            "resource": {"table": "GITHUB_PULL_REQUESTS"},
                            "source": "Pay_Ready/github-pull-requests",
                        },
                        {
                            "resource": {"table": "GITHUB_ISSUES"},
                            "source": "Pay_Ready/github-issues",
                        },
                        {
                            "resource": {"table": "HUBSPOT_CONTACTS"},
                            "source": "Pay_Ready/hubspot-contacts",
                        },
                        {
                            "resource": {"table": "HUBSPOT_DEALS"},
                            "source": "Pay_Ready/hubspot-deals",
                        },
                        {
                            "resource": {"table": "HUBSPOT_COMPANIES"},
                            "source": "Pay_Ready/hubspot-companies",
                        },
                        {
                            "resource": {"table": "SLACK_MESSAGES"},
                            "source": "Pay_Ready/slack-messages",
                        },
                        {
                            "resource": {"table": "SLACK_CHANNELS"},
                            "source": "Pay_Ready/slack-channels",
                        },
                    ],
                }
            }
        }

        # Save configuration
        config_file = self.manager.config_dir / "snowflake-materialization.flow.yaml"
        with open(config_file, "w") as f:
            yaml.dump(materialization_config, f, default_flow_style=False)

        logger.info(f"✅ Snowflake materialization config saved to: {config_file}")
        return config_file

    def create_github_capture_config(self):
        """Create GitHub capture configuration"""
        logger.info("🐙 Creating GitHub capture configuration...")

        # GitHub configuration (using placeholder token - will need real token)
        github_config = {
            "captures": {
                "Pay_Ready/github-capture": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/source-github:dev",
                            "config": {
                                "access_token": "${GITHUB_ACCESS_TOKEN}",  # Will be provided via secrets
                                "repository": "ai-cherry/sophia-main",
                                "start_date": "2024-01-01T00:00:00Z",
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {"stream": "commits"},
                            "target": "Pay_Ready/github-commits",
                        },
                        {
                            "resource": {"stream": "pull_requests"},
                            "target": "Pay_Ready/github-pull-requests",
                        },
                        {
                            "resource": {"stream": "issues"},
                            "target": "Pay_Ready/github-issues",
                        },
                    ],
                }
            }
        }

        # Save configuration
        config_file = self.manager.config_dir / "github-capture.flow.yaml"
        with open(config_file, "w") as f:
            yaml.dump(github_config, f, default_flow_style=False)

        logger.info(f"✅ GitHub capture config saved to: {config_file}")
        return config_file

    def create_hubspot_capture_config(self):
        """Create HubSpot capture configuration"""
        logger.info("🎯 Creating HubSpot capture configuration...")

        # HubSpot configuration (using placeholder credentials)
        hubspot_config = {
            "captures": {
                "Pay_Ready/hubspot-capture": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/source-hubspot:dev",
                            "config": {
                                "credentials": {
                                    "credentials_title": "OAuth Credentials",
                                    "client_id": "${HUBSPOT_CLIENT_ID}",
                                    "client_secret": "${HUBSPOT_CLIENT_SECRET}",
                                    "refresh_token": "${HUBSPOT_REFRESH_TOKEN}",
                                },
                                "start_date": "2024-01-01T00:00:00Z",
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {"stream": "contacts"},
                            "target": "Pay_Ready/hubspot-contacts",
                        },
                        {
                            "resource": {"stream": "deals"},
                            "target": "Pay_Ready/hubspot-deals",
                        },
                        {
                            "resource": {"stream": "companies"},
                            "target": "Pay_Ready/hubspot-companies",
                        },
                    ],
                }
            }
        }

        # Save configuration
        config_file = self.manager.config_dir / "hubspot-capture.flow.yaml"
        with open(config_file, "w") as f:
            yaml.dump(hubspot_config, f, default_flow_style=False)

        logger.info(f"✅ HubSpot capture config saved to: {config_file}")
        return config_file

    def create_slack_capture_config(self):
        """Create Slack capture configuration"""
        logger.info("💬 Creating Slack capture configuration...")

        # Slack configuration (using placeholder token)
        slack_config = {
            "captures": {
                "Pay_Ready/slack-capture": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/source-slack:dev",
                            "config": {
                                "api_token": "${SLACK_API_TOKEN}",
                                "start_date": "2024-01-01T00:00:00Z",
                                "channels": [
                                    "general",
                                    "development",
                                    "sales",
                                    "support",
                                ],
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {"stream": "messages"},
                            "target": "Pay_Ready/slack-messages",
                        },
                        {
                            "resource": {"stream": "channels"},
                            "target": "Pay_Ready/slack-channels",
                        },
                    ],
                }
            }
        }

        # Save configuration
        config_file = self.manager.config_dir / "slack-capture.flow.yaml"
        with open(config_file, "w") as f:
            yaml.dump(slack_config, f, default_flow_style=False)

        logger.info(f"✅ Slack capture config saved to: {config_file}")
        return config_file

    def deploy_foundation(self):
        """Deploy complete Estuary Flow foundation"""
        logger.info("🚀 Starting Estuary Flow foundation deployment...")

        try:
            # Step 1: Create all configuration files
            snowflake_config = self.create_snowflake_materialization_config()
            github_config = self.create_github_capture_config()
            hubspot_config = self.create_hubspot_capture_config()
            slack_config = self.create_slack_capture_config()

            # Step 2: Deploy Snowflake materialization first
            logger.info("📊 Deploying Snowflake materialization...")
            result = self.manager.run_flowctl_command(
                ["catalog", "draft", "--source", str(snowflake_config)],
                "Draft Snowflake materialization",
            )

            if result:
                publish_result = self.manager.run_flowctl_command(
                    ["catalog", "publish", "--source", str(snowflake_config)],
                    "Publish Snowflake materialization",
                )

                if publish_result:
                    logger.info("✅ Snowflake materialization deployed successfully")
                else:
                    logger.error("❌ Failed to publish Snowflake materialization")
                    return False
            else:
                logger.error("❌ Failed to draft Snowflake materialization")
                return False

            # Step 3: Deploy captures (these will be ready for when credentials are provided)
            captures = [
                ("GitHub", github_config),
                ("HubSpot", hubspot_config),
                ("Slack", slack_config),
            ]

            for capture_name, config_file in captures:
                logger.info(f"📡 Preparing {capture_name} capture configuration...")
                # Note: We're not deploying these yet as they need real credentials
                # But the configurations are ready for deployment
                logger.info(
                    f"✅ {capture_name} capture configuration ready at: {config_file}"
                )

            # Step 4: Verify deployment
            logger.info("🔍 Verifying deployment...")
            catalog_result = self.manager.run_flowctl_command(
                ["catalog", "list"], "List deployed catalog items"
            )

            if catalog_result:
                logger.info("✅ Deployment verification successful")
                logger.info("📋 Current catalog items:")
                print(json.dumps(catalog_result, indent=2))

            logger.info("🎉 Estuary Flow foundation deployment completed!")
            logger.info("📝 Next steps:")
            logger.info(
                "   1. Add real API credentials to environment variables or Pulumi ESC"
            )
            logger.info(
                "   2. Deploy capture configurations with: flowctl catalog publish --source <config-file>"
            )
            logger.info(
                "   3. Monitor data flow in Snowflake SOPHIA_AI.ESTUARY_STAGING schema"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Foundation deployment failed: {e}")
            return False


def main():
    """Main deployment function"""
    logger.info("🎯 Starting Estuary Flow Foundation Deployment for Sophia AI...")

    deployment = EstuaryFoundationDeployment()
    success = deployment.deploy_foundation()

    if success:
        logger.info("🎉 Estuary Flow foundation deployment completed successfully!")
        logger.info(
            "🔄 Ready for real-time data ingestion with Snowflake Cortex AI processing"
        )
    else:
        logger.error("❌ Deployment failed - check logs for details")

    return success


if __name__ == "__main__":
    main()
