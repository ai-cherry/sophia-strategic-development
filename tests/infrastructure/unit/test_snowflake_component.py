"""Unit tests for the Snowflake infrastructure component
"""

import os

# Add project root to path to allow imports
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from infrastructure.components.snowflake import SnowflakeComponent


class TestSnowflakeComponent:
    """Unit tests for the Snowflake component.
    These tests verify that the component creates the expected Snowflake resources
    with the correct configuration.
    """

    def test_database_creation(self, pulumi_mock, mock_pulumi_config):
        """Test that the component creates a Snowflake database with the correct parameters.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = SnowflakeComponent("test-snowflake")

            # Assert that a Snowflake database was created
            pulumi_mock.assert_resource_created(
                "snowflake:index/database:Database",
                {
                    "name": "SOPHIA_DB_TEST",
                    "comment": "Database for the Sophia AI platform",
                },
            )

    def test_warehouse_creation(self, pulumi_mock, mock_pulumi_config):
        """Test that the component creates a Snowflake warehouse with the correct parameters.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = SnowflakeComponent("test-snowflake")

            # Assert that a Snowflake warehouse was created
            pulumi_mock.assert_resource_created(
                "snowflake:index/warehouse:Warehouse",
                {
                    "name": "SOPHIA_WH_TEST",
                    "comment": "Warehouse for the Sophia AI platform",
                    "warehouse_size": "X-SMALL",
                    "auto_suspend": 60,
                    "auto_resume": True,
                    "initially_suspended": True,
                },
            )

    def test_schema_creation(self, pulumi_mock, mock_pulumi_config):
        """Test that the component creates a Snowflake schema with the correct parameters.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = SnowflakeComponent("test-snowflake")

            # Assert that a Snowflake schema was created
            pulumi_mock.assert_resource_created(
                "snowflake:index/schema:Schema",
                {
                    "name": "RAW_DATA",
                    "comment": "Schema for raw data ingested from various sources",
                },
            )

    def test_role_creation(self, pulumi_mock, mock_pulumi_config):
        """Test that the component creates a Snowflake role with the correct parameters.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = SnowflakeComponent("test-snowflake")

            # Assert that a Snowflake role was created
            pulumi_mock.assert_resource_created(
                "snowflake:index/role:Role",
                {
                    "name": "SOPHIA_ROLE_TEST",
                    "comment": "Role for Sophia AI application access",
                },
            )

    def test_component_outputs(self, pulumi_mock, mock_pulumi_config):
        """Test that the component exports the expected outputs.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = SnowflakeComponent("test-snowflake")

            # Assert that the component has the expected outputs
            assert "warehouse_name" in component.outputs
            assert "database_name" in component.outputs
            assert "schema_name" in component.outputs
            assert "role_name" in component.outputs

    def test_environment_specific_naming(self, pulumi_mock):
        """Test that the component uses environment-specific naming for resources.
        """
        # Test with different environments
        environments = ["dev", "staging", "production"]

        for env in environments:
            # Mock the Config to return a specific environment
            with patch("pulumi.Config") as mock_config:
                config_instance = MagicMock()
                config_instance.require.return_value = env
                mock_config.return_value = config_instance

                with pulumi_mock.mocked_provider():
                    # Create the component
                    component = SnowflakeComponent("test-snowflake")

                    # Assert that resources are named according to the environment
                    pulumi_mock.assert_resource_created(
                        "snowflake:index/database:Database",
                        {"name": f"SOPHIA_DB_{env.upper()}"},
                    )

                    pulumi_mock.assert_resource_created(
                        "snowflake:index/warehouse:Warehouse",
                        {"name": f"SOPHIA_WH_{env.upper()}"},
                    )

                    pulumi_mock.assert_resource_created(
                        "snowflake:index/role:Role",
                        {"name": f"SOPHIA_ROLE_{env.upper()}"},
                    )
