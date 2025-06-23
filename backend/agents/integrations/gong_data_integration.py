"""
Gong Data Integration with Sophia Agent System.

Intelligent bridge between existing Gong webhook infrastructure and Sophia AI agents.
Provides data transformation, agent routing, and multi-agent workflow orchestration.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field

# Import existing infrastructure components
from backend.agents.core.agno_mcp_bridge import AgnoMCPBridge
from backend.integrations.gong_redis_client import (
    RedisNotificationClient,
    ProcessedCallData,
    ProcessedEmailData,
    ProcessedMeetingData,
    NotificationPriority,
    NotificationType
)
from backend.core.integration_registry import IntegrationRegistry

logger = structlog.get_logger()


# Agent-Specific Data Models

class CallAnalysisAgentData(BaseModel):
    """Optimized data format for call analysis agent."""
    call_id: str
    conversation_flow: List[Dict[str, Any]]
    sentiment_timeline: List[Dict[str, Any]]
    coaching_opportunities: List[Dict[str, Any]]
    competitive_mentions: List[str]
    risk_indicators: List[str]
    key_moments: List[Dict[str, Any]]
    speaker_analytics: Dict[str, Any]


class SalesIntelligenceAgentData(BaseModel):
    """Optimized data format for sales intelligence agent."""
    call_id: str
    deal_progression: Dict[str, Any]
    revenue_signals: List[Dict[str, Any]]
    pipeline_impact: Dict[str, Any]
    forecast_indicators: List[str]
    next_best_actions: List[Dict[str, Any]]
    buyer_engagement_score: float
    closing_probability: float


class BusinessIntelligenceAgentData(BaseModel):
    """Optimized data format for business intelligence agent."""
    call_id: str
    performance_metrics: Dict[str, Any]
    trend_data: List[Dict[str, Any]]
    benchmark_comparisons: Dict[str, Any]
    insight_categories: List[str]
    actionable_recommendations: List[Dict[str, Any]]
    team_performance_impact: Dict[str, Any]
    market_intelligence: Dict[str, Any]


class ExecutiveIntelligenceAgentData(BaseModel):
    """Optimized data format for executive intelligence agent."""
    event_id: str
    strategic_insights: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    opportunity_analysis: Dict[str, Any]
    competitive_intelligence: Dict[str, Any]
    executive_summary: str
    recommended_actions: List[Dict[str, Any]]
    impact_assessment: Dict[str, Any]


class GeneralIntelligenceAgentData(BaseModel):
    """Optimized data format for general intelligence agent."""
    event_id: str
    task_type: str
    task_details: Dict[str, Any]
    context: Dict[str, Any]
    priority: str
    dependencies: List[str]
    estimated_completion_time: Optional[int] = None


class StandardizedAgentEvent(BaseModel):
    """Standardized event format for all agents."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str  # 'call_processed', 'insight_detected', 'action_required'
    source: str = "gong_webhook"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: str
    gong_data: Dict[str, Any]
    agent_context: Dict[str, Any]
    workflow_id: Optional[str] = None
    correlation_id: Optional[str] = None


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class AgentDataTransformer:
    """
    Transforms Gong webhook data into agent-optimized formats.
    """
    
    def __init__(self):
        self.logger = logger.bind(component="agent_data_transformer")
    
    async def transform_for_call_analysis(
        self, 
        call_data: ProcessedCallData
    ) -> CallAnalysisAgentData:
        """Transform call data for call analysis agent."""
        # Extract conversation flow from participants and duration
        conversation_flow = self._extract_conversation_flow(call_data)
        
        # Generate sentiment timeline
        sentiment_timeline = self._generate_sentiment_timeline(call_data)
        
        # Identify coaching opportunities
        coaching_opportunities = self._identify_coaching_opportunities(call_data)
        
        # Extract competitive mentions from insights
        competitive_mentions = self._extract_competitive_mentions(call_data.insights)
        
        # Identify risk indicators
        risk_indicators = self._identify_risk_indicators(call_data)
        
        # Extract key moments
        key_moments = self._extract_key_moments(call_data)
        
        # Generate speaker analytics
        speaker_analytics = self._generate_speaker_analytics(call_data)
        
        return CallAnalysisAgentData(
            call_id=call_data.call_id,
            conversation_flow=conversation_flow,
            sentiment_timeline=sentiment_timeline,
            coaching_opportunities=coaching_opportunities,
            competitive_mentions=competitive_mentions,
            risk_indicators=risk_indicators,
            key_moments=key_moments,
            speaker_analytics=speaker_analytics
        )
    
    async def transform_for_sales_intelligence(
        self,
        call_data: ProcessedCallData
    ) -> SalesIntelligenceAgentData:
        """Transform call data for sales intelligence agent."""
        # Extract deal progression signals
        deal_progression = self._extract_deal_progression(call_data)
        
        # Identify revenue signals
        revenue_signals = self._identify_revenue_signals(call_data)
        
        # Calculate pipeline impact
        pipeline_impact = self._calculate_pipeline_impact(call_data)
        
        # Extract forecast indicators
        forecast_indicators = self._extract_forecast_indicators(call_data)
        
        # Generate next best actions
        next_best_actions = self._generate_next_best_actions(call_data)
        
        # Calculate buyer engagement score
        buyer_engagement_score = self._calculate_buyer_engagement(call_data)
        
        # Calculate closing probability
        closing_probability = self._calculate_closing_probability(call_data)
        
        return SalesIntelligenceAgentData(
            call_id=call_data.call_id,
            deal_progression=deal_progression,
            revenue_signals=revenue_signals,
            pipeline_impact=pipeline_impact,
            forecast_indicators=forecast_indicators,
            next_best_actions=next_best_actions,
            buyer_engagement_score=buyer_engagement_score,
            closing_probability=closing_probability
        )
    
    async def transform_for_business_intelligence(
        self,
        call_data: ProcessedCallData
    ) -> BusinessIntelligenceAgentData:
        """Transform call data for business intelligence agent."""
        # Extract performance metrics
        performance_metrics = self._extract_performance_metrics(call_data)
        
        # Generate trend data
        trend_data = self._generate_trend_data(call_data)
        
        # Create benchmark comparisons
        benchmark_comparisons = self._create_benchmark_comparisons(call_data)
        
        # Categorize insights
        insight_categories = self._categorize_insights(call_data.insights)
        
        # Generate actionable recommendations
        actionable_recommendations = self._generate_recommendations(call_data)
        
        # Calculate team performance impact
        team_performance_impact = self._calculate_team_impact(call_data)
        
        # Extract market intelligence
        market_intelligence = self._extract_market_intelligence(call_data)
        
        return BusinessIntelligenceAgentData(
            call_id=call_data.call_id,
            performance_metrics=performance_metrics,
            trend_data=trend_data,
            benchmark_comparisons=benchmark_comparisons,
            insight_categories=insight_categories,
            actionable_recommendations=actionable_recommendations,
            team_performance_impact=team_performance_impact,
            market_intelligence=market_intelligence
        )
    
    async def transform_for_executive_intelligence(
        self,
        event_data: Dict[str, Any]
    ) -> ExecutiveIntelligenceAgentData:
        """Transform event data for executive intelligence agent."""
        event_id = event_data.get('event_id', str(uuid4()))
        
        # Extract strategic insights
        strategic_insights = self._extract_strategic_insights(event_data)
        
        # Perform risk assessment
        risk_assessment = self._assess_risks(event_data)
        
        # Analyze opportunities
        opportunity_analysis = self._analyze_opportunities(event_data)
        
        # Extract competitive intelligence
        competitive_intelligence = self._extract_competitive_intel(event_data)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(event_data)
        
        # Generate recommended actions
        recommended_actions = self._generate_executive_actions(event_data)
        
        # Assess impact
        impact_assessment = self._assess_impact(event_data)
        
        return ExecutiveIntelligenceAgentData(
            event_id=event_id,
            strategic_insights=strategic_insights,
            risk_assessment=risk_assessment,
            opportunity_analysis=opportunity_analysis,
            competitive_intelligence=competitive_intelligence,
            executive_summary=executive_summary,
            recommended_actions=recommended_actions,
            impact_assessment=impact_assessment
        )
    
    async def transform_for_general_intelligence(
        self,
        action_data: Dict[str, Any]
    ) -> GeneralIntelligenceAgentData:
        """Transform action data for general intelligence agent."""
        event_id = action_data.get('event_id', str(uuid4()))
        
        return GeneralIntelligenceAgentData(
            event_id=event_id,
            task_type=action_data.get('action_type', 'general_task'),
            task_details=action_data.get('data', {}),
            context=action_data.get('context', {}),
            priority=action_data.get('priority', 'medium'),
            dependencies=action_data.get('dependencies', []),
            estimated_completion_time=action_data.get('estimated_time')
        )
    
    # Helper methods for data transformation
    
    def _extract_conversation_flow(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Extract conversation flow patterns."""
        flow = []
        if call_data.summary:
            # Extract flow from summary if available
            topics = call_data.summary.get('topics', [])
            for i, topic in enumerate(topics):
                flow.append({
                    'sequence': i + 1,
                    'topic': topic,
                    'duration_percentage': 100 / len(topics) if topics else 0
                })
        return flow
    
    def _generate_sentiment_timeline(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Generate sentiment timeline from call data."""
        timeline = []
        if call_data.sentiment_score is not None:
            # Create basic sentiment timeline
            timeline.append({
                'timestamp': 0,
                'sentiment': call_data.sentiment_score,
                'label': self._classify_sentiment(call_data.sentiment_score)
            })
        return timeline
    
    def _identify_coaching_opportunities(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Identify coaching opportunities from call data."""
        opportunities = []
        
        # Check talk ratio for coaching opportunity
        if call_data.talk_ratio and call_data.talk_ratio > 0.7:
            opportunities.append({
                'type': 'talk_ratio',
                'description': 'High talk ratio detected - encourage more customer engagement',
                'severity': 'medium',
                'recommendation': 'Aim for 60-40 talk ratio to improve customer engagement'
            })
        
        # Check for missing next steps
        if not call_data.next_steps:
            opportunities.append({
                'type': 'next_steps',
                'description': 'No clear next steps identified',
                'severity': 'high',
                'recommendation': 'Always conclude calls with clear, actionable next steps'
            })
        
        return opportunities
    
    def _extract_competitive_mentions(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Extract competitive mentions from insights."""
        competitors = []
        for insight in insights:
            if insight.get('type') == 'competitor_mention':
                competitors.append(insight.get('competitor_name', 'Unknown'))
        return list(set(competitors))
    
    def _identify_risk_indicators(self, call_data: ProcessedCallData) -> List[str]:
        """Identify risk indicators from call data."""
        risks = []
        
        # Check sentiment for risks
        if call_data.sentiment_score and call_data.sentiment_score < 0.3:
            risks.append('negative_sentiment')
        
        # Check for risk keywords in insights
        risk_keywords = ['concern', 'issue', 'problem', 'unhappy', 'cancel', 'competitor']
        for insight in call_data.insights:
            if any(keyword in str(insight).lower() for keyword in risk_keywords):
                risks.append('risk_keyword_detected')
                break
        
        return risks
    
    def _extract_key_moments(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Extract key moments from call."""
        moments = []
        
        # Extract from insights
        for insight in call_data.insights:
            moments.append({
                'type': insight.get('type', 'general'),
                'description': insight.get('description', ''),
                'impact': insight.get('impact', 'medium')
            })
        
        return moments
    
    def _generate_speaker_analytics(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Generate speaker analytics."""
        return {
            'talk_ratio': call_data.talk_ratio or 0.5,
            'participant_count': len(call_data.participants),
            'engagement_level': 'high' if call_data.talk_ratio and 0.4 < call_data.talk_ratio < 0.6 else 'medium'
        }
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment score into categories."""
        if score >= 0.7:
            return 'positive'
        elif score >= 0.4:
            return 'neutral'
        else:
            return 'negative'
    
    def _extract_deal_progression(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Extract deal progression indicators."""
        return {
            'stage_advancement': any('next step' in str(step).lower() for step in call_data.next_steps),
            'engagement_level': 'high' if call_data.sentiment_score and call_data.sentiment_score > 0.7 else 'medium',
            'decision_maker_involved': any('decision' in str(p).lower() for p in call_data.participants)
        }
    
    def _identify_revenue_signals(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Identify revenue-related signals."""
        signals = []
        
        # Check for budget discussions
        budget_keywords = ['budget', 'cost', 'price', 'investment']
        for insight in call_data.insights:
            if any(keyword in str(insight).lower() for keyword in budget_keywords):
                signals.append({
                    'type': 'budget_discussion',
                    'strength': 'strong',
                    'description': 'Budget or pricing discussed'
                })
        
        return signals
    
    def _calculate_pipeline_impact(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Calculate impact on sales pipeline."""
        positive_signals = len([i for i in call_data.insights if 'positive' in str(i).lower()])
        negative_signals = len([i for i in call_data.insights if 'concern' in str(i).lower()])
        
        return {
            'impact_score': (positive_signals - negative_signals) / max(len(call_data.insights), 1),
            'confidence': 0.7 if call_data.insights else 0.3,
            'factors': {
                'positive_signals': positive_signals,
                'negative_signals': negative_signals
            }
        }
    
    def _extract_forecast_indicators(self, call_data: ProcessedCallData) -> List[str]:
        """Extract indicators for sales forecasting."""
        indicators = []
        
        if call_data.next_steps:
            indicators.append('clear_next_steps')
        
        if call_data.sentiment_score and call_data.sentiment_score > 0.7:
            indicators.append('positive_sentiment')
        
        if any('timeline' in str(i).lower() for i in call_data.insights):
            indicators.append('timeline_discussed')
        
        return indicators
    
    def _generate_next_best_actions(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Generate recommended next actions."""
        actions = []
        
        # Always follow up on next steps
        for step in call_data.next_steps:
            actions.append({
                'action': 'follow_up',
                'description': f'Follow up on: {step}',
                'priority': 'high',
                'due_date': 'within_48_hours'
            })
        
        # Add sentiment-based actions
        if call_data.sentiment_score and call_data.sentiment_score < 0.5:
            actions.append({
                'action': 'address_concerns',
                'description': 'Schedule follow-up to address customer concerns',
                'priority': 'urgent',
                'due_date': 'within_24_hours'
            })
        
        return actions
    
    def _calculate_buyer_engagement(self, call_data: ProcessedCallData) -> float:
        """Calculate buyer engagement score."""
        score = 0.5  # Base score
        
        # Adjust based on talk ratio
        if call_data.talk_ratio:
            if 0.4 <= call_data.talk_ratio <= 0.6:
                score += 0.2
            else:
                score -= 0.1
        
        # Adjust based on sentiment
        if call_data.sentiment_score:
            score += (call_data.sentiment_score - 0.5) * 0.3
        
        return max(0.0, min(1.0, score))
    
    def _calculate_closing_probability(self, call_data: ProcessedCallData) -> float:
        """Calculate probability of closing the deal."""
        probability = 0.3  # Base probability
        
        # Increase for positive indicators
        if call_data.next_steps:
            probability += 0.2
        
        if call_data.sentiment_score and call_data.sentiment_score > 0.7:
            probability += 0.2
        
        # Check for buying signals
        buying_signals = ['timeline', 'budget', 'decision', 'implementation']
        if any(signal in str(call_data.insights).lower() for signal in buying_signals):
            probability += 0.2
        
        return min(0.95, probability)
    
    def _extract_performance_metrics(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Extract performance metrics from call."""
        return {
            'call_duration': call_data.duration_seconds,
            'participant_count': len(call_data.participants),
            'insight_count': len(call_data.insights),
            'action_item_count': len(call_data.action_items),
            'sentiment_score': call_data.sentiment_score or 0.5,
            'engagement_score': self._calculate_buyer_engagement(call_data)
        }
    
    def _generate_trend_data(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Generate trend analysis data."""
        return [
            {
                'metric': 'sentiment',
                'value': call_data.sentiment_score or 0.5,
                'trend': 'stable',  # Would compare with historical data
                'significance': 'medium'
            },
            {
                'metric': 'engagement',
                'value': self._calculate_buyer_engagement(call_data),
                'trend': 'increasing',
                'significance': 'high'
            }
        ]
    
    def _create_benchmark_comparisons(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Create benchmark comparisons."""
        return {
            'duration': {
                'actual': call_data.duration_seconds,
                'benchmark': 1800,  # 30 minutes
                'performance': 'above' if call_data.duration_seconds > 1800 else 'below'
            },
            'engagement': {
                'actual': self._calculate_buyer_engagement(call_data),
                'benchmark': 0.7,
                'performance': 'meeting' if self._calculate_buyer_engagement(call_data) >= 0.7 else 'below'
            }
        }
    
    def _categorize_insights(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Categorize insights by type."""
        categories = set()
        for insight in insights:
            insight_type = insight.get('type', 'general')
            categories.add(insight_type)
        return list(categories)
    
    def _generate_recommendations(self, call_data: ProcessedCallData) -> List[Dict[str, Any]]:
        """Generate actionable business recommendations."""
        recommendations = []
        
        # Recommendation based on sentiment
        if call_data.sentiment_score and call_data.sentiment_score < 0.5:
            recommendations.append({
                'type': 'customer_satisfaction',
                'recommendation': 'Implement customer recovery strategy',
                'priority': 'high',
                'expected_impact': 'Prevent churn risk'
            })
        
        # Recommendation based on engagement
        if not call_data.next_steps:
            recommendations.append({
                'type': 'sales_process',
                'recommendation': 'Strengthen call-to-action and next steps process',
                'priority': 'medium',
                'expected_impact': 'Improve conversion rates'
            })
        
        return recommendations
    
    def _calculate_team_impact(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Calculate impact on team performance."""
        return {
            'performance_contribution': 'positive' if call_data.sentiment_score and call_data.sentiment_score > 0.6 else 'neutral',
            'learning_opportunities': len(self._identify_coaching_opportunities(call_data)),
            'best_practices_demonstrated': len([i for i in call_data.insights if 'success' in str(i).lower()])
        }
    
    def _extract_market_intelligence(self, call_data: ProcessedCallData) -> Dict[str, Any]:
        """Extract market intelligence from call."""
        return {
            'competitor_mentions': self._extract_competitive_mentions(call_data.insights),
            'market_trends': [i for i in call_data.insights if 'trend' in str(i).lower()],
            'customer_needs': [i for i in call_data.insights if 'need' in str(i).lower() or 'requirement' in str(i).lower()]
        }
    
    def _extract_strategic_insights(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract strategic insights for executives."""
        insights = []
        
        # Extract from event data
        if 'insights' in event_data:
            for insight in event_data['insights']:
                if insight.get('strategic_value', False):
                    insights.append({
                        'type': 'strategic',
                        'description': insight.get('description'),
                        'impact': insight.get('impact', 'medium'),
                        'action_required': insight.get('action_required', False)
                    })
        
        return insights
    
    def _assess_risks(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks from event data."""
        risks = {
            'overall_risk_level': 'medium',
            'risk_factors': [],
            'mitigation_strategies': []
        }
        
        # Check for risk indicators
        if event_data.get('sentiment_score', 0.5) < 0.3:
            risks['risk_factors'].append('Low customer satisfaction')
            risks['mitigation_strategies'].append('Immediate customer engagement required')
            risks['overall_risk_level'] = 'high'
        
        return risks
    
    def _analyze_opportunities(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business opportunities."""
        return {
            'opportunity_score': 0.7,
            'opportunity_types': ['upsell', 'cross_sell', 'renewal'],
            'recommended_actions': ['Schedule product expansion discussion'],
            'estimated_value': 'high'
        }
    
    def _extract_competitive_intel(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitive intelligence."""
        return {
            'competitor_activity': event_data.get('competitor_mentions', []),
            'competitive_advantages': ['Superior feature set', 'Better pricing model'],
            'competitive_risks': ['New market entrant mentioned'],
            'recommended_positioning': 'Emphasize unique value proposition'
        }
    
    def _generate_executive_summary(self, event_data: Dict[str, Any]) -> str:
        """Generate executive summary."""
        return f"Strategic opportunity identified with {event_data.get('priority', 'medium')} priority. " \
               f"Key factors include market positioning and customer engagement metrics. " \
               f"Immediate action recommended to capitalize on opportunity window."
    
    def _generate_executive_actions(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate executive-level actions."""
        return [
            {
                'action': 'strategic_review',
                'description': 'Review strategic implications with leadership team',
                'priority': 'high',
                'owner': 'executive_team',
                'timeline': 'this_week'
            }
        ]
    
    def _assess_impact(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business impact."""
        return {
            'revenue_impact': 'positive',
            'customer_impact': 'neutral',
            'operational_impact': 'minimal',
            'strategic_impact': 'significant'
        }


class AgentWorkflowOrchestrator:
    """
    Orchestrates multi-agent workflows triggered by Gong events.
    """
    
    def __init__(self, agno_bridge: AgnoMCPBridge):
        self.agno_bridge = agno_bridge
        self.logger = logger.bind(component="agent_workflow_orchestrator")
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    async def orchestrate_call_analysis_workflow(
        self,
        call_data: ProcessedCallData,
        transformed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Orchestrate multi-agent workflow for call analysis."""
        workflow_id = str(uuid4())
        self.active_workflows[workflow_id] = {
            'status': WorkflowStatus.IN_PROGRESS,
            'started_at': datetime.utcnow(),
            'call_id': call_data.call_id
        }
        
        results = {
            'workflow_id': workflow_id,
            'call_id': call_data.call_id,
            'agent_results': {},
            'consolidated_insights': [],
            'recommended_actions': []
        }
        
        try:
            # Step 1: CallAnalysisAgent - analyze conversation
            call_analysis_result = await self._route_to_agent(
                'call_analysis',
                transformed_data['call_analysis'],
                context={'step': 1, 'workflow_id': workflow_id}
            )
            results['agent_results']['call_analysis'] = call_analysis_result
            
            # Step 2: SalesIntelligenceAgent - extract sales insights
            sales_result = await self._route_to_agent(
                'sales_intelligence',
                transformed_data['sales_intelligence'],
                context={
                    'step': 2,
                    'workflow_id': workflow_id,
                    'call_analysis': call_analysis_result
                }
            )
            results['agent_results']['sales_intelligence'] = sales_result
            
            # Step 3: BusinessIntelligenceAgent - generate metrics
            business_result = await self._route_to_agent(
                'business_intelligence',
                transformed_data['business_intelligence'],
                context={
                    'step': 3,
                    'workflow_id': workflow_id,
                    'previous_results': [call_analysis_result, sales_result]
                }
            )
            results['agent_results']['business_intelligence'] = business_result
            
            # Step 4: Consolidate results
            results['consolidated_insights'] = self._consolidate_insights(
                call_analysis_result,
                sales_result,
                business_result
            )
            
            # Step 5: Generate consolidated actions
            results['recommended_actions'] = self._consolidate_actions(
                call_analysis_result,
                sales_result,
                business_result
            )
            
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.COMPLETED
            self.active_workflows[workflow_id]['completed_at'] = datetime.utcnow()
            
        except Exception as e:
            self.logger.error("Workflow orchestration failed",
                            workflow_id=workflow_id,
                            error=str(e))
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.FAILED
            self.active_workflows[workflow_id]['error'] = str(e)
            results['error'] = str(e)
        
        return results
    
    async def orchestrate_insight_workflow(
        self,
        insight_data: Dict[str, Any],
        transformed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Orchestrate workflow for detected insights."""
        workflow_id = str(uuid4())
        insight_type = insight_data.get('insight_type', 'general')
        
        self.active_workflows[workflow_id] = {
            'status': WorkflowStatus.IN_PROGRESS,
            'started_at': datetime.utcnow(),
            'insight_type': insight_type
        }
        
        results = {
            'workflow_id': workflow_id,
            'insight_type': insight_type,
            'agent_results': {},
            'executive_summary': '',
            'recommended_actions': []
        }
        
        try:
            # Route to appropriate specialist agents based on insight type
            if insight_type in ['competitor_mention', 'churn_risk', 'upsell_opportunity']:
                # Route to ExecutiveIntelligenceAgent for strategic insights
                exec_result = await self._route_to_agent(
                    'executive_intelligence',
                    transformed_data['executive_intelligence'],
                    context={'workflow_id': workflow_id, 'insight_type': insight_type}
                )
                results['agent_results']['executive_intelligence'] = exec_result
                results['executive_summary'] = exec_result.get('content', '')
            
            # Generate consolidated recommendations
            results['recommended_actions'] = self._generate_insight_actions(insight_data, results)
            
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.COMPLETED
            
        except Exception as e:
            self.logger.error("Insight workflow failed", workflow_id=workflow_id, error=str(e))
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.FAILED
            results['error'] = str(e)
        
        return results
    
    async def orchestrate_action_workflow(
        self,
        action_data: Dict[str, Any],
        transformed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Orchestrate workflow for required actions."""
        workflow_id = str(uuid4())
        action_type = action_data.get('action_type', 'general')
        
        self.active_workflows[workflow_id] = {
            'status': WorkflowStatus.IN_PROGRESS,
            'started_at': datetime.utcnow(),
            'action_type': action_type
        }
        
        results = {
            'workflow_id': workflow_id,
            'action_type': action_type,
            'agent_results': {},
            'task_assignment': None,
            'completion_tracking': []
        }
        
        try:
            # Assign action to best-suited agent
            general_result = await self._route_to_agent(
                'general_intelligence',
                transformed_data['general_intelligence'],
                context={
                    'workflow_id': workflow_id,
                    'action_type': action_type,
                    'assigned_to': action_data.get('assigned_to')
                }
            )
            results['agent_results']['general_intelligence'] = general_result
            
            # Create task assignment
            results['task_assignment'] = {
                'agent': 'general_intelligence',
                'task_id': workflow_id,
                'status': 'assigned',
                'estimated_completion': general_result.get('metadata', {}).get('estimated_completion')
            }
            
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.COMPLETED
            
        except Exception as e:
            self.logger.error("Action workflow failed", workflow_id=workflow_id, error=str(e))
            self.active_workflows[workflow_id]['status'] = WorkflowStatus.FAILED
            results['error'] = str(e)
        
        return results
    
    async def _route_to_agent(
        self,
        agent_type: str,
        data: Any,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route data to agent using existing AgnoMCPBridge."""
        # Convert Pydantic model to dict if necessary
        if hasattr(data, 'dict'):
            data_dict = data.dict()
        else:
            data_dict = data
        
        request = {
            'query': self._generate_agent_query(agent_type, data_dict),
            'context': {
                'data_source': 'gong_webhook',
                'data_type': agent_type,
                'priority': context.get('priority', 'medium'),
                'gong_data': data_dict,
                **context
            }
        }
        
        # Use existing AgnoMCPBridge routing
        response = await self.agno_bridge.route_to_agent(agent_type, request)
        return response
    
    def _generate_agent_query(self, agent_type: str, data: Dict[str, Any]) -> str:
        """Generate appropriate query for agent based on type and data."""
        queries = {
            'call_analysis': f"Analyze this Gong call with ID {data.get('call_id')} focusing on conversation flow, sentiment, and coaching opportunities.",
            'sales_intelligence': f"Extract sales insights from call {data.get('call_id')} including deal progression, revenue signals, and next best actions.",
            'business_intelligence': f"Generate business intelligence metrics and recommendations for call {data.get('call_id')}.",
            'executive_intelligence': f"Provide executive-level strategic analysis for event {data.get('event_id')}.",
            'general_intelligence': f"Process task {data.get('task_type')} with details: {data.get('task_details')}"
        }
        
        return queries.get(agent_type, "Process this Gong data and provide insights.")
    
    def _consolidate_insights(self, *agent_results) -> List[Dict[str, Any]]:
        """Consolidate insights from multiple agent results."""
        consolidated = []
        
        for result in agent_results:
            if result and 'content' in result:
                # Extract insights from agent response
                consolidated.append({
                    'agent': result.get('agent_type'),
                    'insight': result.get('content'),
                    'confidence': result.get('confidence', 0.5),
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return consolidated
    
    def _consolidate_actions(self, *agent_results) -> List[Dict[str, Any]]:
        """Consolidate recommended actions from multiple agents."""
        actions = []
        action_set = set()  # To avoid duplicates
        
        for result in agent_results:
            if result and 'metadata' in result:
                agent_actions = result.get('metadata', {}).get('recommended_actions', [])
                for action in agent_actions:
                    action_key = f"{action.get('type')}:{action.get('description')}"
                    if action_key not in action_set:
                        action_set.add(action_key)
                        actions.append({
                            **action,
                            'source_agent': result.get('agent_type'),
                            'confidence': result.get('confidence', 0.5)
                        })
        
        # Sort by priority
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        actions.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 2))
        
        return actions
    
    def _generate_insight_actions(
        self,
        insight_data: Dict[str, Any],
        results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actions based on insight type and results."""
        actions = []
        insight_type = insight_data.get('insight_type')
        
        if insight_type == 'competitor_mention':
            actions.append({
                'action': 'competitive_analysis',
                'description': 'Conduct detailed competitive analysis and positioning',
                'priority': 'high',
                'owner': 'sales_intelligence',
                'due_date': 'within_24_hours'
            })
        elif insight_type == 'churn_risk':
            actions.append({
                'action': 'customer_retention',
                'description': 'Initiate customer retention protocol',
                'priority': 'urgent',
                'owner': 'customer_success',
                'due_date': 'immediate'
            })
        elif insight_type == 'upsell_opportunity':
            actions.append({
                'action': 'upsell_engagement',
                'description': 'Schedule upsell discussion with customer',
                'priority': 'high',
                'owner': 'sales_team',
                'due_date': 'within_week'
            })
        
        return actions


class ConversationIntelligenceUpdater:
    """Provides real-time conversation intelligence updates."""
    
    def __init__(self, redis_client: RedisNotificationClient):
        self.redis_client = redis_client
        self.logger = logger.bind(component="conversation_intelligence_updater")
    
    async def update_call_intelligence(
        self,
        call_id: str,
        agent_insights: Dict[str, Any]
    ):
        """Update call record with agent insights."""
        update_data = {
            'call_id': call_id,
            'agent_insights': agent_insights,
            'updated_at': datetime.utcnow().isoformat(),
            'insight_count': len(agent_insights.get('consolidated_insights', [])),
            'action_count': len(agent_insights.get('recommended_actions', []))
        }
        
        # Send update notification
        await self.redis_client.notify_insight_detected(
            webhook_id=f"update_{call_id}",
            insight_type='agent_analysis_complete',
            insight_data=update_data,
            priority=NotificationPriority.MEDIUM
        )
        
        self.logger.info("Call intelligence updated",
                        call_id=call_id,
                        insights=update_data['insight_count'])
    
    async def update_conversation_trends(self, trend_data: Dict[str, Any]):
        """Update trend analysis."""
        # Publish trend update
        await self.redis_client.redis.publish(
            "sophia:gong:trends",
            json.dumps({
                'event_type': 'trend_update',
                'timestamp': datetime.utcnow().isoformat(),
                'data': trend_data
            })
        )


class GongAgentIntegrationConfig(BaseModel):
    """Configuration for Gong-Agent integration."""
    
    # Agent assignment rules
    agent_assignment_rules: Dict[str, List[str]] = {
        'competitor_mention': ['call_analysis', 'sales_intelligence'],
        'churn_risk': ['call_analysis', 'executive_intelligence'],
        'upsell_opportunity': ['sales_intelligence', 'business_intelligence']
    }
    
    # Workflow orchestration settings
    max_concurrent_workflows: int = 10
    workflow_timeout_seconds: int = 300
    agent_response_timeout_seconds: int = 60
    
    # Performance settings
    agent_pool_size: int = 5
    max_retry_attempts: int = 3
    
    # Agent-specific channels
    agent_channels: Dict[str, str] = {
        'call_analysis_agent': 'sophia:agents:call_analysis:tasks',
        'sales_intelligence_agent': 'sophia:agents:sales_intelligence:tasks',
        'business_intelligence_agent': 'sophia:agents:business_intelligence:tasks',
        'executive_intelligence_agent': 'sophia:agents:executive_intelligence:tasks',
        'general_intelligence_agent': 'sophia:agents:general_intelligence:tasks'
    }
    
    # Agent response channels
    agent_response_channels: Dict[str, str] = {
        'agent_responses': 'sophia:agents:responses',
        'agent_actions': 'sophia:agents:actions',
        'agent_coordination': 'sophia:agents:coordination'
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class GongAgentIntegrationManager:
    """
    Central orchestrator for Gong-Agent integration.
    Bridges existing Gong webhook system with Sophia agent infrastructure.
    """
    
    def __init__(
        self,
        agno_bridge: AgnoMCPBridge,
        redis_client: RedisNotificationClient,
        config: Optional[GongAgentIntegrationConfig] = None
    ):
        self.agno_bridge = agno_bridge
        self.redis_client = redis_client
        self.config = config or GongAgentIntegrationConfig()
        self.logger = logger.bind(component="gong_agent_integration_manager")
        
        # Initialize components
        self.data_transformer = AgentDataTransformer()
        self.workflow_orchestrator = AgentWorkflowOrchestrator(agno_bridge)
        self.intelligence_updater = ConversationIntelligenceUpdater(redis_client)
        
        # Integration registry
        self.integration_registry = IntegrationRegistry()
        
        # Subscription tasks
        self._subscription_tasks: List[asyncio.Task] = []
        
        # Metrics
        self.metrics = {
            'calls_processed': 0,
            'insights_detected': 0,
            'actions_created': 0,
            'workflows_completed': 0,
            'errors': 0
        }
    
    async def initialize(self):
        """Initialize the integration manager."""
        self.logger.info("Initializing Gong-Agent Integration Manager")
        
        # Initialize AgnoMCPBridge if not already initialized
        await self.agno_bridge.initialize()
        
        # Set up Redis subscriptions
        await self._setup_redis_subscriptions()
        
        # Register with integration registry
        await self.integration_registry.register("gong_agent_integration", {
            'type': 'bridge',
            'source': 'gong_webhooks',
            'target': 'sophia_agents',
            'status': 'active'
        })
        
        self.logger.info("Gong-Agent Integration Manager initialized successfully")
    
    async def _setup_redis_subscriptions(self):
        """Subscribe to existing Gong notification channels."""
        # Subscribe to call notifications
        call_task = asyncio.create_task(
            self.redis_client.subscribe_to_channel(
                "sophia:gong:calls",
                self.handle_call_processed
            )
        )
        self._subscription_tasks.append(call_task)
        
        # Subscribe to insight notifications
        insight_task = asyncio.create_task(
            self.redis_client.subscribe_to_channel(
                "sophia:gong:insights",
                self.handle_insight_detected
            )
        )
        self._subscription_tasks.append(insight_task)
        
        # Subscribe to action notifications
        action_task = asyncio.create_task(
            self.redis_client.subscribe_to_channel(
                "sophia:gong:actions",
                self.handle_action_required
            )
        )
        self._subscription_tasks.append(action_task)
        
        # Subscribe to agent response channel for bidirectional communication
        response_task = asyncio.create_task(
            self.redis_client.subscribe_to_channel(
                self.config.agent_response_channels['agent_responses'],
                self.handle_agent_response
            )
        )
        self._subscription_tasks.append(response_task)
        
        self.logger.info("Redis subscriptions established",
                        channels=4)
    
    async def handle_call_processed(self, notification_data: Dict[str, Any]):
        """Handle processed call notifications from Gong webhooks."""
        try:
            self.metrics['calls_processed'] += 1
            
            # Extract call data
            call_data = ProcessedCallData(**notification_data.get('data', {}))
            priority = notification_data.get('priority', 'medium')
            
            self.logger.info("Processing call notification",
                            call_id=call_data.call_id,
                            priority=priority)
            
            # Transform data for each agent type
            transformed_data = {
                'call_analysis': await self.data_transformer.transform_for_call_analysis(call_data),
                'sales_intelligence': await self.data_transformer.transform_for_sales_intelligence(call_data),
                'business_intelligence': await self.data_transformer.transform_for_business_intelligence(call_data)
            }
            
            # Orchestrate multi-agent workflow
            workflow_results = await self.workflow_orchestrator.orchestrate_call_analysis_workflow(
                call_data,
                transformed_data
            )
            
            # Update conversation intelligence
            await self.intelligence_updater.update_call_intelligence(
                call_data.call_id,
                workflow_results
            )
            
            self.metrics['workflows_completed'] += 1
            
            self.logger.info("Call processing completed",
                            call_id=call_data.call_id,
                            workflow_id=workflow_results.get('workflow_id'))
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error("Error processing call notification",
                            error=str(e),
                            notification_data=notification_data)
            
            # Send error notification
            await self.redis_client.notify_processing_error(
                webhook_id=notification_data.get('data', {}).get('webhook_id', 'unknown'),
                error_type='call_processing_error',
                error_message=str(e),
                error_details={'notification_data': notification_data}
            )
    
    async def handle_insight_detected(self, notification_data: Dict[str, Any]):
        """Handle detected insight notifications."""
        try:
            self.metrics['insights_detected'] += 1
            
            insight_data = notification_data.get('data', {})
            insight_type = notification_data.get('insight_type', 'general')
            
            self.logger.info("Processing insight notification",
                            insight_type=insight_type)
            
            # Transform for executive intelligence
            transformed_data = {
                'executive_intelligence': await self.data_transformer.transform_for_executive_intelligence(insight_data)
            }
            
            # Orchestrate insight workflow
            workflow_results = await self.workflow_orchestrator.orchestrate_insight_workflow(
                insight_data,
                transformed_data
            )
            
            # Send consolidated recommendations to action channel
            if workflow_results.get('recommended_actions'):
                for action in workflow_results['recommended_actions']:
                    await self.redis_client.notify_action_required(
                        action_type=action.get('action', 'follow_up'),
                        action_data=action,
                        assigned_to=action.get('owner')
                    )
            
            self.logger.info("Insight processing completed",
                            insight_type=insight_type,
                            actions_generated=len(workflow_results.get('recommended_actions', [])))
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error("Error processing insight notification",
                            error=str(e),
                            notification_data=notification_data)
    
    async def handle_action_required(self, notification_data: Dict[str, Any]):
        """Handle action required notifications."""
        try:
            self.metrics['actions_created'] += 1
            
            action_data = notification_data.get('data', {})
            action_type = notification_data.get('action_type', 'general')
            
            self.logger.info("Processing action notification",
                            action_type=action_type)
            
            # Transform for general intelligence agent
            transformed_data = {
                'general_intelligence': await self.data_transformer.transform_for_general_intelligence(action_data)
            }
            
            # Orchestrate action workflow
            workflow_results = await self.workflow_orchestrator.orchestrate_action_workflow(
                action_data,
                transformed_data
            )
            
            self.logger.info("Action processing completed",
                            action_type=action_type,
                            task_id=workflow_results.get('workflow_id'))
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.logger.error("Error processing action notification",
                            error=str(e),
                            notification_data=notification_data)
    
    async def handle_agent_response(self, response_data: Dict[str, Any]):
        """Handle responses from agents for bidirectional communication."""
        try:
            agent_type = response_data.get('agent_type')
            original_event = response_data.get('original_event')
            recommendations = response_data.get('recommendations', [])
            
            self.logger.info("Processing agent response",
                            agent_type=agent_type,
                            recommendation_count=len(recommendations))
            
            # Process agent recommendations
            for recommendation in recommendations:
                if recommendation.get('type') == 'follow_up_workflow':
                    # Trigger follow-up workflow
                    await self._trigger_follow_up_workflow(recommendation)
                elif recommendation.get('type') == 'data_update':
                    # Update Gong data with agent insights
                    await self._update_gong_data(recommendation)
                elif recommendation.get('type') == 'notification':
                    # Send notification to relevant parties
                    await self._send_notification(recommendation)
            
            # Update metrics
            await self._update_agent_metrics(agent_type, response_data)
            
        except Exception as e:
            self.logger.error("Error processing agent response",
                            error=str(e),
                            response_data=response_data)
    
    async def _trigger_follow_up_workflow(self, recommendation: Dict[str, Any]):
        """Trigger a follow-up workflow based on agent recommendation."""
        workflow_type = recommendation.get('workflow_type')
        workflow_data = recommendation.get('workflow_data', {})
        
        # Create synthetic event to trigger workflow
        if workflow_type == 'deep_analysis':
            await self.handle_insight_detected({
                'event_type': NotificationType.INSIGHT_DETECTED,
                'insight_type': 'agent_requested_analysis',
                'data': workflow_data
            })
    
    async def _update_gong_data(self, recommendation: Dict[str, Any]):
        """Update Gong data based on agent recommendation."""
        update_type = recommendation.get('update_type')
        update_data = recommendation.get('update_data', {})
        
        # Send update notification
        await self.redis_client.notify_insight_detected(
            webhook_id=f"agent_update_{datetime.utcnow().timestamp()}",
            insight_type='agent_data_enrichment',
            insight_data=update_data,
            priority=NotificationPriority.LOW
        )
    
    async def _send_notification(self, recommendation: Dict[str, Any]):
        """Send notification based on agent recommendation."""
        notification_type = recommendation.get('notification_type')
        recipients = recommendation.get('recipients', [])
        message = recommendation.get('message', '')
        
        # Route to appropriate notification channel
        await self.redis_client.redis.publish(
            "sophia:notifications:outbound",
            json.dumps({
                'type': notification_type,
                'recipients': recipients,
                'message': message,
                'source': 'gong_agent_integration',
                'timestamp': datetime.utcnow().isoformat()
            })
        )
    
    async def _update_agent_metrics(self, agent_type: str, response_data: Dict[str, Any]):
        """Update metrics for agent performance tracking."""
        metrics_data = {
            'agent_type': agent_type,
            'response_time': response_data.get('response_time_ms', 0),
            'confidence': response_data.get('confidence', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.redis_client.redis.publish(
            "sophia:metrics:agents",
            json.dumps(metrics_data)
        )
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current status of the integration."""
        return {
            'status': 'active',
            'metrics': self.metrics,
            'active_subscriptions': len(self._subscription_tasks),
            'active_workflows': len(self.workflow_orchestrator.active_workflows),
            'agno_bridge_status': await self.agno_bridge.get_performance_metrics()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the integration manager."""
        self.logger.info("Shutting down Gong-Agent Integration Manager")
        
        # Cancel subscription tasks
        for task in self._subscription_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._subscription_tasks, return_exceptions=True)
        
        # Shutdown components
        await self.agno_bridge.shutdown()
        
        self.logger.info("Gong-Agent Integration Manager shutdown complete")
