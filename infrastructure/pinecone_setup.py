"""
Pulumi script for setting up Pinecone resources for Sophia AI.
This uses a dynamic provider to create vector indexes via the REST API.
"""
import pulumi
import requests
import json

# --- Configuration ---
config = pulumi.Config("pinecone")
api_key = config.require_secret("api_key")

# Define the indexes we need for our application
INDEXES = {
    "sophia-knowledge-base": {
        "dimension": 384, # From 'all-MiniLM-L6-v2'
        "metric": "cosine",
    },
    "sophia-ai-memory": {
        "dimension": 768, # From 'all-mpnet-base-v2'
        "metric": "cosine",
    }
}

class PineconeIndexProvider(pulumi.dynamic.ResourceProvider):
    """A dynamic provider to manage a Pinecone index via their REST API."""

    def create(self, props):
        """Creates a new Pinecone index."""
        index_name = props["name"]
        headers = {"Api-Key": props["api_key"]}
        
        # Pinecone's control plane URL
        controller_url = "https://controller.pinecone.io/databases"

        # Check if index already exists
        response = requests.get(controller_url, headers=headers)
        response.raise_for_status()
        if index_name in response.json():
            pulumi.log.info(f"Pinecone index '{index_name}' already exists.")
            return pulumi.dynamic.CreateResult(id_=index_name, outs=props)

        # Create the index if it doesn't exist
        payload = {
            "name": index_name,
            "dimension": props["dimension"],
            "metric": props["metric"],
        }
        response = requests.post(controller_url, json=payload, headers=headers)
        response.raise_for_status()
        
        return pulumi.dynamic.CreateResult(id_=index_name, outs=props)

    def delete(self, id, props):
        """Deletes a Pinecone index."""
        headers = {"Api-Key": props["api_key"]}
        controller_url = f"https://controller.pinecone.io/databases/{id}"
        
        response = requests.delete(controller_url, headers=headers)
        # Don't raise for status on delete, as it might already be gone.

class PineconeIndex(pulumi.dynamic.Resource):
    """A Pulumi resource representing a Pinecone Index."""
    def __init__(self, name, api_key, dimension, metric, opts=None):
        super().__init__(
            PineconeIndexProvider(),
            name,
            {
                "name": name,
                "api_key": api_key,
                "dimension": dimension,
                "metric": metric,
            },
            opts=opts
        )

# --- Resource Definitions ---
created_indexes = []
for name, spec in INDEXES.items():
    index = PineconeIndex(name,
        api_key=api_key,
        dimension=spec["dimension"],
        metric=spec["metric"]
    )
    created_indexes.append(index)

# --- Outputs ---
pulumi.export("pinecone_knowledge_base_index", created_indexes[0].name)
pulumi.export("pinecone_ai_memory_index", created_indexes[1].name) 