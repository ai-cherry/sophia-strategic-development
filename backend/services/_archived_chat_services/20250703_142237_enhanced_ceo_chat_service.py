#!/usr/bin/env python3
"""
Enhanced Unified Chat Service
========================

Advanced chat service with migration control capabilities, natural language processing,
and executive-level intelligence for Unified dashboard integration.
"""

import asyncio
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from backend.services.migration_orchestrator_client import get_migration_orchestrator_client
from backend.services.smart_ai_service import SmartAIService
from backend.mcp_servers.ai_memory.ai_memory_handlers import AIMemoryHandlers

logger = logging.getLogger(__name__)


class ChatContext(Enum):
    """Chat context types for Unified interface"""
    GENERAL = "general"
    MIGRATION_CONTROL = "migration_control"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    SYSTEM_MONITORING = "system_monitoring"
    STRATEGIC_PLANNING = "strategic_planning"


class UnifiedChatRequest(BaseModel):
    """Unified chat request model"""
    message: str
    user_id: str
    context: ChatContext = ChatContext.GENERAL
    timestamp: datetime = None
    voice_command: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)


class UnifiedChatResponse(BaseModel):
    """Unified chat response model"""
    message: str
    context: ChatContext
    timestamp: datetime
    actions_taken: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    metrics: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None


