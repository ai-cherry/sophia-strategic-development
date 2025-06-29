#!/usr/bin/env python3
from backend.core.optimized_connection_manager import connection_manager
from backend.core.performance_monitor import performance_monitor

"""
Enhanced Chat Context Service for Sophia AI
Provides large contextual windows and intelligent context management
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from snowflake.connector import DictCursor

logger = logging.getLogger(__name__)


class ContextWindow:
    """Manages large contextual windows for chat conversations"""

    def __init__(self, max_tokens: int = 32000):
        self.max_tokens = max_tokens
        self.context_overlap = 500  # Tokens to maintain for continuity

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def truncate_context(
        self, context_items: list[dict], max_tokens: int
    ) -> list[dict]:
        """Intelligently truncate context to fit within token limits"""
        if not context_items:
            return []

        # Calculate current token usage
        total_tokens = sum(
            self.estimate_tokens(item.get("content", "")) for item in context_items
        )

        if total_tokens <= max_tokens:
            return context_items

        # Prioritize recent items and high-relevance items
        prioritized_items = sorted(
            context_items,
            key=lambda x: (
                x.get("relevance_score", 0.5),  # Higher relevance first
                x.get("timestamp", datetime.min),  # More recent first
            ),
            reverse=True,
        )

        selected_items = []
        current_tokens = 0

        for item in prioritized_items:
            item_tokens = self.estimate_tokens(item.get("content", ""))
            if current_tokens + item_tokens <= max_tokens:
                selected_items.append(item)
                current_tokens += item_tokens
            else:
                break

        # Maintain chronological order
        selected_items.sort(key=lambda x: x.get("timestamp", datetime.min))
        return selected_items


class EnhancedChatContextService:
    """Enhanced chat service with large contextual windows and intelligent context management"""

    def __init__(self, snowflake_config: dict[str, str]):
        self.snowflake_config = snowflake_config
        self.connection = None
        self.context_window = ContextWindow()

    @performance_monitor.track_performance
    async def connect(self):
        """Connect to Snowflake"""
        try:
            self.connection = await connection_manager.get_connection()
            logger.info("✅ Enhanced Chat Context Service connected")
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise

    async def get_enhanced_context(
        self, query: str, session_id: str, user_id: str, max_context_tokens: int = 16000
    ) -> dict[str, Any]:
        """Get enhanced context for query with large contextual windows"""

        # Get conversation history
        conversation_context = await self._get_conversation_context(session_id, user_id)

        # Get relevant knowledge base entries
        knowledge_context = await self._get_knowledge_context(query, user_id)

        # Get cross-document context
        cross_document_context = await self._get_cross_document_context(query, user_id)

        # Combine and prioritize context
        all_context = []

        # Add conversation history (highest priority for continuity)
        for msg in conversation_context:
            all_context.append(
                {
                    "type": "conversation",
                    "content": msg["CONTENT"],
                    "timestamp": msg["CREATED_AT"],
                    "relevance_score": 0.9,  # High relevance for conversation continuity
                    "metadata": {"message_type": msg["MESSAGE_TYPE"]},
                }
            )

        # Add knowledge base entries
        for entry in knowledge_context:
            all_context.append(
                {
                    "type": "knowledge",
                    "content": entry["CONTENT"],
                    "timestamp": entry.get("CREATED_AT", datetime.now()),
                    "relevance_score": entry.get("similarity_score", 0.7),
                    "metadata": {
                        "title": entry["TITLE"],
                        "category": entry["CATEGORY_NAME"],
                        "entry_id": entry["ENTRY_ID"],
                    },
                }
            )

        # Add cross-document context
        for entry in cross_document_context:
            all_context.append(
                {
                    "type": "cross_document",
                    "content": entry["CONTENT"],
                    "timestamp": entry.get("CREATED_AT", datetime.now()),
                    "relevance_score": entry.get("similarity_score", 0.6),
                    "metadata": {
                        "title": entry["TITLE"],
                        "category": entry["CATEGORY_NAME"],
                        "source_documents": entry.get("source_documents", []),
                    },
                }
            )

        # Intelligently truncate to fit within token limits
        optimized_context = self.context_window.truncate_context(
            all_context, max_context_tokens
        )

        # Calculate context statistics
        context_stats = self._calculate_context_stats(optimized_context)

        return {
            "context_items": optimized_context,
            "context_summary": self._generate_context_summary(optimized_context),
            "stats": context_stats,
            "total_tokens": sum(
                self.context_window.estimate_tokens(item["content"])
                for item in optimized_context
            ),
        }

    async def _get_conversation_context(
        self, session_id: str, user_id: str
    ) -> list[dict]:
        """Get recent conversation history"""
        cursor = self.connection.cursor(DictCursor)

        # Get last 20 messages for context
        await cursor.execute(
            """
        SELECT MESSAGE_ID, CONTENT, MESSAGE_TYPE, CREATED_AT
        FROM CONVERSATION_MESSAGES
        WHERE SESSION_ID = %s AND USER_ID = %s
        ORDER BY CREATED_AT DESC
        LIMIT 20
        """,
            (session_id, user_id),
        )

        results = await cursor.fetchall()
        cursor.close()

        # Return in chronological order
        return list(reversed(results))

    @performance_monitor.track_performance
    async def _get_knowledge_context(
        self, query: str, user_id: str, limit: int = 10
    ) -> list[dict]:
        """Get relevant knowledge base entries with enhanced search"""
        cursor = self.connection.cursor(DictCursor)

        # Enhanced search with multiple strategies
        search_strategies = [
            # Exact phrase matching
            f"""
            SELECT 
                k.ENTRY_ID, k.TITLE, k.CONTENT, k.CATEGORY_ID, k.CREATED_AT,
                c.CATEGORY_NAME,
                1.0 as similarity_score
            FROM KNOWLEDGE_BASE_ENTRIES k
            JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
            WHERE k.STATUS = 'published'
            AND UPPER(k.CONTENT) LIKE UPPER('%{query}%')
            """,
            # Keyword matching
            f"""
            SELECT 
                k.ENTRY_ID, k.TITLE, k.CONTENT, k.CATEGORY_ID, k.CREATED_AT,
                c.CATEGORY_NAME,
                0.8 as similarity_score
            FROM KNOWLEDGE_BASE_ENTRIES k
            JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
            WHERE k.STATUS = 'published'
            AND (UPPER(k.TITLE) LIKE UPPER('%{query}%') 
                 OR UPPER(k.CONTENT) LIKE UPPER('%{query}%'))
            """,
            # Category-based search
            f"""
            SELECT 
                k.ENTRY_ID, k.TITLE, k.CONTENT, k.CATEGORY_ID, k.CREATED_AT,
                c.CATEGORY_NAME,
                0.6 as similarity_score
            FROM KNOWLEDGE_BASE_ENTRIES k
            JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
            WHERE k.STATUS = 'published'
            AND UPPER(c.CATEGORY_NAME) LIKE UPPER('%{query}%')
            """,
        ]

        all_results = []
        seen_entry_ids = set()

        for strategy_query in search_strategies:
            try:
                await cursor.execute(strategy_query)
                results = await cursor.fetchall()

                for result in results:
                    if result["ENTRY_ID"] not in seen_entry_ids:
                        all_results.append(result)
                        seen_entry_ids.add(result["ENTRY_ID"])

                        if len(all_results) >= limit:
                            break

                if len(all_results) >= limit:
                    break

            except Exception as e:
                logger.warning(f"Search strategy failed: {e}")
                continue

        cursor.close()

        # Sort by relevance score
        all_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return all_results[:limit]

    @performance_monitor.track_performance
    async def _get_cross_document_context(
        self, query: str, user_id: str, limit: int = 5
    ) -> list[dict]:
        """Get cross-document context by finding related entries across different documents"""
        cursor = self.connection.cursor(DictCursor)

        # Find entries that contain similar concepts across different source documents
        query_words = query.lower().split()

        if len(query_words) < 2:
            return []

        # Search for entries that contain multiple query words and are from different sources
        search_query = f"""
        WITH relevant_entries AS (
            SELECT 
                k.ENTRY_ID, k.TITLE, k.CONTENT, k.CATEGORY_ID, k.CREATED_AT,
                c.CATEGORY_NAME,
                JSON_EXTRACT_PATH_TEXT(k.METADATA, 'filename') as source_filename,
                0.7 as similarity_score
            FROM KNOWLEDGE_BASE_ENTRIES k
            JOIN KNOWLEDGE_CATEGORIES c ON k.CATEGORY_ID = c.CATEGORY_ID
            WHERE k.STATUS = 'published'
            AND (
                {" OR ".join([f"UPPER(k.CONTENT) LIKE UPPER('%{word}%')" for word in query_words[:5]])}
            )
        )
        SELECT 
            ENTRY_ID, TITLE, CONTENT, CATEGORY_ID, CREATED_AT, CATEGORY_NAME,
            similarity_score, source_filename,
            ARRAY_AGG(DISTINCT source_filename) OVER (PARTITION BY CATEGORY_ID) as source_documents
        FROM relevant_entries
        WHERE source_filename IS NOT NULL
        ORDER BY similarity_score DESC, CREATED_AT DESC
        LIMIT {limit}
        """

        try:
            await cursor.execute(search_query)
            results = await cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.warning(f"Cross-document search failed: {e}")
            cursor.close()
            return []

    def _calculate_context_stats(self, context_items: list[dict]) -> dict[str, Any]:
        """Calculate statistics about the context"""
        if not context_items:
            return {}

        stats = {
            "total_items": len(context_items),
            "types": {},
            "categories": {},
            "date_range": {},
            "relevance_distribution": {},
        }

        # Count by type
        for item in context_items:
            item_type = item.get("type", "unknown")
            stats["types"][item_type] = stats["types"].get(item_type, 0) + 1

        # Count by category (for knowledge items)
        for item in context_items:
            if item.get("type") == "knowledge":
                category = item.get("metadata", {}).get("category", "unknown")
                stats["categories"][category] = stats["categories"].get(category, 0) + 1

        # Date range
        timestamps = [
            item["timestamp"] for item in context_items if item.get("timestamp")
        ]
        if timestamps:
            stats["date_range"] = {
                "earliest": min(timestamps),
                "latest": max(timestamps),
                "span_hours": (max(timestamps) - min(timestamps)).total_seconds()
                / 3600,
            }

        # Relevance distribution
        relevance_scores = [item.get("relevance_score", 0.5) for item in context_items]
        if relevance_scores:
            stats["relevance_distribution"] = {
                "average": sum(relevance_scores) / len(relevance_scores),
                "min": min(relevance_scores),
                "max": max(relevance_scores),
            }

        return stats

    def _generate_context_summary(self, context_items: list[dict]) -> str:
        """Generate a summary of the context"""
        if not context_items:
            return "No relevant context found."

        summary_parts = []

        # Count items by type
        type_counts = {}
        for item in context_items:
            item_type = item.get("type", "unknown")
            type_counts[item_type] = type_counts.get(item_type, 0) + 1

        # Generate summary
        if type_counts.get("conversation", 0) > 0:
            summary_parts.append(f"{type_counts['conversation']} conversation messages")

        if type_counts.get("knowledge", 0) > 0:
            summary_parts.append(f"{type_counts['knowledge']} knowledge base entries")

        if type_counts.get("cross_document", 0) > 0:
            summary_parts.append(
                f"{type_counts['cross_document']} cross-document references"
            )

        if summary_parts:
            return f"Context includes: {', '.join(summary_parts)}"
        else:
            return "Context available from various sources"

    @performance_monitor.track_performance
    async def generate_enhanced_response(
        self, query: str, context: dict[str, Any], session_id: str, user_id: str
    ) -> str:
        """Generate enhanced AI response using large contextual windows"""

        context_items = context.get("context_items", [])
        context.get("context_summary", "")

        if not context_items:
            return f"""I understand you're asking about "{query}". 

