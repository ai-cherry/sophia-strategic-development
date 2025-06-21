import pulumi.dynamic
from pulumi import ResourceOptions

from .base_component import BaseComponent


class PineconeIndexProvider(pulumi.dynamic.ResourceProvider):
    def create(self, props):
        # ... (Provider logic remains the same)
        pass  # Placeholder for brevity

    def delete(self, id, props):
        # ... (Provider logic remains the same)
        pass  # Placeholder for brevity


class PineconeIndex(pulumi.dynamic.Resource):
    # ... (Dynamic resource class remains the same)
    pass  # Placeholder for brevity


class PineconeComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = pulumi.Config("pinecone")
        api_key = config.require_secret("api_key")

        INDEXES = {
            "sophia-knowledge-base": {"dimension": 384, "metric": "cosine"},
            "sophia-ai-memory": {"dimension": 768, "metric": "cosine"},
        }

        self.indexes = []
        for name, spec in INDEXES.items():
            index = PineconeIndex(
                name,
                api_key=api_key,
                dimension=spec["dimension"],
                metric=spec["metric"],
                opts=component_opts,
            )
            self.indexes.append(index)

        self.register_outputs(
            {
                "knowledge_base_index": self.indexes[0].name,
                "ai_memory_index": self.indexes[1].name,
            }
        )
