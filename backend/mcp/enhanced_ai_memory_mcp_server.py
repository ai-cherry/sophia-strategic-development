#!/usr/bin/env python3
"""
Enhanced AI Memory MCP Server
Extended with Slack, Linear, and Foundational Knowledge Base integration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Enhanced imports
from backend.mcp.ai_memory_mcp_server import EnhancedAiMemoryMCPServer as BaseAiMemoryMCPServer
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)


class EnhancedMemoryCategory(Enum):
    """Extended memory categories for new data sources"""
    # Existing categories
    GONG_CALL_SUMMARY = "gong_call_summary"
    GONG_CALL_INSIGHT = "gong_call_insight"
    HUBSPOT_DEAL_ANALYSIS = "hubspot_deal_analysis"
    SALES_COACHING = "sales_coaching"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    
    # New Slack categories
    SLACK_CONVERSATION = "slack_conversation"
    SLACK_INSIGHT = "slack_insight"
    SLACK_DECISION = "slack_decision"
    SLACK_ACTION_ITEM = "slack_action_item"
    SLACK_KNOWLEDGE_SHARE = "slack_knowledge_share"
    SLACK_TEAM_UPDATE = "slack_team_update"
    SLACK_CUSTOMER_FEEDBACK = "slack_customer_feedback"
    
    # New Linear categories
    LINEAR_ISSUE = "linear_issue"
    LINEAR_PROJECT = "linear_project"
    LINEAR_MILESTONE = "linear_milestone"
    LINEAR_ROADMAP = "linear_roadmap"
    LINEAR_TEAM_VELOCITY = "linear_team_velocity"
    LINEAR_SPRINT_SUMMARY = "linear_sprint_summary"
    LINEAR_FEATURE_REQUEST = "linear_feature_request"
    
    # New Foundational KB categories
    FOUNDATIONAL_EMPLOYEE = "foundational_employee"
    FOUNDATIONAL_CUSTOMER = "foundational_customer"
    FOUNDATIONAL_PRODUCT = "foundational_product"
    FOUNDATIONAL_COMPETITOR = "foundational_competitor"
    FOUNDATIONAL_PROCESS = "foundational_process"
    FOUNDATIONAL_VALUE = "foundational_value"
    
    # New Knowledge Base categories
    KB_ARTICLE = "kb_article"
    KB_ENTITY = "kb_entity"
    KB_DOCUMENT = "kb_document"
    KB_INSIGHT = "kb_insight"
    KB_FAQ = "kb_faq"
    KB_BEST_PRACTICE = "kb_best_practice"


@dataclass
class EnhancedMemoryMetadata:
    """Enhanced metadata for new memory types"""
    # Common fields
    source_type: str
    source_id: str
    confidence_score: float = 0.8
    importance_score: float = 0.5
    business_value_score: float = 0.5
    
    # Slack-specific fields
    slack_channel_id: Optional[str] = None
    slack_channel_name: Optional[str] = None
    slack_user_id: Optional[str] = None
    slack_thread_ts: Optional[str] = None
    slack_participants: Optional[List[str]] = None
    
    # Linear-specific fields
    linear_project_id: Optional[str] = None
    linear_project_name: Optional[str] = None
    linear_team_id: Optional[str] = None
    linear_assignee_id: Optional[str] = None
    linear_priority: Optional[str] = None
    linear_status: Optional[str] = None
    
    # Foundational-specific fields
    foundational_type: Optional[str] = None
    foundational_department: Optional[str] = None
    foundational_tier: Optional[str] = None
    
    # Knowledge base-specific fields
    kb_category: Optional[str] = None
    kb_visibility: Optional[str] = None
    kb_author: Optional[str] = None
    kb_keywords: Optional[List[str]] = None


class EnhancedAiMemoryMCPServer(BaseAiMemoryMCPServer):
    """Enhanced AI Memory MCP Server with new data source integration"""
    
    def __init__(self):
        super().__init__()
        self.server_name = "enhanced-ai-memory"
        
        # Enhanced category exclusions
        self.category_exclusions.update({
            # Exclude test and temporary categories
            "test_category",
            "temp_data",
            "debug_info"
        })
    
    async def store_slack_conversation_memory(
        self,
        conversation_id: str,
        conversation_title: str,
        conversation_summary: str,
        channel_name: str,
        participants: List[str],
        key_topics: List[str],
        decisions_made: List[str],
        action_items: List[str],
        business_value_score: float = 0.6
    ) -> str:
        """Store Slack conversation as memory"""
        
        # Determine category based on content
        category = self._classify_slack_conversation(
            conversation_summary, decisions_made, action_items
        )
        
        # Create enhanced content
        content = f"""
        Slack Conversation: {conversation_title}
        Channel: #{channel_name}
        Participants: {', '.join(participants)}
        
        Summary: {conversation_summary}
        
        Key Topics: {', '.join(key_topics)}
        
        Decisions Made:
        {chr(10).join(f'- {decision}' for decision in decisions_made)}
        
        Action Items:
        {chr(10).join(f'- {item}' for item in action_items)}
        """
        
        # Enhanced metadata
        metadata = EnhancedMemoryMetadata(
            source_type="slack",
            source_id=conversation_id,
            business_value_score=business_value_score,
            slack_channel_name=channel_name,
            slack_participants=participants
        )
        
        # Store memory
        memory_id = await self.store_memory(
            content=content,
            category=category.value,
            tags=["slack", "conversation", channel_name] + key_topics,
            metadata=metadata.__dict__,
            importance_score=business_value_score
        )
        
        logger.info(f"Stored Slack conversation memory: {memory_id}")
        return memory_id
    
    async def store_linear_issue_memory(
        self,
        issue_id: str,
        issue_title: str,
        issue_description: str,
        project_name: str,
        assignee: str,
        priority: str,
        status: str,
        labels: List[str],
        importance_score: float = 0.5
    ) -> str:
        """Store Linear issue as memory"""
        
        # Determine category based on labels and priority
        category = self._classify_linear_issue(labels, priority, status)
        
        # Create content
        content = f"""
        Linear Issue: {issue_title}
        Project: {project_name}
        Assignee: {assignee}
        Priority: {priority}
        Status: {status}
        
        Description: {issue_description}
        
        Labels: {', '.join(labels)}
        """
        
        # Enhanced metadata
        metadata = EnhancedMemoryMetadata(
            source_type="linear",
            source_id=issue_id,
            importance_score=importance_score,
            linear_project_name=project_name,
            linear_assignee_id=assignee,
            linear_priority=priority,
            linear_status=status
        )
        
        # Store memory
        memory_id = await self.store_memory(
            content=content,
            category=category.value,
            tags=["linear", "issue", project_name, priority] + labels,
            metadata=metadata.__dict__,
            importance_score=importance_score
        )
        
        logger.info(f"Stored Linear issue memory: {memory_id}")
        return memory_id
    
    async def store_foundational_knowledge_memory(
        self,
        record_id: str,
        record_type: str,
        title: str,
        description: str,
        category: str,
        department: Optional[str] = None,
        importance_score: float = 0.7
    ) -> str:
        """Store foundational knowledge as memory"""
        
        # Map record type to memory category
        category_map = {
            "employee": EnhancedMemoryCategory.FOUNDATIONAL_EMPLOYEE,
            "customer": EnhancedMemoryCategory.FOUNDATIONAL_CUSTOMER,
            "product": EnhancedMemoryCategory.FOUNDATIONAL_PRODUCT,
            "competitor": EnhancedMemoryCategory.FOUNDATIONAL_COMPETITOR,
            "business_process": EnhancedMemoryCategory.FOUNDATIONAL_PROCESS,
            "organizational_value": EnhancedMemoryCategory.FOUNDATIONAL_VALUE
        }
        
        memory_category = category_map.get(record_type, EnhancedMemoryCategory.FOUNDATIONAL_EMPLOYEE)
        
        # Create content
        content = f"""
        Foundational Knowledge: {title}
        Type: {record_type.replace('_', ' ').title()}
        Category: {category}
        {f'Department: {department}' if department else ''}
        
        Description: {description}
        """
        
        # Enhanced metadata
        metadata = EnhancedMemoryMetadata(
            source_type="foundational",
            source_id=record_id,
            importance_score=importance_score,
            foundational_type=record_type,
            foundational_department=department
        )
        
        # Store memory
        memory_id = await self.store_memory(
            content=content,
            category=memory_category.value,
            tags=["foundational", record_type, category] + ([department] if department else []),
            metadata=metadata.__dict__,
            importance_score=importance_score
        )
        
        logger.info(f"Stored foundational knowledge memory: {memory_id}")
        return memory_id
    
    async def store_kb_article_memory(
        self,
        article_id: str,
        title: str,
        content: str,
        category: str,
        author: str,
        keywords: List[str],
        visibility: str = "internal",
        importance_score: float = 0.6
    ) -> str:
        """Store knowledge base article as memory"""
        
        # Create memory content
        memory_content = f"""
        Knowledge Base Article: {title}
        Category: {category}
        Author: {author}
        Visibility: {visibility}
        
        Content: {content[:2000]}{'...' if len(content) > 2000 else ''}
        
        Keywords: {', '.join(keywords)}
        """
        
        # Enhanced metadata
        metadata = EnhancedMemoryMetadata(
            source_type="knowledge_base",
            source_id=article_id,
            importance_score=importance_score,
            kb_category=category,
            kb_visibility=visibility,
            kb_author=author,
            kb_keywords=keywords
        )
        
        # Store memory
        memory_id = await self.store_memory(
            content=memory_content,
            category=EnhancedMemoryCategory.KB_ARTICLE.value,
            tags=["knowledge_base", "article", category] + keywords,
            metadata=metadata.__dict__,
            importance_score=importance_score
        )
        
        logger.info(f"Stored KB article memory: {memory_id}")
        return memory_id
    
    async def recall_slack_insights(
        self,
        query: str,
        channel_name: Optional[str] = None,
        date_range_days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Recall Slack conversation insights"""
        
        # Build search filters
        filters = {
            "categories": [cat.value for cat in [
                EnhancedMemoryCategory.SLACK_CONVERSATION,
                EnhancedMemoryCategory.SLACK_INSIGHT,
                EnhancedMemoryCategory.SLACK_DECISION,
                EnhancedMemoryCategory.SLACK_ACTION_ITEM
            ]]
        }
        
        if channel_name:
            filters["tags"] = [channel_name]
        
        # Add date filter
        cutoff_date = datetime.now() - timedelta(days=date_range_days)
        filters["created_after"] = cutoff_date.isoformat()
        
        # Perform search
        results = await self.recall_memories(
            query=query,
            filters=filters,
            limit=limit
        )
        
        logger.info(f"Found {len(results)} Slack insights for query: {query}")
        return results
    
    async def recall_linear_issue_details(
        self,
        query: str,
        project_name: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Recall Linear issue details"""
        
        # Build search filters
        filters = {
            "categories": [cat.value for cat in [
                EnhancedMemoryCategory.LINEAR_ISSUE,
                EnhancedMemoryCategory.LINEAR_PROJECT,
                EnhancedMemoryCategory.LINEAR_FEATURE_REQUEST
            ]]
        }
        
        tags = ["linear"]
        if project_name:
            tags.append(project_name)
        if priority:
            tags.append(priority)
        if status:
            tags.append(status)
        
        filters["tags"] = tags
        
        # Perform search
        results = await self.recall_memories(
            query=query,
            filters=filters,
            limit=limit
        )
        
        logger.info(f"Found {len(results)} Linear issues for query: {query}")
        return results
    
    async def recall_foundational_knowledge(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Recall foundational knowledge"""
        
        # Build search filters
        foundational_categories = [cat.value for cat in [
            EnhancedMemoryCategory.FOUNDATIONAL_EMPLOYEE,
            EnhancedMemoryCategory.FOUNDATIONAL_CUSTOMER,
            EnhancedMemoryCategory.FOUNDATIONAL_PRODUCT,
            EnhancedMemoryCategory.FOUNDATIONAL_COMPETITOR,
            EnhancedMemoryCategory.FOUNDATIONAL_PROCESS,
            EnhancedMemoryCategory.FOUNDATIONAL_VALUE
        ]]
        
        filters = {"categories": foundational_categories}
        
        tags = ["foundational"]
        if knowledge_type:
            tags.append(knowledge_type)
        if department:
            tags.append(department)
        
        filters["tags"] = tags
        
        # Perform search
        results = await self.recall_memories(
            query=query,
            filters=filters,
            limit=limit
        )
        
        logger.info(f"Found {len(results)} foundational knowledge items for query: {query}")
        return results
    
    async def recall_kb_articles(
        self,
        query: str,
        category: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Recall knowledge base articles"""
        
        # Build search filters
        filters = {
            "categories": [cat.value for cat in [
                EnhancedMemoryCategory.KB_ARTICLE,
                EnhancedMemoryCategory.KB_INSIGHT,
                EnhancedMemoryCategory.KB_FAQ,
                EnhancedMemoryCategory.KB_BEST_PRACTICE
            ]]
        }
        
        tags = ["knowledge_base"]
        if category:
            tags.append(category)
        if author:
            tags.append(author)
        
        filters["tags"] = tags
        
        # Perform search
        results = await self.recall_memories(
            query=query,
            filters=filters,
            limit=limit
        )
        
        logger.info(f"Found {len(results)} KB articles for query: {query}")
        return results
    
    def _classify_slack_conversation(
        self,
        summary: str,
        decisions: List[str],
        action_items: List[str]
    ) -> EnhancedMemoryCategory:
        """Classify Slack conversation based on content"""
        
        summary_lower = summary.lower()
        
        if decisions:
            return EnhancedMemoryCategory.SLACK_DECISION
        elif action_items:
            return EnhancedMemoryCategory.SLACK_ACTION_ITEM
        elif any(keyword in summary_lower for keyword in ["customer", "client", "feedback"]):
            return EnhancedMemoryCategory.SLACK_CUSTOMER_FEEDBACK
        elif any(keyword in summary_lower for keyword in ["update", "status", "progress"]):
            return EnhancedMemoryCategory.SLACK_TEAM_UPDATE
        elif any(keyword in summary_lower for keyword in ["knowledge", "share", "tip", "learn"]):
            return EnhancedMemoryCategory.SLACK_KNOWLEDGE_SHARE
        else:
            return EnhancedMemoryCategory.SLACK_CONVERSATION
    
    def _classify_linear_issue(
        self,
        labels: List[str],
        priority: str,
        status: str
    ) -> EnhancedMemoryCategory:
        """Classify Linear issue based on attributes"""
        
        labels_lower = [label.lower() for label in labels]
        
        if "feature" in labels_lower or "enhancement" in labels_lower:
            return EnhancedMemoryCategory.LINEAR_FEATURE_REQUEST
        elif "milestone" in labels_lower or "epic" in labels_lower:
            return EnhancedMemoryCategory.LINEAR_MILESTONE
        elif priority.lower() in ["urgent", "high"]:
            return EnhancedMemoryCategory.LINEAR_ISSUE
        else:
            return EnhancedMemoryCategory.LINEAR_ISSUE


# MCP Server setup
server = Server("enhanced-ai-memory")
enhanced_ai_memory = EnhancedAiMemoryMCPServer()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available AI Memory tools"""
    return [
        Tool(
            name="store_slack_conversation",
            description="Store Slack conversation as memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "conversation_title": {"type": "string"},
                    "conversation_summary": {"type": "string"},
                    "channel_name": {"type": "string"},
                    "participants": {"type": "array", "items": {"type": "string"}},
                    "key_topics": {"type": "array", "items": {"type": "string"}},
                    "decisions_made": {"type": "array", "items": {"type": "string"}},
                    "action_items": {"type": "array", "items": {"type": "string"}},
                    "business_value_score": {"type": "number", "default": 0.6}
                },
                "required": ["conversation_id", "conversation_title", "conversation_summary", "channel_name"]
            }
        ),
        Tool(
            name="store_linear_issue",
            description="Store Linear issue as memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string"},
                    "issue_title": {"type": "string"},
                    "issue_description": {"type": "string"},
                    "project_name": {"type": "string"},
                    "assignee": {"type": "string"},
                    "priority": {"type": "string"},
                    "status": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "importance_score": {"type": "number", "default": 0.5}
                },
                "required": ["issue_id", "issue_title", "issue_description", "project_name"]
            }
        ),
        Tool(
            name="store_foundational_knowledge",
            description="Store foundational knowledge as memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string"},
                    "record_type": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string"},
                    "department": {"type": "string"},
                    "importance_score": {"type": "number", "default": 0.7}
                },
                "required": ["record_id", "record_type", "title", "description", "category"]
            }
        ),
        Tool(
            name="store_kb_article",
            description="Store knowledge base article as memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "category": {"type": "string"},
                    "author": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "visibility": {"type": "string", "default": "internal"},
                    "importance_score": {"type": "number", "default": 0.6}
                },
                "required": ["article_id", "title", "content", "category", "author"]
            }
        ),
        Tool(
            name="recall_slack_insights",
            description="Recall Slack conversation insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "channel_name": {"type": "string"},
                    "date_range_days": {"type": "number", "default": 30},
                    "limit": {"type": "number", "default": 10}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="recall_linear_issues",
            description="Recall Linear issue details",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "project_name": {"type": "string"},
                    "priority": {"type": "string"},
                    "status": {"type": "string"},
                    "limit": {"type": "number", "default": 10}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="recall_foundational_knowledge",
            description="Recall foundational knowledge",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "knowledge_type": {"type": "string"},
                    "department": {"type": "string"},
                    "limit": {"type": "number", "default": 10}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="recall_kb_articles",
            description="Recall knowledge base articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "category": {"type": "string"},
                    "author": {"type": "string"},
                    "limit": {"type": "number", "default": 10}
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute AI Memory tools"""
    try:
        if name == "store_slack_conversation":
            result = await enhanced_ai_memory.store_slack_conversation_memory(**arguments)
            return [TextContent(type="text", text=f"Stored Slack conversation memory: {result}")]
        
        elif name == "store_linear_issue":
            result = await enhanced_ai_memory.store_linear_issue_memory(**arguments)
            return [TextContent(type="text", text=f"Stored Linear issue memory: {result}")]
        
        elif name == "store_foundational_knowledge":
            result = await enhanced_ai_memory.store_foundational_knowledge_memory(**arguments)
            return [TextContent(type="text", text=f"Stored foundational knowledge memory: {result}")]
        
        elif name == "store_kb_article":
            result = await enhanced_ai_memory.store_kb_article_memory(**arguments)
            return [TextContent(type="text", text=f"Stored KB article memory: {result}")]
        
        elif name == "recall_slack_insights":
            results = await enhanced_ai_memory.recall_slack_insights(**arguments)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
        elif name == "recall_linear_issues":
            results = await enhanced_ai_memory.recall_linear_issue_details(**arguments)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
        elif name == "recall_foundational_knowledge":
            results = await enhanced_ai_memory.recall_foundational_knowledge(**arguments)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
        elif name == "recall_kb_articles":
            results = await enhanced_ai_memory.recall_kb_articles(**arguments)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the Enhanced AI Memory MCP server"""
    try:
        await enhanced_ai_memory.initialize()
        logger.info("✅ Enhanced AI Memory MCP Server initialized")
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    
    except KeyboardInterrupt:
        logger.info("Shutting down Enhanced AI Memory MCP Server")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 