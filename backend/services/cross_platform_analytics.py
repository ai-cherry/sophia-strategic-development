#!/usr/bin/env python3
"""
Cross-Platform Analytics Engine for Sophia AI - SIMPLIFIED VERSION
==================================================================
Advanced analytics correlating data across Gong, Asana, Notion, Linear, and Pay Ready
(Without sklearn dependencies to avoid compatibility issues)
"""

import asyncio
import json
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os
import sys
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/sophia_analytics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsInsight:
    """Structured analytics insight"""
    type: str
    title: str
    description: str
    confidence: float
    data_points: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class CrossPlatformCorrelation:
    """Cross-platform data correlation"""
    platforms: List[str]
    correlation_type: str
    strength: float
    description: str
    examples: List[Dict[str, Any]]

class CrossPlatformAnalytics:
    """Advanced cross-platform analytics engine (simplified)"""
    
    def __init__(self):
        self.insights_cache = []
        self.correlation_cache = []
        self.analytics_history = []
        
        # Analytics configuration
        self.config = {
            'min_confidence_threshold': 0.6,
            'max_insights_per_type': 5,
            'correlation_threshold': 0.3,
            'text_similarity_threshold': 0.4
        }
        
        logger.info("🧠 Cross-Platform Analytics Engine initialized (simplified)")
    
    def analyze_platform_data(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive analysis of all platform data"""
        logger.info("🔍 Starting comprehensive cross-platform analysis...")
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'data_summary': self._generate_data_summary(platform_data),
            'cross_platform_insights': self._generate_cross_platform_insights(platform_data),
            'correlations': self._find_cross_platform_correlations(platform_data),
            'predictive_analytics': self._generate_predictive_insights(platform_data),
            'business_intelligence': self._generate_business_intelligence(platform_data),
            'recommendations': self._generate_strategic_recommendations(platform_data)
        }
        
        # Cache results
        self.analytics_history.append(analysis_results)
        if len(self.analytics_history) > 100:  # Keep last 100 analyses
            self.analytics_history = self.analytics_history[-100:]
        
        logger.info("✅ Cross-platform analysis complete")
        return analysis_results
    
    def _generate_data_summary(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive data summary across platforms"""
        summary = {
            'total_data_points': 0,
            'platform_health': {},
            'data_freshness': {},
            'coverage_analysis': {}
        }
        
        for platform, data in platform_data.items():
            if platform == 'pay_ready':
                continue
                
            platform_info = data.get('live_platforms', {}).get(platform, {})
            data_count = platform_info.get('data_count', 0)
            status = platform_info.get('status', '')
            
            summary['total_data_points'] += data_count
            summary['platform_health'][platform] = {
                'status': status,
                'data_count': data_count,
                'is_healthy': '✅' in status,
                'contribution_percentage': 0  # Will calculate after total
            }
        
        # Calculate contribution percentages
        total_points = summary['total_data_points']
        if total_points > 0:
            for platform in summary['platform_health']:
                count = summary['platform_health'][platform]['data_count']
                summary['platform_health'][platform]['contribution_percentage'] = (count / total_points) * 100
        
        return summary
    
    def _generate_cross_platform_insights(self, platform_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights by analyzing data across platforms"""
        insights = []
        
        # Insight 1: Platform Integration Health Analysis
        health_insight = self._analyze_platform_integration_health(platform_data)
        if health_insight:
            insights.append(asdict(health_insight))
        
        # Insight 2: Data Volume and Activity Patterns
        activity_insight = self._analyze_activity_patterns(platform_data)
        if activity_insight:
            insights.append(asdict(activity_insight))
        
        # Insight 3: Team Productivity Analysis
        productivity_insight = self._analyze_team_productivity(platform_data)
        if productivity_insight:
            insights.append(asdict(productivity_insight))
        
        # Insight 4: Communication and Collaboration Patterns
        collaboration_insight = self._analyze_collaboration_patterns(platform_data)
        if collaboration_insight:
            insights.append(asdict(collaboration_insight))
        
        # Insight 5: Business Process Optimization
        process_insight = self._analyze_business_processes(platform_data)
        if process_insight:
            insights.append(asdict(process_insight))
        
        return insights
    
    def _analyze_platform_integration_health(self, platform_data: Dict[str, Any]) -> Optional[AnalyticsInsight]:
        """Analyze the health and effectiveness of platform integrations"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        connected_count = sum(1 for p in live_platforms.values() if '✅' in p.get('status', ''))
        total_count = len(live_platforms)
        health_percentage = (connected_count / total_count) * 100 if total_count > 0 else 0
        
        # Determine confidence and recommendations
        if health_percentage >= 80:
            confidence = 0.9
            description = f"Platform integration health is excellent with {connected_count}/{total_count} platforms operational ({health_percentage:.1f}%)"
            recommendations = [
                "Maintain current integration monitoring practices",
                "Consider expanding to additional platforms",
                "Implement automated health checks for proactive maintenance"
            ]
        elif health_percentage >= 60:
            confidence = 0.7
            description = f"Platform integration health is good but has room for improvement with {connected_count}/{total_count} platforms operational ({health_percentage:.1f}%)"
            recommendations = [
                "Focus on fixing disconnected platforms",
                "Implement enhanced error recovery mechanisms",
                "Review API credentials and permissions"
            ]
        else:
            confidence = 0.8
            description = f"Platform integration health needs attention with only {connected_count}/{total_count} platforms operational ({health_percentage:.1f}%)"
            recommendations = [
                "Prioritize fixing critical platform connections",
                "Implement comprehensive monitoring and alerting",
                "Review integration architecture for reliability improvements"
            ]
        
        data_points = [
            {
                'platform': platform,
                'status': info.get('status', ''),
                'data_count': info.get('data_count', 0),
                'has_credentials': info.get('has_credentials', False)
            }
            for platform, info in live_platforms.items()
        ]
        
        return AnalyticsInsight(
            type="platform_health",
            title="Platform Integration Health Analysis",
            description=description,
            confidence=confidence,
            data_points=data_points,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _analyze_activity_patterns(self, platform_data: Dict[str, Any]) -> Optional[AnalyticsInsight]:
        """Analyze activity patterns across platforms"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        activity_data = []
        total_activity = 0
        
        for platform, info in live_platforms.items():
            data_count = info.get('data_count', 0)
            total_activity += data_count
            
            activity_data.append({
                'platform': platform,
                'activity_level': data_count,
                'status': info.get('status', ''),
                'percentage': 0  # Will calculate after total
            })
        
        # Calculate percentages
        if total_activity > 0:
            for item in activity_data:
                item['percentage'] = (item['activity_level'] / total_activity) * 100
        
        # Find most and least active platforms
        active_platforms = [item for item in activity_data if item['activity_level'] > 0]
        if not active_platforms:
            return None
        
        most_active = max(active_platforms, key=lambda x: x['activity_level'])
        least_active = min(active_platforms, key=lambda x: x['activity_level'])
        
        description = f"Activity analysis shows {most_active['platform']} as most active ({most_active['activity_level']} items, {most_active['percentage']:.1f}%) and {least_active['platform']} as least active ({least_active['activity_level']} items, {least_active['percentage']:.1f}%)"
        
        recommendations = [
            f"Leverage high activity in {most_active['platform']} for business insights",
            f"Investigate low activity in {least_active['platform']} - may indicate process gaps",
            "Balance workload distribution across platforms",
            "Implement activity-based performance metrics"
        ]
        
        return AnalyticsInsight(
            type="activity_patterns",
            title="Cross-Platform Activity Analysis",
            description=description,
            confidence=0.8,
            data_points=activity_data,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _analyze_team_productivity(self, platform_data: Dict[str, Any]) -> Optional[AnalyticsInsight]:
        """Analyze team productivity across platforms"""
        pay_ready_data = platform_data.get('data', {}).get('pay_ready', {})
        employee_count = pay_ready_data.get('employees', 0)
        
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        # Calculate productivity metrics
        total_items = sum(info.get('data_count', 0) for info in live_platforms.values())
        items_per_employee = total_items / employee_count if employee_count > 0 else 0
        
        # Analyze by platform type
        productivity_analysis = {
            'communication': live_platforms.get('slack', {}).get('data_count', 0),
            'project_management': live_platforms.get('asana', {}).get('data_count', 0) + live_platforms.get('linear', {}).get('data_count', 0),
            'knowledge_management': live_platforms.get('notion', {}).get('data_count', 0),
            'sales_activity': live_platforms.get('gong', {}).get('data_count', 0)
        }
        
        # Determine productivity level
        if items_per_employee > 0.5:
            productivity_level = "High"
            confidence = 0.8
        elif items_per_employee > 0.2:
            productivity_level = "Moderate"
            confidence = 0.7
        else:
            productivity_level = "Low"
            confidence = 0.6
        
        description = f"Team productivity analysis shows {productivity_level.lower()} activity with {items_per_employee:.2f} items per employee across {employee_count} team members"
        
        recommendations = [
            "Implement productivity tracking dashboards",
            "Identify high-performing teams for best practice sharing",
            "Focus on platforms with low activity for process improvement",
            "Create cross-platform workflow optimization strategies"
        ]
        
        data_points = [
            {
                'metric': 'total_employees',
                'value': employee_count
            },
            {
                'metric': 'total_platform_items',
                'value': total_items
            },
            {
                'metric': 'items_per_employee',
                'value': items_per_employee
            },
            {
                'metric': 'productivity_breakdown',
                'value': productivity_analysis
            }
        ]
        
        return AnalyticsInsight(
            type="team_productivity",
            title="Team Productivity Analysis",
            description=description,
            confidence=confidence,
            data_points=data_points,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _analyze_collaboration_patterns(self, platform_data: Dict[str, Any]) -> Optional[AnalyticsInsight]:
        """Analyze collaboration patterns across platforms"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        collaboration_platforms = {
            'slack': live_platforms.get('slack', {}),
            'asana': live_platforms.get('asana', {}),
            'notion': live_platforms.get('notion', {})
        }
        
        active_collaboration = sum(1 for p in collaboration_platforms.values() if '✅' in p.get('status', ''))
        total_collaboration = len(collaboration_platforms)
        
        collaboration_score = (active_collaboration / total_collaboration) * 100
        
        if collaboration_score >= 80:
            level = "Excellent"
            confidence = 0.9
        elif collaboration_score >= 60:
            level = "Good"
            confidence = 0.7
        else:
            level = "Needs Improvement"
            confidence = 0.8
        
        description = f"Collaboration analysis shows {level.lower()} cross-platform integration with {active_collaboration}/{total_collaboration} collaboration platforms active ({collaboration_score:.1f}%)"
        
        recommendations = [
            "Implement unified collaboration workflows",
            "Create cross-platform notification systems",
            "Establish collaboration best practices",
            "Monitor team communication effectiveness"
        ]
        
        data_points = [
            {
                'platform': platform,
                'status': info.get('status', ''),
                'data_count': info.get('data_count', 0),
                'collaboration_type': self._get_collaboration_type(platform)
            }
            for platform, info in collaboration_platforms.items()
        ]
        
        return AnalyticsInsight(
            type="collaboration_patterns",
            title="Cross-Platform Collaboration Analysis",
            description=description,
            confidence=confidence,
            data_points=data_points,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _analyze_business_processes(self, platform_data: Dict[str, Any]) -> Optional[AnalyticsInsight]:
        """Analyze business process effectiveness"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        process_coverage = {
            'sales_process': '✅' in live_platforms.get('gong', {}).get('status', ''),
            'project_management': '✅' in live_platforms.get('asana', {}).get('status', '') or '✅' in live_platforms.get('linear', {}).get('status', ''),
            'knowledge_management': '✅' in live_platforms.get('notion', {}).get('status', ''),
            'team_communication': '✅' in live_platforms.get('slack', {}).get('status', '')
        }
        
        covered_processes = sum(process_coverage.values())
        total_processes = len(process_coverage)
        coverage_percentage = (covered_processes / total_processes) * 100
        
        if coverage_percentage >= 75:
            effectiveness = "High"
            confidence = 0.9
        elif coverage_percentage >= 50:
            effectiveness = "Moderate"
            confidence = 0.7
        else:
            effectiveness = "Low"
            confidence = 0.8
        
        description = f"Business process analysis shows {effectiveness.lower()} coverage with {covered_processes}/{total_processes} key processes supported ({coverage_percentage:.1f}%)"
        
        recommendations = [
            "Implement end-to-end process monitoring",
            "Create process optimization workflows",
            "Establish process performance metrics",
            "Focus on integrating disconnected processes"
        ]
        
        data_points = [
            {
                'process': process,
                'covered': covered,
                'importance': 'high' if process in ['sales_process', 'project_management'] else 'medium'
            }
            for process, covered in process_coverage.items()
        ]
        
        return AnalyticsInsight(
            type="business_processes",
            title="Business Process Coverage Analysis",
            description=description,
            confidence=confidence,
            data_points=data_points,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _get_collaboration_type(self, platform: str) -> str:
        """Get collaboration type for platform"""
        types = {
            'slack': 'real_time_communication',
            'asana': 'project_collaboration',
            'notion': 'knowledge_sharing',
            'linear': 'development_collaboration',
            'gong': 'sales_collaboration'
        }
        return types.get(platform, 'unknown')
    
    def _find_cross_platform_correlations(self, platform_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find correlations between different platforms"""
        correlations = []
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        # Correlation 1: Project Management and Development Activity
        asana_count = live_platforms.get('asana', {}).get('data_count', 0)
        linear_count = live_platforms.get('linear', {}).get('data_count', 0)
        
        if asana_count > 0 and linear_count > 0:
            correlation_strength = min(asana_count, linear_count) / max(asana_count, linear_count)
            correlations.append(asdict(CrossPlatformCorrelation(
                platforms=['asana', 'linear'],
                correlation_type='project_development_sync',
                strength=correlation_strength,
                description=f"Project management activity ({asana_count} items) correlates with development activity ({linear_count} items)",
                examples=[
                    {'asana_projects': asana_count, 'linear_issues': linear_count, 'sync_ratio': correlation_strength}
                ]
            )))
        
        # Correlation 2: Sales Activity and Team Communication
        gong_count = live_platforms.get('gong', {}).get('data_count', 0)
        slack_count = live_platforms.get('slack', {}).get('data_count', 0)
        
        if gong_count > 0 and slack_count > 0:
            correlation_strength = min(gong_count, slack_count) / max(gong_count, slack_count)
            correlations.append(asdict(CrossPlatformCorrelation(
                platforms=['gong', 'slack'],
                correlation_type='sales_communication_sync',
                strength=correlation_strength,
                description=f"Sales activity ({gong_count} items) correlates with team communication ({slack_count} items)",
                examples=[
                    {'gong_calls': gong_count, 'slack_channels': slack_count, 'communication_ratio': correlation_strength}
                ]
            )))
        
        # Correlation 3: Knowledge Management and Project Activity
        notion_count = live_platforms.get('notion', {}).get('data_count', 0)
        total_project_count = asana_count + linear_count
        
        if notion_count > 0 and total_project_count > 0:
            correlation_strength = min(notion_count, total_project_count) / max(notion_count, total_project_count)
            correlations.append(asdict(CrossPlatformCorrelation(
                platforms=['notion', 'asana', 'linear'],
                correlation_type='knowledge_project_sync',
                strength=correlation_strength,
                description=f"Knowledge management activity ({notion_count} pages) correlates with project activity ({total_project_count} items)",
                examples=[
                    {'notion_pages': notion_count, 'project_items': total_project_count, 'knowledge_ratio': correlation_strength}
                ]
            )))
        
        return correlations
    
    def _generate_predictive_insights(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive analytics insights"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        predictions = {
            'platform_health_forecast': self._predict_platform_health(live_platforms),
            'activity_trends': self._predict_activity_trends(live_platforms),
            'integration_opportunities': self._identify_integration_opportunities(live_platforms)
        }
        
        return predictions
    
    def _predict_platform_health(self, live_platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Predict platform health trends"""
        connected_count = sum(1 for p in live_platforms.values() if '✅' in p.get('status', ''))
        total_count = len(live_platforms)
        current_health = (connected_count / total_count) * 100 if total_count > 0 else 0
        
        # Simple trend prediction based on current state
        if current_health >= 80:
            forecast = "stable_high"
            confidence = 0.8
            description = "Platform health expected to remain high with proper maintenance"
        elif current_health >= 60:
            forecast = "improving"
            confidence = 0.7
            description = "Platform health likely to improve with focused fixes"
        else:
            forecast = "needs_attention"
            confidence = 0.9
            description = "Platform health requires immediate attention to prevent degradation"
        
        return {
            'current_health_percentage': current_health,
            'forecast': forecast,
            'confidence': confidence,
            'description': description,
            'recommended_actions': self._get_health_recommendations(current_health)
        }
    
    def _predict_activity_trends(self, live_platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Predict activity trends across platforms"""
        total_activity = sum(info.get('data_count', 0) for info in live_platforms.values())
        
        # Categorize activity levels
        if total_activity > 20:
            trend = "high_activity"
            description = "High cross-platform activity indicates strong engagement"
        elif total_activity > 10:
            trend = "moderate_activity"
            description = "Moderate activity with room for optimization"
        else:
            trend = "low_activity"
            description = "Low activity may indicate process or adoption issues"
        
        return {
            'current_total_activity': total_activity,
            'trend': trend,
            'description': description,
            'growth_potential': self._calculate_growth_potential(total_activity)
        }
    
    def _identify_integration_opportunities(self, live_platforms: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for better platform integration"""
        opportunities = []
        
        # Check for missing integrations
        platform_status = {name: '✅' in info.get('status', '') for name, info in live_platforms.items()}
        
        if platform_status.get('gong', False) and not platform_status.get('slack', False):
            opportunities.append({
                'type': 'sales_communication_integration',
                'description': 'Integrate Gong sales data with Slack for real-time sales updates',
                'priority': 'high',
                'platforms': ['gong', 'slack']
            })
        
        if platform_status.get('asana', False) and platform_status.get('linear', False):
            opportunities.append({
                'type': 'unified_project_management',
                'description': 'Create unified project management dashboard combining Asana and Linear',
                'priority': 'medium',
                'platforms': ['asana', 'linear']
            })
        
        if platform_status.get('notion', False) and (platform_status.get('asana', False) or platform_status.get('linear', False)):
            opportunities.append({
                'type': 'knowledge_project_sync',
                'description': 'Sync project documentation between Notion and project management tools',
                'priority': 'medium',
                'platforms': ['notion', 'asana', 'linear']
            })
        
        return opportunities
    
    def _get_health_recommendations(self, health_percentage: float) -> List[str]:
        """Get health-based recommendations"""
        if health_percentage >= 80:
            return [
                "Maintain current monitoring practices",
                "Implement proactive health checks",
                "Consider expanding platform integrations"
            ]
        elif health_percentage >= 60:
            return [
                "Focus on fixing disconnected platforms",
                "Implement enhanced error recovery",
                "Review API credentials and permissions"
            ]
        else:
            return [
                "Prioritize critical platform connections",
                "Implement comprehensive monitoring",
                "Review integration architecture"
            ]
    
    def _calculate_growth_potential(self, current_activity: int) -> Dict[str, Any]:
        """Calculate growth potential based on current activity"""
        if current_activity < 10:
            potential = "high"
            multiplier = 3.0
        elif current_activity < 20:
            potential = "medium"
            multiplier = 2.0
        else:
            potential = "low"
            multiplier = 1.5
        
        return {
            'potential_level': potential,
            'estimated_growth_multiplier': multiplier,
            'projected_activity': int(current_activity * multiplier)
        }
    
    def _generate_business_intelligence(self, platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business intelligence insights"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        pay_ready_data = platform_data.get('data', {}).get('pay_ready', {})
        
        bi_insights = {
            'operational_efficiency': self._analyze_operational_efficiency(live_platforms, pay_ready_data),
            'digital_transformation': self._analyze_digital_transformation(live_platforms),
            'roi_analysis': self._analyze_platform_roi(live_platforms),
            'strategic_recommendations': self._generate_strategic_insights(live_platforms, pay_ready_data)
        }
        
        return bi_insights
    
    def _analyze_operational_efficiency(self, live_platforms: Dict[str, Any], pay_ready_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operational efficiency metrics"""
        total_platforms = len(live_platforms)
        active_platforms = sum(1 for p in live_platforms.values() if '✅' in p.get('status', ''))
        employee_count = pay_ready_data.get('employees', 0)
        
        efficiency_score = (active_platforms / total_platforms) * 100 if total_platforms > 0 else 0
        
        return {
            'efficiency_score': efficiency_score,
            'active_platforms': active_platforms,
            'total_platforms': total_platforms,
            'employees': employee_count,
            'platforms_per_employee': total_platforms / employee_count if employee_count > 0 else 0,
            'efficiency_level': 'high' if efficiency_score >= 80 else 'medium' if efficiency_score >= 60 else 'low'
        }
    
    def _analyze_digital_transformation(self, live_platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze digital transformation progress"""
        transformation_areas = {
            'communication': '✅' in live_platforms.get('slack', {}).get('status', ''),
            'project_management': '✅' in live_platforms.get('asana', {}).get('status', '') or '✅' in live_platforms.get('linear', {}).get('status', ''),
            'knowledge_management': '✅' in live_platforms.get('notion', {}).get('status', ''),
            'sales_automation': '✅' in live_platforms.get('gong', {}).get('status', '')
        }
        
        transformation_score = (sum(transformation_areas.values()) / len(transformation_areas)) * 100
        
        return {
            'transformation_score': transformation_score,
            'covered_areas': transformation_areas,
            'maturity_level': 'advanced' if transformation_score >= 75 else 'intermediate' if transformation_score >= 50 else 'basic',
            'next_steps': self._get_transformation_next_steps(transformation_areas)
        }
    
    def _analyze_platform_roi(self, live_platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze return on investment for platforms"""
        platform_values = {
            'gong': {'cost_category': 'high', 'value_score': 8, 'business_impact': 'revenue_generation'},
            'slack': {'cost_category': 'medium', 'value_score': 9, 'business_impact': 'productivity'},
            'asana': {'cost_category': 'medium', 'value_score': 7, 'business_impact': 'project_efficiency'},
            'notion': {'cost_category': 'low', 'value_score': 8, 'business_impact': 'knowledge_management'},
            'linear': {'cost_category': 'medium', 'value_score': 7, 'business_impact': 'development_efficiency'}
        }
        
        roi_analysis = {}
        for platform, info in live_platforms.items():
            if platform in platform_values:
                is_active = '✅' in info.get('status', '')
                data_count = info.get('data_count', 0)
                
                roi_analysis[platform] = {
                    'is_active': is_active,
                    'data_utilization': data_count,
                    'value_score': platform_values[platform]['value_score'],
                    'cost_category': platform_values[platform]['cost_category'],
                    'business_impact': platform_values[platform]['business_impact'],
                    'roi_rating': 'high' if is_active and data_count > 0 else 'low'
                }
        
        return roi_analysis
    
    def _get_transformation_next_steps(self, transformation_areas: Dict[str, bool]) -> List[str]:
        """Get next steps for digital transformation"""
        next_steps = []
        
        if not transformation_areas['communication']:
            next_steps.append("Implement team communication platform (Slack)")
        
        if not transformation_areas['project_management']:
            next_steps.append("Deploy project management solution (Asana/Linear)")
        
        if not transformation_areas['knowledge_management']:
            next_steps.append("Establish knowledge management system (Notion)")
        
        if not transformation_areas['sales_automation']:
            next_steps.append("Implement sales automation and analytics (Gong)")
        
        if all(transformation_areas.values()):
            next_steps.extend([
                "Implement advanced workflow automation",
                "Deploy AI-powered analytics and insights",
                "Create unified business intelligence dashboard"
            ])
        
        return next_steps
    
    def _generate_strategic_recommendations(self, platform_data: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        live_platforms = platform_data.get('data', {}).get('live_platforms', {})
        
        recommendations = []
        
        # Platform-specific recommendations
        connected_count = sum(1 for p in live_platforms.values() if '✅' in p.get('status', ''))
        
        if connected_count < 3:
            recommendations.append("🚨 CRITICAL: Focus on stabilizing core platform integrations before expanding")
        
        if connected_count >= 4:
            recommendations.extend([
                "🚀 OPPORTUNITY: Implement advanced cross-platform workflows",
                "📊 ANALYTICS: Deploy predictive analytics using multi-platform data",
                "🤖 AUTOMATION: Create intelligent automation between platforms"
            ])
        
        # Data-driven recommendations
        total_activity = sum(info.get('data_count', 0) for info in live_platforms.values())
        
        if total_activity > 15:
            recommendations.append("📈 SCALE: High activity indicates readiness for advanced features")
        elif total_activity < 5:
            recommendations.append("🔍 ADOPTION: Focus on increasing platform adoption and usage")
        
        return recommendations
    
    def _generate_strategic_insights(self, live_platforms: Dict[str, Any], pay_ready_data: Dict[str, Any]) -> List[str]:
        """Generate strategic insights for business intelligence"""
        insights = []
        
        connected_count = sum(1 for p in live_platforms.values() if '✅' in p.get('status', ''))
        total_activity = sum(info.get('data_count', 0) for info in live_platforms.values())
        employee_count = pay_ready_data.get('employees', 0)
        
        # Strategic insights based on data
        if connected_count >= 4:
            insights.append("Strong platform integration foundation enables advanced analytics")
        
        if total_activity / employee_count > 0.3:
            insights.append("High per-employee platform activity indicates good digital adoption")
        
        if live_platforms.get('gong', {}).get('data_count', 0) > 0:
            insights.append("Sales data integration provides revenue optimization opportunities")
        
        return insights

# Global analytics instance
analytics_engine = CrossPlatformAnalytics()

def get_comprehensive_analytics(platform_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get comprehensive analytics for platform data"""
    return analytics_engine.analyze_platform_data(platform_data)

def get_analytics_dashboard() -> Dict[str, Any]:
    """Get analytics dashboard data"""
    return {
        'recent_analyses': analytics_engine.analytics_history[-5:],  # Last 5 analyses
        'insights_cache': [asdict(insight) for insight in analytics_engine.insights_cache[-10:]],  # Last 10 insights
        'correlations_cache': [asdict(corr) for corr in analytics_engine.correlation_cache[-10:]],  # Last 10 correlations
        'analytics_config': analytics_engine.config
    }

if __name__ == "__main__":
    # Test the analytics engine
    test_data = {
        'data': {
            'live_platforms': {
                'gong': {'status': '✅ Connected', 'data_count': 5, 'has_credentials': True},
                'slack': {'status': '❌ Error: account_inactive', 'data_count': 0, 'has_credentials': True},
                'asana': {'status': '✅ Connected', 'data_count': 0, 'has_credentials': True},
                'notion': {'status': '✅ Connected', 'data_count': 4, 'has_credentials': True},
                'linear': {'status': '✅ Connected', 'data_count': 10, 'has_credentials': True}
            },
            'pay_ready': {
                'employees': 104,
                'status': '✅ Connected'
            }
        }
    }
    
    results = get_comprehensive_analytics(test_data)
    print(json.dumps(results, indent=2, default=str))

