"""
Gong MCP Client Example
This script demonstrates how to use the MCP client to call the Gong MCP server
instead of making direct API calls to Gong.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from backend.mcp.mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GongMCPClient:
    """
    Gong client that uses the MCP federation model instead of making direct API calls.
    """
    
    def __init__(self, mcp_gateway_url: str = "http://localhost:8090"):
        self.mcp_client = MCPClient(mcp_gateway_url)
        self.server_name = "gong"
    
    async def initialize(self):
        """Connect to the MCP gateway."""
        await self.mcp_client.connect()
        logger.info("MCP Client connected.")
    
    async def close(self):
        """Close the MCP client connection."""
        await self.mcp_client.close()
        logger.info("MCP Client disconnected.")
    
    async def extract_all_available_data(self) -> Dict[str, Any]:
        """Extract all available data using the Gong MCP server."""
        
        extraction_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "extraction_summary": {},
            "errors": []
        }
        
        try:
            # Step 1: Extract users
            logger.info("Extracting users...")
            users_result = await self.extract_users()
            extraction_results["users"] = users_result
            
            # Step 2: Extract workspaces
            logger.info("Extracting workspaces...")
            workspaces_result = await self.extract_workspaces()
            extraction_results["workspaces"] = workspaces_result
            
            # Step 3: Extract calls
            logger.info("Extracting calls...")
            calls_result = await self.extract_calls()
            extraction_results["calls"] = calls_result
            
            # Step 4: Extract library data
            logger.info("Extracting library data...")
            library_result = await self.extract_library_data()
            extraction_results["library"] = library_result
            
            # Step 5: Extract settings
            logger.info("Extracting settings...")
            settings_result = await self.extract_settings()
            extraction_results["settings"] = settings_result
            
            # Step 6: Extract stats
            logger.info("Extracting stats...")
            stats_result = await self.extract_stats()
            extraction_results["stats"] = stats_result
            
            # Store all extracted data
            logger.info("Storing extracted data in database...")
            storage_result = await self.store_all_data(extraction_results)
            extraction_results["database_storage"] = storage_result
            
            # Generate summary
            extraction_results["extraction_summary"] = {
                "total_users": len(users_result.get("users", [])),
                "total_workspaces": len(workspaces_result.get("workspaces", [])),
                "total_calls": len(calls_result.get("calls", [])),
                "working_endpoints": self.get_working_endpoints(extraction_results),
                "data_quality_score": self.calculate_data_quality_score(extraction_results),
                "extraction_success": True
            }
            
            return extraction_results
            
        except Exception as e:
            logger.error(f"Error in extract_all_available_data: {str(e)}")
            extraction_results["errors"].append(str(e))
            extraction_results["extraction_summary"]["extraction_success"] = False
            return extraction_results
    
    async def extract_users(self) -> Dict[str, Any]:
        """Extract users using the Gong MCP server."""
        
        try:
            result = await self.mcp_client.call_tool(
                self.server_name,
                "get_users",
                {}
            )
            
            if result.get("success", False):
                users = result.get("data", {}).get("users", [])
                
                # Enhance users with apartment industry analysis
                enhanced_users = []
                for user in users:
                    user["apartment_relevance"] = self.calculate_user_apartment_relevance(user)
                    user["sophia_profile"] = self.generate_user_sophia_profile(user)
                    enhanced_users.append(user)
                
                return {
                    "success": True,
                    "users": enhanced_users,
                    "total_count": len(enhanced_users),
                    "apartment_relevant_users": len([u for u in enhanced_users if u["apartment_relevance"] > 0.5])
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "users": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "users": []
            }
    
    async def extract_workspaces(self) -> Dict[str, Any]:
        """Extract workspaces using the Gong MCP server."""
        
        try:
            result = await self.mcp_client.call_tool(
                self.server_name,
                "get_workspaces",
                {}
            )
            
            if result.get("success", False):
                workspaces = result.get("data", {}).get("workspaces", [])
                return {
                    "success": True,
                    "workspaces": workspaces,
                    "total_count": len(workspaces)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "workspaces": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workspaces": []
            }
    
    async def extract_calls(self) -> Dict[str, Any]:
        """Extract calls using the Gong MCP server."""
        
        try:
            from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            to_date = datetime.utcnow().strftime("%Y-%m-%d")
            
            result = await self.mcp_client.call_tool(
                self.server_name,
                "get_calls",
                {
                    "from_date": f"{from_date}T00:00:00Z",
                    "to_date": f"{to_date}T23:59:59Z"
                }
            )
            
            if result.get("success", False):
                calls = result.get("data", {}).get("calls", [])
                
                # Enhance calls with apartment analysis
                enhanced_calls = []
                for call in calls:
                    call["apartment_relevance"] = self.calculate_call_apartment_relevance(call)
                    call["sophia_insights"] = self.generate_call_insights(call)
                    enhanced_calls.append(call)
                
                return {
                    "success": True,
                    "calls": enhanced_calls,
                    "total_count": len(enhanced_calls)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "calls": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "calls": []
            }
    
    async def extract_library_data(self) -> Dict[str, Any]:
        """Extract library data using the Gong MCP server."""
        
        try:
            result = await self.mcp_client.call_tool(
                self.server_name,
                "get_library",
                {}
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "library_data": result.get("data", {})
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "library_data": {}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "library_data": {}
            }
    
    async def extract_settings(self) -> Dict[str, Any]:
        """Extract settings using the Gong MCP server."""
        
        try:
            result = await self.mcp_client.call_tool(
                self.server_name,
                "get_settings",
                {}
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "settings": result.get("data", {})
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "settings": {}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "settings": {}
            }
    
    async def extract_stats(self) -> Dict[str, Any]:
        """Extract stats using the Gong MCP server."""
        
        try:
            result = await self.mcp_client.call_tool(
                self.server_name,
                "get_stats",
                {}
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "stats": result.get("data", {})
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "stats": {}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stats": {}
            }
    
    async def store_all_data(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Store all extracted data using the Gong MCP server."""
        
        try:
            result = await self.mcp_client.call_tool(
                self.server_name,
                "store_data",
                {
                    "data": extraction_results
                }
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "users_stored": result.get("data", {}).get("users_stored", 0),
                    "workspaces_stored": result.get("data", {}).get("workspaces_stored", 0),
                    "calls_stored": result.get("data", {}).get("calls_stored", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "users_stored": 0,
                    "workspaces_stored": 0,
                    "calls_stored": 0
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "users_stored": 0,
                "workspaces_stored": 0,
                "calls_stored": 0
            }
    
    def calculate_user_apartment_relevance(self, user: Dict[str, Any]) -> float:
        """Calculate apartment industry relevance for a user."""
        
        relevance_score = 0.0
        
        try:
            # Check user title/role
            title = str(user.get("title", "")).lower()
            for keyword in ["property", "apartment", "real estate", "leasing", "management", "housing"]:
                if keyword in title:
                    relevance_score += 0.15
            
            # Check company name
            company = str(user.get("company", "")).lower()
            for keyword in ["apartment", "property", "management", "real estate", "housing", "residential"]:
                if keyword in company:
                    relevance_score += 0.25
            
            # Check email domain
            email = str(user.get("emailAddress", "")).lower()
            apartment_domains = ["apartments.com", "realpage.com", "yardi.com", "appfolio.com"]
            for domain in apartment_domains:
                if domain in email:
                    relevance_score += 0.3
        
        except Exception as e:
            logger.warning(f"Error calculating user relevance: {str(e)}")
        
        return min(relevance_score, 1.0)
    
    def generate_user_sophia_profile(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Sophia-specific user profile."""
        
        profile = {
            "role_category": "unknown",
            "influence_level": "low",
            "apartment_focus": False,
            "contact_priority": "normal"
        }
        
        try:
            title = str(user.get("title", "")).lower()
            
            # Role categorization
            if any(role in title for role in ["sales", "account", "business development"]):
                profile["role_category"] = "sales"
            elif any(role in title for role in ["manager", "director", "vp", "president", "ceo"]):
                profile["role_category"] = "management"
            elif any(role in title for role in ["property", "leasing", "maintenance"]):
                profile["role_category"] = "operations"
            
            # Influence level
            if any(role in title for role in ["ceo", "president", "founder", "owner"]):
                profile["influence_level"] = "high"
            elif any(role in title for role in ["director", "vp", "manager"]):
                profile["influence_level"] = "medium"
            
            # Apartment focus
            profile["apartment_focus"] = user.get("apartment_relevance", 0.0) > 0.5
            
            # Contact priority
            if profile["influence_level"] == "high" and profile["apartment_focus"]:
                profile["contact_priority"] = "urgent"
            elif profile["apartment_focus"]:
                profile["contact_priority"] = "high"
        
        except Exception as e:
            logger.warning(f"Error generating user profile: {str(e)}")
        
        return profile
    
    def calculate_call_apartment_relevance(self, call: Dict[str, Any]) -> float:
        """Calculate apartment industry relevance for a call."""
        
        relevance_score = 0.0
        
        try:
            # Check call title
            title = str(call.get("title", "")).lower()
            apartment_keywords = ["apartment", "rental", "lease", "tenant", "property", "housing", "pay ready"]
            
            for keyword in apartment_keywords:
                if keyword in title:
                    relevance_score += 0.1
            
            # Check participants
            participants = call.get("participants", [])
            if isinstance(participants, list):
                for participant in participants:
                    if isinstance(participant, dict):
                        company = str(participant.get("company", "")).lower()
                        for keyword in ["apartment", "property", "management", "real estate", "housing"]:
                            if keyword in company:
                                relevance_score += 0.15
            
            # Check call duration
            duration = call.get("duration", 0)
            if isinstance(duration, (int, float)):
                if duration > 1800:  # 30+ minutes
                    relevance_score += 0.1
        
        except Exception as e:
            logger.warning(f"Error calculating call relevance: {str(e)}")
        
        return min(relevance_score, 1.0)
    
    def generate_call_insights(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for a call."""
        
        insights = {
            "business_value": "low",
            "follow_up_priority": "normal",
            "deal_stage": "unknown",
            "apartment_focus": False
        }
        
        try:
            apartment_relevance = call.get("apartment_relevance", 0.0)
            title = str(call.get("title", "")).lower()
            
            if apartment_relevance > 0.7:
                insights["business_value"] = "high"
                insights["follow_up_priority"] = "urgent"
                insights["apartment_focus"] = True
            elif apartment_relevance > 0.4:
                insights["business_value"] = "medium"
                insights["apartment_focus"] = True
            
            # Deal stage identification
            if any(word in title for word in ["demo", "demonstration"]):
                insights["deal_stage"] = "demonstration"
            elif any(word in title for word in ["proposal", "pricing"]):
                insights["deal_stage"] = "proposal"
            elif any(word in title for word in ["discovery", "initial"]):
                insights["deal_stage"] = "discovery"
        
        except Exception as e:
            logger.warning(f"Error generating call insights: {str(e)}")
        
        return insights
    
    def get_working_endpoints(self, extraction_results: Dict[str, Any]) -> List[str]:
        """Get list of working endpoints."""
        
        working_endpoints = []
        
        if extraction_results.get("users", {}).get("success", False):
            working_endpoints.append("users")
        
        if extraction_results.get("workspaces", {}).get("success", False):
            working_endpoints.append("workspaces")
        
        if extraction_results.get("calls", {}).get("success", False):
            working_endpoints.append("calls")
        
        if extraction_results.get("library", {}).get("success", False):
            working_endpoints.append("library")
        
        if extraction_results.get("settings", {}).get("success", False):
            working_endpoints.append("settings")
        
        if extraction_results.get("stats", {}).get("success", False):
            working_endpoints.append("stats")
        
        return working_endpoints
    
    def calculate_data_quality_score(self, extraction_results: Dict[str, Any]) -> float:
        """Calculate overall data quality score."""
        
        score = 0.0
        
        # Users (40% weight)
        if extraction_results.get("users", {}).get("success", False):
            score += 0.4
        
        # Workspaces (20% weight)
        if extraction_results.get("workspaces", {}).get("success", False):
            score += 0.2
        
        # Calls (30% weight)
        if extraction_results.get("calls", {}).get("success", False):
            score += 0.3
        
        # Other endpoints (10% weight)
        other_endpoints = ["library", "settings", "stats"]
        working_other = sum(1 for endpoint in other_endpoints 
                          if extraction_results.get(endpoint, {}).get("success", False))
        score += (working_other / len(other_endpoints)) * 0.1
        
        return score


async def main():
    """
    Main function to run the Gong MCP client.
    """
    # NOTE: This assumes the MCP Gateway and the Gong MCP server are running.
    # You can start them with `docker-compose up mcp-gateway gong-mcp`
    
    client = GongMCPClient()
    try:
        await client.initialize()
        results = await client.extract_all_available_data()
        
        print("\n🎯 GONG MCP CLIENT TEST COMPLETE")
        
        # Save results to file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"gong_mcp_extraction_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results saved to: {filename}")
        
        # Print summary
        summary = results.get("extraction_summary", {})
        print(f"Users extracted: {summary.get('total_users', 0)}")
        print(f"Workspaces extracted: {summary.get('total_workspaces', 0)}")
        print(f"Calls extracted: {summary.get('total_calls', 0)}")
        print(f"Working endpoints: {', '.join(summary.get('working_endpoints', []))}")
        print(f"Data quality score: {summary.get('data_quality_score', 0.0):.2f}")
        
        # Print database storage results
        storage = results.get("database_storage", {})
        if storage.get("success"):
            print(f"\n💾 DATABASE STORAGE:")
            print(f"Users stored: {storage.get('users_stored', 0)}")
            print(f"Workspaces stored: {storage.get('workspaces_stored', 0)}")
            print(f"Calls stored: {storage.get('calls_stored', 0)}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    # Run the Gong MCP client
    asyncio.run(main())
