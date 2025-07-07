import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

"""
Enhanced AI Memory MCP Server with Cline v3.18 Features
Implements WebFetch, Self-Knowledge, Improved Diff, and Model Routing
"""

import asyncio
import json
import os
import sys
import time
import uuid
from dataclasses import asdict, replace
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from backend.agents.enhanced.data_models import MemoryRecord
from backend.mcp_servers.base.standardized_mcp_server import (
    HealthCheckResult,
    HealthStatus,
    MCPServerConfig,
    ModelProvider,
    ServerCapability,
    StandardizedMCPServer,
    SyncPriority,
)
from backend.services.comprehensive_memory_service import ComprehensiveMemoryService


class EnhancedAIMemoryServer(StandardizedMCPServer):
    """AI Memory MCP Server with v3.18 enhancements"""

    def __init__(self):
        config = MCPServerConfig(
            server_name="ai_memory",
            port=9001,  # Fixed port based on our testing
            sync_priority=SyncPriority.HIGH,
            enable_webfetch=True,
            enable_self_knowledge=True,
            enable_improved_diff=True,
            preferred_model=ModelProvider.CLAUDE_4,
        )
        super().__init__(config)
        self.logger = logger
        self.memory_service: ComprehensiveMemoryService | None = None
        self.conversation_history: list[dict[str, Any]] = []

    async def server_specific_init(self) -> None:
        """Initialize AI Memory specific components"""
        try:
            self.memory_service = ComprehensiveMemoryService()

            if self.memory_service:
                await self._load_conversation_history()

            self.logger.info("AI Memory server initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Memory server: {e}")
            self.memory_service = None

    async def check_external_api(self) -> bool:
        """Check if Pinecone/Weaviate are accessible"""
        try:
            if self.memory_service and self.memory_service.pinecone_index:
                return True
            return False
        except Exception:
            return False

    async def get_server_capabilities(self) -> list[ServerCapability]:
        """Return AI Memory server capabilities"""
        return [
            ServerCapability(
                name="store_conversation",
                description="Store conversations with automatic AI categorization",
                category="memory_management",
                available=True,
                version="3.18.0",
                metadata={
                    "ai_features": ["categorization", "summarization", "tagging"],
                    "storage_types": [
                        "conversation",
                        "code_snippet",
                        "decision",
                        "bug_fix",
                    ],
                    "max_size": "10MB per entry",
                },
            ),
            ServerCapability(
                name="smart_recall",
                description="Retrieve relevant memories using semantic search",
                category="memory_retrieval",
                available=True,
                version="3.18.0",
                metadata={
                    "search_types": ["semantic", "keyword", "temporal", "category"],
                    "ai_ranking": True,
                    "context_aware": True,
                },
            ),
            ServerCapability(
                name="webfetch_documentation",
                description="Fetch and store external documentation",
                category="knowledge_acquisition",
                available=True,
                version="3.18.0",
                metadata={
                    "supported_sources": ["api_docs", "tutorials", "guides"],
                    "auto_summarization": True,
                    "update_tracking": True,
                },
            ),
            ServerCapability(
                name="pattern_recognition",
                description="Identify and track code patterns and decisions",
                category="intelligence",
                available=True,
                version="3.18.0",
                metadata={
                    "pattern_types": [
                        "architectural",
                        "implementation",
                        "bug_patterns",
                    ],
                    "trend_analysis": True,
                    "recommendation_engine": True,
                },
            ),
        ]

    async def _load_conversation_history(self):
        """Load recent conversation history"""
        try:
            if self.memory_service:
                recent_memories = await self.memory_service.recall_memories(
                    query="", top_k=100, category="conversation"
                )
                self.conversation_history = [asdict(m) for m in recent_memories]
        except Exception as e:
            self.logger.warning(f"Could not load conversation history: {e}")

    async def store_conversation_enhanced(
        self, request: dict[str, Any]
    ) -> dict[str, Any]:
        """Store conversation with AI-powered categorization and WebFetch integration"""
        try:
            conversation_content = request.get("conversation", {})
            metadata = request.get("metadata", {})
            memory_id = str(uuid.uuid4())

            urls = self._extract_urls(str(conversation_content))
            fetched_docs = {}

            if urls:
                for url in urls[:3]:
                    try:
                        result = await self.webfetch(url)
                        fetched_docs[url] = {
                            "content": result.markdown_content[:5000]
                            if hasattr(result, "markdown_content")
                            else "",
                            "title": result.title if hasattr(result, "title") else "No Title",  # type: ignore
                            "cached": result.cached
                            if hasattr(result, "cached")
                            else False,
                        }
                    except Exception as e:
                        self.logger.warning(f"Could not fetch {url}: {e}")

            model, model_metadata = await self.route_to_model(
                task="categorize conversation and extract key insights",
                context_size=len(json.dumps(conversation_content)),
            )

            categorization_prompt = f"""
            Analyze this conversation and provide:
            1. Primary category (architecture, bug_fix, feature, optimization, other)
            2. Key topics (list of 3-5 topics)
            3. Decision points (any key decisions made)
            4. Action items (any todos or next steps)
            5. Related documentation (from fetched docs if any)

            Conversation: {json.dumps(conversation_content, indent=2)}

            Fetched Documentation: {json.dumps(fetched_docs, indent=2) if fetched_docs else "None"}

            Return as JSON.
            """

            categorization = await self.process_with_ai(
                {"prompt": categorization_prompt}, model=model
            )

            try:
                ai_analysis = json.loads(categorization.get("response", "{}"))
            except Exception:
                ai_analysis = {
                    "category": "other",
                    "topics": [],
                    "decisions": [],
                    "action_items": [],
                }

            if self.memory_service:
                memory_record = MemoryRecord(
                    id=memory_id,
                    content=json.dumps(conversation_content),
                    category=ai_analysis.get("category", "conversation"),
                    tags=metadata.get("tags", []),
                    importance_score=metadata.get("importance_score", 0.5),
                    source_system="sophia_ai_mcp",
                    additional_metadata={
                        **metadata,
                        "ai_analysis": ai_analysis,
                        "fetched_docs": fetched_docs,
                        "model_used": str(model),
                        "stored_at": datetime.now(UTC).isoformat(),
                    },
                )
                await self.memory_service.store_memory(memory_record)

                self.conversation_history.append(
                    {
                        "id": memory_id,
                        "conversation": conversation_content,
                        "analysis": ai_analysis,
                    }
                )

                return {
                    "success": True,
                    "memory_id": memory_id,
                    "categorization": ai_analysis,
                    "fetched_documentation": len(fetched_docs),
                    "model_used": str(model),
                }
            else:
                return {"success": False, "error": "Memory service not initialized"}

        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
            return {"success": False, "error": str(e)}

    async def smart_recall_enhanced(self, request: dict[str, Any]) -> dict[str, Any]:
        """Enhanced memory recall with AI ranking and context awareness"""
        try:
            query_context = await self._prepare_query_context(request)
            enhanced_query = await self._enhance_query_with_ai(query_context)
            raw_memories = await self._search_memories(enhanced_query, request)
            ranked_memories = await self._rank_memories_with_ai(
                raw_memories, query_context
            )

            return self._format_recall_response(ranked_memories, enhanced_query)
        except Exception as e:
            return self._handle_recall_error(e)

    async def _prepare_query_context(self, request: dict[str, Any]) -> dict[str, Any]:
        """Extract and prepare query context from request"""
        query = request.get("query", "")
        context = request.get("context", {})
        filters = request.get("filters", {})

        return {
            "query": query,
            "context": context,
            "filters": filters,
            "limit": request.get("limit", 10),
        }

    async def _enhance_query_with_ai(self, query_context: dict[str, Any]) -> str:
        """Use AI to enhance search query based on context"""
        query = query_context["query"]
        context = query_context["context"]

        if not context:
            return query

        model, _ = await self.route_to_model(
            task="enhance search query", context_size=len(str(context))
        )

        enhancement_prompt = f"""
        Enhance this search query based on the current context:
        Query: {query}
        Context: {context}

        Return an enhanced search query that will find the most relevant memories.
        """

        result = await self.process_with_ai({"prompt": enhancement_prompt}, model=model)
        return result.get("response", query)

    async def _search_memories(
        self, enhanced_query: str, request: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Search memories with enhanced query"""
        filters = request.get("filters", {})
        limit = request.get("limit", 10)

        if self.memory_service:
            memories = await self.memory_service.recall_memories(
                query=enhanced_query,
                top_k=limit * 2,
                category=filters.get("type"),
            )
            return [asdict(m) for m in memories]
        return []

    async def _rank_memories_with_ai(
        self, memories: list[dict], query_context: dict[str, Any]
    ) -> list[dict]:
        """Use AI to rank and filter search results"""
        if not memories or len(memories) <= query_context["limit"]:
            return memories[: query_context["limit"]]

        model, _ = await self.route_to_model(
            task="rank search results", context_size=len(str(memories))
        )

        ranking_prompt = f"""
        Rank these search results by relevance to the query and context.
        Return the top {query_context["limit"]} results with relevance scores.

        Query: {query_context["query"]}
        Context: {query_context["context"]}
        Results: {memories}

        Return as JSON array with relevance scores.
        """

        ranking_result = await self.process_with_ai(
            {"prompt": ranking_prompt}, model=model
        )

        try:
            ranked_memories = json.loads(ranking_result.get("response", "[]"))
            return ranked_memories[: query_context["limit"]]
        except Exception:
            return memories[: query_context["limit"]]

    def _format_recall_response(
        self, memories: list[dict], enhanced_query: str
    ) -> dict[str, Any]:
        """Format the final recall response"""
        return {
            "success": True,
            "memories": memories,
            "query": enhanced_query,
            "total_found": len(memories),
        }

    def _handle_recall_error(self, error: Exception) -> dict[str, Any]:
        """Handle recall errors consistently"""
        logger.error(f"Error in smart recall: {error}")
        return {"success": False, "error": str(error)}

    async def update_memory_enhanced(self, request: dict[str, Any]) -> dict[str, Any]:
        """Update memory using improved diff editing"""
        try:
            memory_id = request.get("memory_id")
            updates = request.get("updates", {})

            if self.memory_service:
                existing_memory_record = await self.memory_service.get_memory_by_id(
                    str(memory_id)
                )
                if not existing_memory_record:
                    return {"success": False, "error": "Memory not found"}

                existing_json = json.dumps(asdict(existing_memory_record), indent=2)

                updated_memory_record = replace(existing_memory_record, **updates)
                updated_json = json.dumps(asdict(updated_memory_record), indent=2)

                diff_result = await self.improved_diff_edit(
                    file_path=f"memories/{memory_id}.json",
                    search_content=existing_json,
                    replace_content=updated_json,
                    strategy="auto",
                )

                if diff_result["success"]:
                    # TODO: Implement update_memory in ComprehensiveMemoryService
                    return {
                        "success": True,
                        "memory_id": memory_id,
                        "diff_strategy": diff_result["strategy_used"],
                        "attempts": diff_result["attempts"],
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to update memory",
                        "diff_error": diff_result.get("error"),
                    }
            else:
                return {"success": False, "error": "Memory service not initialized"}

        except Exception as e:
            self.logger.error(f"Error updating memory: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_and_store_documentation(
        self, request: dict[str, Any]
    ) -> dict[str, Any]:
        """Fetch external documentation and store as memory"""
        try:
            url: str | None = request.get("url")
            category = request.get("category", "documentation")

            if not url:
                return {"success": False, "error": "URL is required"}

            result = await self.webfetch(url)

            content = (
                result.markdown_content if hasattr(result, "markdown_content") else ""
            )
            summary = None

            if len(content) > 10000:
                model, _ = await self.route_to_model(
                    task="summarize documentation", context_size=len(content)
                )

                summary_result = await self.process_with_ai(
                    {"prompt": f"Summarize this documentation:\n\n{content[:50000]}"},
                    model=model,
                )
                summary = summary_result.get("response", "")

            if self.memory_service:
                new_memory_id = str(uuid.uuid4())
                memory_record = MemoryRecord(
                    id=new_memory_id,
                    content=json.dumps(
                        {
                            "url": url,
                            "title": result.title if hasattr(result, "title") else "No Title",  # type: ignore
                            "content": content,
                            "summary": summary,
                        }
                    ),
                    category=category,
                    tags=["documentation", "webfetch"],
                    source_system="webfetch",
                    additional_metadata={
                        "fetched_at": datetime.now(UTC).isoformat(),
                        "cached": result.cached if hasattr(result, "cached") else False,  # type: ignore
                    },
                )
                await self.memory_service.store_memory(memory_record)

                return {
                    "success": True,
                    "memory_id": new_memory_id,
                    "title": result.title if hasattr(result, "title") else "No Title",  # type: ignore
                    "content_size": len(content),
                    "has_summary": summary is not None,
                    "cached": result.cached if hasattr(result, "cached") else False,  # type: ignore
                }
            else:
                return {"success": False, "error": "Memory service not initialized"}

        except Exception as e:
            self.logger.error(f"Error fetching documentation: {e}")
            return {"success": False, "error": str(e)}

    def _extract_urls(self, text: str) -> list[str]:
        """Extract URLs from text"""
        import re

        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)

    def _setup_routes(self):
        """Setup FastAPI routes with v3.18 enhancements"""
        super()._setup_routes()

        @self.app.post("/store_conversation")
        async def store_conversation(request: dict[str, Any]):
            return await self.store_conversation_enhanced(request)

        @self.app.post("/smart_recall")
        async def smart_recall(request: dict[str, Any]):
            return await self.smart_recall_enhanced(request)

        @self.app.post("/update_memory")
        async def update_memory(request: dict[str, Any]):
            return await self.update_memory_enhanced(request)

        @self.app.post("/fetch_documentation")
        async def fetch_documentation(request: dict[str, Any]):
            return await self.fetch_and_store_documentation(request)

        @self.app.get("/help/{capability}")
        async def get_capability_help(capability: str):
            """Self-knowledge endpoint for capability help"""
            capabilities = await self.get_server_capabilities()
            for cap in capabilities:
                if cap.name == capability:
                    return {
                        "capability": cap.name,
                        "description": cap.description,
                        "category": cap.category,
                        "metadata": cap.metadata,
                        "examples": self._get_capability_examples(capability),
                    }
            raise HTTPException(
                status_code=404, detail=f"Capability '{capability}' not found"
            )

    def _get_capability_examples(self, capability: str) -> list[dict[str, str]]:
        """Get usage examples for capabilities"""
        examples = {
            "store_conversation": [
                {
                    "description": "Store a bug fix conversation",
                    "request": {
                        "conversation": {
                            "user": "How do I fix the login timeout issue?",
                            "assistant": "The timeout is in config.py, line 45...",
                        },
                        "metadata": {"tags": ["bug", "authentication"]},
                    },
                }
            ],
            "smart_recall": [
                {
                    "description": "Find similar bug fixes",
                    "request": {
                        "query": "login timeout issues",
                        "context": {"current_file": "auth.py"},
                        "filters": {"type": "bug_fix"},
                    },
                }
            ],
        }
        return examples.get(capability, [])

    async def server_specific_cleanup(self) -> None:
        """Cleanup AI Memory specific resources"""
        try:
            if self.memory_service:
                # TODO: Implement shutdown in ComprehensiveMemoryService
                pass
            self.logger.info("AI Memory server cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during AI Memory server cleanup: {e}")

    async def server_specific_health_check(self) -> HealthCheckResult:
        """Perform AI Memory specific health checks"""
        try:
            start_time = time.time()

            if self.memory_service:
                try:
                    test_memories = await self.memory_service.recall_memories(
                        query="health_check", top_k=1
                    )
                    memory_service_status = "operational"
                    status = HealthStatus.HEALTHY
                except Exception as e:
                    memory_service_status = f"error: {str(e)}"
                    status = HealthStatus.DEGRADED
            else:
                memory_service_status = "not_initialized"
                status = HealthStatus.DEGRADED

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component="ai_memory",
                status=status,
                response_time_ms=response_time,
                metadata={
                    "memory_service": memory_service_status,
                    "conversation_history_size": len(self.conversation_history),
                    "capabilities": len(self.server_capabilities),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                component="ai_memory",
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                error_message=str(e),
            )

    async def sync_data(self) -> dict[str, Any]:
        """Sync AI Memory data (process and vectorize available data)"""
        try:
            if not self.memory_service:
                return {"status": "failed", "error": "Memory service not initialized"}

            gong_processed = await self.memory_service.process_and_vectorize_gong_data(
                batch_size=50
            )

            slack_processed = (
                await self.memory_service.process_and_vectorize_slack_data(
                    batch_size=100
                )
            )

            integrated_created = (
                await self.memory_service.create_integrated_conversation_memories(
                    limit=50
                )
            )

            return {
                "status": "completed",
                "records_synced": gong_processed + slack_processed + integrated_created,
                "gong_records": gong_processed,
                "slack_records": slack_processed,
                "integrated_conversations": integrated_created,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"AI Memory sync failed: {e}")
            return {"status": "failed", "error": str(e), "records_synced": 0}

    async def process_with_ai(
        self, data: Any, model: ModelProvider | None = None
    ) -> Any:
        """Process data using AI models"""
        try:
            if not model:
                model, _ = await self.route_to_model(
                    task="process ai memory data",
                    context_size=len(str(data))
                    if isinstance(data, (str, dict))
                    else 1000,
                )

            if isinstance(data, dict) and "prompt" in data:
                prompt = data["prompt"]
            else:
                prompt = str(data)

            if model == ModelProvider.SNOWFLAKE_CORTEX:
                self.logger.warning(
                    "Snowflake Cortex generate_completion not directly supported here. Using mock response."
                )
                return {
                    "response": f"Mock AI processing completed for Cortex: {prompt[:100]}...",
                    "model_used": str(model.value),
                    "mock": True,
                }

            else:
                return {
                    "response": f"AI processing completed for: {prompt[:100]}...",
                    "model_used": str(model.value),
                    "mock": True,
                }

        except Exception as e:
            self.logger.error(f"AI processing failed: {e}")
            return {"error": str(e), "response": None}


if __name__ == "__main__":
    server = EnhancedAIMemoryServer()
    asyncio.run(server.start())
