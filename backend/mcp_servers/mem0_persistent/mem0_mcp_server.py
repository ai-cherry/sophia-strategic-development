from mem0 import MemoryClient

from backend.core.config_manager import get_config_value
from backend.core.standardized_mcp_server import StandardizedMCPServer


class Mem0PersistentMCPServer(StandardizedMCPServer):
    def __init__(self):
        super().__init__(
            name="mem0_persistent",
            description="Persistent memory with cross-session learning",
            port=9010,
        )
        self.mem0_client = MemoryClient(api_key=get_config_value("mem0_api_key"))

    async def store_episodic_memory(self, content: str, context: dict) -> str:
        memory_response = await self.mem0_client.add_memory(
            messages=[{"role": "user", "content": content}],
            user_id=context.get("user_id", "system"),
            metadata=context,
        )
        return memory_response.id
