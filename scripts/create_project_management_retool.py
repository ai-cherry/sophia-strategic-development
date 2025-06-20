#!/usr/bin/env python3
"""Create Project Management Admin Panel in Retool
Generates a comprehensive Retool application configuration for unified project intelligence
"""

import json
from typing import Any, Dict, List


class ProjectManagementRetoolBuilder:
    """Builds Retool configuration for project management admin panel"""

    def __init__(self):
        self.app_name = "Sophia Project Intelligence"
        self.api_base = "{{ environment.SOPHIA_API_URL }}/api/project-management"

    def generate_config(self) -> Dict[str, Any]:
        """Generate complete Retool app configuration"""
        return {
            "name": self.app_name,
            "description": "Unified project intelligence across Linear, GitHub, Asana, and Slack",
            "resources": self._create_resources(),
            "queries": self._create_queries(),
            "components": self._create_components(),
            "globalState": self._create_global_state(),
            "theme": self._create_theme(),
        }

    def _create_resources(self) -> List[Dict[str, Any]]:
        """Create API resources"""
        return [
            {
                "name": "ProjectManagementAPI",
                "type": "restapi",
                "config": {
                    "baseURL": self.api_base,
                    "headers": [
                        {
                            "key": "Authorization",
                            "value": "Bearer {{ current_user.authToken }}",
                        },
                        {"key": "Content-Type", "value": "application/json"},
                    ],
                    "authentication": "bearer",
                    "bearerToken": "{{ environment.SOPHIA_API_KEY }}",
                },
            }
        ]

    def _create_queries(self) -> List[Dict[str, Any]]:
        """Create all API queries"""
        return [
            # Dashboard queries
            {
                "name": "getDashboardSummary",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/dashboard/summary",
                "runOnPageLoad": True,
                "pollingInterval": 60000,  # Refresh every minute
            },
            # OKR queries
            {
                "name": "getOKRAlignment",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/okr/alignment",
                "urlParams": [
                    {"key": "quarter", "value": "{{ quarterSelector.value }}"}
                ],
                "runOnPageLoad": True,
            },
            {
                "name": "updateOKR",
                "resource": "ProjectManagementAPI",
                "type": "POST",
                "url": "/okr/update",
                "body": {
                    "objective_id": "{{ okrUpdateModal.data.objective_id }}",
                    "key_result_id": "{{ okrUpdateModal.data.key_result_id }}",
                    "current_value": "{{ okrValueInput.value }}",
                    "notes": "{{ okrNotesInput.value }}",
                },
                "onSuccess": [
                    "okrUpdateModal.close()",
                    "getOKRAlignment.trigger()",
                    "utils.showNotification({text: 'OKR updated successfully', type: 'success'})",
                ],
            },
            # Blockers queries
            {
                "name": "getBlockers",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/blockers",
                "runOnPageLoad": True,
            },
            # Recommendations queries
            {
                "name": "getRecommendations",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/recommendations",
                "urlParams": [
                    {"key": "focus_area", "value": "{{ focusAreaSelect.value }}"}
                ],
                "runOnPageLoad": True,
            },
            {
                "name": "updateRecommendationStatus",
                "resource": "ProjectManagementAPI",
                "type": "POST",
                "url": "/recommendations/action",
                "body": {
                    "action_id": "{{ currentRecommendation.action_id }}",
                    "status": "{{ actionStatusSelect.value }}",
                    "notes": "{{ actionNotesInput.value }}",
                },
                "onSuccess": [
                    "getRecommendations.trigger()",
                    "utils.showNotification({text: 'Action updated', type: 'success'})",
                ],
            },
            # Project details
            {
                "name": "getProjectDetails",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/projects/{{ selectedProject.id }}",
                "runWhenModelUpdates": ["selectedProject.id"],
            },
            # Team performance
            {
                "name": "getTeamPerformance",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/teams/performance",
                "urlParams": [{"key": "team_name", "value": "{{ teamFilter.value }}"}],
            },
            # Trends
            {
                "name": "getProjectTrends",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/insights/trends",
                "urlParams": [
                    {"key": "days", "value": "{{ trendPeriodSelect.value }}"}
                ],
                "runOnPageLoad": True,
            },
            # Milestones
            {
                "name": "getMilestones",
                "resource": "ProjectManagementAPI",
                "type": "GET",
                "url": "/calendar/milestones",
                "urlParams": [
                    {"key": "start_date", "value": "{{ calendarView.startDate }}"},
                    {"key": "end_date", "value": "{{ calendarView.endDate }}"},
                ],
            },
            # Custom reports
            {
                "name": "generateCustomReport",
                "resource": "ProjectManagementAPI",
                "type": "POST",
                "url": "/reports/custom",
                "body": {
                    "name": "{{ reportNameInput.value }}",
                    "filters": "{{ reportFilters.value }}",
                    "metrics": "{{ selectedMetrics.value }}",
                    "grouping": "{{ groupingSelect.value }}",
                },
            },
        ]

    def _create_components(self) -> Dict[str, Any]:
        """Create UI components"""
        return {
            "root": {
                "type": "frame",
                "sticky": True,
                "children": ["header", "mainTabs"],
            },
            "header": {
                "type": "container",
                "backgroundColor": "#1a1a1a",
                "padding": 16,
                "children": ["titleRow", "statsRow"],
            },
            "titleRow": {
                "type": "container",
                "direction": "row",
                "children": [
                    {
                        "type": "text",
                        "value": "🚀 Project Intelligence Command Center",
                        "size": "h1",
                        "color": "white",
                        "weight": "bold",
                    },
                    {
                        "type": "container",
                        "direction": "row",
                        "align": "right",
                        "children": [
                            {
                                "type": "select",
                                "id": "quarterSelector",
                                "value": "Q1_2024",
                                "options": ["Q1_2024", "Q2_2024", "Q3_2024", "Q4_2024"],
                                "width": 120,
                            },
                            {
                                "type": "button",
                                "text": "🔄 Refresh",
                                "onClick": [
                                    "getDashboardSummary.trigger()",
                                    "getOKRAlignment.trigger()",
                                    "getBlockers.trigger()",
                                ],
                            },
                        ],
                    },
                ],
            },
            "statsRow": {
                "type": "container",
                "direction": "row",
                "gap": 16,
                "children": [
                    self._create_stat_card(
                        "Total Projects",
                        "{{ getDashboardSummary.data.summary.total_projects }}",
                        "📊",
                    ),
                    self._create_stat_card(
                        "On Track",
                        "{{ getDashboardSummary.data.summary.status_breakdown.on_track }}",
                        "✅",
                        "green",
                    ),
                    self._create_stat_card(
                        "At Risk",
                        "{{ getDashboardSummary.data.summary.status_breakdown.at_risk }}",
                        "⚠️",
                        "yellow",
                    ),
                    self._create_stat_card(
                        "Blocked",
                        "{{ getDashboardSummary.data.summary.status_breakdown.blocked }}",
                        "🚫",
                        "red",
                    ),
                    self._create_stat_card(
                        "Portfolio Health",
                        "{{ getDashboardSummary.data.summary.health_score.toFixed(1) }}%",
                        "💪",
                        "blue",
                    ),
                ],
            },
            "mainTabs": {
                "type": "tabs",
                "tabs": [
                    {
                        "name": "Portfolio Overview",
                        "icon": "fas fa-th",
                        "content": self._create_portfolio_tab(),
                    },
                    {
                        "name": "OKR Alignment",
                        "icon": "fas fa-bullseye",
                        "content": self._create_okr_tab(),
                    },
                    {
                        "name": "Blockers & Actions",
                        "icon": "fas fa-exclamation-triangle",
                        "content": self._create_blockers_tab(),
                    },
                    {
                        "name": "Team Performance",
                        "icon": "fas fa-users",
                        "content": self._create_team_tab(),
                    },
                    {
                        "name": "Analytics",
                        "icon": "fas fa-chart-line",
                        "content": self._create_analytics_tab(),
                    },
                ],
            },
        }

    def _create_stat_card(
        self, label: str, value: str, icon: str, color: str = "white"
    ) -> Dict[str, Any]:
        """Create a statistics card"""
        return {
            "type": "statistic",
            "label": label,
            "value": value,
            "prefix": icon,
            "color": color,
            "backgroundColor": "#2a2a2a",
            "borderRadius": 8,
            "padding": 12,
        }

    def _create_portfolio_tab(self) -> Dict[str, Any]:
        """Create portfolio overview tab"""
        return {
            "type": "container",
            "padding": 16,
            "children": [
                {
                    "type": "container",
                    "direction": "row",
                    "marginBottom": 16,
                    "children": [
                        {
                            "type": "text",
                            "value": "Project Portfolio",
                            "size": "h2",
                            "weight": "bold",
                        },
                        {
                            "type": "container",
                            "direction": "row",
                            "align": "right",
                            "gap": 8,
                            "children": [
                                {
                                    "type": "select",
                                    "id": "statusFilter",
                                    "placeholder": "Filter by status",
                                    "options": [
                                        "All",
                                        "on_track",
                                        "at_risk",
                                        "blocked",
                                        "completed",
                                    ],
                                    "value": "All",
                                    "width": 150,
                                },
                                {
                                    "type": "input",
                                    "id": "projectSearch",
                                    "placeholder": "Search projects...",
                                    "icon": "search",
                                    "width": 200,
                                },
                            ],
                        },
                    ],
                },
                {
                    "type": "table",
                    "id": "projectsTable",
                    "data": """{{
                        getDashboardSummary.data.projects
                            .filter(p => statusFilter.value === 'All' || p.status === statusFilter.value)
                            .filter(p => !projectSearch.value || p.name.toLowerCase().includes(projectSearch.value.toLowerCase()))
                    }}""",
                    "columns": [
                        {
                            "key": "name",
                            "label": "Project",
                            "width": 250,
                            "render": """
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span>{{ item }}</span>
                                    <div style="display: flex; gap: 4px;">
                                        {{ currentRow.sources.map(s =>
                                            `<span style="
                                                background: ${s === 'linear' ? '#5E6AD2' :
                                                           s === 'github' ? '#238636' :
                                                           s === 'slack' ? '#4A154B' : '#666'};
                                                color: white;
                                                padding: 2px 6px;
                                                border-radius: 4px;
                                                font-size: 10px;
                                            ">${s}</span>`
                                        ).join('') }}
                                    </div>
                                </div>
                            """,
                        },
                        {
                            "key": "status",
                            "label": "Status",
                            "width": 120,
                            "render": """
                                <span style="
                                    background: {{
                                        item === 'on_track' ? '#10B981' :
                                        item === 'at_risk' ? '#F59E0B' :
                                        item === 'blocked' ? '#EF4444' :
                                        item === 'completed' ? '#6366F1' : '#6B7280'
                                    }};
                                    color: white;
                                    padding: 4px 12px;
                                    border-radius: 16px;
                                    font-size: 12px;
                                ">{{ item.replace('_', ' ').toUpperCase() }}</span>
                            """,
                        },
                        {
                            "key": "metrics.completion",
                            "label": "Progress",
                            "width": 150,
                            "render": """
                                <div style="width: 100%;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                        <span style="font-size: 12px;">{{ item.toFixed(1) }}%</span>
                                    </div>
                                    <div style="background: #E5E7EB; height: 8px; border-radius: 4px; overflow: hidden;">
                                        <div style="
                                            background: {{ item > 80 ? '#10B981' : item > 50 ? '#F59E0B' : '#EF4444' }};
                                            width: {{ item }}%;
                                            height: 100%;
                                            transition: width 0.3s;
                                        "></div>
                                    </div>
                                </div>
                            """,
                        },
                        {
                            "key": "metrics.velocity",
                            "label": "Velocity",
                            "width": 80,
                            "align": "center",
                            "render": "{{ item.toFixed(1) }}",
                        },
                        {
                            "key": "metrics.blocked_items",
                            "label": "Blockers",
                            "width": 80,
                            "align": "center",
                            "render": """
                                <span style="
                                    color: {{ item > 0 ? '#EF4444' : '#10B981' }};
                                    font-weight: {{ item > 0 ? 'bold' : 'normal' }};
                                ">{{ item }}</span>
                            """,
                        },
                        {
                            "key": "okr_alignment",
                            "label": "OKRs",
                            "width": 80,
                            "align": "center",
                            "render": """
                                <span style="
                                    background: {{ item.length > 0 ? '#10B981' : '#6B7280' }};
                                    color: white;
                                    padding: 2px 8px;
                                    border-radius: 12px;
                                    font-size: 12px;
                                ">{{ item.length }}</span>
                            """,
                        },
                    ],
                    "onRowClick": "selectedProject.setValue(currentRow)",
                    "height": 400,
                    "pagination": True,
                    "pageSize": 20,
                },
                # Project details panel
                {
                    "type": "container",
                    "hidden": "{{ !selectedProject.value }}",
                    "marginTop": 24,
                    "backgroundColor": "#f9fafb",
                    "borderRadius": 8,
                    "padding": 16,
                    "children": [
                        {
                            "type": "text",
                            "value": "{{ selectedProject.value.name }} Details",
                            "size": "h3",
                            "weight": "bold",
                            "marginBottom": 16,
                        },
                        {
                            "type": "container",
                            "direction": "row",
                            "gap": 24,
                            "children": [
                                self._create_project_insights_panel(),
                                self._create_project_timeline_panel(),
                                self._create_project_team_panel(),
                            ],
                        },
                    ],
                },
            ],
        }

    def _create_okr_tab(self) -> Dict[str, Any]:
        """Create OKR alignment tab"""
        return {
            "type": "container",
            "padding": 16,
            "children": [
                {
                    "type": "text",
                    "value": "OKR Alignment & Progress",
                    "size": "h2",
                    "weight": "bold",
                    "marginBottom": 24,
                },
                # OKR summary cards
                {
                    "type": "container",
                    "direction": "row",
                    "gap": 16,
                    "marginBottom": 24,
                    "children": [
                        self._create_okr_summary_card(
                            "Total Objectives",
                            "{{ getOKRAlignment.data.summary.total_objectives }}",
                            "🎯",
                        ),
                        self._create_okr_summary_card(
                            "Key Results",
                            "{{ getOKRAlignment.data.summary.total_key_results }}",
                            "📊",
                        ),
                        self._create_okr_summary_card(
                            "At Risk",
                            "{{ getOKRAlignment.data.summary.at_risk_key_results }}",
                            "⚠️",
                            "yellow",
                        ),
                        self._create_okr_summary_card(
                            "Overall Progress",
                            "{{ getOKRAlignment.data.summary.overall_progress.toFixed(1) }}%",
                            "📈",
                            "blue",
                        ),
                    ],
                },
                # OKR tree view
                {
                    "type": "container",
                    "children": """{{
                        getOKRAlignment.data.report.objectives.map(obj => ({
                            type: 'container',
                            marginBottom: 24,
                            backgroundColor: 'white',
                            borderRadius: 8,
                            padding: 16,
                            border: '1px solid #e5e7eb',
                            children: [
                                {
                                    type: 'text',
                                    value: obj.title,
                                    size: 'h3',
                                    weight: 'bold',
                                    marginBottom: 16
                                },
                                {
                                    type: 'container',
                                    children: obj.key_results.map(kr => ({
                                        type: 'container',
                                        marginBottom: 12,
                                        padding: 12,
                                        backgroundColor: '#f9fafb',
                                        borderRadius: 6,
                                        children: [
                                            {
                                                type: 'container',
                                                direction: 'row',
                                                alignItems: 'center',
                                                children: [
                                                    {
                                                        type: 'text',
                                                        value: kr.title,
                                                        weight: 'medium',
                                                        flex: 1
                                                    },
                                                    {
                                                        type: 'button',
                                                        text: 'Update',
                                                        size: 'small',
                                                        onClick: () => {
                                                            okrUpdateModal.data.setValue({
                                                                objective_id: obj.id,
                                                                key_result_id: kr.id,
                                                                current_value: kr.current
                                                            });
                                                            okrUpdateModal.open();
                                                        }
                                                    }
                                                ]
                                            },
                                            {
                                                type: 'container',
                                                direction: 'row',
                                                marginTop: 8,
                                                gap: 16,
                                                children: [
                                                    {
                                                        type: 'text',
                                                        value: `Current: ${kr.current} ${kr.unit}`,
                                                        size: 'small'
                                                    },
                                                    {
                                                        type: 'text',
                                                        value: `Target: ${kr.target} ${kr.unit}`,
                                                        size: 'small'
                                                    },
                                                    {
                                                        type: 'text',
                                                        value: `Progress: ${kr.progress_percentage.toFixed(1)}%`,
                                                        size: 'small',
                                                        color: kr.progress_percentage >= 70 ? 'green' : kr.progress_percentage >= 50 ? 'orange' : 'red'
                                                    }
                                                ]
                                            },
                                            {
                                                type: 'progress',
                                                value: kr.progress_percentage,
                                                max: 100,
                                                color: kr.progress_percentage >= 70 ? 'green' : kr.progress_percentage >= 50 ? 'orange' : 'red',
                                                height: 8,
                                                marginTop: 8
                                            },
                                            kr.contributing_projects.length > 0 ? {
                                                type: 'container',
                                                marginTop: 8,
                                                children: [
                                                    {
                                                        type: 'text',
                                                        value: 'Contributing Projects:',
                                                        size: 'small',
                                                        weight: 'medium'
                                                    },
                                                    {
                                                        type: 'container',
                                                        direction: 'row',
                                                        flexWrap: 'wrap',
                                                        gap: 4,
                                                        marginTop: 4,
                                                        children: kr.contributing_projects.map(p => ({
                                                            type: 'tag',
                                                            text: p.name,
                                                            color: p.status === 'on_track' ? 'green' : p.status === 'at_risk' ? 'orange' : 'red'
                                                        }))
                                                    }
                                                ]
                                            } : null,
                                            kr.risks.length > 0 ? {
                                                type: 'alert',
                                                type: 'warning',
                                                message: kr.risks.join(', '),
                                                marginTop: 8
                                            } : null
                                        ].filter(Boolean)
                                    }))
                                }
                            ]
                        }))
                    }}""",
                },
            ],
        }

    def _create_blockers_tab(self) -> Dict[str, Any]:
        """Create blockers and actions tab"""
        return {
            "type": "container",
            "padding": 16,
            "children": [
                {
                    "type": "container",
                    "direction": "row",
                    "gap": 24,
                    "children": [
                        # Blockers section
                        {
                            "type": "container",
                            "flex": 1,
                            "children": [
                                {
                                    "type": "text",
                                    "value": "🚫 Cross-Project Blockers",
                                    "size": "h3",
                                    "weight": "bold",
                                    "marginBottom": 16,
                                },
                                {
                                    "type": "container",
                                    "children": [
                                        self._create_blocker_summary(),
                                        self._create_blocker_patterns(),
                                        self._create_blocker_resolutions(),
                                    ],
                                },
                            ],
                        },
                        # Recommendations section
                        {
                            "type": "container",
                            "flex": 1,
                            "children": [
                                {
                                    "type": "container",
                                    "direction": "row",
                                    "marginBottom": 16,
                                    "children": [
                                        {
                                            "type": "text",
                                            "value": "💡 Strategic Recommendations",
                                            "size": "h3",
                                            "weight": "bold",
                                            "flex": 1,
                                        },
                                        {
                                            "type": "select",
                                            "id": "focusAreaSelect",
                                            "placeholder": "Focus area",
                                            "options": [
                                                "All",
                                                "OKR Achievement",
                                                "Resource Optimization",
                                                "Risk Mitigation",
                                            ],
                                            "value": "All",
                                            "width": 180,
                                            "onChange": "getRecommendations.trigger()",
                                        },
                                    ],
                                },
                                self._create_recommendations_list(),
                            ],
                        },
                    ],
                }
            ],
        }

    def _create_team_tab(self) -> Dict[str, Any]:
        """Create team performance tab"""
        return {
            "type": "container",
            "padding": 16,
            "children": [
                {
                    "type": "container",
                    "direction": "row",
                    "marginBottom": 24,
                    "children": [
                        {
                            "type": "text",
                            "value": "Team Performance Analytics",
                            "size": "h2",
                            "weight": "bold",
                            "flex": 1,
                        },
                        {
                            "type": "select",
                            "id": "teamFilter",
                            "placeholder": "Select team",
                            "options": "{{ ['All Teams'].concat(Object.keys(getTeamPerformance.data.teams)) }}",
                            "value": "All Teams",
                            "width": 200,
                            "onChange": "getTeamPerformance.trigger()",
                        },
                    ],
                },
                # Team metrics grid
                {
                    "type": "container",
                    "direction": "row",
                    "flexWrap": "wrap",
                    "gap": 16,
                    "children": """{{
                        Object.entries(getTeamPerformance.data.teams).map(([team, metrics]) => ({
                            type: 'container',
                            width: '48%',
                            backgroundColor: 'white',
                            borderRadius: 8,
                            padding: 16,
                            border: '1px solid #e5e7eb',
                            children: [
                                {
                                    type: 'container',
                                    direction: 'row',
                                    marginBottom: 12,
                                    children: [
                                        {
                                            type: 'text',
                                            value: team,
                                            size: 'h4',
                                            weight: 'bold',
                                            flex: 1
                                        },
                                        {
                                            type: 'text',
                                            value: `Health: ${metrics.health_score.toFixed(0)}%`,
                                            color: metrics.health_score >= 80 ? 'green' : metrics.health_score >= 60 ? 'orange' : 'red',
                                            weight: 'medium'
                                        }
                                    ]
                                },
                                {
                                    type: 'container',
                                    direction: 'row',
                                    gap: 16,
                                    children: [
                                        {
                                            type: 'statistic',
                                            label: 'Projects',
                                            value: metrics.project_count,
                                            size: 'small'
                                        },
                                        {
                                            type: 'statistic',
                                            label: 'Avg Velocity',
                                            value: metrics.avg_velocity.toFixed(1),
                                            size: 'small'
                                        },
                                        {
                                            type: 'statistic',
                                            label: 'Blockers',
                                            value: metrics.blocked_items,
                                            color: metrics.blocked_items > 0 ? 'red' : 'green',
                                            size: 'small'
                                        }
                                    ]
                                },
                                {
                                    type: 'container',
                                    marginTop: 12,
                                    children: [
                                        {
                                            type: 'text',
                                            value: 'Sentiment',
                                            size: 'small',
                                            marginBottom: 4
                                        },
                                        {
                                            type: 'progress',
                                            value: metrics.avg_sentiment * 100,
                                            max: 100,
                                            color: metrics.avg_sentiment >= 0.7 ? 'green' : metrics.avg_sentiment >= 0.5 ? 'orange' : 'red',
                                            height: 8
                                        }
                                    ]
                                }
                            ]
                        }))
                    }}""",
                },
            ],
        }

    def _create_analytics_tab(self) -> Dict[str, Any]:
        """Create analytics tab"""
        return {
            "type": "container",
            "padding": 16,
            "children": [
                {
                    "type": "text",
                    "value": "Project Analytics & Insights",
                    "size": "h2",
                    "weight": "bold",
                    "marginBottom": 24,
                },
                # Trend selector
                {
                    "type": "container",
                    "direction": "row",
                    "marginBottom": 24,
                    "children": [
                        {
                            "type": "text",
                            "value": "Trend Period:",
                            "marginRight": 8,
                            "alignSelf": "center",
                        },
                        {
                            "type": "select",
                            "id": "trendPeriodSelect",
                            "options": [
                                {"label": "Last 7 days", "value": 7},
                                {"label": "Last 30 days", "value": 30},
                                {"label": "Last 90 days", "value": 90},
                            ],
                            "value": 30,
                            "width": 150,
                            "onChange": "getProjectTrends.trigger()",
                        },
                    ],
                },
                # Trend cards
                {
                    "type": "container",
                    "direction": "row",
                    "gap": 16,
                    "marginBottom": 24,
                    "children": [
                        self._create_trend_card("Velocity", "velocity_trend"),
                        self._create_trend_card("Blockers", "blocker_trend"),
                        self._create_trend_card("Completion", "completion_trend"),
                        self._create_trend_card(
                            "Team Sentiment", "team_sentiment_trend"
                        ),
                    ],
                },
                # Charts section
                {
                    "type": "container",
                    "direction": "row",
                    "gap": 24,
                    "children": [
                        {
                            "type": "chart",
                            "title": "Project Status Distribution",
                            "chartType": "pie",
                            "data": """{{
                                Object.entries(getDashboardSummary.data.summary.status_breakdown).map(([status, count]) => ({
                                    name: status.replace('_', ' ').toUpperCase(),
                                    value: count,
                                    color: {
                                        'on_track': '#10B981',
                                        'at_risk': '#F59E0B',
                                        'blocked': '#EF4444',
                                        'completed': '#6366F1',
                                        'not_started': '#6B7280'
                                    }[status]
                                }))
                            }}""",
                            "height": 300,
                            "flex": 1,
                        },
                        {
                            "type": "chart",
                            "title": "Team Velocity Comparison",
                            "chartType": "bar",
                            "data": """{{
                                Object.entries(getTeamPerformance.data.teams).map(([team, metrics]) => ({
                                    name: team,
                                    velocity: metrics.avg_velocity,
                                    health: metrics.health_score
                                }))
                            }}""",
                            "xKey": "name",
                            "yKeys": ["velocity"],
                            "height": 300,
                            "flex": 1,
                        },
                    ],
                },
                # Custom report builder
                self._create_custom_report_builder(),
            ],
        }

    def _create_project_insights_panel(self) -> Dict[str, Any]:
        """Create project insights panel"""
        return {
            "type": "container",
            "flex": 1,
            "children": [
                {
                    "type": "text",
                    "value": "Insights",
                    "weight": "medium",
                    "marginBottom": 8,
                },
                {
                    "type": "container",
                    "children": """{{
                        selectedProject.value.insights.map(insight => ({
                            type: 'text',
                            value: `• ${insight}`,
                            size: 'small',
                            marginBottom: 4
                        }))
                    }}""",
                },
            ],
        }

    def _create_project_timeline_panel(self) -> Dict[str, Any]:
        """Create project timeline panel"""
        return {
            "type": "container",
            "flex": 1,
            "children": [
                {
                    "type": "text",
                    "value": "Recent Activity",
                    "weight": "medium",
                    "marginBottom": 8,
                },
                {
                    "type": "timeline",
                    "data": "{{ getProjectDetails.data.detailed_timeline }}",
                    "height": 200,
                },
            ],
        }

    def _create_project_team_panel(self) -> Dict[str, Any]:
        """Create project team panel"""
        return {
            "type": "container",
            "flex": 1,
            "children": [
                {
                    "type": "text",
                    "value": "Team Members",
                    "weight": "medium",
                    "marginBottom": 8,
                },
                {
                    "type": "container",
                    "children": """{{
                        getProjectDetails.data.team_members.map(member => ({
                            type: 'container',
                            direction: 'row',
                            alignItems: 'center',
                            marginBottom: 8,
                            children: [
                                {
                                    type: 'avatar',
                                    src: member.avatar,
                                    name: member.name,
                                    size: 32
                                },
                                {
                                    type: 'text',
                                    value: `${member.name} (${member.issue_count} issues)`,
                                    size: 'small',
                                    marginLeft: 8
                                }
                            ]
                        }))
                    }}""",
                },
            ],
        }

    def _create_okr_summary_card(
        self, label: str, value: str, icon: str, color: str = "default"
    ) -> Dict[str, Any]:
        """Create OKR summary card"""
        return {
            "type": "container",
            "flex": 1,
            "backgroundColor": "white",
            "borderRadius": 8,
            "padding": 16,
            "border": "1px solid #e5e7eb",
            "children": [
                {
                    "type": "container",
                    "direction": "row",
                    "alignItems": "center",
                    "children": [
                        {"type": "text", "value": icon, "size": "h3", "marginRight": 8},
                        {
                            "type": "text",
                            "value": label,
                            "size": "small",
                            "color": "gray",
                        },
                    ],
                },
                {
                    "type": "text",
                    "value": value,
                    "size": "h2",
                    "weight": "bold",
                    "color": color,
                    "marginTop": 8,
                },
            ],
        }

    def _create_blocker_summary(self) -> Dict[str, Any]:
        """Create blocker summary"""
        return {
            "type": "container",
            "backgroundColor": "#FEE2E2",
            "borderRadius": 8,
            "padding": 12,
            "marginBottom": 16,
            "children": [
                {
                    "type": "text",
                    "value": "Total Blockers: { getBlockers.data.total_blockers }",
                    "weight": "bold",
                    "color": "#DC2626",
                }
            ],
        }

    def _create_blocker_patterns(self) -> Dict[str, Any]:
        """Create blocker patterns view"""
        return {
            "type": "container",
            "marginBottom": 16,
            "children": [
                {
                    "type": "text",
                    "value": "Common Patterns",
                    "weight": "medium",
                    "marginBottom": 8,
                },
                {
                    "type": "container",
                    "children": """{{
                        getBlockers.data.patterns.map(pattern => ({
                            type: 'container',
                            backgroundColor: 'white',
                            borderRadius: 6,
                            padding: 8,
                            marginBottom: 8,
                            border: '1px solid #e5e7eb',
                            children: [
                                {
                                    type: 'text',
                                    value: pattern.type.replace('_', ' ').toUpperCase(),
                                    size: 'small',
                                    weight: 'medium'
                                },
                                {
                                    type: 'text',
                                    value: `${pattern.blocker_count} occurrences`,
                                    size: 'small',
                                    color: 'gray'
                                }
                            ]
                        }))
                    }}""",
                },
            ],
        }

    def _create_blocker_resolutions(self) -> Dict[str, Any]:
        """Create blocker resolutions"""
        return {
            "type": "container",
            "children": [
                {
                    "type": "text",
                    "value": "Recommended Resolutions",
                    "weight": "medium",
                    "marginBottom": 8,
                },
                {
                    "type": "container",
                    "children": """{{
                        getBlockers.data.resolutions.map(resolution => ({
                            type: 'container',
                            backgroundColor: '#F0FDF4',
                            borderRadius: 6,
                            padding: 8,
                            marginBottom: 8,
                            border: '1px solid #86EFAC',
                            children: [
                                {
                                    type: 'text',
                                    value: resolution.action,
                                    size: 'small'
                                },
                                {
                                    type: 'container',
                                    direction: 'row',
                                    marginTop: 4,
                                    children: [
                                        {
                                            type: 'tag',
                                            text: `Impact: ${resolution.impact}`,
                                            size: 'small',
                                            color: 'green'
                                        },
                                        {
                                            type: 'tag',
                                            text: `Effort: ${resolution.effort}`,
                                            size: 'small',
                                            color: 'blue',
                                            marginLeft: 8
                                        }
                                    ]
                                }
                            ]
                        }))
                    }}""",
                },
            ],
        }

    def _create_recommendations_list(self) -> Dict[str, Any]:
        """Create recommendations list"""
        return {
            "type": "container",
            "children": """{{
                getRecommendations.data.actions.map((action, index) => ({
                    type: 'container',
                    backgroundColor: 'white',
                    borderRadius: 8,
                    padding: 12,
                    marginBottom: 12,
                    border: action.priority === 'critical' ? '2px solid #EF4444' : '1px solid #e5e7eb',
                    children: [
                        {
                            type: 'container',
                            direction: 'row',
                            alignItems: 'center',
                            children: [
                                {
                                    type: 'tag',
                                    text: action.priority.toUpperCase(),
                                    color: action.priority === 'critical' ? 'red' : action.priority === 'high' ? 'orange' : 'blue',
                                    size: 'small'
                                },
                                {
                                    type: 'tag',
                                    text: action.category.replace('_', ' ').toUpperCase(),
                                    color: 'gray',
                                    size: 'small',
                                    marginLeft: 8
                                }
                            ]
                        },
                        {
                            type: 'text',
                            value: action.action,
                            marginTop: 8,
                            marginBottom: 8
                        },
                        {
                            type: 'text',
                            value: `Impact: ${action.impact}`,
                            size: 'small',
                            color: 'gray',
                            marginBottom: 8
                        },
                        {
                            type: 'container',
                            direction: 'row',
                            gap: 8,
                            children: [
                                {
                                    type: 'button',
                                    text: 'Mark Complete',
                                    size: 'small',
                                    color: 'green',
                                    onClick: () => {
                                        currentRecommendation.setValue(action);
                                        actionStatusSelect.setValue('completed');
                                        updateRecommendationStatus.trigger();
                                    }
                                },
                                {
                                    type: 'button',
                                    text: 'In Progress',
                                    size: 'small',
                                    color: 'blue',
                                    onClick: () => {
                                        currentRecommendation.setValue(action);
                                        actionStatusSelect.setValue('in_progress');
                                        updateRecommendationStatus.trigger();
                                    }
                                },
                                {
                                    type: 'button',
                                    text: 'Dismiss',
                                    size: 'small',
                                    color: 'gray',
                                    onClick: () => {
                                        currentRecommendation.setValue(action);
                                        actionStatusSelect.setValue('dismissed');
                                        updateRecommendationStatus.trigger();
                                    }
                                }
                            ]
                        }
                    ]
                }))
            }}""",
        }

    def _create_trend_card(self, title: str, trend_key: str) -> Dict[str, Any]:
        """Create trend card"""
        return {
            "type": "container",
            "flex": 1,
            "backgroundColor": "white",
            "borderRadius": 8,
            "padding": 16,
            "border": "1px solid #e5e7eb",
            "children": [
                {
                    "type": "text",
                    "value": title,
                    "size": "small",
                    "color": "gray",
                    "marginBottom": 8,
                },
                {
                    "type": "container",
                    "direction": "row",
                    "alignItems": "baseline",
                    "children": [
                        {
                            "type": "text",
                            "value": f"{{ getProjectTrends.data.{trend_key}.current }}",
                            "size": "h3",
                            "weight": "bold",
                        },
                        {
                            "type": "container",
                            "direction": "row",
                            "alignItems": "center",
                            "marginLeft": 8,
                            "children": [
                                {
                                    "type": "icon",
                                    "icon": f"{{ getProjectTrends.data.{trend_key}.trend === 'increasing' ? 'arrow-up' : 'arrow-down' }}",
                                    "color": f"{{ getProjectTrends.data.{trend_key}.trend === 'increasing' ? 'green' : 'red' }}",
                                    "size": 16,
                                },
                                {
                                    "type": "text",
                                    "value": f"{{ Math.abs(getProjectTrends.data.{trend_key}.change_percentage).toFixed(1) }}%",
                                    "size": "small",
                                    "color": f"{{ getProjectTrends.data.{trend_key}.trend === 'increasing' ? 'green' : 'red' }}",
                                    "marginLeft": 4,
                                },
                            ],
                        },
                    ],
                },
                {
                    "type": "text",
                    "value": f"vs {{ getProjectTrends.data.{trend_key}.previous }}",
                    "size": "small",
                    "color": "gray",
                    "marginTop": 4,
                },
            ],
        }

    def _create_custom_report_builder(self) -> Dict[str, Any]:
        """Create custom report builder"""
        return {
            "type": "container",
            "marginTop": 24,
            "backgroundColor": "#f9fafb",
            "borderRadius": 8,
            "padding": 16,
            "children": [
                {
                    "type": "text",
                    "value": "Custom Report Builder",
                    "size": "h3",
                    "weight": "bold",
                    "marginBottom": 16,
                },
                {
                    "type": "container",
                    "direction": "row",
                    "gap": 16,
                    "marginBottom": 16,
                    "children": [
                        {
                            "type": "input",
                            "id": "reportNameInput",
                            "placeholder": "Report name",
                            "flex": 1,
                        },
                        {
                            "type": "multiselect",
                            "id": "selectedMetrics",
                            "placeholder": "Select metrics",
                            "options": [
                                "completion",
                                "velocity",
                                "blocked_items",
                                "overdue_items",
                                "team_sentiment",
                                "code_quality",
                                "okr_count",
                                "days_until_deadline",
                            ],
                            "flex": 1,
                        },
                        {
                            "type": "select",
                            "id": "groupingSelect",
                            "placeholder": "Group by",
                            "options": ["None", "status", "team", "source"],
                            "value": "None",
                            "width": 150,
                        },
                    ],
                },
                {
                    "type": "button",
                    "text": "Generate Report",
                    "color": "primary",
                    "onClick": "generateCustomReport.trigger()",
                    "disabled": "{{ !reportNameInput.value || !selectedMetrics.value.length }}",
                },
            ],
        }

    def _create_global_state(self) -> Dict[str, Any]:
        """Create global state variables"""
        return {
            "selectedProject": {"type": "object", "value": None},
            "currentRecommendation": {"type": "object", "value": None},
            "reportFilters": {"type": "object", "value": {}},
            "okrUpdateModal": {
                "type": "modal",
                "title": "Update OKR Progress",
                "children": [
                    {
                        "type": "numberInput",
                        "id": "okrValueInput",
                        "label": "Current Value",
                        "required": True,
                    },
                    {
                        "type": "textarea",
                        "id": "okrNotesInput",
                        "label": "Notes",
                        "rows": 3,
                    },
                ],
                "footer": [
                    {
                        "type": "button",
                        "text": "Cancel",
                        "onClick": "okrUpdateModal.close()",
                    },
                    {
                        "type": "button",
                        "text": "Update",
                        "color": "primary",
                        "onClick": "updateOKR.trigger()",
                    },
                ],
            },
            "actionStatusSelect": {"type": "string", "value": ""},
            "actionNotesInput": {"type": "string", "value": ""},
        }

    def _create_theme(self) -> Dict[str, Any]:
        """Create custom theme"""
        return {
            "primary": "#5E6AD2",
            "secondary": "#10B981",
            "danger": "#EF4444",
            "warning": "#F59E0B",
            "info": "#3B82F6",
            "success": "#10B981",
            "backgroundColor": "#F9FAFB",
            "borderRadius": 8,
            "fontFamily": "Inter, system-ui, sans-serif",
        }

    def save_config(self, filename: str = "retool_project_management_config.json"):
        """Save configuration to file"""
        config = self.generate_config()
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Retool configuration saved to {filename}")

        # Also generate implementation guide
        guide = self._generate_implementation_guide()
        with open("retool_project_management_guide.md", "w") as f:
            f.write(guide)
        print("📚 Implementation guide saved to retool_project_management_guide.md")

    def _generate_implementation_guide(self) -> str:
        """Generate implementation guide"""
        return """# Sophia Project Management - Retool Implementation Guide

## 🚀 Overview
This Retool application provides a unified project intelligence dashboard that aggregates data from Linear, GitHub, Asana, and Slack to provide comprehensive project insights aligned with company OKRs.

## 📋 Prerequisites
1. Sophia AI backend running with project management routes enabled
2. Linear API key configured
3. GitHub integration connected
4. Slack bot configured
5. Retool account with API resource capabilities

## 🛠️ Setup Instructions

### 1. Create New Retool App
1. Log into Retool
2. Create a new app named "Sophia Project Intelligence"
3. Set the theme to match your brand

### 2. Configure API Resource
1. Go to Resources → Add Resource → REST API
2. Configure as follows:
   - Name: `ProjectManagementAPI`
   - Base URL: `https://your-sophia-backend.com/api/project-management`
   - Headers:
     - Authorization: `Bearer {{ environment.SOPHIA_API_KEY }}`
     - Content-Type: `application/json`

### 3. Import Configuration
1. Open the app editor
2. Go to Settings → App JSON
3. Copy the contents of `retool_project_management_config.json`
4. Paste and save

### 4. Environment Variables
Set these in Retool's environment settings:
- `SOPHIA_API_URL`: Your Sophia backend URL
- `SOPHIA_API_KEY`: Your API authentication key

## 🎯 Key Features

### Portfolio Overview
- Real-time project status across all tools
- Progress tracking with visual indicators
- Multi-source integration badges
- Detailed project drill-down

### OKR Alignment
- Quarterly OKR tracking
- Project contribution mapping
- Progress visualization
- Risk identification

### Blocker Analysis
- Cross-project blocker detection
- Pattern recognition
- AI-generated resolutions
- Priority-based recommendations

### Team Performance
- Team health scores
- Velocity tracking
- Sentiment analysis from Slack
- Resource allocation insights

### Analytics & Reporting
- Trend analysis over time
- Custom report builder
- Export capabilities
- Predictive insights

## 🔧 Customization

### Adding New Metrics
1. Update the backend agent to calculate new metrics
2. Add to the `selectedMetrics` options in custom report builder
3. Update the project table columns if needed

### Modifying OKRs
1. Update the OKR structure in `ProjectIntelligenceAgent`
2. The UI will automatically reflect new objectives and key results

### Custom Integrations
1. Add new data sources to the backend agent
2. Update the source badges in the project table
3. Add new tabs or sections as needed

## 📊 Usage Tips

### For Executives
- Start with the Portfolio Overview for high-level status
- Check OKR Alignment weekly to track progress
- Review Recommendations for strategic actions

### For Project Managers
- Use Blockers & Actions tab daily
- Monitor Team Performance for resource needs
- Create custom reports for stakeholder updates

### For Team Leads
- Track team velocity trends
- Address blockers quickly
- Use sentiment data to gauge team morale

## 🚨 Troubleshooting

### No Data Loading
1. Check API connection in browser console
2. Verify authentication token
3. Ensure backend is running

### Slow Performance
1. Reduce polling intervals
2. Implement pagination for large datasets
3. Use caching where appropriate

### Missing Projects
1. Verify all integrations are connected
2. Check project name matching logic
3. Review unification algorithm

## 📈 Best Practices

1. **Regular Updates**: Keep OKRs current with weekly updates
2. **Action Items**: Address critical recommendations within 24 hours
3. **Team Sync**: Use team performance data in 1-on-1s
4. **Custom Reports**: Save frequently used report configurations

## 🔗 Related Documentation
- [Project Intelligence Agent Documentation](../backend/agents/specialized/project_intelligence_agent.py)
- [API Route Documentation](../backend/app/routes/project_management_routes.py)
- [Sophia AI Architecture Guide](../docs/SOPHIA_ARCHITECTURE.md)

## 💡 Future Enhancements
- Asana integration when API key available
- GitHub project boards visualization
- Automated report scheduling
- Mobile-responsive design
- Real-time collaboration features
"""


def main():
    """Generate Retool configuration"""
    builder = ProjectManagementRetoolBuilder()
    builder.save_config()

    print("\n📊 Next Steps:")
    print("1. Import the configuration into Retool")
    print("2. Configure the API resource with your backend URL")
    print("3. Set environment variables")
    print("4. Test the connection with your Linear projects")
    print("5. Customize as needed for your organization")


if __name__ == "__main__":
    main()
