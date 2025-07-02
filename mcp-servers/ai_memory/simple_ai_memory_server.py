#!/usr/bin/env python3
"""Simple AI Memory MCP Server that can actually run."""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Basic FastAPI setup
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMemoryStore:
    """Simple in-memory storage for development."""
    
    def __init__(self):
        self.memories: List[Dict[str, Any]] = []
        self.next_id = 1
    
    async def store_memory(self, content: str, category: str = "general", 
                          tags: List[str] = None, importance_score: float = 0.5) -> Dict[str, Any]:
        """Store a memory."""
        memory = {
            "id": str(self.next_id),
            "content": content,
            "category": category,
            "tags": tags or [],
            "importance_score": importance_score,
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.memories.append(memory)
        self.next_id += 1
        
        logger.info(f"Stored memory {memory['id']}: {content[:50]}...")
        return {"memory_id": memory["id"], "status": "stored"}
    
    async def recall_memory(self, query: str = "", category: str = None, 
                           limit: int = 5) -> List[Dict[str, Any]]:
        """Recall memories with simple text matching."""
        results = []
        
        for memory in self.memories:
            # Simple text matching
            if query.lower() in memory["content"].lower():
                if category is None or memory["category"] == category:
                    results.append(memory)
        
        # Sort by importance and recency
        results.sort(key=lambda x: (x["importance_score"], x["timestamp"]), reverse=True)
        
        return results[:limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_memories": len(self.memories),
            "categories": list(set(m["category"] for m in self.memories)),
            "average_importance": sum(m["importance_score"] for m in self.memories) / len(self.memories) if self.memories else 0
        }

# Create FastAPI app
app = FastAPI(title="Simple AI Memory MCP Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create memory store
memory_store = SimpleMemoryStore()

@app.get("/")
async def root():
    return {
        "name": "Simple AI Memory MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    stats = await memory_store.get_stats()
    return {
        "status": "healthy",
        "service": "ai_memory_mcp",
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/memory/store")
async def store_memory(data: Dict[str, Any]):
    """Store a memory."""
    try:
        content = data.get("content")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        category = data.get("category", "general")
        tags = data.get("tags", [])
        importance_score = data.get("importance_score", 0.5)
        
        result = await memory_store.store_memory(
            content=content,
            category=category,
            tags=tags,
            importance_score=importance_score
        )
        
        return result
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/memory/recall")
async def recall_memory(data: Dict[str, Any]):
    """Recall memories."""
    try:
        query = data.get("query", "")
        category = data.get("category")
        limit = data.get("limit", 5)
        
        results = await memory_store.recall_memory(
            query=query,
            category=category,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error recalling memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/memory/stats")
async def get_stats():
    """Get memory statistics."""
    try:
        return await memory_store.get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def main():
    """Run the server."""
    logger.info("Starting Simple AI Memory MCP Server on port 9001...")
    
    try:
        # Try to load ESC config if available
        try:
            from backend.core.auto_esc_config import get_config_value
            logger.info("✅ Pulumi ESC integration available")
        except Exception as e:
            logger.warning(f"Pulumi ESC not available: {e}")
        
        # Start server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=9001,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
