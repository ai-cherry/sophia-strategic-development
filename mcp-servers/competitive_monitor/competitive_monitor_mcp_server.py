"""
Competitive Intelligence Monitor MCP Server for Pay Ready
Real-time monitoring of competitive landscape for strategic intelligence
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

import aiohttp
from pydantic import BaseModel, Field
from redis import Redis
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slack_sdk.webhook import WebhookClient
import schedule

from backend.agents.core.base_agent import BaseAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompetitorMonitoringRequest(BaseModel):
    """Request model for competitor monitoring"""
    competitor_name: str
    monitoring_type: str = Field(default="comprehensive", pattern="^(basic|comprehensive|deep)$")
    alert_threshold: str = Field(default="medium", pattern="^(low|medium|high)$")
    

class CompetitiveInsight(BaseModel):
    """Competitive insight data model"""
    competitor: str
    insight_type: str
    severity: str
    description: str
    detected_at: datetime
    source_url: Optional[str] = None
    screenshot_path: Optional[str] = None
    action_required: bool = False
    recommendations: List[str] = []


class CompetitorProfile(BaseModel):
    """Competitor profile data model"""
    name: str
    website: str
    monitor_urls: List[str]
    keywords: List[str]
    threat_level: str
    monitoring_frequency: int  # minutes


class CompetitiveMonitorMCPServer(BaseAgent):
    """Competitive Intelligence Monitor MCP Server"""
    
    def __init__(self, config_dict: Optional[Dict] = None):
        super().__init__(config_dict or {
            "name": "Competitive Intelligence Monitor",
            "description": "Real-time competitive monitoring for Pay Ready strategic advantage"
        })
        
        # Redis cache configuration
        self.redis_client = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # Slack webhook for alerts
        self.slack_webhook = WebhookClient(
            url=os.getenv("SLACK_WEBHOOK_URL", "")
        )
        self.alert_channel = os.getenv("ALERT_CHANNEL", "#competitive-intelligence")
        
        # Monitoring configuration
        self.monitoring_frequency = int(os.getenv("MONITORING_FREQUENCY", 300))  # 5 minutes default
        
        # Define competitor profiles
        self.competitors = self._initialize_competitor_profiles()
        
        # Selenium configuration
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Add MCP capabilities
        self.capabilities.extend([
            "competitive_monitoring",
            "threat_detection",
            "market_intelligence",
            "alert_management"
        ])
        
    def _initialize_competitor_profiles(self) -> Dict[str, CompetitorProfile]:
        """Initialize competitor monitoring profiles"""
        return {
            "elise_ai": CompetitorProfile(
                name="EliseAI",
                website="https://www.eliseai.com",
                monitor_urls=[
                    "https://www.eliseai.com/",
                    "https://www.eliseai.com/blog",
                    "https://www.eliseai.com/product",
                    "https://www.eliseai.com/pricing"
                ],
                keywords=[
                    "collections", "payment", "revenue", "property management",
                    "AI assistant", "leasing", "resident communication"
                ],
                threat_level="high",
                monitoring_frequency=300  # 5 minutes
            ),
            "hunter_warfield": CompetitorProfile(
                name="Hunter Warfield",
                website="https://www.hunterwarfield.com",
                monitor_urls=[
                    "https://www.hunterwarfield.com/",
                    "https://www.hunterwarfield.com/services",
                    "https://www.hunterwarfield.com/resources"
                ],
                keywords=[
                    "collections", "debt recovery", "property management",
                    "multifamily", "apartment collections"
                ],
                threat_level="medium",
                monitoring_frequency=600  # 10 minutes
            ),
            "collecttech": CompetitorProfile(
                name="CollectTech",
                website="https://www.collecttech.com",
                monitor_urls=[
                    "https://www.collecttech.com/",
                    "https://www.collecttech.com/solutions",
                    "https://www.collecttech.com/news"
                ],
                keywords=[
                    "digital collections", "payment solutions", "automation",
                    "resident portal", "payment processing"
                ],
                threat_level="medium",
                monitoring_frequency=600  # 10 minutes
            ),
            "entrata": CompetitorProfile(
                name="Entrata",
                website="https://www.entrata.com",
                monitor_urls=[
                    "https://www.entrata.com/",
                    "https://www.entrata.com/products/eli",
                    "https://www.entrata.com/blog"
                ],
                keywords=[
                    "ELI+", "AI leasing", "property management", "collections",
                    "revenue management", "resident payments"
                ],
                threat_level="high",
                monitoring_frequency=300  # 5 minutes
            ),
            "yardi": CompetitorProfile(
                name="Yardi",
                website="https://www.yardi.com",
                monitor_urls=[
                    "https://www.yardi.com/",
                    "https://www.yardi.com/products",
                    "https://www.yardi.com/news"
                ],
                keywords=[
                    "rent payment", "collections", "property management",
                    "payment processing", "revenue optimization"
                ],
                threat_level="medium",
                monitoring_frequency=600  # 10 minutes
            )
        }
        
    async def monitor_competitor(self, competitor_key: str) -> List[CompetitiveInsight]:
        """Monitor a specific competitor for changes and insights"""
        
        competitor = self.competitors.get(competitor_key)
        if not competitor:
            logger.error(f"Unknown competitor: {competitor_key}")
            return []
            
        insights = []
        
        # Check each monitoring URL
        for url in competitor.monitor_urls:
            try:
                # Check cache for recent monitoring
                cache_key = f"monitor:{competitor_key}:{urlparse(url).path}"
                last_content = self.redis_client.get(cache_key)
                
                # Fetch current content
                current_content = await self._fetch_page_content(url)
                
                if current_content:
                    # Analyze for changes and insights
                    if last_content:
                        changes = await self._analyze_changes(
                            competitor,
                            url,
                            last_content,
                            current_content
                        )
                        insights.extend(changes)
                    
                    # Look for keyword mentions
                    keyword_insights = await self._analyze_keywords(
                        competitor,
                        url,
                        current_content
                    )
                    insights.extend(keyword_insights)
                    
                    # Cache the current content
                    self.redis_client.setex(
                        cache_key,
                        86400,  # 24 hour cache
                        current_content
                    )
                    
            except Exception as e:
                logger.error(f"Error monitoring {competitor.name} at {url}: {e}")
                
        # Process and prioritize insights
        insights = self._prioritize_insights(insights)
        
        # Send alerts for high-priority insights
        for insight in insights:
            if insight.severity in ["high", "critical"] or insight.action_required:
                await self._send_alert(insight)
                
        return insights
        
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch page content using Selenium for dynamic content"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source
            page_source = driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Take screenshot for critical pages
            if any(keyword in url for keyword in ["pricing", "product", "eli"]):
                screenshot_path = f"/app/screenshots/{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                
            return text_content
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()
                
    async def _analyze_changes(
        self,
        competitor: CompetitorProfile,
        url: str,
        old_content: str,
        new_content: str
    ) -> List[CompetitiveInsight]:
        """Analyze content changes for competitive insights"""
        insights = []
        
        # Simple change detection (would be more sophisticated in production)
        old_words = set(old_content.lower().split())
        new_words = set(new_content.lower().split())
        
        added_words = new_words - old_words
        removed_words = old_words - new_words
        
        # Check for significant additions
        significant_keywords = [
            "ai", "artificial intelligence", "collections", "payments",
            "revenue", "automation", "integration", "api", "partnership",
            "launch", "release", "new", "feature", "update"
        ]
        
        significant_additions = [
            word for word in added_words 
            if any(keyword in word for keyword in significant_keywords)
        ]
        
        if significant_additions:
            insight = CompetitiveInsight(
                competitor=competitor.name,
                insight_type="content_change",
                severity="high" if len(significant_additions) > 5 else "medium",
                description=f"Significant content changes detected on {competitor.name} - Keywords: {', '.join(significant_additions[:10])}",
                detected_at=datetime.utcnow(),
                source_url=url,
                action_required=True,
                recommendations=[
                    f"Review {competitor.name}'s updated content for new features or strategies",
                    "Assess potential impact on Pay Ready's competitive position",
                    "Update competitive battle cards if necessary"
                ]
            )
            insights.append(insight)
            
        return insights
        
    async def _analyze_keywords(
        self,
        competitor: CompetitorProfile,
        url: str,
        content: str
    ) -> List[CompetitiveInsight]:
        """Analyze content for strategic keyword mentions"""
        insights = []
        content_lower = content.lower()
        
        # Pay Ready specific threat keywords
        threat_keywords = {
            "buzz": "Direct competitor mention",
            "pay ready": "Direct competitor mention",
            "ai collections": "Core capability overlap",
            "automated collections": "Core capability overlap",
            "revenue optimization": "Value proposition overlap",
            "nmhc": "Target market overlap",
            "multifamily collections": "Target market overlap"
        }
        
        for keyword, threat_type in threat_keywords.items():
            if keyword in content_lower:
                # Count occurrences
                count = content_lower.count(keyword)
                
                insight = CompetitiveInsight(
                    competitor=competitor.name,
                    insight_type="keyword_detection",
                    severity="critical" if keyword in ["buzz", "pay ready"] else "high",
                    description=f"{competitor.name} mentioned '{keyword}' {count} times - {threat_type}",
                    detected_at=datetime.utcnow(),
                    source_url=url,
                    action_required=True,
                    recommendations=[
                        f"Investigate {competitor.name}'s strategy regarding {keyword}",
                        "Prepare competitive response messaging",
                        "Alert sales team about potential competitive encounters"
                    ]
                )
                insights.append(insight)
                
        # Product launch detection
        launch_indicators = [
            "introducing", "announcing", "launch", "now available",
            "new feature", "beta", "coming soon", "preview"
        ]
        
        for indicator in launch_indicators:
            if indicator in content_lower:
                context_start = max(0, content_lower.find(indicator) - 100)
                context_end = min(len(content_lower), content_lower.find(indicator) + 100)
                context = content[context_start:context_end]
                
                insight = CompetitiveInsight(
                    competitor=competitor.name,
                    insight_type="product_launch",
                    severity="high",
                    description=f"Potential product launch detected - '{indicator}' found in context: ...{context}...",
                    detected_at=datetime.utcnow(),
                    source_url=url,
                    action_required=True,
                    recommendations=[
                        "Analyze competitive product features",
                        "Update competitive positioning",
                        "Consider acceleration of roadmap if needed"
                    ]
                )
                insights.append(insight)
                break
                
        return insights
        
    def _prioritize_insights(self, insights: List[CompetitiveInsight]) -> List[CompetitiveInsight]:
        """Prioritize insights by severity and relevance"""
        # Define severity order
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        # Sort by severity and then by detection time
        insights.sort(
            key=lambda x: (
                severity_order.get(x.severity, 999),
                x.detected_at
            )
        )
        
        return insights
        
    async def _send_alert(self, insight: CompetitiveInsight) -> None:
        """Send alert to Slack for high-priority insights"""
        if not self.slack_webhook.url:
            logger.warning("Slack webhook not configured, skipping alert")
            return
            
        try:
            # Format alert message
            alert_message = {
                "text": f"🚨 Competitive Intelligence Alert: {insight.competitor}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"Competitive Alert: {insight.competitor}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Type:* {insight.insight_type}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Severity:* {insight.severity.upper()}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Description:*\n{insight.description}"
                        }
                    }
                ]
            }
            
            # Add recommendations if present
            if insight.recommendations:
                recommendations_text = "\n".join([f"• {rec}" for rec in insight.recommendations])
                alert_message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Recommended Actions:*\n{recommendations_text}"
                    }
                })
                
            # Add source URL if present
            if insight.source_url:
                alert_message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{insight.source_url}|View Source>"
                    }
                })
                
            # Send to Slack
            response = self.slack_webhook.send(**alert_message)
            logger.info(f"Alert sent to Slack: {response.status_code}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            
    async def analyze_competitive_landscape(self) -> Dict[str, Any]:
        """Analyze overall competitive landscape"""
        landscape_analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "competitors": {},
            "market_trends": [],
            "threats": [],
            "opportunities": [],
            "recommendations": []
        }
        
        # Monitor all competitors
        all_insights = []
        for competitor_key in self.competitors:
            insights = await self.monitor_competitor(competitor_key)
            all_insights.extend(insights)
            
            # Aggregate by competitor
            competitor_insights = [i for i in insights if i.competitor == self.competitors[competitor_key].name]
            landscape_analysis["competitors"][competitor_key] = {
                "name": self.competitors[competitor_key].name,
                "threat_level": self.competitors[competitor_key].threat_level,
                "recent_activity": len(competitor_insights),
                "critical_insights": len([i for i in competitor_insights if i.severity == "critical"])
            }
            
        # Identify market trends
        insight_types = {}
        for insight in all_insights:
            insight_types[insight.insight_type] = insight_types.get(insight.insight_type, 0) + 1
            
        # Top trends
        top_trends = sorted(insight_types.items(), key=lambda x: x[1], reverse=True)[:5]
        landscape_analysis["market_trends"] = [
            {"trend": trend, "frequency": count} for trend, count in top_trends
        ]
        
        # Identify threats
        critical_insights = [i for i in all_insights if i.severity in ["critical", "high"]]
        landscape_analysis["threats"] = [
            {
                "competitor": i.competitor,
                "description": i.description,
                "severity": i.severity
            } for i in critical_insights[:5]
        ]
        
        # Generate strategic recommendations
        if any(i.insight_type == "product_launch" for i in all_insights):
            landscape_analysis["recommendations"].append(
                "Accelerate product roadmap to maintain competitive advantage"
            )
            
        if any("eli" in i.description.lower() for i in all_insights):
            landscape_analysis["recommendations"].append(
                "Strengthen Buzz AI differentiation against Entrata ELI+"
            )
            
        if len(critical_insights) > 3:
            landscape_analysis["recommendations"].append(
                "Schedule emergency competitive strategy session"
            )
            
        return landscape_analysis
        
    async def generate_competitive_report(self) -> Dict[str, Any]:
        """Generate comprehensive competitive intelligence report"""
        
        # Get landscape analysis
        landscape = await self.analyze_competitive_landscape()
        
        # Generate executive summary
        report = {
            "report_date": datetime.utcnow().isoformat(),
            "executive_summary": self._generate_executive_summary(landscape),
            "competitive_landscape": landscape,
            "action_items": self._generate_action_items(landscape),
            "sales_enablement": self._generate_sales_enablement(landscape)
        }
        
        return report
        
    def _generate_executive_summary(self, landscape: Dict[str, Any]) -> str:
        """Generate executive summary for competitive report"""
        total_threats = len(landscape.get("threats", []))
        critical_competitors = [
            name for name, data in landscape.get("competitors", {}).items()
            if data.get("critical_insights", 0) > 0
        ]
        
        summary = f"""
