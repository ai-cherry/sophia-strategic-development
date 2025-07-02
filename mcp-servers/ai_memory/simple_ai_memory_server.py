#!/usr/bin/env python3
"""
Simple AI Memory MCP Server
Stores and recalls coding memories and patterns
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleAIMemoryServer:
    def __init__(self):
        self.app = FastAPI(title="Simple AI Memory MCP Server", version="1.0.0")
        self.memories = []  # In-memory storage for demo
        self.setup_routes()
        self.setup_middleware()

    def setup_middleware(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            return {
                "name": "Simple AI Memory MCP Server",
                "version": "1.0.0",
                "status": "running",
                "capabilities": ["store_memory", "recall_memory", "get_ai_coding_tips"],
                "memory_count": len(self.memories)
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "memory_count": len(self.memories),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/api/store_memory")
        async def store_memory(request: Dict[str, Any]):
            """Store a coding memory"""
            try:
                memory_id = str(uuid.uuid4())
                memory = {
                    "id": memory_id,
                    "content": request.get("content", ""),
                    "category": request.get("category", "general"),
                    "tags": request.get("tags", []),
                    "importance_score": request.get("importance_score", 0.5),
                    "auto_detected": request.get("auto_detected", False),
                    "timestamp": datetime.now().isoformat(),
                    "usage_count": 0
                }
                
                self.memories.append(memory)
                logger.info(f"Stored memory: {memory_id}")
                
                return {
                    "success": True,
                    "memory_id": memory_id,
                    "message": "Memory stored successfully"
                }
                
            except Exception as e:
                logger.error(f"Error storing memory: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/recall_memory")
        async def recall_memory(request: Dict[str, Any]):
            """Recall memories based on query"""
            try:
                query = request.get("query", "").lower()
                category = request.get("category")
                limit = request.get("limit", 5)
                
                # Simple text-based search
                matching_memories = []
                for memory in self.memories:
                    # Check if query matches content, tags, or category
                    content_match = query in memory["content"].lower()
                    tag_match = any(query in tag.lower() for tag in memory["tags"])
                    category_match = category is None or memory["category"] == category
                    
                    if (content_match or tag_match) and category_match:
                        # Update usage count
                        memory["usage_count"] += 1
                        matching_memories.append(memory)
                
                # Sort by importance score and usage count
                matching_memories.sort(
                    key=lambda x: (x["importance_score"], x["usage_count"]), 
                    reverse=True
                )
                
                result_memories = matching_memories[:limit]
                
                logger.info(f"Recalled {len(result_memories)} memories for query: {query}")
                
                return {
                    "success": True,
                    "memories": result_memories,
                    "total_found": len(matching_memories),
                    "query": query
                }
                
            except Exception as e:
                logger.error(f"Error recalling memories: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/auto_store_conversation")
        async def auto_store_conversation(request: Dict[str, Any]):
            """Automatically analyze and store conversation if important"""
            try:
                content = request.get("content", "")
                participants = request.get("participants", [])
                
                # Simple analysis - look for coding keywords
                coding_keywords = [
                    "function", "class", "import", "api", "database", "authentication",
                    "security", "bug", "fix", "implementation", "pattern", "algorithm",
                    "jwt", "sql", "react", "python", "javascript", "error", "solution"
                ]
                
                importance_score = 0.0
                detected_tags = []
                
                content_lower = content.lower()
                for keyword in coding_keywords:
                    if keyword in content_lower:
                        importance_score += 0.1
                        detected_tags.append(keyword)
                
                # Auto-store if importance score is high enough
                should_store = importance_score >= 0.3
                
                if should_store:
                    memory_id = str(uuid.uuid4())
                    memory = {
                        "id": memory_id,
                        "content": content,
                        "category": "conversation",
                        "tags": detected_tags,
                        "importance_score": min(importance_score, 1.0),
                        "auto_detected": True,
                        "participants": participants,
                        "timestamp": datetime.now().isoformat(),
                        "usage_count": 0
                    }
                    
                    self.memories.append(memory)
                    
                    return {
                        "success": True,
                        "auto_stored": True,
                        "memory_id": memory_id,
                        "importance_score": importance_score,
                        "detected_tags": detected_tags
                    }
                else:
                    return {
                        "success": True,
                        "auto_stored": False,
                        "importance_score": importance_score,
                        "reason": "Content not important enough to store automatically"
                    }
                
            except Exception as e:
                logger.error(f"Error in auto-store conversation: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/get_ai_coding_tips")
        async def get_ai_coding_tips(request: Dict[str, Any]):
            """Get AI coding tips for a specific topic"""
            try:
                topic = request.get("topic", "").lower()
                
                # Pre-loaded coding tips
                coding_tips = {
                    "security": [
                        "Always use parameterized queries to prevent SQL injection",
                        "Store secrets in environment variables, never hardcode them",
                        "Implement proper input validation and sanitization",
                        "Use HTTPS for all API communications",
                        "Implement proper authentication and authorization"
                    ],
                    "performance": [
                        "Use database indexes for frequently queried columns",
                        "Implement caching for expensive operations",
                        "Optimize loops and avoid N+1 query problems",
                        "Use async/await for I/O operations",
                        "Profile your code to identify bottlenecks"
                    ],
                    "authentication": [
                        "Use JWT tokens with proper expiration times",
                        "Implement refresh token rotation",
                        "Store tokens in httpOnly cookies for web apps",
                        "Use bcrypt or similar for password hashing",
                        "Implement rate limiting for login attempts"
                    ],
                    "react": [
                        "Use functional components with hooks",
                        "Implement proper error boundaries",
                        "Optimize re-renders with useMemo and useCallback",
                        "Use TypeScript for better type safety",
                        "Implement accessibility with ARIA attributes"
                    ],
                    "python": [
                        "Follow PEP 8 style guidelines",
                        "Use type hints for better code documentation",
                        "Implement proper exception handling",
                        "Use virtual environments for dependency management",
                        "Write unit tests with pytest"
                    ]
                }
                
                # Find relevant tips
                relevant_tips = []
                for category, tips in coding_tips.items():
                    if not topic or topic in category:
                        relevant_tips.extend([{"category": category, "tip": tip} for tip in tips])
                
                # Also search stored memories for tips
                memory_tips = []
                for memory in self.memories:
                    if ("tip" in memory["content"].lower() or 
                        "pattern" in memory["content"].lower() or
                        "best practice" in memory["content"].lower()):
                        if not topic or topic in memory["content"].lower():
                            memory_tips.append({
                                "category": memory["category"],
                                "tip": memory["content"],
                                "tags": memory["tags"],
                                "from_memory": True
                            })
                
                all_tips = relevant_tips + memory_tips
                
                return {
                    "success": True,
                    "topic": topic or "general",
                    "tips": all_tips[:10],  # Limit to 10 tips
                    "total_available": len(all_tips)
                }
                
            except Exception as e:
                logger.error(f"Error getting coding tips: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/stats")
        async def get_stats():
            """Get memory statistics"""
            try:
                categories = {}
                total_usage = 0
                
                for memory in self.memories:
                    category = memory["category"]
                    categories[category] = categories.get(category, 0) + 1
                    total_usage += memory["usage_count"]
                
                return {
                    "total_memories": len(self.memories),
                    "categories": categories,
                    "total_usage": total_usage,
                    "most_used": max(self.memories, key=lambda x: x["usage_count"])["content"][:100] + "..." if self.memories else "No memories yet"
                }
                
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def start_server(self, port: int = 9000):
        """Start the AI Memory MCP server"""
        logger.info(f"🧠 Starting Simple AI Memory MCP Server on port {port}")
        
        # Pre-load some useful coding knowledge
        await self.preload_knowledge()
        
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def preload_knowledge(self):
        """Pre-load useful coding knowledge"""
        knowledge_base = [
            {
                "content": "JWT authentication implementation: Use httpOnly cookies, implement refresh token rotation, and set proper expiration times. Always validate tokens on server side.",
                "category": "security_pattern",
                "tags": ["jwt", "authentication", "security", "cookies"],
                "importance_score": 0.9,
                "auto_detected": False
            },
            {
                "content": "SQL injection prevention: Always use parameterized queries or prepared statements. Never concatenate user input directly into SQL strings.",
                "category": "security_pattern", 
                "tags": ["sql", "security", "injection", "database"],
                "importance_score": 0.95,
                "auto_detected": False
            },
            {
                "content": "React component best practices: Use functional components with hooks, implement proper error boundaries, optimize with useMemo/useCallback, and ensure accessibility.",
                "category": "ui_pattern",
                "tags": ["react", "components", "hooks", "performance", "accessibility"],
                "importance_score": 0.8,
                "auto_detected": False
            },
            {
                "content": "Python async patterns: Use async/await for I/O operations, implement proper exception handling in async functions, and use asyncio.gather for concurrent operations.",
                "category": "performance_pattern",
                "tags": ["python", "async", "performance", "concurrency"],
                "importance_score": 0.85,
                "auto_detected": False
            }
        ]
        
        for knowledge in knowledge_base:
            memory_id = str(uuid.uuid4())
            memory = {
                "id": memory_id,
                "timestamp": datetime.now().isoformat(),
                "usage_count": 0,
                **knowledge
            }
            self.memories.append(memory)
        
        logger.info(f"Pre-loaded {len(knowledge_base)} coding knowledge items")

def main():
    """Main function to run the server"""
    server = SimpleAIMemoryServer()
    
    try:
        asyncio.run(server.start_server(port=9000))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()
