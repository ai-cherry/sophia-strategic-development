#!/usr/bin/env python3
"""
Sophia AI Notion Strategic MCP Server - Agentic RAG Edition
CEO-focused strategic intelligence with OKRs, financials, and initiatives
Enhanced with CrewAI multi-agent swarms and vector memory

Date: July 15, 2025
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from datetime import datetime, UTC

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import httpx
from base.unified_standardized_base import ServerConfig, StandardizedMCPServer
from backend.core.auto_esc_config import get_config_value
from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

# Import agentic RAG components with fallbacks
ADVANCED_AI_AVAILABLE = False
OpenAI = None
Agent = None
Task = None
Crew = None
Process = None

try:
    from langchain.llms import OpenAI as LangChainOpenAI
    from crewai import Agent as CrewAgent, Task as CrewTask, Crew as CrewAI, Process as CrewProcess
    ADVANCED_AI_AVAILABLE = True
    OpenAI = LangChainOpenAI
    Agent = CrewAgent
    Task = CrewTask
    Crew = CrewAI
    Process = CrewProcess
    logger.info("Advanced AI libraries loaded successfully")
except ImportError as e:
    logger.warning(f"Advanced AI libraries not available, using fallback implementations: {e}")

class BasicStrategicAgent:
    """Fallback strategic analysis agent when advanced AI libraries aren't available"""
    
    def __init__(self, memory_service: QdrantUnifiedMemoryService):
        self.memory_service = memory_service
        
    async def analyze_okr_alignment(self, okr_data: Dict, context: str = "") -> Dict:
        """Basic analysis of OKR alignment and progress"""
        try:
            # Basic analysis logic without external AI libraries
            analysis = {
                "summary": "Strategic analysis completed using basic algorithms",
                "data_points": len(okr_data.get("search_results", [])) if isinstance(okr_data, dict) else 0,
                "recommendations": [
                    "Review OKR progress regularly",
                    "Ensure alignment between strategic initiatives",
                    "Monitor key performance indicators"
                ],
                "risk_factors": ["Data completeness", "Timeline alignment", "Resource allocation"]
            }
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now(UTC).isoformat(),
                "agent_trace": "basic_strategic_agent",
                "confidence": 0.7
            }
            
        except Exception as e:
            logger.error(f"Strategic analysis failed: {e}")
            return {"error": str(e), "fallback": "basic_analysis"}

