import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import os
from pathlib import Path

from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import BaseChatMessageHistory

from ...core.secret_manager import secret_manager
from backend.core.comprehensive_memory_manager import comprehensive_memory_manager, MemoryRequest, MemoryOperationType


logger = logging.getLogger(__name__)

class PersistentMemory:
    """
    A simple file-based persistent memory store for agents.
    Each agent's memory is stored in a separate JSON file.
    """
    def __init__(self, storage_path: str = "./agent_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.lock = asyncio.Lock()

    def _get_agent_memory_file(self, agent_id: str) -> Path:
        """Gets the memory file path for a given agent."""
        return self.storage_path / f"{agent_id}_memory.json"

    async def _read_memory(self, agent_id: str) -> Dict[str, Any]:
        """Reads the entire memory for an agent."""
        memory_file = self._get_agent_memory_file(agent_id)
        if not memory_file.exists():
            return {}
        
        async with self.lock:
            with open(memory_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}

    async def _write_memory(self, agent_id: str, memory_data: Dict[str, Any]):
        """Writes the entire memory for an agent."""
        memory_file = self._get_agent_memory_file(agent_id)
        async with self.lock:
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)

    async def store_memory(self, agent_id: str, memory_type: str, content: Any, metadata: Optional[Dict[str, Any]] = None):
        """Stores a specific piece of memory for an agent."""
        memory_data = await self._read_memory(agent_id)
        if memory_type not in memory_data:
            memory_data[memory_type] = []
        
        memory_data[memory_type].append({
            "content": content,
            "metadata": metadata or {}
        })
        await self._write_memory(agent_id, memory_data)

    async def retrieve_memories(self, agent_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves memories. This is a simple implementation that returns the latest memories.
        A real implementation would have more sophisticated querying.
        """
        memory_data = await self._read_memory(agent_id)
        all_memories = []
        for mem_type in memory_data:
            all_memories.extend(memory_data[mem_type])
        
        # Return the most recent memories, regardless of query for this simple version
        return all_memories[-limit:]

class Mem0PersistentMemory(PersistentMemory):
    """Persistent memory using mem0 for long-term context"""
    
    def __init__(self, agent_id: str, memory_type: str = "buffer", redis_url: Optional[str] = None, ttl: int = 86400, mem0_url: Optional[str] = None):
        """
        Initialize mem0 persistent memory
        
        Args:
            agent_id: Unique identifier for the agent
            memory_type: Type of memory to use ("buffer" or "summary")
            redis_url: Redis URL for persistent storage (if None, will use environment variable)
            ttl: Time to live for memory in seconds (default: 24 hours)
            mem0_url: mem0 API URL (if None, will use environment variable)
        """
        super().__init__(agent_id, memory_type, redis_url, ttl)
        self.mem0_url = mem0_url
        self.mem0_client = None
        
    async def initialize(self):
        """Initialize the memory"""
        await super().initialize()
        
        try:
            # Get mem0 URL if not provided
            if not self.mem0_url:
                self.mem0_url = os.environ.get("MEM0_URL")
                
                if not self.mem0_url:
                    # Try to get from secret manager
                    try:
                        self.mem0_url = await secret_manager.get_secret("mem0_url", "memory")
                    except Exception:
                        # Default to local mem0
                        self.mem0_url = "http://localhost:8000"
            
            # Initialize mem0 client
            import aiohttp
            
            self.mem0_client = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            self.logger.info(f"Initialized mem0 persistent memory for agent {self.agent_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize mem0 persistent memory: {e}")
            raise
    
    async def close(self):
        """Close the memory"""
        if self.mem0_client:
            await self.mem0_client.close()
            self.mem0_client = None
    
    async def add_user_message(self, message: str):
        """Add a user message to the memory"""
        await super().add_user_message(message)
        
        # Also add to mem0
        await self._add_to_mem0("user", message)
    
    async def add_ai_message(self, message: str):
        """Add an AI message to the memory"""
        await super().add_ai_message(message)
        
        # Also add to mem0
        await self._add_to_mem0("ai", message)
    
    async def _add_to_mem0(self, role: str, message: str):
        """Add a message to mem0"""
        if not self.mem0_client:
            return
        
        try:
            # Prepare payload
            payload = {
                "agent_id": self.agent_id,
                "role": role,
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to mem0
            async with self.mem0_client.post(f"{self.mem0_url}/api/memory", json=payload) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    self.logger.error(f"Failed to add message to mem0: {response.status} - {response_text}")
                    
        except Exception as e:
            self.logger.error(f"Error adding message to mem0: {e}")
    
    async def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant messages"""
        if not self.mem0_client:
            await self.initialize()
        
        try:
            # Prepare payload
            payload = {
                "agent_id": self.agent_id,
                "query": query,
                "limit": limit
            }
            
            # Send to mem0
            async with self.mem0_client.post(f"{self.mem0_url}/api/memory/search", json=payload) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    self.logger.error(f"Failed to search mem0: {response.status} - {response_text}")
                    return []
                
                result = await response.json()
                return result.get("results", [])
                
        except Exception as e:
            self.logger.error(f"Error searching mem0: {e}")
            return []
    
    async def get_relevant_context(self, query: str, limit: int = 5) -> str:
        """Get relevant context for a query"""
        results = await self.search_memory(query, limit)
        
        if not results:
            return ""
        
        # Format results as context
        context = "Relevant past interactions:\n\n"
        
        for result in results:
            role = result.get("role", "unknown")
            content = result.get("content", "")
            timestamp = result.get("timestamp", "")
            
            if role == "user":
                context += f"User ({timestamp}): {content}\n"
            elif role == "ai":
                context += f"AI ({timestamp}): {content}\n"
            else:
                context += f"{role.capitalize()} ({timestamp}): {content}\n"
            
            context += "\n"
        
        return context
    
    async def load_memory_variables(self) -> Dict[str, Any]:
        """Load memory variables"""
        variables = await super().load_memory_variables()
        
        # Add mem0 context
        try:
            # Get most recent messages as context
            recent_context = await self.get_relevant_context("recent", 3)
            
            if recent_context:
                variables["long_term_memory"] = recent_context
                
        except Exception as e:
            self.logger.error(f"Error loading mem0 variables: {e}")
        
        return variables

class VectorPersistentMemory(PersistentMemory):
    """Persistent memory using vector database for long-term context"""
    
    def __init__(self, agent_id: str, memory_type: str = "buffer", redis_url: Optional[str] = None, ttl: int = 86400, vector_db: str = "pinecone", collection: Optional[str] = None):
        """
        Initialize vector persistent memory
        
        Args:
            agent_id: Unique identifier for the agent
            memory_type: Type of memory to use ("buffer" or "summary")
            redis_url: Redis URL for persistent storage (if None, will use environment variable)
            ttl: Time to live for memory in seconds (default: 24 hours)
            vector_db: Vector database to use ("pinecone" or "weaviate")
            collection: Collection or namespace to use (if None, will use agent_id)
        """
        super().__init__(agent_id, memory_type, redis_url, ttl)
        self.vector_db = vector_db
        self.collection = collection or f"sophia_memory_{agent_id}"
        self.pinecone_client = None
        self.weaviate_client = None
        self.openai_client = None
        
    async def initialize(self):
        """Initialize the memory"""
        await super().initialize()
        
        try:
            # Initialize vector database client
            if self.vector_db == "pinecone":
                import pinecone
                
                api_key = await secret_manager.get_secret("api_key", "pinecone")
                environment = os.environ.get("PINECONE_ENVIRONMENT", "us-east1-gcp")
                
                # Replaced pinecone.init with ComprehensiveMemoryManager
# Original: # Replaced pinecone.init with ComprehensiveMemoryManager
# Original: pinecone.init(api_key=api_key, environment=environment)
                
                index_name = os.environ.get("PINECONE_INDEX", "sophia-index")
                self.# Replaced pinecone.Index with ComprehensiveMemoryManager
# Original: # Replaced pinecone.Index with ComprehensiveMemoryManager
# Original: pinecone_client = pinecone.Index(index_name)
pinecone_client = comprehensive_memory_manager
pinecone_client = comprehensive_memory_manager
                
            elif self.vector_db == "weaviate":
                import weaviate
                
                api_key = await secret_manager.get_secret("api_key", "weaviate")
                url = os.environ.get("WEAVIATE_URL", "http://localhost:8080")
                
                self.weaviate_client = weaviate.Client(
                    url=url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=api_key)
                )
                
                # Check if class exists, create if not
                class_name = self.collection.replace("-", "_").capitalize()
                
                if not self.weaviate_client.schema.contains(class_name):
                    class_obj = {
                        "class": class_name,
                        "vectorizer": "none",  # We'll provide our own vectors
                        "properties": [
                            {
                                "name": "agent_id",
                                "dataType": ["string"]
                            },
                            {
                                "name": "role",
                                "dataType": ["string"]
                            },
                            {
                                "name": "content",
                                "dataType": ["text"]
                            },
                            {
                                "name": "timestamp",
                                "dataType": ["date"]
                            }
                        ]
                    }
                    
                    self.weaviate_client.schema.create_class(class_obj)
            
            # Initialize OpenAI client for embeddings
            from openai import OpenAI
            api_key = await secret_manager.get_secret("api_key", "openai")
            self.openai_client = OpenAI(api_key=api_key)
            
            self.logger.info(f"Initialized vector persistent memory for agent {self.agent_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize vector persistent memory: {e}")
            raise
    
    async def add_user_message(self, message: str):
        """Add a user message to the memory"""
        await super().add_user_message(message)
        
        # Also add to vector database
        await self._add_to_vector_db("user", message)
    
    async def add_ai_message(self, message: str):
        """Add an AI message to the memory"""
        await super().add_ai_message(message)
        
        # Also add to vector database
        await self._add_to_vector_db("ai", message)
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.openai_client:
            await self.initialize()
        
        response = self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        
        return response.data[0].embedding
    
    async def _add_to_vector_db(self, role: str, message: str):
        """Add a message to vector database"""
        try:
            # Generate embedding
            embedding = await self._generate_embedding(message)
            
            # Prepare metadata
            metadata = {
                "agent_id": self.agent_id,
                "role": role,
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to vector database
            if self.vector_db == "pinecone":
                if not self.pinecone_client:
                    await self.initialize()
                
                # Generate ID
                item_id = str(uuid.uuid4())
                
                # Upsert vector
                self.pinecone_client.upsert(
                    vectors=[(item_id, embedding, metadata)],
                    namespace=self.collection
                )
                
            elif self.vector_db == "weaviate":
                if not self.weaviate_client:
                    await self.initialize()
                
                # Prepare data object
                class_name = self.collection.replace("-", "_").capitalize()
                
                # Create object with vector
                self.weaviate_client.data_object.create(
                    class_name=class_name,
                    data_object=metadata,
                    vector=embedding
                )
                
        except Exception as e:
            self.logger.error(f"Error adding message to vector database: {e}")
    
    async def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant messages"""
        try:
            # Generate embedding for query
            embedding = await self._generate_embedding(query)
            
            # Search vector database
            if self.vector_db == "pinecone":
                if not self.pinecone_client:
                    await self.initialize()
                
                # Perform query
                query_response = self.pinecone_client.query(
                    vector=embedding,
                    top_k=limit,
                    namespace=self.collection,
                    filter={"agent_id": {"$eq": self.agent_id}},
                    include_metadata=True
                )
                
                # Format results
                results = []
                for match in query_response.matches:
                    result = match.metadata
                    result["score"] = match.score
                    results.append(result)
                
                return results
                
            elif self.vector_db == "weaviate":
                if not self.weaviate_client:
                    await self.initialize()
                
                # Prepare query
                class_name = self.collection.replace("-", "_").capitalize()
                
                # Build query
                query = (
                    self.weaviate_client.query
                    .get(class_name, ["agent_id", "role", "content", "timestamp"])
                    .with_near_vector({
                        "vector": embedding
                    })
                    .with_where({
                        "path": ["agent_id"],
                        "operator": "Equal",
                        "valueString": self.agent_id
                    })
                    .with_limit(limit)
                    .with_additional(["certainty"])
                )
                
                # Execute query
                result = query.do()
                
                # Format results
                results = []
                if "data" in result and "Get" in result["data"] and class_name in result["data"]["Get"]:
                    for item in result["data"]["Get"][class_name]:
                        result_item = {
                            "agent_id": item.get("agent_id"),
                            "role": item.get("role"),
                            "content": item.get("content"),
                            "timestamp": item.get("timestamp"),
                            "score": item.get("_additional", {}).get("certainty")
                        }
                        results.append(result_item)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error searching vector database: {e}")
            return []
    
    async def get_relevant_context(self, query: str, limit: int = 5) -> str:
        """Get relevant context for a query"""
        results = await self.search_memory(query, limit)
        
        if not results:
            return ""
        
        # Format results as context
        context = "Relevant past interactions:\n\n"
        
        for result in results:
            role = result.get("role", "unknown")
            content = result.get("content", "")
            timestamp = result.get("timestamp", "")
            
            if role == "user":
                context += f"User ({timestamp}): {content}\n"
            elif role == "ai":
                context += f"AI ({timestamp}): {content}\n"
            else:
                context += f"{role.capitalize()} ({timestamp}): {content}\n"
            
            context += "\n"
        
        return context
    
    async def load_memory_variables(self) -> Dict[str, Any]:
        """Load memory variables"""
        variables = await super().load_memory_variables()
        
        # Add vector context
        try:
            # Get most recent messages as context
            recent_context = await self.get_relevant_context("recent", 3)
            
            if recent_context:
                variables["long_term_memory"] = recent_context
                
        except Exception as e:
            self.logger.error(f"Error loading vector variables: {e}")
        
        return variables
