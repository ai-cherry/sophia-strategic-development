"""Sophia AI Tool Registry.

Comprehensive catalog of all available tools, integrations, and capabilities
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Status of tool integration."""
        ACTIVE = "active"
    CONFIGURED = "configured"
    PLANNED = "planned"
    DEPRECATED = "deprecated"
    PLACEHOLDER = "placeholder"


class ToolCategory(Enum):
    """Categories of tools."""
        AI_LLM = "AI/LLM Services"

    VECTOR_DB = "Vector Databases"
    CRM_SALES = "CRM & Sales"
    COMMUNICATION = "Communication"
    DATA_ANALYTICS = "Data & Analytics"
    AUTOMATION = "Automation"
    MONITORING = "Monitoring"
    INFRASTRUCTURE = "Infrastructure"
    WEB_INTELLIGENCE = "Web Intelligence"
    PROJECT_MANAGEMENT = "Project Management"
    DEVELOPMENT = "Development Tools"


@dataclass
class ToolCapability:
    """Represents a specific capability of a tool."""
        name: str
    description: str
    example_usage: str
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)


@dataclass
class ToolIntegration:
    """Represents a tool/integration in the system."""
        id: str
    name: str
    category: ToolCategory
    status: ToolStatus
    description: str
    capabilities: List[ToolCapability]
    mcp_server: Optional[str] = None
    api_key_env: Optional[str] = None
    documentation_url: Optional[str] = None
    example_workflows: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class SophiaToolRegistry:
    """Central registry for all Sophia AI tools and integrations."""
    def __init__(self):.

        self.tools: Dict[str, ToolIntegration] = {}
        self._initialize_registry()

    def _initialize_registry(self):
        """Initialize the tool registry with all known integrations."""
        # AI/LLM Services.

        self.register_tool(
            ToolIntegration(
                id="openai",
                name="OpenAI GPT",
                category=ToolCategory.AI_LLM,
                status=ToolStatus.ACTIVE,
                description="Primary LLM for general intelligence and reasoning",
                api_key_env="OPENAI_API_KEY",
                capabilities=[
                    ToolCapability(
                        name="chat_completion",
                        description="Generate intelligent responses to queries",
                        example_usage="await openai_client.chat.completions.create(model='gpt-4', messages=[...])",
                        required_params=["messages", "model"],
                        optional_params=["temperature", "max_tokens", "tools"],
                    ),
                    ToolCapability(
                        name="embeddings",
                        description="Generate vector embeddings for semantic search",
                        example_usage="await openai_client.embeddings.create(input=text, model='text-embedding-3-small')",
                        required_params=["input", "model"],
                    ),
                ],
                example_workflows=[
                    "Strategic intelligence synthesis",
                    "Sales call analysis",
                    "Knowledge base Q&A",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="anthropic",
                name="Anthropic Claude",
                category=ToolCategory.AI_LLM,
                status=ToolStatus.ACTIVE,
                description="Advanced reasoning and analysis, especially for complex tasks",
                api_key_env="ANTHROPIC_API_KEY",
                mcp_server="claude",
                capabilities=[
                    ToolCapability(
                        name="messages_create",
                        description="Claude's advanced reasoning for complex analysis",
                        example_usage="await anthropic_client.messages.create(model='claude-3-opus', messages=[...])",
                        required_params=["messages", "model", "max_tokens"],
                    )
                ],
                example_workflows=[
                    "Code generation and review",
                    "Document analysis",
                    "Strategic planning",
                ],
            )
        )

        # Vector Databases
        self.register_tool(
            ToolIntegration(
                id="pinecone",
                name="Pinecone",
                category=ToolCategory.VECTOR_DB,
                status=ToolStatus.ACTIVE,
                description="Primary vector database for semantic search and RAG",
                api_key_env="PINECONE_API_KEY",
                mcp_server="pinecone",
                capabilities=[
                    ToolCapability(
                        name="upsert_vectors",
                        description="Store embeddings with metadata",
                        example_usage="await pinecone_index.upsert(vectors=[(id, embedding, metadata)])",
                        required_params=["vectors"],
                    ),
                    ToolCapability(
                        name="query_vectors",
                        description="Semantic similarity search",
                        example_usage="await pinecone_index.query(vector=embedding, top_k=10)",
                        required_params=["vector", "top_k"],
                        optional_params=["filter", "include_metadata"],
                    ),
                ],
                example_workflows=[
                    "Knowledge base retrieval",
                    "Similar client search",
                    "Call transcript analysis",
                ],
            )
        )

        # CRM & Sales
        self.register_tool(
            ToolIntegration(
                id="gong",
                name="Gong.io",
                category=ToolCategory.CRM_SALES,
                status=ToolStatus.ACTIVE,
                description="Sales call recording and conversation intelligence",
                api_key_env="GONG_API_KEY",
                mcp_server="gong",
                capabilities=[
                    ToolCapability(
                        name="get_calls",
                        description="Retrieve call recordings and metadata",
                        example_usage="await gong_client.get_calls(from_date='2024-01-01')",
                        required_params=["from_date"],
                        optional_params=["to_date", "limit"],
                    ),
                    ToolCapability(
                        name="get_call_transcript",
                        description="Get full transcript of a call",
                        example_usage="await gong_client.get_call_transcript(call_id='123')",
                        required_params=["call_id"],
                    ),
                    ToolCapability(
                        name="analyze_call_metrics",
                        description="Get talk ratios, sentiment, topics",
                        example_usage="await gong_client.get_call_stats(call_id='123')",
                        required_params=["call_id"],
                    ),
                ],
                example_workflows=[
                    "Sales coaching insights",
                    "Client sentiment tracking",
                    "Competitor mention detection",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="hubspot",
                name="HubSpot",
                category=ToolCategory.CRM_SALES,
                status=ToolStatus.CONFIGURED,
                description="CRM for contact and deal management",
                api_key_env="HUBSPOT_API_KEY",
                mcp_server="hubspot",
                capabilities=[
                    ToolCapability(
                        name="get_contacts",
                        description="Retrieve contact information",
                        example_usage="await hubspot_client.get_contacts(limit=100)",
                        optional_params=["limit", "properties"],
                    ),
                    ToolCapability(
                        name="create_deal",
                        description="Create new sales opportunity",
                        example_usage="await hubspot_client.create_deal(properties={...})",
                        required_params=["properties"],
                    ),
                    ToolCapability(
                        name="update_contact",
                        description="Update contact properties",
                        example_usage="await hubspot_client.update_contact(contact_id='123', properties={...})",
                        required_params=["contact_id", "properties"],
                    ),
                ],
                example_workflows=[
                    "Lead scoring automation",
                    "Deal pipeline management",
                    "Contact enrichment",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="apollo",
                name="Apollo.io",
                category=ToolCategory.CRM_SALES,
                status=ToolStatus.CONFIGURED,
                description="B2B data enrichment and prospecting",
                api_key_env="APOLLO_API_KEY",
                mcp_server="apollo",
                capabilities=[
                    ToolCapability(
                        name="enrich_company",
                        description="Get company details, funding, employees",
                        example_usage="await apollo_client.enrich_company(domain='example.com')",
                        required_params=["domain"],
                    ),
                    ToolCapability(
                        name="find_contacts",
                        description="Find decision makers at companies",
                        example_usage="await apollo_client.people_search(company_name='Acme Corp')",
                        required_params=["company_name"],
                        optional_params=["titles", "departments"],
                    ),
                ],
                example_workflows=[
                    "Client company enrichment",
                    "Contact discovery",
                    "Market intelligence",
                ],
            )
        )

        # Communication
        self.register_tool(
            ToolIntegration(
                id="slack",
                name="Slack",
                category=ToolCategory.COMMUNICATION,
                status=ToolStatus.ACTIVE,
                description="Team communication and notifications",
                api_key_env="SLACK_BOT_TOKEN",
                mcp_server="slack",
                capabilities=[
                    ToolCapability(
                        name="send_message",
                        description="Send messages to channels or users",
                        example_usage="await slack_client.chat_postMessage(channel='#general', text='Hello')",
                        required_params=["channel", "text"],
                        optional_params=["blocks", "thread_ts"],
                    ),
                    ToolCapability(
                        name="create_reminder",
                        description="Set reminders for users",
                        example_usage="await slack_client.reminders_add(text='Follow up', time='in 2 hours')",
                        required_params=["text", "time"],
                    ),
                ],
                example_workflows=[
                    "Client health alerts",
                    "Daily summaries",
                    "Task notifications",
                ],
            )
        )

        # Data & Analytics
        self.register_tool(
            ToolIntegration(
                id="snowflake",
                name="Snowflake",
                category=ToolCategory.DATA_ANALYTICS,
                status=ToolStatus.ACTIVE,
                description="Data warehouse for analytics and reporting",
                api_key_env="SNOWFLAKE_PASSWORD",
                mcp_server="snowflake",
                capabilities=[
                    ToolCapability(
                        name="execute_query",
                        description="Run SQL queries for analysis",
                        example_usage="await snowflake_client.execute('SELECT * FROM clients WHERE health_score < 70')",
                        required_params=["query"],
                    ),
                    ToolCapability(
                        name="create_table",
                        description="Create new data tables",
                        example_usage="await snowflake_client.create_table('metrics', schema={...})",
                        required_params=["table_name", "schema"],
                    ),
                ],
                example_workflows=[
                    "Business intelligence queries",
                    "Client health calculations",
                    "Revenue reporting",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="costar",
                name="CoStar",
                category=ToolCategory.DATA_ANALYTICS,
                status=ToolStatus.CONFIGURED,
                description="Commercial real estate data and analytics",
                api_key_env="COSTAR_API_KEY",
                mcp_server="costar",
                capabilities=[
                    ToolCapability(
                        name="get_property_data",
                        description="Get property details and comparables",
                        example_usage="await costar_client.get_property(address='123 Main St')",
                        required_params=["address"],
                    ),
                    ToolCapability(
                        name="market_analysis",
                        description="Get market trends and analytics",
                        example_usage="await costar_client.get_market_trends(market='Seattle')",
                        required_params=["market"],
                    ),
                ],
                example_workflows=[
                    "Property valuation",
                    "Market trend analysis",
                    "Competitive intelligence",
                ],
            )
        )

        # Automation
        self.register_tool(
            ToolIntegration(
                id="bardeen",
                name="Bardeen",
                category=ToolCategory.AUTOMATION,
                status=ToolStatus.CONFIGURED,
                description="No-code automation platform",
                api_key_env="BARDEEN_ID",
                capabilities=[
                    ToolCapability(
                        name="create_workflow",
                        description="Create automated workflows",
                        example_usage="await bardeen_client.create_workflow(trigger='client_health_low', actions=[...])",
                        required_params=["trigger", "actions"],
                    ),
                    ToolCapability(
                        name="trigger_playbook",
                        description="Execute existing automation",
                        example_usage="await bardeen_client.run_playbook('follow_up_sequence')",
                        required_params=["playbook_id"],
                    ),
                ],
                example_workflows=[
                    "Automated follow-ups",
                    "Data sync workflows",
                    "Alert automation",
                ],
            )
        )

        # Monitoring
        self.register_tool(
            ToolIntegration(
                id="arize",
                name="Arize",
                category=ToolCategory.MONITORING,
                status=ToolStatus.CONFIGURED,
                description="ML observability and monitoring",
                api_key_env="ARIZE_API_KEY",
                capabilities=[
                    ToolCapability(
                        name="log_prediction",
                        description="Log model predictions for monitoring",
                        example_usage="await arize_client.log(prediction=pred, actual=actual, features=features)",
                        required_params=["prediction", "features"],
                        optional_params=["actual", "tags"],
                    ),
                    ToolCapability(
                        name="get_model_metrics",
                        description="Retrieve model performance metrics",
                        example_usage="await arize_client.get_metrics(model_id='health_scorer')",
                        required_params=["model_id"],
                    ),
                ],
                example_workflows=[
                    "Model drift detection",
                    "Performance monitoring",
                    "A/B testing analysis",
                ],
            )
        )

        # Web Intelligence
        self.register_tool(
            ToolIntegration(
                id="perplexity",
                name="Perplexity",
                category=ToolCategory.WEB_INTELLIGENCE,
                status=ToolStatus.CONFIGURED,
                description="AI-powered web search and research",
                api_key_env="PERPLEXITY_API_KEY",
                capabilities=[
                    ToolCapability(
                        name="search",
                        description="Search web with AI understanding",
                        example_usage="await perplexity_client.search('latest property management trends')",
                        required_params=["query"],
                        optional_params=["sources", "recency"],
                    )
                ],
                example_workflows=[
                    "Market research",
                    "Competitor analysis",
                    "Industry trends",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="tavily",
                name="Tavily",
                category=ToolCategory.WEB_INTELLIGENCE,
                status=ToolStatus.CONFIGURED,
                description="Specialized search API for LLMs",
                api_key_env="TAVILY_API_KEY",
                capabilities=[
                    ToolCapability(
                        name="search",
                        description="Deep web search optimized for AI",
                        example_usage="await tavily_client.search(query='property tech startups 2024')",
                        required_params=["query"],
                        optional_params=["search_depth", "max_results"],
                    )
                ],
                example_workflows=["Deep research", "Fact checking", "News monitoring"],
            )
        )

        # Infrastructure
        self.register_tool(
            ToolIntegration(
                id="lambda_labs",
                name="Lambda Labs",
                category=ToolCategory.INFRASTRUCTURE,
                status=ToolStatus.ACTIVE,
                description="GPU cloud infrastructure",
                api_key_env="LAMBDA_LABS_API_KEY",
                mcp_server="lambda-labs",
                capabilities=[
                    ToolCapability(
                        name="launch_instance",
                        description="Launch GPU instance",
                        example_usage="await lambda_client.launch_instance(instance_type='gpu_1x_a100')",
                        required_params=["instance_type"],
                    ),
                    ToolCapability(
                        name="get_instance_status",
                        description="Check instance health",
                        example_usage="await lambda_client.get_status(instance_id='i-123')",
                        required_params=["instance_id"],
                    ),
                ],
                example_workflows=[
                    "Model training",
                    "Batch processing",
                    "Infrastructure scaling",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="vercel",
                name="Vercel",
                category=ToolCategory.INFRASTRUCTURE,
                status=ToolStatus.ACTIVE,
                description="Frontend deployment platform",
                api_key_env="VERCEL_ACCESS_TOKEN",
                mcp_server="vercel",
                capabilities=[
                    ToolCapability(
                        name="deploy",
                        description="Deploy frontend applications",
                        example_usage="await vercel_client.deploy(project='sophia-dashboard')",
                        required_params=["project"],
                    ),
                    ToolCapability(
                        name="get_deployment_status",
                        description="Check deployment status",
                        example_usage="await vercel_client.get_deployment(deployment_id='dpl_123')",
                        required_params=["deployment_id"],
                    ),
                ],
                example_workflows=[
                    "Dashboard deployment",
                    "Preview deployments",
                    "Rollback management",
                ],
            )
        )

        # Development Tools
        self.register_tool(
            ToolIntegration(
                id="retool",
                name="Retool",
                category=ToolCategory.DEVELOPMENT,
                status=ToolStatus.CONFIGURED,
                description="Low-code platform for internal tools",
                api_key_env="RETOOL_API_TOKEN",
                mcp_server="retool",
                capabilities=[
                    ToolCapability(
                        name="create_app",
                        description="Programmatically create Retool apps",
                        example_usage="await retool_client.create_app(name='Client Dashboard', config={...})",
                        required_params=["name", "config"],
                    ),
                    ToolCapability(
                        name="update_resource",
                        description="Update data sources",
                        example_usage="await retool_client.update_resource(resource_id='123', config={...})",
                        required_params=["resource_id", "config"],
                    ),
                ],
                example_workflows=[
                    "Dynamic dashboard creation",
                    "Admin tool generation",
                    "Custom reporting UIs",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="linear",
                name="Linear",
                category=ToolCategory.PROJECT_MANAGEMENT,
                status=ToolStatus.ACTIVE,
                description="Modern issue tracking and project management",
                api_key_env="LINEAR_API_TOKEN",
                mcp_server="linear",
                capabilities=[
                    ToolCapability(
                        name="create_issue",
                        description="Create new issues",
                        example_usage="await linear_client.create_issue(title='Bug: Client health calculation', team_id='ENG')",
                        required_params=["title", "team_id"],
                        optional_params=["description", "priority", "assignee"],
                    ),
                    ToolCapability(
                        name="update_issue_status",
                        description="Update issue progress",
                        example_usage="await linear_client.update_issue(issue_id='ENG-123', status='In Progress')",
                        required_params=["issue_id", "status"],
                    ),
                ],
                example_workflows=[
                    "Bug tracking from alerts",
                    "Feature request management",
                    "Sprint planning automation",
                ],
            )
        )

        # Placeholder/Planned Tools
        self.register_tool(
            ToolIntegration(
                id="firecrawl",
                name="Firecrawl",
                category=ToolCategory.WEB_INTELLIGENCE,
                status=ToolStatus.PLANNED,
                description="Web scraping and data extraction",
                api_key_env="FIRECRAWL_API_KEY",
                capabilities=[
                    ToolCapability(
                        name="scrape_website",
                        description="Extract structured data from websites",
                        example_usage="await firecrawl_client.scrape(url='competitor.com', schema={...})",
                        required_params=["url", "schema"],
                    )
                ],
                example_workflows=[
                    "Competitor monitoring",
                    "Price tracking",
                    "Content aggregation",
                ],
            )
        )

        self.register_tool(
            ToolIntegration(
                id="spider",
                name="Spider",
                category=ToolCategory.WEB_INTELLIGENCE,
                status=ToolStatus.PLANNED,
                description="Advanced web crawling",
                api_key_env="SPIDER_API_KEY",
                capabilities=[
                    ToolCapability(
                        name="crawl_site",
                        description="Deep crawl entire websites",
                        example_usage="await spider_client.crawl(domain='example.com', depth=3)",
                        required_params=["domain"],
                        optional_params=["depth", "patterns"],
                    )
                ],
                example_workflows=[
                    "Site indexing",
                    "Documentation scraping",
                    "Change detection",
                ],
            )
        )

    def register_tool(self, tool: ToolIntegration):
        """Register a tool in the registry."""self.tools[tool.id] = tool.

        logger.info(f"Registered tool: {tool.name} ({tool.status.value})")

    def get_tool(self, tool_id: str) -> Optional[ToolIntegration]:
        """Get a specific tool by ID."""
        return self.tools.get(tool_id).

    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        status: Optional[ToolStatus] = None,
    ) -> List[ToolIntegration]:
        """List tools with optional filtering."""
        tools = list(self.tools.values()).

        if category:
            tools = [t for t in tools if t.category == category]

        if status:
            tools = [t for t in tools if t.status == status]

        return sorted(tools, key=lambda t: (t.category.value, t.name))

    def get_categories(self) -> Dict[ToolCategory, int]:
        """Get tool count by category."""
        counts = {}.

        for tool in self.tools.values():
            counts[tool.category] = counts.get(tool.category, 0) + 1
        return counts

    def get_status_summary(self) -> Dict[ToolStatus, int]:
        """Get tool count by status."""
        counts = {}.

        for tool in self.tools.values():
            counts[tool.status] = counts.get(tool.status, 0) + 1
        return counts

    def search_tools(self, query: str) -> List[ToolIntegration]:
        """Search tools by name, description, or capabilities."""
        query_lower = query.lower().

        results = []

        for tool in self.tools.values():
            if (
                query_lower in tool.name.lower()
                or query_lower in tool.description.lower()
                or any(
                    query_lower in cap.name.lower()
                    or query_lower in cap.description.lower()
                    for cap in tool.capabilities
                )
            ):
                results.append(tool)

        return results

    def get_workflow_tools(self, workflow: str) -> List[ToolIntegration]:
        """Get tools that support a specific workflow."""
        workflow_lower = workflow.lower().

        return [
            tool
            for tool in self.tools.values()
            if any(workflow_lower in w.lower() for w in tool.example_workflows)
        ]

    def export_registry(self, format: str = "json") -> str:
        """Export the registry in various formats."""
        if format == "json":
            return json.dumps(
                {
                    tool_id: {
                        "name": tool.name,
                        "category": tool.category.value,
                        "status": tool.status.value,
                        "description": tool.description,
                        "capabilities": [
                            {"name": cap.name, "description": cap.description}
                            for cap in tool.capabilities
                        ],
                        "workflows": tool.example_workflows,
                    }
                    for tool_id, tool in self.tools.items()
                },
                indent=2,
            )

        elif format == "markdown":
            md = "# Sophia AI Tool Registry\n\n"

            for category in ToolCategory:
                tools_in_category = self.list_tools(category=category)
                if tools_in_category:
                    md += f"\n## {category.value}\n\n"

                    for tool in tools_in_category:
                        status_emoji = {
                            ToolStatus.ACTIVE: "✅",
                            ToolStatus.CONFIGURED: "🔧",
                            ToolStatus.PLANNED: "📋",
                            ToolStatus.DEPRECATED: "⚠️",
                            ToolStatus.PLACEHOLDER: "🔲",
                        }.get(tool.status, "❓")

                        md += f"### {status_emoji} {tool.name}\n"
                        md += f"- **Status**: {tool.status.value}\n"
                        md += f"- **Description**: {tool.description}\n"

                        if tool.mcp_server:
                            md += f"- **MCP Server**: `{tool.mcp_server}`\n"

                        if tool.capabilities:
                            md += "- **Capabilities**:\n"
                            for cap in tool.capabilities:
                                md += f"  - `{cap.name}`: {cap.description}\n"

                        if tool.example_workflows:
                            md += "- **Example Workflows**:\n"
                            for workflow in tool.example_workflows:
                                md += f"  - {workflow}\n"

                        md += "\n"

            return md

        else:
            raise ValueError(f"Unsupported format: {format}")


# Global registry instance
tool_registry = SophiaToolRegistry()
