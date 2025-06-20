"""
Shared fixtures and utilities for infrastructure testing
"""

import os
import uuid
import pytest
import asyncio
import json
from typing import Dict, Any, List, Optional
import pulumi
import pulumi.runtime
from pulumi import automation as auto
from unittest.mock import MagicMock, patch

class PulumiMock:
    """
    A utility class for mocking Pulumi resources during unit tests.
    This allows testing infrastructure components without actually creating resources.
    """
    
    def __init__(self):
        self.mocks = pulumi.runtime.Mocks()
        self.resources = []
        
        # Override the resource creation function to track created resources
        def new_resource_mock(type_, name, inputs, provider, id_):
            self.resources.append({
                "type": type_,
                "name": name,
                "inputs": inputs,
                "provider": provider,
                "id": id_ or f"{name}-{uuid.uuid4()}"
            })
            return {
                "id": id_ or f"{name}-{uuid.uuid4()}",
                "urn": f"urn:pulumi:{pulumi.get_stack()}::{pulumi.get_project()}::{type_}::{name}",
                "state": inputs
            }
        
        self.mocks.new_resource = new_resource_mock
        
        # Override the call function to return mock outputs
        def call_mock(token, args, provider, version):
            return args
        
        self.mocks.call = call_mock
    
    def mocked_provider(self):
        """
        Returns a context manager that sets up the Pulumi mocks for testing.
        
        Usage:
            with pulumi_mock.mocked_provider():
                # Create resources using Pulumi
                component = MyComponent("test")
                # Assert resources were created correctly
        """
        return patch('pulumi.runtime._set_mocks', return_value=self.mocks)
    
    def assert_resource_created(self, resource_type: str, expected_inputs: Dict[str, Any]):
        """
        Asserts that a resource of the specified type was created with the expected inputs.
        
        Args:
            resource_type: The type of resource to check for (e.g., "aws:s3/bucket:Bucket")
            expected_inputs: A dictionary of expected input values
        
        Raises:
            AssertionError: If no matching resource was found
        """
        for resource in self.resources:
            if resource["type"] == resource_type:
                inputs = resource["inputs"]
                for key, value in expected_inputs.items():
                    assert key in inputs, f"Expected input '{key}' not found in resource inputs"
                    assert inputs[key] == value, f"Expected input '{key}' to be '{value}', got '{inputs[key]}'"
                return
        
        raise AssertionError(f"No resource of type '{resource_type}' was created")
    
    def get_resources_by_type(self, resource_type: str) -> List[Dict[str, Any]]:
        """
        Returns all resources of the specified type that were created.
        
        Args:
            resource_type: The type of resource to filter by
        
        Returns:
            A list of resource dictionaries
        """
        return [r for r in self.resources if r["type"] == resource_type]


class TestEnvironmentManager:
    """
    A utility class for creating and managing isolated test environments.
    This allows running tests without affecting production resources.
    """
    
    def __init__(self):
        self.stacks = []
    
    def create_test_stack(self, name_prefix: str) -> str:
        """
        Creates a new Pulumi stack for testing.
        
        Args:
            name_prefix: A prefix for the stack name
        
        Returns:
            The name of the created stack
        """
        # Generate a unique stack name
        stack_name = f"{name_prefix}-{uuid.uuid4().hex[:8]}"
        self.stacks.append(stack_name)
        
        # Create the stack
        stack = auto.create_or_select_stack(
            stack_name=stack_name,
            project_name="sophia-iac-test",
            program=lambda: None  # Empty program initially
        )
        
        # Set stack configuration for testing
        stack.set_config("environment", auto.ConfigValue(value="test"))
        
        return stack_name
    
    def cleanup_test_stack(self, stack_name: str):
        """
        Cleans up a test stack by destroying all resources.
        
        Args:
            stack_name: The name of the stack to clean up
        """
        if stack_name in self.stacks:
            try:
                stack = auto.select_stack(
                    stack_name=stack_name,
                    project_name="sophia-iac-test",
                    program=lambda: None
                )
                
                # Destroy all resources in the stack
                stack.destroy(on_output=lambda msg: None)
                
                # Remove the stack
                stack.workspace.remove_stack(stack_name)
                
                self.stacks.remove(stack_name)
            except Exception as e:
                print(f"Error cleaning up stack {stack_name}: {e}")
    
    def __del__(self):
        """
        Ensures all test stacks are cleaned up when the manager is garbage collected.
        """
        for stack_name in list(self.stacks):
            self.cleanup_test_stack(stack_name)


