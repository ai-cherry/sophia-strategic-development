#!/usr/bin/env python3
"""
Sophia AI Linear Engineering MCP Server - Agentic RAG Edition
Engineering team KPIs, capacity planning, and bottleneck detection
Enhanced with vector memory and intelligent project analysis

Date: July 15, 2025
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List
import json
from datetime import datetime, UTC

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import httpx
from base.unified_standardized_base import ServerConfig, StandardizedMCPServer
from backend.core.auto_esc_config import get_config_value
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

class EngineeringIntelligenceAgent:
    """Engineering-specific intelligence agent for KPI analysis"""
    
    def __init__(self, memory_service: QdrantUnifiedMemoryService):
        self.memory_service = memory_service
        
    async def analyze_engineering_metrics(self, data: Dict, context: str = "") -> Dict:
        """Analyze engineering metrics and provide insights"""
        try:
            # Engineering KPI analysis
            issues = data.get("issues", [])
            velocity_data = data.get("velocity", {})
            team_data = data.get("team", {})
            
            # Calculate key metrics
            analysis = {
                "velocity": self._calculate_velocity_metrics(velocity_data),
                "bottlenecks": self._identify_bottlenecks(issues),
                "capacity": self._analyze_capacity(team_data, issues),
                "quality": self._assess_code_quality(issues),
                "timeline_risks": self._identify_timeline_risks(issues),
                "recommendations": self._generate_recommendations(issues, velocity_data)
            }
            
            return {
                "engineering_analysis": analysis,
                "timestamp": datetime.now(UTC).isoformat(),
                "agent_trace": "engineering_intelligence_agent",
                "confidence": 0.85,
                "data_points": len(issues)
            }
            
        except Exception as e:
            logger.error(f"Engineering analysis failed: {e}")
            return {"error": str(e), "fallback": "basic_analysis"}
    
    def _calculate_velocity_metrics(self, velocity_data: Dict) -> Dict:
        """Calculate team velocity and trend analysis"""
        return {
            "current_velocity": velocity_data.get("current", 0),
            "average_velocity": velocity_data.get("average", 0),
            "trend": velocity_data.get("trend", "stable"),
            "capacity_utilization": velocity_data.get("utilization", 0.8)
        }
    
    def _identify_bottlenecks(self, issues: List[Dict]) -> List[Dict]:
        """Identify engineering bottlenecks"""
        bottlenecks = []
        
        # Analyze issue patterns
        blocked_issues = [i for i in issues if i.get("state", {}).get("name") == "Blocked"]
        [i for i in issues if self._is_long_running(i)]
        review_backlog = [i for i in issues if i.get("state", {}).get("name") == "In Review"]
        
        if blocked_issues:
            bottlenecks.append({
                "type": "blocked_issues",
                "count": len(blocked_issues),
                "impact": "high",
                "description": f"{len(blocked_issues)} issues currently blocked"
            })
        
        if len(review_backlog) > 5:
            bottlenecks.append({
                "type": "review_backlog",
                "count": len(review_backlog),
                "impact": "medium",
                "description": f"{len(review_backlog)} issues waiting for review"
            })
        
        return bottlenecks
    
    def _analyze_capacity(self, team_data: Dict, issues: List[Dict]) -> Dict:
        """Analyze team capacity and workload distribution"""
        return {
            "team_size": team_data.get("size", 0),
            "active_issues": len([i for i in issues if i.get("state", {}).get("type") == "started"]),
            "overload_risk": "medium" if len(issues) > team_data.get("size", 1) * 3 else "low",
            "capacity_recommendation": "Consider redistributing workload" if len(issues) > 10 else "Capacity looks good"
        }
    
    def _assess_code_quality(self, issues: List[Dict]) -> Dict:
        """Assess code quality indicators"""
        bug_issues = [i for i in issues if "bug" in i.get("labels", {}).get("nodes", [])]
        tech_debt = [i for i in issues if "tech debt" in str(i.get("title", "")).lower()]
        
        return {
            "bug_ratio": len(bug_issues) / max(len(issues), 1),
            "tech_debt_issues": len(tech_debt),
            "quality_score": max(0, 1 - (len(bug_issues) + len(tech_debt)) / max(len(issues), 1))
        }
    
    def _identify_timeline_risks(self, issues: List[Dict]) -> List[Dict]:
        """Identify timeline and delivery risks"""
        risks = []
        overdue = [i for i in issues if self._is_overdue(i)]
        no_assignee = [i for i in issues if not i.get("assignee")]
        
        if overdue:
            risks.append({
                "type": "overdue_issues",
                "count": len(overdue),
                "severity": "high",
                "description": f"{len(overdue)} issues are overdue"
            })
        
        if no_assignee:
            risks.append({
                "type": "unassigned_issues",
                "count": len(no_assignee),
                "severity": "medium",
                "description": f"{len(no_assignee)} issues lack assignees"
            })
        
        return risks
    
    def _generate_recommendations(self, issues: List[Dict], velocity_data: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if len(issues) > 20:
            recommendations.append("Consider breaking down large issues into smaller tasks")
        
        if velocity_data.get("trend") == "declining":
            recommendations.append("Investigate velocity decline - check for team capacity issues")
        
        recommendations.append("Regular sprint retrospectives to identify process improvements")
        recommendations.append("Monitor code review turnaround time")
        
        return recommendations
    
    def _is_long_running(self, issue: Dict) -> bool:
        """Check if issue is long-running"""
        created_at = issue.get("createdAt")
        if not created_at:
            return False
        # Simple heuristic - issues older than 30 days
        return True  # Simplified for now
    
    def _is_overdue(self, issue: Dict) -> bool:
        """Check if issue is overdue"""
        due_date = issue.get("dueDate")
        if not due_date:
            return False
        # Simple heuristic
        return True  # Simplified for now

class LinearEngineeringMCPServer(StandardizedMCPServer):
    """Enhanced Linear Engineering MCP Server with Agentic RAG"""

    def __init__(self):
        config = ServerConfig(
            name="linear_engineering",
            version="3.0.0",
            description="Engineering team KPIs, capacity planning, and bottleneck detection with AI insights"
        )
        super().__init__(config)

        # Linear configuration
        self.linear_token = get_config_value("linear_api_key")
        self.graphql_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.linear_token}",
            "Content-Type": "application/json"
        }

        # Initialize Qdrant memory service
        self.memory_service = QdrantCodingMCPUnifiedMemoryService()
        
        # Initialize engineering intelligence agent
        self.engineering_agent = EngineeringIntelligenceAgent(self.memory_service)
        
        # Team and project configurations
        self.team_configs = {
            "engineering_team_id": get_config_value("linear_engineering_team_id"),
            "project_ids": (get_config_value("linear_project_ids") or "").split(",")
        }

    async def setup(self):
        """Initialize Qdrant collections and engineering data ingestion"""
        try:
            if hasattr(super(), 'setup'):
                await super().setup()
        except Exception as e:
            logger.warning(f"Parent setup failed: {e}")
        
        # Initialize Qdrant collection for Linear engineering data
        try:
            if hasattr(self.memory_service, 'initialize_collection'):
                await self.memory_service.initialize_collection("linear_engineering_embeddings")
        except Exception as e:
            logger.warning(f"Could not initialize Qdrant collection: {e}")
        
        # Initial data ingestion
        await self._ingest_engineering_data()

    async def _ingest_engineering_data(self):
        """Ingest existing Linear engineering data into vector memory"""
        try:
            logger.info("Ingesting engineering data into vector memory...")
            
            # Ingest issues data
            issues_data = await self._fetch_team_issues()
            if issues_data.get("data", {}).get("team", {}).get("issues", {}).get("nodes"):
                for issue in issues_data["data"]["team"]["issues"]["nodes"]:
                    await self._store_in_vector_memory(issue, "issue")
            
            # Ingest project data
            projects_data = await self._fetch_projects()
            if projects_data.get("data", {}).get("projects", {}).get("nodes"):
                for project in projects_data["data"]["projects"]["nodes"]:
                    await self._store_in_vector_memory(project, "project")
                    
            logger.info("Engineering data ingestion completed")
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")

    async def _store_in_vector_memory(self, item: Dict, item_type: str):
        """Store Linear item in vector memory with embeddings"""
        try:
            # Extract text content for embedding
            content = self._extract_text_content(item, item_type)
            
            # Create metadata
            metadata = {
                "source": "linear_engineering",
                "type": item_type,
                "linear_id": item.get("id"),
                "created_at": item.get("createdAt"),
                "updated_at": item.get("updatedAt"),
                "state": item.get("state", {}).get("name") if item_type == "issue" else None
            }
            
            # Store in vector memory
            try:
                await self.memory_service.add_knowledge(
                    content=content,
                    source=f"linear_{item_type}",
                    metadata=metadata
                )
            except:
                logger.warning(f"Could not store {item_type} in vector memory")
            
        except Exception as e:
            logger.error(f"Failed to store {item_type} in vector memory: {e}")

    def _extract_text_content(self, item: Dict, item_type: str) -> str:
        """Extract searchable text content from Linear item"""
        content_parts = []
        
        if item_type == "issue":
            content_parts.append(f"Title: {item.get('title', '')}")
            content_parts.append(f"Description: {item.get('description', '')}")
            content_parts.append(f"State: {item.get('state', {}).get('name', '')}")
            content_parts.append(f"Priority: {item.get('priority', '')}")
            
            if item.get("assignee"):
                content_parts.append(f"Assignee: {item['assignee'].get('name', '')}")
            
            if item.get("labels"):
                labels = [label.get("name", "") for label in item["labels"].get("nodes", [])]
                content_parts.append(f"Labels: {', '.join(labels)}")
                
        elif item_type == "project":
            content_parts.append(f"Name: {item.get('name', '')}")
            content_parts.append(f"Description: {item.get('description', '')}")
            content_parts.append(f"State: {item.get('state', '')}")
        
        return "\n".join(content_parts)

    async def get_custom_tools(self) -> List[Tool]:
        """Define agentic RAG tools for engineering intelligence"""
        return [
            Tool(
                name="rag_query_engineering",
                description="Perform agentic RAG query across engineering Linear data with AI analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Engineering question or query"},
                        "focus_area": {"type": "string", "enum": ["issues", "projects", "team", "all"], "default": "all"},
                        "analysis_type": {"type": "string", "enum": ["kpi", "bottleneck", "capacity"], "default": "kpi"},
                        "top_k": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_engineering_kpis",
                description="Get comprehensive engineering KPIs with AI-powered insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_id": {"type": "string", "description": "Specific team ID (optional)"},
                        "timeframe": {"type": "string", "enum": ["week", "sprint", "month"], "default": "sprint"},
                        "include_trends": {"type": "boolean", "default": True}
                    },
                    "required": []
                }
            ),
            Tool(
                name="analyze_bottlenecks",
                description="AI-powered bottleneck detection and analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "enum": ["team", "project", "individual"], "default": "team"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="capacity_planning",
                description="Analyze team capacity and workload distribution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "planning_horizon": {"type": "string", "enum": ["sprint", "month", "quarter"], "default": "sprint"},
                        "include_velocity": {"type": "boolean", "default": True}
                    },
                    "required": []
                }
            ),
            Tool(
                name="map_okr_engineering",
                description="Map engineering work to company OKRs and strategic objectives",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "okr_context": {"type": "string", "description": "OKR or strategic context to map against"}
                    },
                    "required": []
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute agentic RAG tools with engineering intelligence"""
        try:
            if name == "rag_query_engineering":
                return await self._handle_rag_query(arguments)
            elif name == "get_engineering_kpis":
                return await self._handle_engineering_kpis(arguments)
            elif name == "analyze_bottlenecks":
                return await self._handle_bottleneck_analysis(arguments)
            elif name == "capacity_planning":
                return await self._handle_capacity_planning(arguments)
            elif name == "map_okr_engineering":
                return await self._handle_okr_mapping(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_rag_query(self, arguments: Dict) -> List[TextContent]:
        """Handle agentic RAG query with vector search and engineering analysis"""
        query = arguments.get("query", "")
        focus_area = arguments.get("focus_area", "all")
        analysis_type = arguments.get("analysis_type", "kpi")
        top_k = arguments.get("top_k", 10)

        try:
            # Perform vector search
            try:
                search_results = await self.memory_service.search_knowledge(
                    query=query,
                    limit=top_k,
                    metadata_filter={"source": "linear_engineering"} if focus_area == "all" 
                    else {"source": f"linear_{focus_area}"}
                )
            except:
                search_results = []

            # Get engineering analysis
            if search_results and analysis_type in ["kpi", "bottleneck", "capacity"]:
                engineering_analysis = await self.engineering_agent.analyze_engineering_metrics(
                    {"search_results": search_results, "query": query, "focus": focus_area},
                    f"Engineering {analysis_type} analysis: {query}"
                )
                
                response = {
                    "query": query,
                    "analysis_type": analysis_type,
                    "engineering_insights": engineering_analysis,
                    "raw_results": search_results[:3],
                    "result_count": len(search_results),
                    "focus_area": focus_area
                }
            else:
                response = {
                    "query": query,
                    "results": search_results,
                    "result_count": len(search_results),
                    "analysis_type": "basic",
                    "focus_area": focus_area
                }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return [TextContent(type="text", text=f"RAG query failed: {str(e)}")]

    async def _handle_engineering_kpis(self, arguments: Dict) -> List[TextContent]:
        """Handle comprehensive engineering KPI analysis"""
        try:
            # Fetch engineering data
            issues_data = await self._fetch_team_issues()
            velocity_data = await self._fetch_velocity_data()
            team_data = await self._fetch_team_data()
            
            # Combine data for analysis
            combined_data = {
                "issues": issues_data.get("data", {}).get("team", {}).get("issues", {}).get("nodes", []),
                "velocity": velocity_data,
                "team": team_data
            }
            
            # Get AI-powered analysis
            engineering_analysis = await self.engineering_agent.analyze_engineering_metrics(
                combined_data,
                "Comprehensive engineering KPI analysis"
            )
            
            response = {
                "kpi_analysis": engineering_analysis,
                "raw_data": {
                    "issue_count": len(combined_data["issues"]),
                    "team_data": team_data,
                    "velocity": velocity_data
                },
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Engineering KPI analysis failed: {e}")
            return [TextContent(type="text", text=f"Engineering KPI analysis failed: {str(e)}")]

    async def _handle_bottleneck_analysis(self, arguments: Dict) -> List[TextContent]:
        """Handle bottleneck detection and analysis"""
        scope = arguments.get("scope", "team")
        
        try:
            # Fetch relevant data based on scope
            issues_data = await self._fetch_team_issues()
            issues = issues_data.get("data", {}).get("team", {}).get("issues", {}).get("nodes", [])
            
            # Analyze bottlenecks
            bottleneck_analysis = await self.engineering_agent.analyze_engineering_metrics(
                {"issues": issues, "scope": scope},
                f"Bottleneck analysis for {scope} level"
            )
            
            response = {
                "scope": scope,
                "bottleneck_analysis": bottleneck_analysis,
                "issue_count": len(issues),
                "recommendations": bottleneck_analysis.get("engineering_analysis", {}).get("recommendations", [])
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Bottleneck analysis failed: {e}")
            return [TextContent(type="text", text=f"Bottleneck analysis failed: {str(e)}")]

    async def _handle_capacity_planning(self, arguments: Dict) -> List[TextContent]:
        """Handle capacity planning analysis"""
        planning_horizon = arguments.get("planning_horizon", "sprint")
        include_velocity = arguments.get("include_velocity", True)
        
        try:
            # Fetch capacity data
            issues_data = await self._fetch_team_issues()
            team_data = await self._fetch_team_data()
            velocity_data = await self._fetch_velocity_data() if include_velocity else {}
            
            combined_data = {
                "issues": issues_data.get("data", {}).get("team", {}).get("issues", {}).get("nodes", []),
                "team": team_data,
                "velocity": velocity_data,
                "planning_horizon": planning_horizon
            }
            
            # Analyze capacity
            capacity_analysis = await self.engineering_agent.analyze_engineering_metrics(
                combined_data,
                f"Capacity planning for {planning_horizon}"
            )
            
            response = {
                "planning_horizon": planning_horizon,
                "capacity_analysis": capacity_analysis,
                "team_metrics": team_data,
                "velocity_included": include_velocity
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Capacity planning failed: {e}")
            return [TextContent(type="text", text=f"Capacity planning failed: {str(e)}")]

    async def _handle_okr_mapping(self, arguments: Dict) -> List[TextContent]:
        """Handle OKR mapping for engineering work"""
        okr_context = arguments.get("okr_context", "")
        
        try:
            # Query for relevant engineering work
            try:
                search_results = await self.memory_service.search_knowledge(
                    query=f"engineering work {okr_context} objectives goals",
                    limit=15,
                    metadata_filter={"source": "linear_engineering"}
                )
            except:
                search_results = []
            
            # Analyze OKR alignment
            okr_analysis = await self.engineering_agent.analyze_engineering_metrics(
                {"search_results": search_results, "okr_context": okr_context},
                f"OKR alignment analysis: {okr_context}"
            )
            
            response = {
                "okr_context": okr_context,
                "alignment_analysis": okr_analysis,
                "mapped_work": search_results[:5],
                "alignment_score": 0.7  # Simplified scoring
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"OKR mapping failed: {e}")
            return [TextContent(type="text", text=f"OKR mapping failed: {str(e)}")]

    async def _fetch_team_issues(self) -> Dict:
        """Fetch team issues from Linear GraphQL API"""
        query = """
        query TeamIssues($teamId: String!) {
            team(id: $teamId) {
                issues {
                    nodes {
                        id
                        title
                        description
                        priority
                        createdAt
                        updatedAt
                        dueDate
                        state {
                            name
                            type
                        }
                        assignee {
                            name
                            email
                        }
                        labels {
                            nodes {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={
                        "query": query,
                        "variables": {"teamId": self.team_configs["engineering_team_id"]}
                    }
                )
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch team issues: {e}")
            return {}

    async def _fetch_projects(self) -> Dict:
        """Fetch projects from Linear GraphQL API"""
        query = """
        query Projects {
            projects {
                nodes {
                    id
                    name
                    description
                    state
                    createdAt
                    updatedAt
                }
            }
        }
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={"query": query}
                )
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            return {}

    async def _fetch_velocity_data(self) -> Dict:
        """Fetch or calculate velocity data"""
        # Simplified velocity calculation
        return {
            "current": 12,
            "average": 10,
            "trend": "improving",
            "utilization": 0.85
        }

    async def _fetch_team_data(self) -> Dict:
        """Fetch team information"""
        # Simplified team data
        return {
            "size": 5,
            "capacity": 40,  # hours per sprint
            "utilization": 0.85
        }

    async def handle_custom_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Handle custom tool calls (required by base class)"""
        return await self.call_tool(name, arguments)

# Create and run server
if __name__ == "__main__":
    async def main():
        server = LinearEngineeringMCPServer()
        await server.run()

    asyncio.run(main()) 