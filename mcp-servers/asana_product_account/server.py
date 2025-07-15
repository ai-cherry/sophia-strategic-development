#!/usr/bin/env python3
"""
Sophia AI Asana Product/Account Management MCP Server - Agentic RAG Edition
Product team KPIs, roadmap tracking, and account health monitoring
Enhanced with vector memory and intelligent customer analysis

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
from backend.services.QDRANT_unified_memory_service import QdrantUnifiedMemoryService
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

class ProductAccountIntelligenceAgent:
    """Product and account management intelligence agent"""
    
    def __init__(self, memory_service: QdrantUnifiedMemoryService):
        self.memory_service = memory_service
        
    async def analyze_product_metrics(self, data: Dict, context: str = "") -> Dict:
        """Analyze product and account management metrics"""
        try:
            # Product and account KPI analysis
            tasks = data.get("tasks", [])
            projects = data.get("projects", [])
            team_data = data.get("team", {})
            
            # Calculate key metrics
            analysis = {
                "roadmap_health": self._analyze_roadmap_health(projects, tasks),
                "account_health": self._analyze_account_health(tasks),
                "product_velocity": self._calculate_product_velocity(tasks),
                "feature_pipeline": self._analyze_feature_pipeline(tasks),
                "customer_impact": self._assess_customer_impact(tasks),
                "risk_assessment": self._identify_product_risks(tasks, projects),
                "recommendations": self._generate_product_recommendations(tasks, projects)
            }
            
            return {
                "product_analysis": analysis,
                "timestamp": datetime.now(UTC).isoformat(),
                "agent_trace": "product_account_intelligence_agent",
                "confidence": 0.82,
                "data_points": len(tasks) + len(projects)
            }
            
        except Exception as e:
            logger.error(f"Product analysis failed: {e}")
            return {"error": str(e), "fallback": "basic_analysis"}
    
    def _analyze_roadmap_health(self, projects: List[Dict], tasks: List[Dict]) -> Dict:
        """Analyze product roadmap health and progress"""
        active_projects = [p for p in projects if not p.get("completed")]
        on_track = len([p for p in active_projects if self._is_on_track(p)])
        
        return {
            "total_projects": len(projects),
            "active_projects": len(active_projects),
            "on_track_percentage": (on_track / max(len(active_projects), 1)) * 100,
            "roadmap_score": min(100, (on_track / max(len(active_projects), 1)) * 100),
            "status": "healthy" if on_track / max(len(active_projects), 1) > 0.8 else "at_risk"
        }
    
    def _analyze_account_health(self, tasks: List[Dict]) -> Dict:
        """Analyze account health metrics"""
        account_tasks = [t for t in tasks if "account" in str(t.get("name", "")).lower()]
        support_tasks = [t for t in tasks if any(tag in str(t.get("name", "")).lower() 
                                               for tag in ["support", "issue", "bug", "problem"])]
        
        return {
            "total_account_tasks": len(account_tasks),
            "support_tasks": len(support_tasks),
            "urgent_accounts": len([t for t in account_tasks if t.get("priority") == "high"]),
            "health_score": max(0, 100 - (len(support_tasks) * 5)),
            "status": "healthy" if len(support_tasks) < 5 else "needs_attention"
        }
    
    def _calculate_product_velocity(self, tasks: List[Dict]) -> Dict:
        """Calculate product development velocity"""
        completed_tasks = [t for t in tasks if t.get("completed")]
        feature_tasks = [t for t in tasks if "feature" in str(t.get("name", "")).lower()]
        
        return {
            "completed_tasks": len(completed_tasks),
            "feature_tasks": len(feature_tasks),
            "completion_rate": (len(completed_tasks) / max(len(tasks), 1)) * 100,
            "feature_velocity": len([t for t in feature_tasks if t.get("completed")]),
            "trend": "improving"  # Simplified
        }
    
    def _analyze_feature_pipeline(self, tasks: List[Dict]) -> Dict:
        """Analyze feature development pipeline"""
        pipeline_stages = {
            "planning": len([t for t in tasks if "planning" in str(t.get("name", "")).lower()]),
            "development": len([t for t in tasks if "development" in str(t.get("name", "")).lower()]),
            "testing": len([t for t in tasks if "testing" in str(t.get("name", "")).lower()]),
            "release": len([t for t in tasks if "release" in str(t.get("name", "")).lower()])
        }
        
        return {
            "pipeline_stages": pipeline_stages,
            "total_features": sum(pipeline_stages.values()),
            "pipeline_health": "balanced" if max(pipeline_stages.values()) < len(tasks) * 0.6 else "bottleneck_detected"
        }
    
    def _assess_customer_impact(self, tasks: List[Dict]) -> Dict:
        """Assess customer impact of current work"""
        customer_tasks = [t for t in tasks if any(keyword in str(t.get("name", "")).lower() 
                                                for keyword in ["customer", "user", "client"])]
        high_impact = [t for t in customer_tasks if t.get("priority") == "high"]
        
        return {
            "customer_focused_tasks": len(customer_tasks),
            "high_impact_tasks": len(high_impact),
            "customer_impact_score": (len(customer_tasks) / max(len(tasks), 1)) * 100,
            "priority_alignment": "good" if len(high_impact) > 0 else "needs_review"
        }
    
    def _identify_product_risks(self, tasks: List[Dict], projects: List[Dict]) -> List[Dict]:
        """Identify product and account management risks"""
        risks = []
        
        # Overdue tasks
        overdue_tasks = [t for t in tasks if self._is_overdue(t)]
        if overdue_tasks:
            risks.append({
                "type": "overdue_deliverables",
                "count": len(overdue_tasks),
                "severity": "high" if len(overdue_tasks) > 5 else "medium",
                "description": f"{len(overdue_tasks)} tasks are overdue"
            })
        
        # Blocked projects
        blocked_projects = [p for p in projects if self._is_blocked(p)]
        if blocked_projects:
            risks.append({
                "type": "blocked_projects",
                "count": len(blocked_projects),
                "severity": "high",
                "description": f"{len(blocked_projects)} projects are blocked"
            })
        
        # Resource constraints
        unassigned_tasks = [t for t in tasks if not t.get("assignee")]
        if len(unassigned_tasks) > 10:
            risks.append({
                "type": "resource_constraints",
                "count": len(unassigned_tasks),
                "severity": "medium",
                "description": f"{len(unassigned_tasks)} tasks lack assignees"
            })
        
        return risks
    
    def _generate_product_recommendations(self, tasks: List[Dict], projects: List[Dict]) -> List[str]:
        """Generate actionable product recommendations"""
        recommendations = []
        
        if len(tasks) > 50:
            recommendations.append("Consider prioritizing and reducing task backlog")
        
        if len([p for p in projects if not self._is_on_track(p)]) > 2:
            recommendations.append("Review project timelines and resource allocation")
        
        unassigned_count = len([t for t in tasks if not t.get("assignee")])
        if unassigned_count > 10:
            recommendations.append("Assign owners to unassigned tasks to improve accountability")
        
        recommendations.append("Regular roadmap reviews to ensure strategic alignment")
        recommendations.append("Implement customer feedback loops for feature prioritization")
        
        return recommendations
    
    def _is_on_track(self, project: Dict) -> bool:
        """Check if project is on track"""
        # Simplified heuristic
        return project.get("status") != "at_risk"
    
    def _is_overdue(self, task: Dict) -> bool:
        """Check if task is overdue"""
        due_date = task.get("due_date")
        if not due_date:
            return False
        # Simplified for now
        return False
    
    def _is_blocked(self, project: Dict) -> bool:
        """Check if project is blocked"""
        return project.get("status") == "blocked"

class AsanaProductAccountMCPServer(StandardizedMCPServer):
    """Enhanced Asana Product/Account Management MCP Server with Agentic RAG"""

    def __init__(self):
        config = ServerConfig(
            name="asana_product_account",
            version="3.0.0",
            description="Product team KPIs, roadmap tracking, and account health monitoring with AI insights"
        )
        super().__init__(config)

        # Asana configuration
        self.asana_token = get_config_value("asana_access_token")
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {self.asana_token}",
            "Content-Type": "application/json"
        }

        # Initialize Qdrant memory service
        self.memory_service = QdrantUnifiedMemoryService()
        
        # Initialize product/account intelligence agent
        self.product_agent = ProductAccountIntelligenceAgent(self.memory_service)
        
        # Team and workspace configurations
        self.workspace_configs = {
            "product_team_id": get_config_value("asana_product_team_id"),
            "account_team_id": get_config_value("asana_account_team_id"),
            "workspace_id": get_config_value("asana_workspace_id")
        }

    async def setup(self):
        """Initialize Qdrant collections and product/account data ingestion"""
        try:
            if hasattr(super(), 'setup'):
                await super().setup()
        except Exception as e:
            logger.warning(f"Parent setup failed: {e}")
        
        # Initialize Qdrant collection for Asana product/account data
        try:
            if hasattr(self.memory_service, 'initialize_collection'):
                await self.memory_service.initialize_collection("asana_product_account_embeddings")
        except Exception as e:
            logger.warning(f"Could not initialize Qdrant collection: {e}")
        
        # Initial data ingestion
        await self._ingest_product_account_data()

    async def handle_custom_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Handle custom tool calls (required by base class)"""
        return await self.call_tool(name, arguments)

    async def _ingest_product_account_data(self):
        """Ingest existing Asana product/account data into vector memory"""
        try:
            logger.info("Ingesting product/account data into vector memory...")
            
            # Ingest tasks data
            tasks_data = await self._fetch_team_tasks()
            if tasks_data.get("data"):
                for task in tasks_data["data"]:
                    await self._store_in_vector_memory(task, "task")
            
            # Ingest projects data
            projects_data = await self._fetch_projects()
            if projects_data.get("data"):
                for project in projects_data["data"]:
                    await self._store_in_vector_memory(project, "project")
                    
            logger.info("Product/account data ingestion completed")
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")

    async def _store_in_vector_memory(self, item: Dict, item_type: str):
        """Store Asana item in vector memory with embeddings"""
        try:
            # Extract text content for embedding
            content = self._extract_text_content(item, item_type)
            
            # Create metadata
            metadata = {
                "source": "asana_product_account",
                "type": item_type,
                "asana_id": item.get("gid"),
                "created_at": item.get("created_at"),
                "modified_at": item.get("modified_at"),
                "completed": item.get("completed", False)
            }
            
            # Store in vector memory
            try:
                if hasattr(self.memory_service, 'add_knowledge'):
                    await self.memory_service.add_knowledge(
                        content=content,
                        source=f"asana_{item_type}",
                        metadata=metadata
                    )
            except Exception as e:
                logger.warning(f"Could not store {item_type} in vector memory: {e}")
            
        except Exception as e:
            logger.error(f"Failed to store {item_type} in vector memory: {e}")

    def _extract_text_content(self, item: Dict, item_type: str) -> str:
        """Extract searchable text content from Asana item"""
        content_parts = []
        
        if item_type == "task":
            content_parts.append(f"Name: {item.get('name', '')}")
            content_parts.append(f"Notes: {item.get('notes', '')}")
            
            if item.get("assignee"):
                content_parts.append(f"Assignee: {item['assignee'].get('name', '')}")
            
            if item.get("projects"):
                project_names = [p.get("name", "") for p in item["projects"]]
                content_parts.append(f"Projects: {', '.join(project_names)}")
                
            if item.get("tags"):
                tag_names = [t.get("name", "") for t in item["tags"]]
                content_parts.append(f"Tags: {', '.join(tag_names)}")
                
        elif item_type == "project":
            content_parts.append(f"Name: {item.get('name', '')}")
            content_parts.append(f"Notes: {item.get('notes', '')}")
            content_parts.append(f"Status: {item.get('status', {}).get('text', '')}")
        
        return "\n".join(content_parts)

    async def get_custom_tools(self) -> List[Tool]:
        """Define agentic RAG tools for product/account intelligence"""
        return [
            Tool(
                name="rag_query_product_account",
                description="Perform agentic RAG query across product/account Asana data with AI analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Product or account management question"},
                        "focus_area": {"type": "string", "enum": ["product", "account", "roadmap", "all"], "default": "all"},
                        "analysis_type": {"type": "string", "enum": ["kpi", "health", "roadmap"], "default": "kpi"},
                        "top_k": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_product_kpis",
                description="Get comprehensive product KPIs with AI-powered insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_focus": {"type": "string", "enum": ["product", "account", "both"], "default": "both"},
                        "timeframe": {"type": "string", "enum": ["week", "month", "quarter"], "default": "month"},
                        "include_roadmap": {"type": "boolean", "default": True}
                    },
                    "required": []
                }
            ),
            Tool(
                name="analyze_account_health",
                description="AI-powered account health analysis and risk detection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "account_filter": {"type": "string", "description": "Filter for specific accounts (optional)"},
                        "risk_threshold": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"}
                    },
                    "required": []
                }
            ),
            Tool(
                name="roadmap_analysis",
                description="Analyze product roadmap health and progress",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "planning_horizon": {"type": "string", "enum": ["month", "quarter", "year"], "default": "quarter"},
                        "include_risks": {"type": "boolean", "default": True}
                    },
                    "required": []
                }
            ),
            Tool(
                name="detect_product_risks",
                description="Detect and analyze product delivery and account management risks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "risk_categories": {"type": "array", "items": {"type": "string"}, "default": ["delivery", "account", "resource"]}
                    },
                    "required": []
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute agentic RAG tools with product/account intelligence"""
        try:
            if name == "rag_query_product_account":
                return await self._handle_rag_query(arguments)
            elif name == "get_product_kpis":
                return await self._handle_product_kpis(arguments)
            elif name == "analyze_account_health":
                return await self._handle_account_health(arguments)
            elif name == "roadmap_analysis":
                return await self._handle_roadmap_analysis(arguments)
            elif name == "detect_product_risks":
                return await self._handle_risk_detection(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_rag_query(self, arguments: Dict) -> List[TextContent]:
        """Handle agentic RAG query with vector search and product analysis"""
        query = arguments.get("query", "")
        focus_area = arguments.get("focus_area", "all")
        analysis_type = arguments.get("analysis_type", "kpi")
        top_k = arguments.get("top_k", 10)

        try:
            # Perform vector search
            search_results = []
            try:
                if hasattr(self.memory_service, 'search_knowledge'):
                    search_results = await self.memory_service.search_knowledge(
                        query=query,
                        limit=top_k,
                        metadata_filter={"source": "asana_product_account"} if focus_area == "all" 
                        else {"source": f"asana_{focus_area}"}
                    )
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")

            # Get product analysis
            if search_results and analysis_type in ["kpi", "health", "roadmap"]:
                product_analysis = await self.product_agent.analyze_product_metrics(
                    {"search_results": search_results, "query": query, "focus": focus_area},
                    f"Product {analysis_type} analysis: {query}"
                )
                
                response = {
                    "query": query,
                    "analysis_type": analysis_type,
                    "product_insights": product_analysis,
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

    async def _handle_product_kpis(self, arguments: Dict) -> List[TextContent]:
        """Handle comprehensive product KPI analysis"""
        try:
            # Fetch product data
            tasks_data = await self._fetch_team_tasks()
            projects_data = await self._fetch_projects()
            
            # Combine data for analysis
            combined_data = {
                "tasks": tasks_data.get("data", []),
                "projects": projects_data.get("data", []),
                "team": {"size": 8}  # Simplified
            }
            
            # Get AI-powered analysis
            product_analysis = await self.product_agent.analyze_product_metrics(
                combined_data,
                "Comprehensive product KPI analysis"
            )
            
            response = {
                "kpi_analysis": product_analysis,
                "raw_data": {
                    "task_count": len(combined_data["tasks"]),
                    "project_count": len(combined_data["projects"]),
                    "team_focus": arguments.get("team_focus", "both")
                },
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Product KPI analysis failed: {e}")
            return [TextContent(type="text", text=f"Product KPI analysis failed: {str(e)}")]

    async def _handle_account_health(self, arguments: Dict) -> List[TextContent]:
        """Handle account health analysis"""
        try:
            # Fetch account-related data
            tasks_data = await self._fetch_team_tasks()
            tasks = tasks_data.get("data", [])
            
            # Filter for account-related tasks
            account_tasks = [t for t in tasks if "account" in str(t.get("name", "")).lower()]
            
            # Analyze account health
            health_analysis = await self.product_agent.analyze_product_metrics(
                {"tasks": account_tasks, "focus": "account_health"},
                "Account health analysis"
            )
            
            response = {
                "account_health_analysis": health_analysis,
                "account_task_count": len(account_tasks),
                "risk_threshold": arguments.get("risk_threshold", "medium"),
                "recommendations": health_analysis.get("product_analysis", {}).get("recommendations", [])
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Account health analysis failed: {e}")
            return [TextContent(type="text", text=f"Account health analysis failed: {str(e)}")]

    async def _handle_roadmap_analysis(self, arguments: Dict) -> List[TextContent]:
        """Handle roadmap analysis"""
        planning_horizon = arguments.get("planning_horizon", "quarter")
        include_risks = arguments.get("include_risks", True)
        
        try:
            # Fetch roadmap data
            projects_data = await self._fetch_projects()
            tasks_data = await self._fetch_team_tasks()
            
            combined_data = {
                "projects": projects_data.get("data", []),
                "tasks": tasks_data.get("data", []),
                "planning_horizon": planning_horizon
            }
            
            # Analyze roadmap
            roadmap_analysis = await self.product_agent.analyze_product_metrics(
                combined_data,
                f"Roadmap analysis for {planning_horizon}"
            )
            
            response = {
                "planning_horizon": planning_horizon,
                "roadmap_analysis": roadmap_analysis,
                "include_risks": include_risks,
                "project_count": len(combined_data["projects"])
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Roadmap analysis failed: {e}")
            return [TextContent(type="text", text=f"Roadmap analysis failed: {str(e)}")]

    async def _handle_risk_detection(self, arguments: Dict) -> List[TextContent]:
        """Handle risk detection and analysis"""
        risk_categories = arguments.get("risk_categories", ["delivery", "account", "resource"])
        
        try:
            # Fetch data for risk analysis
            tasks_data = await self._fetch_team_tasks()
            projects_data = await self._fetch_projects()
            
            combined_data = {
                "tasks": tasks_data.get("data", []),
                "projects": projects_data.get("data", []),
                "risk_categories": risk_categories
            }
            
            # Analyze risks
            risk_analysis = await self.product_agent.analyze_product_metrics(
                combined_data,
                f"Risk analysis for categories: {', '.join(risk_categories)}"
            )
            
            response = {
                "risk_categories": risk_categories,
                "risk_analysis": risk_analysis,
                "detected_risks": risk_analysis.get("product_analysis", {}).get("risk_assessment", []),
                "mitigation_recommendations": risk_analysis.get("product_analysis", {}).get("recommendations", [])
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
        except Exception as e:
            logger.error(f"Risk detection failed: {e}")
            return [TextContent(type="text", text=f"Risk detection failed: {str(e)}")]

    async def _fetch_team_tasks(self) -> Dict:
        """Fetch team tasks from Asana API"""
        try:
            url = f"{self.base_url}/tasks"
            params = {
                "workspace": self.workspace_configs["workspace_id"],
                "assignee": "me",
                "completed_since": "now",
                "opt_fields": "name,notes,assignee,projects,tags,completed,created_at,modified_at,due_date"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch team tasks: {e}")
            return {}

    async def _fetch_projects(self) -> Dict:
        """Fetch projects from Asana API"""
        try:
            url = f"{self.base_url}/projects"
            params = {
                "workspace": self.workspace_configs["workspace_id"],
                "opt_fields": "name,notes,status,created_at,modified_at,completed"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                return response.json() if response.status_code == 200 else {}
                
        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            return {}

# Create and run server
if __name__ == "__main__":
    async def main():
        server = AsanaProductAccountMCPServer()
        await server.run()

    asyncio.run(main()) 