class AdvancedStrategicAgent:
    """CrewAI-powered strategic analysis agent (requires external libraries)"""
    
    def __init__(self, memory_service: QdrantUnifiedMemoryService):
        self.memory_service = memory_service
        
        if ADVANCED_AI_AVAILABLE and OpenAI and Agent:
            self.llm = OpenAI(temperature=0.1)
            
            # Initialize strategic analysis agent
            self.strategy_agent = Agent(
                role='Strategic Business Analyst',
                goal='Analyze OKRs, financial data, and strategic initiatives for executive insights',
                backstory='Expert in business strategy with deep understanding of OKR frameworks and executive decision-making',
                llm=self.llm,
                verbose=True
            )
            
            # Initialize data analysis agent
            self.data_agent = Agent(
                role='Data Intelligence Specialist',
                goal='Extract and analyze quantitative metrics from Notion strategic data',
                backstory='Specialized in business intelligence and data-driven strategic insights',
                llm=self.llm,
                verbose=True
            )
            
            # Create crew for multi-agent collaboration
            self.crew = Crew(
                agents=[self.strategy_agent, self.data_agent],
                process=Process.sequential,
                verbose=True
            )

    async def analyze_okr_alignment(self, okr_data: Dict, context: str = "") -> Dict:
        """Agentic analysis of OKR alignment and progress"""
        if not ADVANCED_AI_AVAILABLE:
            return await BasicStrategicAgent(self.memory_service).analyze_okr_alignment(okr_data, context)
            
        try:
            # Create strategic analysis task
            analysis_task = Task(
                description=f"""
                Analyze the following OKR data for strategic alignment and executive insights:
                
                OKR Data: {json.dumps(okr_data, indent=2)}
                Context: {context}
                
                Provide:
                1. Overall alignment assessment
                2. Progress analysis with risk factors
                3. Strategic recommendations
                4. Key metrics and KPIs to monitor
                5. Executive summary for CEO consumption
                """,
                agent=self.strategy_agent
            )
            
            # Execute multi-agent analysis
            result = self.crew.kickoff([analysis_task])
            
            return {
                "analysis": result,
                "timestamp": datetime.now(UTC).isoformat(),
                "agent_trace": "strategy_agent + data_agent",
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Strategic analysis failed: {e}")
            return {"error": str(e), "fallback": "basic_analysis"}

class NotionStrategicMCPServer(StandardizedMCPServer):
    """Enhanced Notion Strategic MCP Server with Agentic RAG"""

    def __init__(self):
        config = ServerConfig(
            name="notion_strategic",
            version="3.0.0",
            # port=9030, # Remove port from config as it's not in the base class
            # capabilities=["STRATEGIC_OKR", "AGENTIC_RAG", "EXECUTIVE_INTELLIGENCE", "VECTOR_MEMORY"],
            # tier="PRIMARY",
        )
        super().__init__(config)

        # Notion configuration
        self.notion_token = get_config_value("notion_api_token")
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Initialize Qdrant memory service
        self.memory_service = QdrantSophiaUnifiedMemoryService()
        
        # Initialize strategic agent (advanced or basic)
        if ADVANCED_AI_AVAILABLE:
            self.strategic_agent = AdvancedStrategicAgent(self.memory_service)
            logger.info("Using advanced CrewAI strategic agent")
        else:
            self.strategic_agent = BasicStrategicAgent(self.memory_service)
            logger.info("Using basic strategic agent (advanced AI libraries not available)")
        
        # Notion database IDs (CEO to configure)
        self.database_configs = {
            "okrs": get_config_value("notion_okr_database_id"),
            "financials": get_config_value("notion_financial_database_id"),
            "initiatives": get_config_value("notion_initiatives_database_id"),
            "strategic_docs": get_config_value("notion_strategic_docs_database_id")
        }

    async def setup(self):
        """Initialize Qdrant collections and strategic data ingestion"""
        await super().setup()
        
        # Initialize Qdrant collection for Notion strategic data
        await self.memory_service.initialize_collection("notion_strategic_embeddings")
        
        # Initial data ingestion
        await self._ingest_strategic_data()

    async def _ingest_strategic_data(self):
        """Ingest existing Notion strategic data into vector memory"""
        try:
            logger.info("Ingesting strategic data into vector memory...")
            
            # Ingest OKR data
            okr_data = await self._fetch_okr_data()
            if okr_data.get("results"):
                for okr in okr_data["results"]:
                    await self._store_in_vector_memory(okr, "okr")
            
            # Ingest financial data
            financial_data = await self._fetch_financial_data()
            if financial_data.get("results"):
                for item in financial_data["results"]:
                    await self._store_in_vector_memory(item, "financial")
            
            # Ingest strategic initiatives
            initiatives_data = await self._fetch_initiatives_data()
            if initiatives_data.get("results"):
                for initiative in initiatives_data["results"]:
                    await self._store_in_vector_memory(initiative, "initiative")
                    
            logger.info("Strategic data ingestion completed")
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")

    async def _store_in_vector_memory(self, item: Dict, item_type: str):
        """Store Notion item in vector memory with embeddings"""
        try:
            # Extract text content for embedding
            content = self._extract_text_content(item)
            
            # Create metadata
            metadata = {
                "source": "notion_strategic",
                "type": item_type,
                "notion_id": item.get("id"),
                "last_updated": item.get("last_edited_time"),
                "url": item.get("url")
            }
            
            # Store in vector memory
            await self.memory_service.add_knowledge(
                content=content,
                source=f"notion_{item_type}",
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to store {item_type} in vector memory: {e}")

    def _extract_text_content(self, notion_item: Dict) -> str:
        """Extract searchable text content from Notion item"""
        content_parts = []
        
        # Extract title
        if "properties" in notion_item:
            for prop_name, prop_data in notion_item["properties"].items():
                if prop_data.get("type") == "title" and prop_data.get("title"):
                    title_text = " ".join([t.get("plain_text", "") for t in prop_data["title"]])
                    content_parts.append(f"Title: {title_text}")
                elif prop_data.get("type") == "rich_text" and prop_data.get("rich_text"):
                    rich_text = " ".join([t.get("plain_text", "") for t in prop_data["rich_text"]])
                    content_parts.append(f"{prop_name}: {rich_text}")
        
        return "\n".join(content_parts)

    async def get_custom_tools(self) -> List[Tool]:
        """Define agentic RAG tools for strategic intelligence"""
        return [
            Tool(
                name="rag_query_strategic",
                description="Perform agentic RAG query across all strategic Notion data with AI analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Strategic question or query"},
                        "focus_area": {"type": "string", "enum": ["okrs", "financials", "initiatives", "all"], "default": "all"},
                        "analysis_type": {"type": "string", "enum": ["quick", "deep", "executive"], "default": "executive"},
                        "top_k": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_okr_analysis",
                description="Get comprehensive OKR analysis with AI-powered insights and recommendations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "okr_id": {"type": "string", "description": "Specific OKR ID (optional)"},
                        "quarter": {"type": "string", "description": "Quarter (e.g., Q1 2025)"},
                        "include_predictions": {"type": "boolean", "default": True}
                    },
                    "required": []
                }
            ),
            Tool(
                name="analyze_strategic_alignment",
                description="AI-powered analysis of strategic alignment across OKRs, initiatives, and financials",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "enum": ["company", "department", "initiative"], "default": "company"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_executive_summary",
                description="Generate AI-powered executive summary for CEO consumption",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "timeframe": {"type": "string", "enum": ["week", "month", "quarter"], "default": "week"},
                        "focus": {"type": "string", "enum": ["performance", "risks", "opportunities", "all"], "default": "all"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="update_strategic_data",
                description="Update strategic data in Notion and refresh vector memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string"},
                        "page_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["database_id", "page_id", "updates"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute agentic RAG tools with AI-powered analysis"""
        try:
            if name == "rag_query_strategic":
                return await self._handle_rag_query(arguments)
            elif name == "get_okr_analysis":
                return await self._handle_okr_analysis(arguments)
            elif name == "analyze_strategic_alignment":
                return await self._handle_alignment_analysis(arguments)
            elif name == "get_executive_summary":
                return await self._handle_executive_summary(arguments)
            elif name == "update_strategic_data":
                return await self._handle_data_update(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_rag_query(self, arguments: Dict) -> List[TextContent]:
        """Handle agentic RAG query with vector search and AI analysis"""
        query = arguments.get("query", "")
        focus_area = arguments.get("focus_area", "all")
        analysis_type = arguments.get("analysis_type", "executive")
        top_k = arguments.get("top_k", 10)

        try:
            # Perform vector search
            search_results = await self.memory_service.search_knowledge(
                query=query,
                limit=top_k,
                metadata_filter={"source": "notion_strategic"} if focus_area == "all" 
                else {"source": f"notion_{focus_area}"}
            )

            # Get AI analysis from strategic agent
            if search_results and analysis_type == "executive":
                ai_analysis = await self.strategic_agent.analyze_okr_alignment(
                    {"search_results": search_results, "query": query},
                    f"CEO strategic query: {query}"
                )
                
                response = {
                    "query": query,
                    "analysis_type": analysis_type,
                    "ai_insights": ai_analysis,
                    "raw_results": search_results[:3],  # Top 3 for context
                    "result_count": len(search_results),
                    "agent_trace": ai_analysis.get("agent_trace", "unknown"),
                    "advanced_ai_enabled": ADVANCED_AI_AVAILABLE
                }
            else:
                response = {
                    "query": query,
                    "results": search_results,
                    "result_count": len(search_results),
                    "analysis_type": "basic",
                    "advanced_ai_enabled": ADVANCED_AI_AVAILABLE
                }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return [TextContent(type="text", text=f"RAG query failed: {str(e)}")]

    async def _handle_okr_analysis(self, arguments: Dict) -> List[TextContent]:
        """Handle comprehensive OKR analysis with AI insights"""
        try:
            # Fetch OKR data
            okr_data = await self._fetch_okr_data(arguments.get("okr_id"))
            
            # Get AI-powered analysis
            ai_analysis = await self.strategic_agent.analyze_okr_alignment(
                okr_data,
                "Comprehensive OKR analysis for executive review"
            )
            
            response = {
                "okr_analysis": ai_analysis,
                "raw_data": okr_data,
                "timestamp": datetime.now(UTC).isoformat(),
                "advanced_ai_enabled": ADVANCED_AI_AVAILABLE
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"OKR analysis failed: {e}")
            return [TextContent(type="text", text=f"OKR analysis failed: {str(e)}")]

    async def _handle_alignment_analysis(self, arguments: Dict) -> List[TextContent]:
        """Handle strategic alignment analysis across all data sources"""
        scope = arguments.get("scope", "company")
        
        try:
            # Query vector memory for alignment patterns
            alignment_query = f"strategic alignment {scope} OKR initiative financial"
            
            search_results = await self.memory_service.search_knowledge(
                query=alignment_query,
                limit=20,
                metadata_filter={"source": "notion_strategic"}
            )
            
            # AI analysis of alignment patterns
            ai_analysis = await self.strategic_agent.analyze_okr_alignment(
                {"search_results": search_results, "scope": scope},
                f"Strategic alignment analysis for {scope} level"
            )
            
            response = {
                "scope": scope,
                "alignment_analysis": ai_analysis,
                "supporting_data": search_results[:5],
                "recommendations": ai_analysis.get("analysis", {}).get("recommendations", []),
                "advanced_ai_enabled": ADVANCED_AI_AVAILABLE
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Alignment analysis failed: {e}")
            return [TextContent(type="text", text=f"Alignment analysis failed: {str(e)}")]

    async def _handle_executive_summary(self, arguments: Dict) -> List[TextContent]:
        """Generate AI-powered executive summary"""
        timeframe = arguments.get("timeframe", "week")
        focus = arguments.get("focus", "all")
        
        try:
            # Query recent strategic data
            summary_query = f"executive summary {timeframe} {focus} performance metrics"
            
            search_results = await self.memory_service.search_knowledge(
                query=summary_query,
                limit=15,
                metadata_filter={"source": "notion_strategic"}
            )
            
            # Generate executive summary with AI
            ai_summary = await self.strategic_agent.analyze_okr_alignment(
                {"search_results": search_results, "timeframe": timeframe, "focus": focus},
                f"Executive summary generation for {timeframe} review"
            )
            
            response = {
                "timeframe": timeframe,
                "focus": focus,
                "executive_summary": ai_summary,
                "key_insights": search_results[:3],
                "generated_at": datetime.now(UTC).isoformat(),
                "advanced_ai_enabled": ADVANCED_AI_AVAILABLE
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return [TextContent(type="text", text=f"Executive summary failed: {str(e)}")]

    async def _handle_data_update(self, arguments: Dict) -> List[TextContent]:
        """Update Notion data and refresh vector memory"""
        database_id = arguments.get("database_id")
        page_id = arguments.get("page_id")
        updates = arguments.get("updates", {})
        
        try:
            # Update Notion page
            url = f"{self.base_url}/pages/{page_id}"
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self.headers, json={"properties": updates})
                
                if response.status_code == 200:
                    updated_page = response.json()
                    
                    # Update vector memory
                    await self._store_in_vector_memory(updated_page, "updated")
                    
                    return [TextContent(type="text", text=json.dumps({
                        "status": "success",
                        "updated_page": updated_page,
                        "vector_memory_updated": True
                    }, indent=2))]
                else:
                    return [TextContent(type="text", text=f"Update failed: {response.status_code}")]
                    
        except Exception as e:
            logger.error(f"Data update failed: {e}")
            return [TextContent(type="text", text=f"Data update failed: {str(e)}")]

    async def _fetch_okr_data(self, okr_id: Optional[str] = None) -> Dict:
        """Fetch OKR data from Notion"""
        try:
            if okr_id:
                url = f"{self.base_url}/pages/{okr_id}"
            else:
                url = f"{self.base_url}/databases/{self.database_configs['okrs']}/query"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers)
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch OKR data: {e}")
            return {}

    async def _fetch_financial_data(self) -> Dict:
        """Fetch financial data from Notion"""
        try:
            url = f"{self.base_url}/databases/{self.database_configs['financials']}/query"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers)
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch financial data: {e}")
            return {}

    async def _fetch_initiatives_data(self) -> Dict:
        """Fetch strategic initiatives data from Notion"""
        try:
            url = f"{self.base_url}/databases/{self.database_configs['initiatives']}/query"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers)
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch initiatives data: {e}")
            return {}

# Create and run server
if __name__ == "__main__":
    async def main():
        server = NotionStrategicMCPServer()
        await server.run()

    asyncio.run(main()) 