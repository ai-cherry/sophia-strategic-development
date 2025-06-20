"""Integration tests for Snowflake and Gong components
"""

import os
import sys
import time

import pulumi
import pytest
from pulumi import automation as auto

# Add project root to path to allow imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from infrastructure.components.gong import GongComponent
from infrastructure.components.snowflake import SnowflakeComponent


@pytest.mark.integration
class TestSnowflakeGongIntegration:
    """Integration tests for the Snowflake and Gong components.
    These tests verify that data flows correctly from Gong to Snowflake.
    """

    def setup_method(self):
        """Set up the test environment before each test.
        """
        self.env_manager = pytest.importorskip(
            "tests.infrastructure.conftest"
        ).TestEnvironmentManager()
        self.test_stack = self.env_manager.create_test_stack("snowflake-gong-test")

    def teardown_method(self):
        """Clean up the test environment after each test.
        """
        self.env_manager.cleanup_test_stack(self.test_stack)

    @pytest.mark.asyncio
    async def test_gong_data_flow_to_snowflake(
        self, mock_snowflake_client, mock_gong_client
    ):
        """Test that data flows correctly from Gong to Snowflake.

        This test:
        1. Creates a test stack with Snowflake and Gong components
        2. Sends test data to Gong
        3. Verifies that the data appears in Snowflake
        """

        # Define a simple program that creates Snowflake and Gong components
        def create_test_components():
            snowflake = SnowflakeComponent("test-snowflake")
            gong = GongComponent("test-gong")

            # Export outputs
            pulumi.export("snowflake", snowflake.outputs)
            pulumi.export("gong", gong.outputs)

        # Create or select the stack
        stack = auto.create_or_select_stack(
            stack_name=self.test_stack,
            project_name="sophia-iac-test",
            program=create_test_components,
        )

        # Set stack configuration
        stack.set_config("environment", auto.ConfigValue(value="test"))

        # Deploy the stack
        up_result = await stack.up()

        # Get the outputs
        snowflake_outputs = up_result.outputs.get("snowflake").value
        gong_outputs = up_result.outputs.get("gong").value

        # Create test data
        test_data = {
            "call_id": "test-123",
            "duration": 300,
            "participants": ["user1", "user2"],
            "transcript": "This is a test transcript",
            "timestamp": "2025-06-20T00:00:00Z",
        }

        # Send test data to Gong
        mock_gong_client.send_test_data(test_data)

        # Wait for data to flow through the pipeline
        # In a real test, we would use a more sophisticated approach to wait for the data
        time.sleep(2)

        # Query Snowflake to verify the data was received
        query = f"SELECT * FROM gong_calls WHERE call_id = '{test_data['call_id']}'"
        result = mock_snowflake_client.query(query)

        # Assert that the data was received
        assert len(result) == 1, "Data was not found in Snowflake"
        assert result[0]["duration"] == test_data["duration"], "Duration does not match"
        assert (
            result[0]["transcript"] == test_data["transcript"]
        ), "Transcript does not match"

    @pytest.mark.asyncio
    async def test_gong_webhook_configuration(self, mock_gong_client):
        """Test that the Gong component configures webhooks correctly.

        This test:
        1. Creates a test stack with Gong component
        2. Verifies that the webhook URL is configured correctly
        """

        # Define a simple program that creates a Gong component
        def create_gong_component():
            gong = GongComponent("test-gong")

            # Export outputs
            pulumi.export("gong", gong.outputs)

        # Create or select the stack
        stack = auto.create_or_select_stack(
            stack_name=self.test_stack,
            project_name="sophia-iac-test",
            program=create_gong_component,
        )

        # Set stack configuration
        stack.set_config("environment", auto.ConfigValue(value="test"))

        # Deploy the stack
        up_result = await stack.up()

        # Get the outputs
        gong_outputs = up_result.outputs.get("gong").value

        # Assert that the webhook URL is configured
        assert "webhook_url" in gong_outputs, "Webhook URL not found in outputs"
        assert gong_outputs["webhook_url"].startswith(
            "https://"
        ), "Webhook URL is not HTTPS"

    @pytest.mark.asyncio
    async def test_snowflake_schema_for_gong_data(self, mock_snowflake_client):
        """Test that the Snowflake component creates the correct schema for Gong data.

        This test:
        1. Creates a test stack with Snowflake component
        2. Verifies that the schema includes tables for Gong data
        """

        # Define a simple program that creates a Snowflake component
        def create_snowflake_component():
            snowflake = SnowflakeComponent("test-snowflake")

            # Export outputs
            pulumi.export("snowflake", snowflake.outputs)

        # Create or select the stack
        stack = auto.create_or_select_stack(
            stack_name=self.test_stack,
            project_name="sophia-iac-test",
            program=create_snowflake_component,
        )

        # Set stack configuration
        stack.set_config("environment", auto.ConfigValue(value="test"))

        # Deploy the stack
        up_result = await stack.up()

        # Get the outputs
        snowflake_outputs = up_result.outputs.get("snowflake").value

        # Query Snowflake to verify the schema
        tables_query = "SHOW TABLES IN SCHEMA RAW_DATA"
        tables = mock_snowflake_client.query(tables_query)

        # Assert that the schema includes tables for Gong data
        table_names = [table["name"] for table in tables]
        assert "GONG_CALLS" in table_names, "GONG_CALLS table not found"
        assert "GONG_TRANSCRIPTS" in table_names, "GONG_TRANSCRIPTS table not found"

        # Query the table structure to verify it has the correct columns
        columns_query = "DESCRIBE TABLE RAW_DATA.GONG_CALLS"
        columns = mock_snowflake_client.query(columns_query)

        # Assert that the table has the expected columns
        column_names = [column["name"] for column in columns]
        expected_columns = ["CALL_ID", "DURATION", "TIMESTAMP", "PARTICIPANTS"]
        for column in expected_columns:
            assert (
                column in column_names
            ), f"{column} column not found in GONG_CALLS table"
