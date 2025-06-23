"""
Apollo.io MCP Server for Pay Ready Prospect Intelligence
Provides NMHC Top 50 prospect enrichment and contact discovery
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import aiohttp
from pydantic import BaseModel, Field
from redis import Redis
from dotenv import load_dotenv

from backend.agents.core.base_agent import BaseAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProspectEnrichmentRequest(BaseModel):
    """Request model for prospect enrichment"""
    company_name: str
    enrichment_level: str = Field(default="comprehensive", pattern="^(basic|comprehensive|maximum)$")
    include_contacts: bool = True
    target_departments: List[str] = ["C-Suite", "Property Management", "Finance", "Operations"]
    

class ApolloContact(BaseModel):
    """Apollo.io contact data model"""
    id: str
    first_name: str
    last_name: str
    title: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None


class ApolloCompany(BaseModel):
    """Apollo.io company data model"""
    id: str
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    technologies: List[str] = []
    keywords: List[str] = []
    

class ApolloMCPServer(BaseAgent):
    """Apollo.io MCP Server for NMHC Top 50 prospect intelligence"""
    
    def __init__(self, config_dict: Optional[Dict] = None):
        super().__init__(config_dict or {
            "name": "Apollo.io MCP Server",
            "description": "Prospect enrichment for Pay Ready sales acceleration"
        })
        
        # Apollo.io configuration
        self.apollo_api_key = os.getenv("APOLLO_API_KEY")
        self.apollo_base_url = "https://api.apollo.io/v1"
        
        # Redis cache configuration
        self.redis_client = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        self.cache_ttl = 3600  # 1 hour cache
        
        # NMHC Top 50 targeting
        self.nmhc_top_50 = self._load_nmhc_list()
        
        # Add MCP capabilities
        self.capabilities.extend([
            "prospect_enrichment",
            "contact_discovery",
            "technology_stack_analysis",
            "competitive_intelligence"
        ])
        
    def _load_nmhc_list(self) -> List[str]:
        """Load NMHC Top 50 property management companies"""
        # This would be loaded from a database or file
        return [
            "Greystar Real Estate Partners",
            "Lincoln Property Company", 
            "Cushman & Wakefield",
            "AvalonBay Communities",
            "Equity Residential",
            "Camden Property Trust",
            "MAA",
            "Essex Property Trust",
            "UDR Inc.",
            "AIMCO",
            # ... rest of NMHC Top 50
        ]
        
    async def _make_apollo_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Apollo.io API"""
        headers = {
            "Authorization": f"Bearer {self.apollo_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.apollo_base_url}/{endpoint}",
                    headers=headers,
                    params=params
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"Apollo API request failed: {e}")
                raise
                
    async def enrich_company(self, company_name: str, enrichment_level: str = "comprehensive") -> Dict[str, Any]:
        """Enrich company data using Apollo.io"""
        
        # Check cache first
        cache_key = f"apollo:company:{company_name}:{enrichment_level}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for {company_name}")
            return json.loads(cached_data)
            
        # Search for company in Apollo
        search_params = {
            "organization_name": company_name,
            "limit": 1
        }
        
        search_result = await self._make_apollo_request("organizations/search", search_params)
        
        if not search_result.get("organizations"):
            logger.warning(f"Company not found in Apollo: {company_name}")
            return {"error": "Company not found", "company_name": company_name}
            
        company_data = search_result["organizations"][0]
        
        # Enrich based on level
        enriched_data = {
            "apollo_id": company_data.get("id"),
            "name": company_data.get("name"),
            "domain": company_data.get("primary_domain"),
            "industry": company_data.get("industry"),
            "employee_count": company_data.get("estimated_num_employees"),
            "revenue_range": company_data.get("revenue_range"),
            "technologies": company_data.get("technologies", []),
            "keywords": company_data.get("keywords", []),
            "is_nmhc_top_50": company_name in self.nmhc_top_50
        }
        
        if enrichment_level in ["comprehensive", "maximum"]:
            # Get additional insights
            enriched_data["technology_stack"] = await self._analyze_technology_stack(company_data)
            enriched_data["competitive_position"] = await self._analyze_competitive_position(company_data)
            
        if enrichment_level == "maximum":
            # Get all available contacts
            enriched_data["key_contacts"] = await self.discover_contacts(
                company_name,
                departments=["C-Suite", "Property Management", "Finance", "Operations"],
                limit=20
            )
            
        # Cache the result
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(enriched_data)
        )
        
        return enriched_data
        
    async def discover_contacts(
        self, 
        company_name: str, 
        departments: List[str] = None,
        seniority_levels: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Discover key contacts at target company"""
        
        # Build search query
        search_params = {
            "organization_name": company_name,
            "limit": limit
        }
        
        if departments:
            search_params["departments"] = departments
            
        if seniority_levels:
            search_params["seniority_levels"] = seniority_levels
        else:
            # Default to decision makers
            search_params["seniority_levels"] = ["c_suite", "vp", "director", "manager"]
            
        # Search for contacts
        contact_result = await self._make_apollo_request("people/search", search_params)
        
        contacts = []
        for contact_data in contact_result.get("people", []):
            contact = {
                "apollo_id": contact_data.get("id"),
                "first_name": contact_data.get("first_name"),
                "last_name": contact_data.get("last_name"),
                "title": contact_data.get("title"),
                "department": contact_data.get("departments", [None])[0],
                "seniority_level": contact_data.get("seniority"),
                "email": contact_data.get("email"),
                "phone": contact_data.get("phone_numbers", [{}])[0].get("number"),
                "linkedin_url": contact_data.get("linkedin_url"),
                "decision_maker_score": self._calculate_decision_maker_score(contact_data)
            }
            contacts.append(contact)
            
        # Sort by decision maker score
        contacts.sort(key=lambda x: x["decision_maker_score"], reverse=True)
        
        return contacts
        
    def _calculate_decision_maker_score(self, contact_data: Dict[str, Any]) -> float:
        """Calculate likelihood of being a decision maker for Pay Ready solutions"""
        score = 0.0
        
        # Title scoring
        title = contact_data.get("title", "").lower()
        if any(keyword in title for keyword in ["ceo", "president", "owner", "founder"]):
            score += 1.0
        elif any(keyword in title for keyword in ["cfo", "coo", "cto", "vp", "vice president"]):
            score += 0.8
        elif any(keyword in title for keyword in ["director", "head of"]):
            score += 0.6
        elif "manager" in title:
            score += 0.4
            
        # Department scoring
        departments = contact_data.get("departments", [])
        if any(dept in ["C-Suite", "Executive"] for dept in departments):
            score += 0.5
        elif any(dept in ["Property Management", "Operations", "Finance"] for dept in departments):
            score += 0.3
            
        # Seniority scoring  
        seniority = contact_data.get("seniority", "")
        if seniority in ["c_suite", "owner"]:
            score += 0.5
        elif seniority == "vp":
            score += 0.4
        elif seniority == "director":
            score += 0.3
        elif seniority == "manager":
            score += 0.2
            
        return min(score, 1.0)  # Cap at 1.0
        
    async def _analyze_technology_stack(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company's technology stack for competitive intelligence"""
        technologies = company_data.get("technologies", [])
        
        # Categorize technologies
        tech_analysis = {
            "property_management_systems": [],
            "payment_systems": [],
            "accounting_systems": [],
            "crm_systems": [],
            "competitive_solutions": [],
            "integration_opportunities": []
        }
        
        # Known competitor technologies
        competitor_tech = [
            "eliseai", "entrata", "yardi", "appfolio", "buildium",
            "rentmanager", "propertyware", "mri software"
        ]
        
        # Pay Ready integration opportunities
        integration_tech = [
            "salesforce", "hubspot", "quickbooks", "netsuite",
            "stripe", "square", "authorize.net"
        ]
        
        for tech in technologies:
            tech_lower = tech.lower()
            
            # Check for competitors
            if any(comp in tech_lower for comp in competitor_tech):
                tech_analysis["competitive_solutions"].append(tech)
                
            # Check for integration opportunities
            elif any(integ in tech_lower for integ in integration_tech):
                tech_analysis["integration_opportunities"].append(tech)
                
            # Categorize by type
            if "payment" in tech_lower or "billing" in tech_lower:
                tech_analysis["payment_systems"].append(tech)
            elif "property" in tech_lower or "pms" in tech_lower:
                tech_analysis["property_management_systems"].append(tech)
            elif "accounting" in tech_lower or "finance" in tech_lower:
                tech_analysis["accounting_systems"].append(tech)
            elif "crm" in tech_lower or "customer" in tech_lower:
                tech_analysis["crm_systems"].append(tech)
                
        return tech_analysis
        
    async def _analyze_competitive_position(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive positioning for Pay Ready opportunity"""
        
        competitive_analysis = {
            "opportunity_score": 0.0,
            "competitive_threats": [],
            "pay_ready_advantages": [],
            "recommended_approach": ""
        }
        
        # Check for existing competitive solutions
        technologies = [tech.lower() for tech in company_data.get("technologies", [])]
        
        # EliseAI presence
        if any("elise" in tech for tech in technologies):
            competitive_analysis["competitive_threats"].append("EliseAI - AI leasing assistant")
            competitive_analysis["pay_ready_advantages"].append("Buzz integration for complete revenue cycle")
            competitive_analysis["opportunity_score"] += 0.3
            
        # Entrata presence
        elif any("entrata" in tech for tech in technologies):
            competitive_analysis["competitive_threats"].append("Entrata - Full PMS suite")
            competitive_analysis["pay_ready_advantages"].append("Specialized collections AI vs generic PMS")
            competitive_analysis["opportunity_score"] += 0.4
            
        # No major competitor
        else:
            competitive_analysis["opportunity_score"] += 0.7
            competitive_analysis["pay_ready_advantages"].append("First-mover advantage with AI collections")
            
        # Size-based opportunity
        employee_count = company_data.get("estimated_num_employees", 0)
        if employee_count > 1000:
            competitive_analysis["opportunity_score"] += 0.2
            competitive_analysis["recommended_approach"] = "Enterprise sales approach with ROI validation"
        elif employee_count > 100:
            competitive_analysis["opportunity_score"] += 0.1
            competitive_analysis["recommended_approach"] = "Mid-market approach with quick implementation"
        else:
            competitive_analysis["recommended_approach"] = "SMB approach with simplified onboarding"
            
        # Cap opportunity score at 1.0
        competitive_analysis["opportunity_score"] = min(competitive_analysis["opportunity_score"], 1.0)
        
        return competitive_analysis
        
    async def generate_sales_brief(self, company_name: str) -> Dict[str, Any]:
        """Generate comprehensive sales brief for Pay Ready team"""
        
        # Get enriched company data
        company_data = await self.enrich_company(company_name, "maximum")
        
        # Generate executive summary
        sales_brief = {
            "company_overview": {
                "name": company_data.get("name"),
                "size": company_data.get("employee_count"),
                "industry": company_data.get("industry"),
                "is_nmhc_top_50": company_data.get("is_nmhc_top_50")
            },
            "opportunity_assessment": {
                "score": company_data.get("competitive_position", {}).get("opportunity_score", 0),
                "competitive_landscape": company_data.get("competitive_position", {}).get("competitive_threats", []),
                "pay_ready_advantages": company_data.get("competitive_position", {}).get("pay_ready_advantages", []),
                "recommended_approach": company_data.get("competitive_position", {}).get("recommended_approach", "")
            },
            "key_contacts": company_data.get("key_contacts", [])[:5],  # Top 5 contacts
            "technology_insights": company_data.get("technology_stack", {}),
            "talking_points": self._generate_talking_points(company_data),
            "next_steps": self._generate_next_steps(company_data)
        }
        
        return sales_brief
        
    def _generate_talking_points(self, company_data: Dict[str, Any]) -> List[str]:
        """Generate customized talking points for sales team"""
        talking_points = []
        
        # NMHC Top 50 specific
        if company_data.get("is_nmhc_top_50"):
            talking_points.append("As an NMHC Top 50 company, you're managing significant portfolio scale - Buzz AI can help optimize collections across your entire portfolio")
            
        # Competitive displacement
        competitive_threats = company_data.get("competitive_position", {}).get("competitive_threats", [])
        if "EliseAI" in str(competitive_threats):
            talking_points.append("While EliseAI focuses on leasing, Buzz specializes in the critical revenue collection phase - where the real ROI happens")
            
        # Integration opportunities
        integrations = company_data.get("technology_stack", {}).get("integration_opportunities", [])
        if integrations:
            talking_points.append(f"Buzz seamlessly integrates with your existing {', '.join(integrations[:2])} systems")
            
        # Generic value props
        talking_points.extend([
            "Our current clients see 15-20% improvement in collection rates within 90 days",
            "Buzz reduces collections labor costs by 40% while improving resident satisfaction",
            "24/7 AI-powered collections that never miss a follow-up"
        ])
        
        return talking_points
        
    def _generate_next_steps(self, company_data: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps for sales team"""
        next_steps = []
        
        # High-value prospect
        if company_data.get("competitive_position", {}).get("opportunity_score", 0) > 0.7:
            next_steps.append("Schedule executive briefing with C-suite contacts")
            next_steps.append("Prepare custom ROI analysis based on portfolio size")
            
        # Competitive displacement opportunity
        if company_data.get("competitive_position", {}).get("competitive_threats"):
            next_steps.append("Prepare competitive comparison deck")
            next_steps.append("Gather switching testimonials from similar clients")
            
        # Standard steps
        next_steps.extend([
            "Send personalized outreach to top 3 decision makers",
            "Schedule product demo focusing on their specific use case",
            "Connect with existing Pay Ready client for reference"
        ])
        
        return next_steps
        
    # MCP Server Interface Methods
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available MCP tools"""
        return [
            {
                "name": "enrich_prospect",
                "description": "Enrich prospect company with Apollo.io data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"},
                        "enrichment_level": {
                            "type": "string",
                            "enum": ["basic", "comprehensive", "maximum"],
                            "default": "comprehensive"
                        }
                    },
                    "required": ["company_name"]
                }
            },
            {
                "name": "discover_contacts",
                "description": "Discover key contacts at target company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"},
                        "departments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["C-Suite", "Property Management", "Finance"]
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["company_name"]
                }
            },
            {
                "name": "generate_sales_brief",
                "description": "Generate comprehensive sales intelligence brief",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"}
                    },
                    "required": ["company_name"]
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool"""
        try:
            if tool_name == "enrich_prospect":
                return await self.enrich_company(
                    parameters["company_name"],
                    parameters.get("enrichment_level", "comprehensive")
                )
            elif tool_name == "discover_contacts":
                contacts = await self.discover_contacts(
                    parameters["company_name"],
                    parameters.get("departments"),
                    limit=parameters.get("limit", 10)
                )
                return {"contacts": contacts, "count": len(contacts)}
            elif tool_name == "generate_sales_brief":
                return await self.generate_sales_brief(parameters["company_name"])
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "apollo-mcp",
            "timestamp": datetime.utcnow().isoformat(),
            "apollo_connected": bool(self.apollo_api_key),
            "redis_connected": self.redis_client.ping(),
            "nmhc_list_loaded": len(self.nmhc_top_50) > 0
        }


# MCP Server Runner
async def run_mcp_server():
    """Run the Apollo MCP server"""
    server = ApolloMCPServer()
    
    # Basic HTTP server for health checks and MCP interface
    from aiohttp import web
    
    async def health_handler(request):
        health_status = await server.health_check()
        return web.json_response(health_status)
        
    async def tools_handler(request):
        tools = server.get_tools()
        return web.json_response({"tools": tools})
        
    async def execute_handler(request):
        data = await request.json()
        result = await server.execute_tool(
            data.get("tool_name"),
            data.get("parameters", {})
        )
        return web.json_response(result)
        
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/tools", tools_handler)
    app.router.add_post("/execute", execute_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 3000)
    
    logger.info("Apollo.io MCP Server starting on port 3000...")
    await site.start()
    
    # Keep server running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