I don't have specific information about this in our current knowledge base. To help you better, please upload relevant documents such as:

• Customer lists and contact information
• Product catalogs and service descriptions  
• Employee directories and organizational charts
• Business processes and procedure manuals
• Financial reports and analytics
• Contracts and legal documents

Once you upload these documents, I'll be able to provide detailed, contextualized responses based on your specific business information."""

        # Build comprehensive response with context
        response_parts = [
            f'Based on our comprehensive knowledge base, here\'s what I found regarding "{query}":',
            "",
        ]

        # Group context by type and category
        knowledge_items = [
            item for item in context_items if item.get("type") == "knowledge"
        ]
        conversation_items = [
            item for item in context_items if item.get("type") == "conversation"
        ]
        cross_doc_items = [
            item for item in context_items if item.get("type") == "cross_document"
        ]

        # Add knowledge base information
        if knowledge_items:
            response_parts.append("**From your knowledge base:**")

            # Group by category
            by_category = {}
            for item in knowledge_items:
                category = item.get("metadata", {}).get("category", "General")
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)

            for category, items in by_category.items():
                response_parts.append(f"\n*{category}:*")
                for item in items[:3]:  # Limit to top 3 per category
                    title = item.get("metadata", {}).get("title", "Document")
                    content_preview = (
                        item["content"][:300] + "..."
                        if len(item["content"]) > 300
                        else item["content"]
                    )
                    response_parts.append(f"• **{title}**: {content_preview}")

        # Add cross-document insights
        if cross_doc_items:
            response_parts.append("\n**Related information across documents:**")
            for item in cross_doc_items[:2]:  # Limit to top 2
                title = item.get("metadata", {}).get("title", "Related Document")
                content_preview = (
                    item["content"][:250] + "..."
                    if len(item["content"]) > 250
                    else item["content"]
                )
                response_parts.append(f"• **{title}**: {content_preview}")

        # Add conversation context if relevant
        if conversation_items and len(conversation_items) > 2:
            response_parts.append(
                "\n**Continuing our conversation:** Based on our discussion, I can provide more specific details about any aspect you'd like to explore further."
            )

        # Add helpful suggestions
        response_parts.extend(
            [
                "",
                "**Would you like me to:**",
                "• Provide more details about any specific item mentioned above?",
                "• Search for related information in other categories?",
                "• Help you upload additional documents to expand our knowledge base?",
                "• Create a summary or report based on this information?",
            ]
        )

        # Add context statistics
        stats = context.get("stats", {})
        if stats:
            total_tokens = context.get("total_tokens", 0)
            response_parts.append(
                f"\n*Context used: {stats.get('total_items', 0)} items, ~{total_tokens:,} tokens processed*"
            )

        return "\n".join(response_parts)

    async def save_enhanced_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        message_type: str,
        context_metadata: dict | None = None,
    ) -> str:
        """Save message with enhanced context metadata"""
        message_id = str(uuid4())

        # Enhanced metadata including context information
        metadata = {
            "context_items_used": (
                len(context_metadata.get("context_items", []))
                if context_metadata
                else 0
            ),
            "context_tokens": (
                context_metadata.get("total_tokens", 0) if context_metadata else 0
            ),
            "context_summary": (
                context_metadata.get("context_summary", "") if context_metadata else ""
            ),
            "enhanced_processing": True,
            "timestamp": datetime.now().isoformat(),
        }

        cursor = self.connection.cursor()
        await cursor.execute(
            """
        INSERT INTO CONVERSATION_MESSAGES 
        (MESSAGE_ID, SESSION_ID, USER_ID, CONTENT, MESSAGE_TYPE, CREATED_AT, METADATA)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                message_id,
                session_id,
                user_id,
                content,
                message_type,
                datetime.now(),
                json.dumps(metadata),
            ),
        )
        cursor.close()

        return message_id

    @performance_monitor.track_performance
    async def get_session_analytics(
        self, session_id: str, user_id: str
    ) -> dict[str, Any]:
        """Get analytics for a chat session"""
        cursor = self.connection.cursor(DictCursor)

        # Get session statistics
        await cursor.execute(
            """
        SELECT 
            COUNT(*) as total_messages,
            COUNT(CASE WHEN MESSAGE_TYPE = 'user' THEN 1 END) as user_messages,
            COUNT(CASE WHEN MESSAGE_TYPE = 'assistant' THEN 1 END) as assistant_messages,
            MIN(CREATED_AT) as session_start,
            MAX(CREATED_AT) as session_end,
            AVG(LENGTH(CONTENT)) as avg_message_length
        FROM CONVERSATION_MESSAGES
        WHERE SESSION_ID = %s AND USER_ID = %s
        """,
            (session_id, user_id),
        )

        stats = await cursor.fetchone()
        cursor.close()

        # Calculate session duration
        if stats["session_start"] and stats["session_end"]:
            duration = stats["session_end"] - stats["session_start"]
            duration_minutes = duration.total_seconds() / 60
        else:
            duration_minutes = 0

        return {
            "total_messages": stats["total_messages"],
            "user_messages": stats["user_messages"],
            "assistant_messages": stats["assistant_messages"],
            "session_duration_minutes": duration_minutes,
            "average_message_length": stats["avg_message_length"],
            "session_start": stats["session_start"],
            "session_end": stats["session_end"],
        }
