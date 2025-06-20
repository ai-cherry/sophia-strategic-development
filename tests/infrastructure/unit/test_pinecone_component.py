"""
Unit tests for the Pinecone infrastructure component
"""

import pytest
from unittest.mock import patch, MagicMock
import pulumi

# Add project root to path to allow imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from infrastructure.components.pinecone import PineconeComponent


class TestPineconeComponent:
    """
    Unit tests for the Pinecone component.
    These tests verify that the component creates the expected Pinecone resources
    with the correct configuration.
    """
    
    def test_knowledge_base_index_creation(self, pulumi_mock, mock_pulumi_config):
        """
        Test that the component creates a knowledge base index with the correct parameters.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = PineconeComponent("test-pinecone")
            
            # Assert that a Pinecone index was created for the knowledge base
            # Note: Since Pinecone doesn't have a native Pulumi provider, we're likely using
            # a custom resource or dynamic provider. The exact resource type may vary.
            resources = pulumi_mock.get_resources_by_type("sophia:pinecone:Index")
            
            # Find the knowledge base index
            kb_index = None
            for resource in resources:
                if "knowledge_base" in resource["name"]:
                    kb_index = resource
                    break
            
            assert kb_index is not None, "Knowledge base index was not created"
            assert "dimension" in kb_index["inputs"], "Index dimension not specified"
            assert "name" in kb_index["inputs"], "Index name not specified"
    
    def test_ai_memory_index_creation(self, pulumi_mock, mock_pulumi_config):
        """
        Test that the component creates an AI memory index with the correct parameters.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = PineconeComponent("test-pinecone")
            
            # Assert that a Pinecone index was created for AI memory
            resources = pulumi_mock.get_resources_by_type("sophia:pinecone:Index")
            
            # Find the AI memory index
            memory_index = None
            for resource in resources:
                if "memory" in resource["name"]:
                    memory_index = resource
                    break
            
            assert memory_index is not None, "AI memory index was not created"
            assert "dimension" in memory_index["inputs"], "Index dimension not specified"
            assert "name" in memory_index["inputs"], "Index name not specified"
    
    def test_component_outputs(self, pulumi_mock, mock_pulumi_config):
        """
        Test that the component exports the expected outputs.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = PineconeComponent("test-pinecone")
            
            # Assert that the component has the expected outputs
            assert "knowledge_base_index" in component.outputs
            assert "ai_memory_index" in component.outputs
    
    def test_environment_specific_naming(self, pulumi_mock):
        """
        Test that the component uses environment-specific naming for resources.
        """
        # Test with different environments
        environments = ["dev", "staging", "production"]
        
        for env in environments:
            # Mock the Config to return a specific environment
            with patch('pulumi.Config') as mock_config:
                config_instance = MagicMock()
                config_instance.require.return_value = env
                mock_config.return_value = config_instance
                
                with pulumi_mock.mocked_provider():
                    # Create the component
                    component = PineconeComponent("test-pinecone")
                    
                    # Assert that resources are named according to the environment
                    resources = pulumi_mock.get_resources_by_type("sophia:pinecone:Index")
                    
                    # Check that index names include the environment
                    for resource in resources:
                        if "name" in resource["inputs"]:
                            assert env in resource["inputs"]["name"].lower(), \
                                f"Environment '{env}' not found in index name: {resource['inputs']['name']}"
    
    def test_index_dimension_configuration(self, pulumi_mock, mock_pulumi_config):
        """
        Test that the component configures the correct vector dimensions for indices.
        """
        with pulumi_mock.mocked_provider():
            # Create the component
            component = PineconeComponent("test-pinecone")
            
            # Assert that indices have the correct dimensions
            resources = pulumi_mock.get_resources_by_type("sophia:pinecone:Index")
            
            for resource in resources:
                assert "dimension" in resource["inputs"], "Index dimension not specified"
                # Typical embedding dimensions are 768, 1024, 1536, etc.
                assert resource["inputs"]["dimension"] >= 128, "Index dimension is too small"