Competitive Intelligence Executive Summary - {datetime.utcnow().strftime('%B %d, %Y')}

Key Findings:
- Identified {total_threats} high-priority competitive threats requiring immediate attention
- {len(critical_competitors)} competitors showing critical activity: {', '.join(critical_competitors)}
- Top market trend: {landscape.get('market_trends', [{}])[0].get('trend', 'N/A')}

Immediate Action Required:
{chr(10).join(['- ' + rec for rec in landscape.get('recommendations', [])])}
        """
        
        return summary.strip()
        
    def _generate_action_items(self, landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized action items"""
        action_items = []
        
        # Critical threats need immediate response
        for threat in landscape.get("threats", []):
            if threat["severity"] == "critical":
                action_items.append({
                    "priority": "immediate",
                    "owner": "executive_team",
                    "action": f"Address competitive threat from {threat['competitor']}",
                    "description": threat["description"],
                    "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
                })
                
        # High severity items need quick response
        for threat in landscape.get("threats", []):
            if threat["severity"] == "high":
                action_items.append({
                    "priority": "high",
                    "owner": "product_team",
                    "action": f"Analyze and respond to {threat['competitor']} activity",
                    "description": threat["description"],
                    "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat()
                })
                
        return action_items
        
    def _generate_sales_enablement(self, landscape: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales enablement materials based on competitive intelligence"""
        enablement = {
            "battle_cards_updates": [],
            "talking_points": [],
            "objection_handlers": []
        }
        
        # Update battle cards for active competitors
        for competitor_key, data in landscape.get("competitors", {}).items():
            if data.get("recent_activity", 0) > 0:
                enablement["battle_cards_updates"].append({
                    "competitor": data["name"],
                    "update_needed": True,
                    "reason": f"{data['recent_activity']} new insights detected"
                })
                
        # Generate talking points
        enablement["talking_points"] = [
            "Buzz AI provides specialized collections intelligence vs generic solutions",
            "Our AI is trained specifically on multifamily collections best practices",
            "24/7 automated collections with proven ROI within 90 days"
        ]
        
        # Objection handlers based on threats
        if any("elise" in str(threat).lower() for threat in landscape.get("threats", [])):
            enablement["objection_handlers"].append({
                "objection": "We already use EliseAI for leasing",
                "response": "EliseAI focuses on leasing, while Buzz specializes in collections - the most critical part of your revenue cycle. They complement each other perfectly."
            })
            
        return enablement
        
    # MCP Server Interface Methods
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available MCP tools"""
        return [
            {
                "name": "monitor_competitor",
                "description": "Monitor specific competitor for changes and insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "competitor_name": {
                            "type": "string",
                            "enum": list(self.competitors.keys())
                        }
                    },
                    "required": ["competitor_name"]
                }
            },
            {
                "name": "analyze_landscape",
                "description": "Analyze overall competitive landscape",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "generate_report",
                "description": "Generate comprehensive competitive intelligence report",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "check_threat_level",
                "description": "Check current threat level for specific competitor",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "competitor_name": {
                            "type": "string",
                            "enum": list(self.competitors.keys())
                        }
                    },
                    "required": ["competitor_name"]
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool"""
        try:
            if tool_name == "monitor_competitor":
                insights = await self.monitor_competitor(parameters["competitor_name"])
                return {
                    "insights": [insight.dict() for insight in insights],
                    "count": len(insights)
                }
            elif tool_name == "analyze_landscape":
                return await self.analyze_competitive_landscape()
            elif tool_name == "generate_report":
                return await self.generate_competitive_report()
            elif tool_name == "check_threat_level":
                competitor = self.competitors.get(parameters["competitor_name"])
                if competitor:
                    return {
                        "competitor": competitor.name,
                        "threat_level": competitor.threat_level,
                        "monitoring_frequency": competitor.monitoring_frequency
                    }
                else:
                    return {"error": "Unknown competitor"}
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "competitive-monitor-mcp",
            "timestamp": datetime.utcnow().isoformat(),
            "redis_connected": self.redis_client.ping(),
            "slack_configured": bool(self.slack_webhook.url),
            "competitors_monitored": len(self.competitors),
            "monitoring_active": True
        }
        
    async def start_scheduled_monitoring(self):
        """Start scheduled monitoring jobs"""
        logger.info("Starting scheduled competitive monitoring...")
        
        # Schedule monitoring for each competitor based on their frequency
        while True:
            for competitor_key, competitor in self.competitors.items():
                # Check if it's time to monitor
                cache_key = f"last_monitor:{competitor_key}"
                last_monitor = self.redis_client.get(cache_key)
                
                if not last_monitor or (
                    datetime.utcnow() - datetime.fromisoformat(last_monitor)
                ).seconds >= competitor.monitoring_frequency:
                    # Monitor competitor
                    logger.info(f"Monitoring {competitor.name}...")
                    await self.monitor_competitor(competitor_key)
                    
                    # Update last monitor time
                    self.redis_client.set(cache_key, datetime.utcnow().isoformat())
                    
            # Sleep for a minute before checking again
            await asyncio.sleep(60)


# MCP Server Runner
async def run_mcp_server():
    """Run the Competitive Monitor MCP server"""
    server = CompetitiveMonitorMCPServer()
    
    # Start scheduled monitoring in background
    asyncio.create_task(server.start_scheduled_monitoring())
    
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
    
    logger.info("Competitive Intelligence Monitor MCP Server starting on port 3000...")
    await site.start()
    
    # Keep server running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