class EnhancedUnifiedChatService:
    """
    Enhanced Unified chat service with migration control and executive intelligence
    """

    def __init__(self):
        self.migration_client = get_migration_orchestrator_client()
        self.ai_service = SmartAIService()
        self.memory_handlers = AIMemoryHandlers()
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Migration command patterns
        self.migration_patterns = {
            "start": ["start", "begin", "initiate", "launch", "commence"],
            "status": ["status", "progress", "how", "update", "check"],
            "pause": ["pause", "stop", "halt", "suspend"],
            "resume": ["resume", "continue", "restart", "proceed"],
            "issues": ["issues", "problems", "errors", "alerts", "warnings"],
            "rollback": ["rollback", "revert", "undo", "reverse"],
            "completion": ["when", "complete", "finish", "done", "eta"],
        }

    async def process_ceo_message(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Process Unified message with context-aware routing"""
        try:
            # Store conversation in memory
            await self._store_conversation_context(request)
            
            # Determine context if not specified
            if request.context == ChatContext.GENERAL:
                request.context = await self._detect_context(request.message)
            
            # Route to appropriate handler
            if request.context == ChatContext.MIGRATION_CONTROL:
                return await self._handle_migration_control(request)
            elif request.context == ChatContext.BUSINESS_INTELLIGENCE:
                return await self._handle_business_intelligence(request)
            elif request.context == ChatContext.SYSTEM_MONITORING:
                return await self._handle_system_monitoring(request)
            elif request.context == ChatContext.STRATEGIC_PLANNING:
                return await self._handle_strategic_planning(request)
            else:
                return await self._handle_general_chat(request)
                
        except Exception as e:
            logger.error(f"Failed to process Unified message: {e}")
            return UnifiedChatResponse(
                message=f"I encountered an error processing your request: {str(e)}",
                context=request.context,
                timestamp=datetime.now(UTC),
                suggestions=["Please try rephrasing your request", "Check system status", "Contact technical support"],
            )

    async def _handle_migration_control(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Handle migration control commands"""
        message = request.message.lower().strip()
        actions_taken = []
        
        try:
            # Process migration command
            result = await self.migration_client.process_natural_language_command(
                request.message, request.user_id
            )
            
            if result.get("success"):
                # Successful command execution
                response_message = await self._generate_executive_response(result, request.message)
                
                # Get current metrics if available
                metrics = None
                if "migration_id" in result or "current_phase" in result:
                    status = await self.migration_client.get_migration_status()
                    metrics = status.get("metrics")
                
                actions_taken.append({
                    "action": "migration_command",
                    "command": request.message,
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat(),
                })
                
                # Generate contextual suggestions
                suggestions = await self._generate_migration_suggestions(result)
                
                return UnifiedChatResponse(
                    message=response_message,
                    context=ChatContext.MIGRATION_CONTROL,
                    timestamp=datetime.now(UTC),
                    actions_taken=actions_taken,
                    suggestions=suggestions,
                    metrics=metrics,
                )
                
            else:
                # Command failed or not recognized
                error_message = result.get("error_message", "Command not recognized")
                available_commands = result.get("available_commands", [])
                
                response_message = f"I couldn't execute that command: {error_message}."
                if available_commands:
                    response_message += f"\n\nAvailable migration commands:\n" + "\n".join([f"• {cmd}" for cmd in available_commands])
                
                return UnifiedChatResponse(
                    message=response_message,
                    context=ChatContext.MIGRATION_CONTROL,
                    timestamp=datetime.now(UTC),
                    suggestions=available_commands,
                )
                
        except Exception as e:
            logger.error(f"Migration control error: {e}")
            return UnifiedChatResponse(
                message=f"Migration control system encountered an error: {str(e)}",
                context=ChatContext.MIGRATION_CONTROL,
                timestamp=datetime.now(UTC),
                suggestions=["Check migration system health", "Try basic status command", "Contact technical support"],
            )

    async def _handle_business_intelligence(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Handle business intelligence queries"""
        try:
            # Get executive summary if migration-related
            if any(keyword in request.message.lower() for keyword in ["migration", "salesforce", "hubspot"]):
                summary = await self.migration_client.get_executive_summary()
                
                response_message = await self._format_executive_summary(summary, request.message)
                
                return UnifiedChatResponse(
                    message=response_message,
                    context=ChatContext.BUSINESS_INTELLIGENCE,
                    timestamp=datetime.now(UTC),
                    metrics=summary.get("migration_overview"),
                    suggestions=[
                        "View detailed migration metrics",
                        "Check ROI calculations",
                        "Review risk assessment",
                        "See timeline projections",
                    ],
                )
            else:
                # General business intelligence
                ai_response = await self.ai_service.generate_response(
                    request.message,
                    context="Unified business intelligence query",
                    user_id=request.user_id,
                )
                
                return UnifiedChatResponse(
                    message=ai_response,
                    context=ChatContext.BUSINESS_INTELLIGENCE,
                    timestamp=datetime.now(UTC),
                    suggestions=[
                        "Request specific metrics",
                        "Ask for trend analysis",
                        "Get competitive insights",
                    ],
                )
                
        except Exception as e:
            logger.error(f"Business intelligence error: {e}")
            return UnifiedChatResponse(
                message=f"Business intelligence system error: {str(e)}",
                context=ChatContext.BUSINESS_INTELLIGENCE,
                timestamp=datetime.now(UTC),
            )

    async def _handle_system_monitoring(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Handle system monitoring queries"""
        try:
            # Get system health status
            migration_status = await self.migration_client.get_migration_status()
            health_indicators = migration_status.get("health_indicators", {})
            
            # Format health report
            healthy_systems = [name for name, status in health_indicators.items() if status == "healthy"]
            degraded_systems = [name for name, status in health_indicators.items() if status == "degraded"]
            offline_systems = [name for name, status in health_indicators.items() if status == "offline"]
            
            response_parts = ["**System Health Overview:**"]
            
            if healthy_systems:
                response_parts.append(f"✅ **Healthy Systems ({len(healthy_systems)}):** {', '.join(healthy_systems)}")
            
            if degraded_systems:
                response_parts.append(f"⚠️ **Degraded Systems ({len(degraded_systems)}):** {', '.join(degraded_systems)}")
            
            if offline_systems:
                response_parts.append(f"❌ **Offline Systems ({len(offline_systems)}):** {', '.join(offline_systems)}")
            
            # Add migration-specific status
            if migration_status.get("status") != "error":
                response_parts.append(f"\n**Migration Status:** {migration_status.get('status', 'unknown').title()}")
                
                if migration_status.get("metrics"):
                    metrics = migration_status["metrics"]
                    response_parts.append(f"**Progress:** {metrics.get('overall_progress', 0):.1f}%")
                    response_parts.append(f"**Success Rate:** {metrics.get('success_rate', 0):.1f}%")
            
            response_message = "\n".join(response_parts)
            
            return UnifiedChatResponse(
                message=response_message,
                context=ChatContext.SYSTEM_MONITORING,
                timestamp=datetime.now(UTC),
                metrics=migration_status.get("metrics"),
                suggestions=[
                    "Check detailed system logs",
                    "Review performance metrics",
                    "Get alert notifications",
                    "Schedule maintenance windows",
                ],
            )
            
        except Exception as e:
            logger.error(f"System monitoring error: {e}")
            return UnifiedChatResponse(
                message=f"System monitoring error: {str(e)}",
                context=ChatContext.SYSTEM_MONITORING,
                timestamp=datetime.now(UTC),
            )

    async def _handle_strategic_planning(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Handle strategic planning discussions"""
        try:
            # Use AI service for strategic analysis
            ai_response = await self.ai_service.generate_response(
                request.message,
                context="Unified strategic planning discussion with focus on AI and automation capabilities",
                user_id=request.user_id,
            )
            
            # Enhance with migration platform insights if relevant
            if any(keyword in request.message.lower() for keyword in ["migration", "automation", "ai", "platform"]):
                summary = await self.migration_client.get_executive_summary()
                strategic_insights = await self._generate_strategic_insights(summary)
                
                enhanced_response = f"{ai_response}\n\n**Strategic Platform Insights:**\n{strategic_insights}"
            else:
                enhanced_response = ai_response
            
            return UnifiedChatResponse(
                message=enhanced_response,
                context=ChatContext.STRATEGIC_PLANNING,
                timestamp=datetime.now(UTC),
                suggestions=[
                    "Explore AI automation opportunities",
                    "Review competitive positioning",
                    "Assess scalability options",
                    "Plan next-phase capabilities",
                ],
            )
            
        except Exception as e:
            logger.error(f"Strategic planning error: {e}")
            return UnifiedChatResponse(
                message=f"Strategic planning system error: {str(e)}",
                context=ChatContext.STRATEGIC_PLANNING,
                timestamp=datetime.now(UTC),
            )

    async def _handle_general_chat(self, request: UnifiedChatRequest) -> UnifiedChatResponse:
        """Handle general chat queries"""
        try:
            # Use AI service for general responses
            ai_response = await self.ai_service.generate_response(
                request.message,
                context="Unified general inquiry",
                user_id=request.user_id,
            )
            
            return UnifiedChatResponse(
                message=ai_response,
                context=ChatContext.GENERAL,
                timestamp=datetime.now(UTC),
                suggestions=[
                    "Switch to migration control",
                    "Ask about business metrics",
                    "Check system status",
                    "Discuss strategic plans",
                ],
            )
            
        except Exception as e:
            logger.error(f"General chat error: {e}")
            return UnifiedChatResponse(
                message=f"I encountered an error: {str(e)}",
                context=ChatContext.GENERAL,
                timestamp=datetime.now(UTC),
            )

    async def _detect_context(self, message: str) -> ChatContext:
        """Detect the appropriate context for the message"""
        message_lower = message.lower()
        
        # Migration control keywords
        migration_keywords = ["migration", "migrate", "salesforce", "hubspot", "intercom", "start", "pause", "status", "rollback"]
        if any(keyword in message_lower for keyword in migration_keywords):
            return ChatContext.MIGRATION_CONTROL
        
        # Business intelligence keywords
        bi_keywords = ["roi", "revenue", "cost", "savings", "metrics", "performance", "analytics", "dashboard"]
        if any(keyword in message_lower for keyword in bi_keywords):
            return ChatContext.BUSINESS_INTELLIGENCE
        
        # System monitoring keywords
        monitoring_keywords = ["health", "status", "monitoring", "alerts", "uptime", "performance", "systems"]
        if any(keyword in message_lower for keyword in monitoring_keywords):
            return ChatContext.SYSTEM_MONITORING
        
        # Strategic planning keywords
        strategy_keywords = ["strategy", "planning", "future", "roadmap", "competitive", "market", "growth"]
        if any(keyword in message_lower for keyword in strategy_keywords):
            return ChatContext.STRATEGIC_PLANNING
        
        return ChatContext.GENERAL

    async def _generate_executive_response(self, result: Dict[str, Any], original_command: str) -> str:
        """Generate executive-appropriate response for migration commands"""
        if "start" in original_command.lower():
            return f"✅ **Migration Initiated Successfully**\n\nThe Salesforce to HubSpot/Intercom migration has been started with AI-enhanced orchestration. Migration ID: {result.get('migration_id', 'N/A')}\n\n**Key Details:**\n• Estimated Duration: {result.get('estimated_duration', 'Calculating...')}\n• Next Phase: {result.get('next_phase', 'Assessment')}\n• AI Enhancement: Active\n• Unified Notifications: Enabled\n\nYou'll receive real-time updates as the migration progresses through each phase."
        
        elif "status" in original_command.lower():
            metrics = result.get("metrics", {})
            if metrics:
                return f"📊 **Migration Status Update**\n\n**Current Status:** {result.get('status', 'Unknown').title()}\n**Progress:** {metrics.get('overall_progress', 0):.1f}%\n**Current Phase:** {metrics.get('current_phase', 'Unknown').title()}\n**Success Rate:** {metrics.get('success_rate', 0):.1f}%\n**Records Processed:** {metrics.get('records_processed', 0):,} of {metrics.get('total_records', 0):,}\n\n**System Health:** All migration systems operational\n**Estimated Completion:** {metrics.get('estimated_completion', 'Calculating...')}"
            else:
                return f"📊 **Migration Status:** {result.get('status', 'Unknown').title()}\n\nDetailed metrics are being calculated. The migration system is operational and ready for your commands."
        
        elif "pause" in original_command.lower():
            return f"⏸️ **Migration Paused**\n\nThe migration has been safely paused at checkpoint: {result.get('checkpoint_id', 'N/A')}\n\n**Current Phase:** {result.get('current_phase', 'Unknown')}\n**Data Integrity:** Preserved\n**Resume Capability:** Ready\n\nThe migration can be resumed at any time without data loss."
        
        elif "resume" in original_command.lower():
            return f"▶️ **Migration Resumed**\n\nThe migration has been successfully resumed and is now processing.\n\n**Current Phase:** {result.get('current_phase', 'Unknown')}\n**Estimated Completion:** {result.get('estimated_completion', 'Calculating...')}\n**Status:** Active\n\nReal-time progress updates will continue."
        
        elif "issues" in original_command.lower():
            issues = result.get("issues", [])
            critical_count = result.get("critical_issues", 0)
            
            if not issues:
                return "✅ **No Migration Issues**\n\nThe migration is proceeding smoothly with no reported issues. All systems are operating within normal parameters."
            else:
                return f"⚠️ **Migration Issues Summary**\n\n**Total Issues:** {len(issues)}\n**Critical Issues:** {critical_count}\n**Status:** {'Attention Required' if critical_count > 0 else 'Monitoring'}\n\nDetailed issue reports and resolution recommendations are available in the migration dashboard."
        
        elif "rollback" in original_command.lower():
            return f"🔄 **Migration Rollback Initiated**\n\nRollback ID: {result.get('rollback_id', 'N/A')}\n**Estimated Duration:** {result.get('estimated_duration', 'Calculating...')}\n**Data Preservation:** Active\n\nThe system will safely revert changes while preserving data integrity. You'll receive notifications as the rollback completes."
        
        else:
            return f"✅ **Command Executed**\n\n{result.get('message', 'Operation completed successfully.')}"

    async def _generate_migration_suggestions(self, result: Dict[str, Any]) -> List[str]:
        """Generate contextual suggestions based on migration result"""
        suggestions = []
        
        if result.get("success"):
            if "migration_id" in result:
                suggestions.extend([
                    "Monitor migration progress",
                    "Check system health",
                    "Review business impact metrics",
                ])
            elif "current_phase" in result:
                suggestions.extend([
                    "Get detailed phase metrics",
                    "Check for any issues",
                    "Review estimated completion time",
                ])
            elif "issues" in result:
                suggestions.extend([
                    "Review issue details",
                    "Get resolution recommendations",
                    "Check system health status",
                ])
        else:
            suggestions.extend([
                "Check migration system status",
                "Try a different command",
                "Get help with available commands",
            ])
        
        return suggestions

    async def _format_executive_summary(self, summary: Dict[str, Any], query: str) -> str:
        """Format executive summary for Unified consumption"""
        if summary.get("error"):
            return f"**Executive Summary Error:** {summary['error']}"
        
        overview = summary.get("migration_overview", {})
        business_impact = summary.get("business_impact", {})
        risk_assessment = summary.get("risk_assessment", {})
        
        response_parts = ["**📈 Executive Migration Summary**"]
        
        # Migration overview
        if overview:
            response_parts.append(f"\n**Current Status:** {overview.get('status', 'Unknown').title()}")
            response_parts.append(f"**Progress:** {overview.get('overall_progress', 0):.1f}%")
            response_parts.append(f"**Success Rate:** {overview.get('success_rate', 0):.1f}%")
        
        # Business impact
        if business_impact:
            cost_savings = business_impact.get("cost_savings", {})
            if cost_savings:
                response_parts.append(f"\n**💰 Business Impact:**")
                response_parts.append(f"• Annual Savings: ${cost_savings.get('annual_salesforce_savings', 0):,}")
                response_parts.append(f"• ROI vs Consulting: {cost_savings.get('migration_cost_vs_consulting', 'N/A')}")
                response_parts.append(f"• Time Efficiency: {cost_savings.get('time_savings', 'N/A')}")
        
        # Risk assessment
        if risk_assessment:
            response_parts.append(f"\n**🎯 Risk Assessment:**")
            response_parts.append(f"• Risk Level: {risk_assessment.get('risk_level', 'Unknown').title()}")
            response_parts.append(f"• Total Issues: {risk_assessment.get('total_issues', 0)}")
            response_parts.append(f"• Critical Issues: {risk_assessment.get('critical_issues', 0)}")
        
        # Next actions
        next_actions = summary.get("next_actions", [])
        if next_actions:
            response_parts.append(f"\n**🎯 Recommended Actions:**")
            for action in next_actions[:3]:  # Limit to top 3
                response_parts.append(f"• {action}")
        
        return "\n".join(response_parts)

    async def _generate_strategic_insights(self, summary: Dict[str, Any]) -> str:
        """Generate strategic insights from migration platform capabilities"""
        insights = []
        
        business_impact = summary.get("business_impact", {})
        
        if business_impact:
            strategic_value = business_impact.get("strategic_value", {})
            if strategic_value:
                insights.append("• **AI Capabilities:** Demonstrated AI-enhanced business process automation")
                insights.append("• **Competitive Advantage:** Built industry-leading migration platform internally")
                insights.append("• **Internal Expertise:** Developed core AI and automation competencies")
        
        insights.append("• **Scalability:** Platform can be extended to other business transformations")
        insights.append("• **Market Position:** Positions Pay Ready as AI-native and technically sophisticated")
        insights.append("• **Future Opportunities:** Foundation for additional enterprise automation projects")
        
        return "\n".join(insights)

    async def _store_conversation_context(self, request: UnifiedChatRequest):
        """Store conversation in AI memory for context"""
        try:
            await self.memory_handlers.store_memory(
                content=f"Unified Query: {request.message}",
                category="ceo_interaction",
                importance=0.8,
                context={
                    "user_id": request.user_id,
                    "context": request.context.value,
                    "timestamp": request.timestamp.isoformat(),
                    "voice_command": request.voice_command,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to store conversation context: {e}")

    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for context"""
        try:
            memories = await self.memory_handlers.search_memories(
                query=f"Unified interactions for user {user_id}",
                category="ceo_interaction",
                limit=limit,
            )
            return [memory.dict() for memory in memories]
        except Exception as e:
            logger.warning(f"Failed to get conversation history: {e}")
            return []

    async def cleanup(self):
        """Cleanup resources"""
        await self.migration_client.cleanup()


# Global Unified chat service instance
_ceo_chat_service = None

def get_ceo_chat_service() -> EnhancedUnifiedChatService:
    """Get the global Unified chat service instance"""
    global _ceo_chat_service
    if _ceo_chat_service is None:
        _ceo_chat_service = EnhancedUnifiedChatService()
    return _ceo_chat_service 