# Common fixtures for infrastructure tests

@pytest.fixture
def pulumi_mock():
    """
    Fixture that provides a PulumiMock instance for unit testing.
    """
    return PulumiMock()

@pytest.fixture
def test_env_manager():
    """
    Fixture that provides a TestEnvironmentManager instance for integration testing.
    """
    manager = TestEnvironmentManager()
    yield manager
    # Cleanup is handled by the manager's __del__ method

@pytest.fixture
def mock_pulumi_config():
    """
    Fixture that mocks the Pulumi Config class for testing.
    """
    with patch('pulumi.Config') as mock_config:
        # Set up the mock to return test values
        config_instance = MagicMock()
        config_instance.require.side_effect = lambda key: {
            "environment": "test",
            "region": "us-west-2",
            "instance_type": "t3.micro"
        }.get(key, f"test-value-for-{key}")
        
        mock_config.return_value = config_instance
        yield mock_config

@pytest.fixture
def mock_snowflake_client():
    """
    Fixture that provides a mock Snowflake client for testing.
    """
    class MockSnowflakeClient:
        def __init__(self, connection_string=None):
            self.connection_string = connection_string
            self.queries = []
            self.data = {}
        
        def test_connection(self):
            return True
        
        def query(self, sql):
            self.queries.append(sql)
            if "COUNT(*)" in sql:
                return [{"COUNT(*)": len(self.data.get("test_table", []))}]
            return []
        
        def execute(self, sql):
            self.queries.append(sql)
            if sql.startswith("DELETE"):
                table = sql.split("FROM")[1].strip()
                self.data[table] = []
            return True
        
        def insert_data(self, table, data):
            if table not in self.data:
                self.data[table] = []
            self.data[table].extend(data)
        
        def create_backup(self, name):
            backup_id = f"backup-{uuid.uuid4().hex[:8]}"
            self.data[f"backup_{backup_id}"] = {
                table: data.copy() for table, data in self.data.items()
            }
            return backup_id
        
        def restore_backup(self, backup_id):
            backup_data = self.data.get(f"backup_{backup_id}")
            if backup_data:
                for table, data in backup_data.items():
                    self.data[table] = data.copy()
    
    return MockSnowflakeClient()

@pytest.fixture
def mock_pinecone_client():
    """
    Fixture that provides a mock Pinecone client for testing.
    """
    class MockPineconeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.indexes = {}
            self.vectors = {}
        
        def test_connection(self):
            return True
        
        def create_index(self, name, dimension):
            self.indexes[name] = {"dimension": dimension, "created_at": "2025-06-20T00:00:00Z"}
            self.vectors[name] = []
        
        def delete_index(self, name):
            if name in self.indexes:
                del self.indexes[name]
                del self.vectors[name]
        
        def list_indexes(self):
            class IndexList:
                def __init__(self, indexes):
                    self._indexes = indexes
                
                def names(self):
                    return list(self._indexes.keys())
            
            return IndexList(self.indexes)
        
        def generate_test_vectors(self, count=100, index_name="test-index"):
            if index_name not in self.indexes:
                self.create_index(index_name, 128)
            
            import random
            for i in range(count):
                self.vectors[index_name].append({
                    "id": f"vec-{i}",
                    "values": [random.random() for _ in range(128)],
                    "metadata": {"test": f"data-{i}"}
                })
        
        def search(self, vector, top_k=10, index_name="test-index"):
            if index_name not in self.vectors or not self.vectors[index_name]:
                return {"matches": []}
            
            # Simulate vector search by returning random vectors
            import random
            matches = random.sample(self.vectors[index_name], min(top_k, len(self.vectors[index_name])))
            return {
                "matches": [
                    {"id": m["id"], "score": random.random(), "metadata": m["metadata"]}
                    for m in matches
                ]
            }
    
    return MockPineconeClient()

@pytest.fixture
def mock_gong_client():
    """
    Fixture that provides a mock Gong client for testing.
    """
    class MockGongClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.calls = []
        
        def test_connection(self):
            return True
        
        def send_test_data(self, data):
            self.calls.append(data)
            return {"status": "success", "call_id": data.get("call_id", f"call-{uuid.uuid4().hex[:8]}")}
        
        def get_calls(self, limit=10):
            return self.calls[:limit]
    
    return MockGongClient()
