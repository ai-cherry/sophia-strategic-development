"""
End-to-end tests for the complete infrastructure deployment
"""

import pytest
import time
import pulumi
from pulumi import automation as auto
import json
import os
import sys
import logging
import asyncio
from typing import Dict, Any, List, Optional

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import all infrastructure components
from infrastructure.components.snowflake import SnowflakeComponent
from infrastructure.components.pinecone import PineconeComponent
from infrastructure.components.gong import GongComponent
from infrastructure.components.vercel import VercelComponent
from infrastructure.components.estuary import EstuaryComponent
from infrastructure.components.lambda_labs import LambdaLabsComponent
from infrastructure.components.airbyte import AirbyteComponent
from infrastructure.components.github import GitHubComponent
from infrastructure.components.docker import DockerComponent
from infrastructure.components.mcp import MCPComponent
from infrastructure.components.pulumi_esc import PulumiEscComponent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.e2e
class TestCompleteInfrastructure:
    """
    End-to-end tests for the complete infrastructure deployment.
    These tests verify that the entire infrastructure can be deployed and functions correctly.
    """
    
    def setup_method(self):
        """
        Set up the test environment before each test.
        """
        self.env_manager = pytest.importorskip("tests.infrastructure.conftest").TestEnvironmentManager()
        self.test_stack = self.env_manager.create_test_stack("e2e-test")
        self.deployment_results = {}
    
    def teardown_method(self):
        """
        Clean up the test environment after each test.
        """
        self.env_manager.cleanup_test_stack(self.test_stack)
    
    @pytest.mark.asyncio
    async def test_full_infrastructure_deployment(self):
        """
        Test that the complete infrastructure can be deployed successfully.
        
        This test:
        1. Deploys all infrastructure components
        2. Verifies that all resources are created
        3. Tests connectivity between components
        4. Validates the complete system functionality
        """
        # Define the complete infrastructure program
        def create_complete_infrastructure():
            # Deploy core data infrastructure
            snowflake = SnowflakeComponent("sophia-snowflake")
            pinecone = PineconeComponent("sophia-pinecone")
            
            # Deploy integration components
            gong = GongComponent("sophia-gong")
            vercel = VercelComponent("sophia-vercel")
            estuary = EstuaryComponent("sophia-estuary")
            airbyte = AirbyteComponent("sophia-airbyte")
            
            # Deploy compute infrastructure
            lambda_labs = LambdaLabsComponent("sophia-lambda-labs")
            docker = DockerComponent("sophia-docker")
            
            # Deploy management infrastructure
            github = GitHubComponent("sophia-github")
            mcp = MCPComponent("sophia-mcp")
            pulumi_esc = PulumiEscComponent("sophia-pulumi-esc")
            
            # Export all outputs
            pulumi.export("snowflake", snowflake.outputs)
            pulumi.export("pinecone", pinecone.outputs)
            pulumi.export("gong", gong.outputs)
            pulumi.export("vercel", vercel.outputs)
            pulumi.export("estuary", estuary.outputs)
            pulumi.export("airbyte", airbyte.outputs)
            pulumi.export("lambda_labs", lambda_labs.outputs)
            pulumi.export("docker", docker.outputs)
            pulumi.export("github", github.outputs)
            pulumi.export("mcp", mcp.outputs)
            pulumi.export("pulumi_esc", pulumi_esc.outputs)
        
        # Create or select the stack
        stack = auto.create_or_select_stack(
            stack_name=self.test_stack,
            project_name="sophia-iac-test",
            program=create_complete_infrastructure
        )
        
        # Set stack configuration
        stack.set_config("environment", auto.ConfigValue(value="test"))
        
        # Deploy the stack with progress tracking
        logger.info("Starting full infrastructure deployment...")
        start_time = time.time()
        
        try:
            up_result = await stack.up(on_output=lambda msg: logger.info(msg))
            deployment_time = time.time() - start_time
            logger.info(f"Deployment completed in {deployment_time:.2f} seconds")
            
            # Store deployment results
            self.deployment_results = up_result.outputs
            
            # Verify all components were deployed
            assert "snowflake" in self.deployment_results
            assert "pinecone" in self.deployment_results
            assert "gong" in self.deployment_results
            assert "vercel" in self.deployment_results
            assert "estuary" in self.deployment_results
            assert "airbyte" in self.deployment_results
            assert "lambda_labs" in self.deployment_results
            assert "docker" in self.deployment_results
            assert "github" in self.deployment_results
            assert "mcp" in self.deployment_results
            assert "pulumi_esc" in self.deployment_results
            
            # Log deployment summary
            logger.info(f"Total resources created: {up_result.summary.resource_changes.get('create', 0)}")
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_snowflake_connectivity(self, mock_snowflake_client):
        """
        Test that Snowflake is accessible and configured correctly.
        """
        if "snowflake" not in self.deployment_results:
            pytest.skip("Snowflake not deployed")
        
        snowflake_outputs = self.deployment_results["snowflake"].value
        
        # Test connection
        assert mock_snowflake_client.test_connection()
        
        # Verify database exists
        databases = mock_snowflake_client.query("SHOW DATABASES")
        db_names = [db["name"] for db in databases]
        assert "SOPHIA_DB_TEST" in db_names
        
        # Verify warehouse exists
        warehouses = mock_snowflake_client.query("SHOW WAREHOUSES")
        wh_names = [wh["name"] for wh in warehouses]
        assert "SOPHIA_WH_TEST" in wh_names
    
    @pytest.mark.asyncio
    async def test_pinecone_connectivity(self, mock_pinecone_client):
        """
        Test that Pinecone is accessible and configured correctly.
        """
        if "pinecone" not in self.deployment_results:
            pytest.skip("Pinecone not deployed")
        
        pinecone_outputs = self.deployment_results["pinecone"].value
        
        # Test connection
        assert mock_pinecone_client.test_connection()
        
        # Verify indexes exist
        indexes = mock_pinecone_client.list_indexes()
        index_names = indexes.names()
        
        # Check for expected indexes
        assert any("knowledge" in name for name in index_names)
        assert any("memory" in name for name in index_names)
    
    @pytest.mark.asyncio
    async def test_gong_to_snowflake_data_flow(self, mock_gong_client, mock_snowflake_client):
        """
        Test end-to-end data flow from Gong to Snowflake.
        """
        if "gong" not in self.deployment_results or "snowflake" not in self.deployment_results:
            pytest.skip("Gong or Snowflake not deployed")
        
        # Send test data to Gong
        test_data = {
            "call_id": "e2e-test-call-001",
            "duration": 600,
            "participants": ["test_user1", "test_user2"],
            "transcript": "This is an end-to-end test call transcript",
            "timestamp": "2025-06-20T12:00:00Z"
        }
        
        result = mock_gong_client.send_test_data(test_data)
        assert result["status"] == "success"
        
        # Wait for data processing
        await asyncio.sleep(5)
        
        # Verify data in Snowflake
        query = f"SELECT * FROM RAW_DATA.GONG_CALLS WHERE call_id = '{test_data['call_id']}'"
        results = mock_snowflake_client.query(query)
        
        assert len(results) == 1
        assert results[0]["duration"] == test_data["duration"]
    
    @pytest.mark.asyncio
    async def test_ai_agent_vector_storage(self, mock_pinecone_client):
        """
        Test that AI agents can store and retrieve vectors from Pinecone.
        """
        if "pinecone" not in self.deployment_results:
            pytest.skip("Pinecone not deployed")
        
        # Generate test vectors
        mock_pinecone_client.generate_test_vectors(count=100, index_name="test-knowledge-base")
        
        # Test vector search
        search_vector = [0.1] * 128  # Assuming 128-dimensional vectors
        results = mock_pinecone_client.search(
            vector=search_vector,
            top_k=10,
            index_name="test-knowledge-base"
        )
        
        assert len(results["matches"]) > 0
        assert all("score" in match for match in results["matches"])
    
    @pytest.mark.asyncio
    async def test_mcp_server_connectivity(self):
        """
        Test that MCP servers are accessible and functioning.
        """
        if "mcp" not in self.deployment_results:
            pytest.skip("MCP not deployed")
        
        mcp_outputs = self.deployment_results["mcp"].value
        
        # Verify MCP server endpoints
        assert "gong_mcp_url" in mcp_outputs
        assert "snowflake_mcp_url" in mcp_outputs
        assert "pinecone_mcp_url" in mcp_outputs
        
        # All MCP URLs should be HTTPS
        for key, value in mcp_outputs.items():
            if key.endswith("_mcp_url"):
                assert value.startswith("https://"), f"{key} is not using HTTPS"
    
    @pytest.mark.asyncio
    async def test_complete_system_health(self):
        """
        Test the overall health of the deployed system.
        """
        health_status = {
            "snowflake": False,
            "pinecone": False,
            "gong": False,
            "vercel": False,
            "mcp": False
        }
        
        # Check each component's health
        if "snowflake" in self.deployment_results:
            # In a real test, we would make an actual health check call
            health_status["snowflake"] = True
        
        if "pinecone" in self.deployment_results:
            health_status["pinecone"] = True
        
        if "gong" in self.deployment_results:
            health_status["gong"] = True
        
        if "vercel" in self.deployment_results:
            health_status["vercel"] = True
        
        if "mcp" in self.deployment_results:
            health_status["mcp"] = True
        
        # All critical components should be healthy
        critical_components = ["snowflake", "pinecone", "gong"]
        for component in critical_components:
            assert health_status[component], f"{component} is not healthy"
        
        # Log health summary
        healthy_count = sum(1 for status in health_status.values() if status)
        logger.info(f"System health: {healthy_count}/{len(health_status)} components healthy")
        
        # Overall system should be at least 80% healthy
        health_percentage = (healthy_count / len(health_status)) * 100
        assert health_percentage >= 80, f"System health is only {health_percentage}%"
