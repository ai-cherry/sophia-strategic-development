"""Project Intelligence Agent.

Unifies project data from Linear, GitHub, Asana, and Slack to provide
centralized insights, progress tracking, and recommendations against OKRs/KPIs
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List

from backend.agents.core.agno_performance_optimizer import AgnoPerformanceOptimizer
from backend.agents.core.base_agent import BaseAgent, Task, TaskResult
from backend.integrations.linear_integration import linear_integration
from backend.integrations.slack.slack_integration import slack_integration
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project health status."""

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    NOT_STARTED = "not_started"


@dataclass
class ProjectMetrics:
    """Metrics for a project."""
    completion_percentage: float
    velocity: float  # Story points per sprint
    blocked_items: int
    overdue_items: int
    team_sentiment: float  # 0-1 based on Slack analysis
    code_quality: float  # 0-1 based on GitHub metrics


@dataclass
class OKRAlignment:
    """How a project aligns with OKRs."""
    objective: str
    key_result: str
    contribution_percentage: float
    current_progress: float
    projected_completion: datetime


class ProjectIntelligenceAgent(BaseAgent):
    """Analyzes project data across all tools to provide unified intelligence.

            and recommendations for achieving company OKRs
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mcp_client = MCPClient()
        self.okrs = self._load_company_okrs()

    @classmethod
    async def pooled(cls, config: Dict[str, Any]) -> 'ProjectIntelligenceAgent':
        """Get a pooled or new instance using AgnoPerformanceOptimizer."""
        optimizer = AgnoPerformanceOptimizer()
        await optimizer.register_agent_class('project_intelligence', cls)
        agent = await optimizer.get_or_create_agent('project_intelligence', {'config': config})
        logger.info(f"[AgnoPerformanceOptimizer] Provided ProjectIntelligenceAgent instance (pooled or new)")
        return agent

    def _load_company_okrs(self) -> Dict[str, Any]:
        """Load company OKRs and KPIs."""
        # In production, this would load from database.
        return {
            "Q1_2024": {
                "objectives": [
                    {
                        "id": "obj_1",
                        "title": "Achieve Product-Market Fit",
                        "key_results": [
                            {
                                "id": "kr_1_1",
                                "title": "Reach 100 paying customers",
                                "target": 100,
                                "current": 45,
                                "unit": "customers",
                            },
                            {
                                "id": "kr_1_2",
                                "title": "Achieve 90% customer satisfaction",
                                "target": 90,
                                "current": 87,
                                "unit": "percentage",
                            },
                        ],
                    },
                    {
                        "id": "obj_2",
                        "title": "Build Scalable Infrastructure",
                        "key_results": [
                            {
                                "id": "kr_2_1",
                                "title": "99.9% uptime",
                                "target": 99.9,
                                "current": 99.5,
                                "unit": "percentage",
                            },
                            {
                                "id": "kr_2_2",
                                "title": "Sub-200ms API response time",
                                "target": 200,
                                "current": 245,
                                "unit": "milliseconds",
                            },
                        ],
                    },
                ]
            }
        }

    async def execute_task(self, task: Task) -> TaskResult:
        """Execute project intelligence tasks."""
        try:
            if task.task_type == "analyze_project_portfolio":
                return await self._analyze_project_portfolio()
            elif task.task_type == "generate_okr_report":
                return await self._generate_okr_alignment_report()
            elif task.task_type == "identify_blockers":
                return await self._identify_cross_project_blockers()
            elif task.task_type == "recommend_actions":
                return await self._recommend_strategic_actions()
            else:
                return TaskResult(
                    success=False, error=f"Unknown task type: {task.task_type}"
                )
        except Exception as e:
            logger.error(f"Project intelligence task failed: {e}", exc_info=True)
            return TaskResult(success=False, error=str(e))

    async def _analyze_project_portfolio(self) -> TaskResult:
        """Analyze all projects across tools."""# Gather data from all sources in parallel.

        linear_data, github_data, asana_data, slack_data = await asyncio.gather(
            self._get_linear_projects(),
            self._get_github_projects(),
            self._get_asana_projects(),
            self._analyze_slack_conversations(),
            return_exceptions=True,
        )

        # Merge and deduplicate projects
        unified_projects = self._unify_project_data(
            linear_data, github_data, asana_data, slack_data
        )

        # Analyze each project
        project_analyses = []
        for project in unified_projects:
            analysis = await self._analyze_single_project(project)
            project_analyses.append(analysis)

        # Generate portfolio summary
        portfolio_summary = self._generate_portfolio_summary(project_analyses)

        return TaskResult(
            success=True,
            data={
                "projects": project_analyses,
                "summary": portfolio_summary,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _get_linear_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from Linear."""try:.

            # Get all teams and their projects
            teams = await linear_integration.get_teams()
            projects = []

            for team in teams:
                team_projects = await linear_integration.get_projects(team["id"])
                for project in team_projects:
                    # Get issues for velocity calculation
                    issues = await linear_integration.get_project_issues(project["id"])

                    projects.append(
                        {
                            "source": "linear",
                            "id": project["id"],
                            "name": project["name"],
                            "team": team["name"],
                            "status": project.get("state", {}).get("name", "Unknown"),
                            "progress": project.get("progress", 0),
                            "issues": issues,
                            "start_date": project.get("startDate"),
                            "target_date": project.get("targetDate"),
                            "description": project.get("description", ""),
                        }
                    )

            return projects
        except Exception as e:
            logger.error(f"Failed to get Linear projects: {e}")
            return []

    async def _get_github_projects(self) -> List[Dict[str, Any]]:
        """Get projects from GitHub."""try:.

            # Use GitHub MCP server
            result = await self.mcp_client.call_tool(
                "github", "list_projects", org="sophia-ai"
            )

            projects = []
            for project in result.get("projects", []):
                # Get additional metrics
                issues = await self.mcp_client.call_tool(
                    "github", "get_project_issues", project_id=project["id"]
                )

                prs = await self.mcp_client.call_tool(
                    "github", "get_project_prs", project_id=project["id"]
                )

                projects.append(
                    {
                        "source": "github",
                        "id": project["id"],
                        "name": project["name"],
                        "status": project.get("state", "open"),
                        "progress": self._calculate_github_progress(issues, prs),
                        "issues": issues.get("issues", []),
                        "pull_requests": prs.get("pull_requests", []),
                        "description": project.get("body", ""),
                    }
                )

            return projects
        except Exception as e:
            logger.error(f"Failed to get GitHub projects: {e}")
            return []

    async def _get_asana_projects(self) -> List[Dict[str, Any]]:
        """Get projects from Asana (when available)."""# Placeholder for Asana integration.

        return []

    async def _analyze_slack_conversations(self) -> Dict[str, Any]:
        """Analyze Slack for project-related discussions."""try:.

            # Search for project-related messages
            channels = ["#engineering", "#product", "#general"]
            project_mentions = {}
            sentiment_data = {}

            for channel in channels:
                # Search for project keywords
                messages = await slack_integration.search_messages(
                    channel=channel,
                    query="project OR sprint OR deadline OR blocked",
                    count=100,
                )

                # Analyze sentiment and extract project mentions
                for message in messages:
                    sentiment = await self._analyze_message_sentiment(message["text"])
                    projects_mentioned = self._extract_project_mentions(message["text"])

                    for project in projects_mentioned:
                        if project not in project_mentions:
                            project_mentions[project] = []
                            sentiment_data[project] = []

                        project_mentions[project].append(message)
                        sentiment_data[project].append(sentiment)

            return {
                "project_mentions": project_mentions,
                "sentiment_data": sentiment_data,
            }
        except Exception as e:
            logger.error(f"Failed to analyze Slack: {e}")
            return {}

    def _unify_project_data(self, *data_sources) -> List[Dict[str, Any]]:
        """Merge project data from multiple sources."""unified = {}.

        for source_data in data_sources:
            if isinstance(source_data, Exception):
                continue

            if isinstance(source_data, list):
                # Linear and GitHub return lists
                for project in source_data:
                    key = self._generate_project_key(project)
                    if key not in unified:
                        unified[key] = {"sources": [], "data": {}}
                    unified[key]["sources"].append(project["source"])
                    unified[key]["data"][project["source"]] = project
            elif isinstance(source_data, dict):
                # Slack returns dict
                for project_name, data in source_data.get(
                    "project_mentions", {}
                ).items():
                    key = project_name.lower().strip()
                    if key not in unified:
                        unified[key] = {"sources": [], "data": {}}
                    unified[key]["sources"].append("slack")
                    unified[key]["data"]["slack"] = {
                        "mentions": data,
                        "sentiment": source_data.get("sentiment_data", {}).get(
                            project_name, []
                        ),
                    }

        return list(unified.values())

    def _generate_project_key(self, project: Dict[str, Any]) -> str:
        """Generate a unique key for project deduplication."""# Simple approach - in production would use more sophisticated matching.

        return project.get("name", "").lower().strip()

    async def _analyze_single_project(
        self, unified_project: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze a single unified project."""project_data = unified_project["data"].

        # Calculate metrics
        metrics = ProjectMetrics(
            completion_percentage=self._calculate_completion(project_data),
            velocity=self._calculate_velocity(project_data),
            blocked_items=self._count_blocked_items(project_data),
            overdue_items=self._count_overdue_items(project_data),
            team_sentiment=self._calculate_sentiment(project_data),
            code_quality=self._calculate_code_quality(project_data),
        )

        # Determine status
        status = self._determine_project_status(metrics)

        # Find OKR alignment
        okr_alignment = self._find_okr_alignment(project_data)

        # Generate insights
        insights = self._generate_project_insights(project_data, metrics, status)

        return {
            "name": self._get_project_name(project_data),
            "sources": unified_project["sources"],
            "status": status.value,
            "metrics": {
                "completion": metrics.completion_percentage,
                "velocity": metrics.velocity,
                "blocked_items": metrics.blocked_items,
                "overdue_items": metrics.overdue_items,
                "team_sentiment": metrics.team_sentiment,
                "code_quality": metrics.code_quality,
            },
            "okr_alignment": okr_alignment,
            "insights": insights,
            "raw_data": project_data,
        }

    def _calculate_completion(self, project_data: Dict[str, Any]) -> float:
        """Calculate overall completion percentage."""completions = [].

        # Linear completion
        if "linear" in project_data:
            completions.append(project_data["linear"].get("progress", 0))

        # GitHub completion (based on closed vs open issues)
        if "github" in project_data:
            issues = project_data["github"].get("issues", [])
            if issues:
                closed = sum(1 for i in issues if i.get("state") == "closed")
                completions.append((closed / len(issues)) * 100)

        return sum(completions) / len(completions) if completions else 0

    def _calculate_velocity(self, project_data: Dict[str, Any]) -> float:
        """Calculate project velocity (story points per sprint)."""# Simplified - would need sprint data in production.

        if "linear" in project_data:
            issues = project_data["linear"].get("issues", [])
            completed_last_sprint = sum(
                1
                for i in issues
                if i.get("completedAt")
                and self._is_within_last_sprint(i["completedAt"])
            )
            return completed_last_sprint * 3  # Assume 3 points average
        return 0

    def _is_within_last_sprint(self, date_str: str) -> bool:
        """Check if date is within last 2 weeks."""try:.

            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date > datetime.now() - timedelta(days=14)
        except:
            return False

    def _calculate_sentiment(self, project_data: Dict[str, Any]) -> float:
        """Calculate team sentiment from Slack data."""if "slack" in project_data:.

            sentiments = project_data["slack"].get("sentiment", [])
            if sentiments:
                return sum(sentiments) / len(sentiments)
        return 0.7  # Neutral default

    def _calculate_code_quality(self, project_data: Dict[str, Any]) -> float:
        """Calculate code quality from GitHub metrics."""if "github" in project_data:.

            prs = project_data["github"].get("pull_requests", [])
            if prs:
                # Simple metric: approved PRs / total PRs
                approved = sum(1 for pr in prs if pr.get("merged"))
                return approved / len(prs) if prs else 0.8
        return 0.8  # Default

    def _determine_project_status(self, metrics: ProjectMetrics) -> ProjectStatus:
        """Determine overall project status."""if metrics.completion_percentage >= 100:.

            return ProjectStatus.COMPLETED
        elif metrics.blocked_items > 3 or metrics.overdue_items > 5:
            return ProjectStatus.BLOCKED
        elif metrics.velocity < 5 or metrics.team_sentiment < 0.5:
            return ProjectStatus.AT_RISK
        elif metrics.completion_percentage == 0:
            return ProjectStatus.NOT_STARTED
        else:
            return ProjectStatus.ON_TRACK

    def _generate_portfolio_summary(
        self, project_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate portfolio-level summary."""total_projects = len(project_analyses).

        status_breakdown = {
            "on_track": sum(1 for p in project_analyses if p["status"] == "on_track"),
            "at_risk": sum(1 for p in project_analyses if p["status"] == "at_risk"),
            "blocked": sum(1 for p in project_analyses if p["status"] == "blocked"),
            "completed": sum(1 for p in project_analyses if p["status"] == "completed"),
            "not_started": sum(
                1 for p in project_analyses if p["status"] == "not_started"
            ),
        }

        # Calculate OKR impact
        okr_impact = self._calculate_portfolio_okr_impact(project_analyses)

        # Identify top risks
        top_risks = self._identify_portfolio_risks(project_analyses)

        # Generate recommendations
        recommendations = self._generate_portfolio_recommendations(
            project_analyses, status_breakdown, okr_impact
        )

        return {
            "total_projects": total_projects,
            "status_breakdown": status_breakdown,
            "okr_impact": okr_impact,
            "top_risks": top_risks,
            "recommendations": recommendations,
            "health_score": self._calculate_portfolio_health(status_breakdown),
        }

    def _calculate_portfolio_okr_impact(
        self, projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate how projects impact OKRs."""okr_contributions = {}.

        for project in projects:
            alignments = project.get("okr_alignment", [])
            for alignment in alignments:
                okr_id = alignment["key_result"]
                if okr_id not in okr_contributions:
                    okr_contributions[okr_id] = {
                        "projects": [],
                        "total_contribution": 0,
                    }
                okr_contributions[okr_id]["projects"].append(project["name"])
                okr_contributions[okr_id]["total_contribution"] += alignment[
                    "contribution_percentage"
                ]

        return okr_contributions

    async def _generate_okr_alignment_report(self) -> TaskResult:
        """Generate detailed OKR alignment report."""# Get current project portfolio.

        portfolio_result = await self._analyze_project_portfolio()
        if not portfolio_result.success:
            return portfolio_result

        projects = portfolio_result.data["projects"]
        okrs = self.okrs["Q1_2024"]["objectives"]

        report = {"objectives": []}

        for objective in okrs:
            obj_report = {"title": objective["title"], "key_results": []}

            for kr in objective["key_results"]:
                kr_report = {
                    "title": kr["title"],
                    "target": kr["target"],
                    "current": kr["current"],
                    "unit": kr["unit"],
                    "progress_percentage": (kr["current"] / kr["target"]) * 100,
                    "contributing_projects": [],
                    "risks": [],
                    "recommendations": [],
                }

                # Find contributing projects
                for project in projects:
                    for alignment in project.get("okr_alignment", []):
                        if alignment["key_result"] == kr["id"]:
                            kr_report["contributing_projects"].append(
                                {
                                    "name": project["name"],
                                    "status": project["status"],
                                    "contribution": alignment[
                                        "contribution_percentage"
                                    ],
                                    "projected_completion": alignment[
                                        "projected_completion"
                                    ],
                                }
                            )

                # Identify risks
                if kr_report["progress_percentage"] < 70:
                    kr_report["risks"].append("Behind target")

                at_risk_projects = [
                    p
                    for p in kr_report["contributing_projects"]
                    if p["status"] in ["at_risk", "blocked"]
                ]
                if at_risk_projects:
                    kr_report["risks"].append(
                        f"{len(at_risk_projects)} contributing projects at risk"
                    )

                # Generate recommendations
                if kr_report["risks"]:
                    kr_report["recommendations"] = self._generate_kr_recommendations(
                        kr, kr_report["contributing_projects"]
                    )

                obj_report["key_results"].append(kr_report)

            report["objectives"].append(obj_report)

        return TaskResult(
            success=True,
            data={
                "report": report,
                "summary": self._generate_okr_summary(report),
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _generate_kr_recommendations(
        self, kr: Dict[str, Any], contributing_projects: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for a key result."""recommendations = [].

        # Check if we need more projects
        total_contribution = sum(p["contribution"] for p in contributing_projects)
        if total_contribution < 80:
            recommendations.append(
                f"Allocate more resources: Current projects only contribute {total_contribution}% to this KR"
            )

        # Check for blocked projects
        blocked = [p for p in contributing_projects if p["status"] == "blocked"]
        if blocked:
            recommendations.append(
                f"Unblock {len(blocked)} projects: {', '.join(p['name'] for p in blocked)}"
            )

        # Check timeline
        current_progress = (kr["current"] / kr["target"]) * 100
        if (
            current_progress < 50
        ):  # Less than halfway at presumably halfway through quarter
            recommendations.append(
                "Accelerate progress: Current pace will not meet quarterly target"
            )

        return recommendations

    async def _identify_cross_project_blockers(self) -> TaskResult:
        """Identify blockers affecting multiple projects."""# Get all blocked items across tools.

        blocked_items = await asyncio.gather(
            self._get_linear_blocked_items(),
            self._get_github_blocked_items(),
            return_exceptions=True,
        )

        # Analyze patterns
        blocker_patterns = self._analyze_blocker_patterns(blocked_items)

        # Generate resolution recommendations
        resolutions = self._generate_blocker_resolutions(blocker_patterns)

        return TaskResult(
            success=True,
            data={
                "total_blockers": sum(
                    len(items)
                    for items in blocked_items
                    if not isinstance(items, Exception)
                ),
                "patterns": blocker_patterns,
                "resolutions": resolutions,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _recommend_strategic_actions(self) -> TaskResult:
        """Generate strategic recommendations based on all data."""# Get current state.

        portfolio = await self._analyze_project_portfolio()
        okr_report = await self._generate_okr_alignment_report()
        blockers = await self._identify_cross_project_blockers()

        if not all([portfolio.success, okr_report.success, blockers.success]):
            return TaskResult(
                success=False,
                error="Failed to gather necessary data for recommendations",
            )

        # Analyze gaps
        okr_gaps = self._identify_okr_gaps(okr_report.data["report"])
        resource_gaps = self._identify_resource_gaps(portfolio.data["projects"])
        timeline_risks = self._identify_timeline_risks(portfolio.data["projects"])

        # Generate prioritized actions
        actions = []

        # Critical actions (blockers)
        for resolution in blockers.data["resolutions"]:
            actions.append(
                {
                    "priority": "critical",
                    "category": "blocker",
                    "action": resolution["action"],
                    "impact": resolution["impact"],
                    "effort": resolution["effort"],
                    "owner": resolution["suggested_owner"],
                }
            )

        # High priority (OKR risks)
        for gap in okr_gaps:
            actions.append(
                {
                    "priority": "high",
                    "category": "okr_gap",
                    "action": gap["recommended_action"],
                    "impact": f"Improve {gap['kr_title']} by {gap['gap_percentage']:.1f}%",
                    "effort": "medium",
                    "owner": "leadership",
                }
            )

        # Medium priority (resource optimization)
        for gap in resource_gaps:
            actions.append(
                {
                    "priority": "medium",
                    "category": "resource",
                    "action": gap["action"],
                    "impact": gap["impact"],
                    "effort": gap["effort"],
                    "owner": gap["team"],
                }
            )

        # Sort by priority and impact
        actions.sort(
            key=lambda x: (
                {"critical": 0, "high": 1, "medium": 2}.get(x["priority"], 3),
                -self._estimate_impact_score(x["impact"]),
            )
        )

        return TaskResult(
            success=True,
            data={
                "actions": actions[:10],  # Top 10 actions
                "summary": {
                    "total_recommendations": len(actions),
                    "critical_actions": sum(
                        1 for a in actions if a["priority"] == "critical"
                    ),
                    "estimated_okr_improvement": self._estimate_okr_improvement(
                        actions
                    ),
                    "key_themes": self._extract_action_themes(actions),
                },
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _extract_action_themes(self, actions: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes from recommended actions."""themes = [].

        blocker_count = sum(1 for a in actions if a["category"] == "blocker")
        if blocker_count > 3:
            themes.append("Significant cross-project dependencies need resolution")

        okr_gap_count = sum(1 for a in actions if a["category"] == "okr_gap")
        if okr_gap_count > 2:
            themes.append("Multiple OKRs at risk of missing targets")

        resource_count = sum(1 for a in actions if a["category"] == "resource")
        if resource_count > 2:
            themes.append("Resource allocation needs optimization")

        return themes

    async def _analyze_message_sentiment(self, text: str) -> float:
        """Analyze sentiment of a message (0-1, 0.5 is neutral)."""# Simple keyword-based sentiment.

        positive_words = [
            "great",
            "excellent",
            "good",
            "progress",
            "completed",
            "shipped",
            "launched",
        ]
        negative_words = [
            "blocked",
            "delayed",
            "issue",
            "problem",
            "bug",
            "failed",
            "stuck",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count + negative_count == 0:
            return 0.5

        return positive_count / (positive_count + negative_count)

    def _extract_project_mentions(self, text: str) -> List[str]:
        """Extract project names from text."""# Simple approach - look for common project name patterns.

        import re

        patterns = [
            r"project[:\s]+([a-zA-Z0-9\-_]+)",
            r"#([a-zA-Z0-9\-_]+)",
            r"PROJ-([0-9]+)",
        ]

        projects = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            projects.extend(matches)

        return list(set(projects))

    def _count_blocked_items(self, project_data: Dict[str, Any]) -> int:
        """Count blocked items across all sources."""count = 0.

        if "linear" in project_data:
            issues = project_data["linear"].get("issues", [])
            count += sum(
                1 for i in issues if i.get("state", {}).get("name") == "Blocked"
            )

        if "github" in project_data:
            issues = project_data["github"].get("issues", [])
            count += sum(
                1
                for i in issues
                if "blocked" in [l.get("name", "").lower() for l in i.get("labels", [])]
            )

        return count

    def _count_overdue_items(self, project_data: Dict[str, Any]) -> int:
        """Count overdue items."""count = 0.

        now = datetime.now()

        if "linear" in project_data:
            issues = project_data["linear"].get("issues", [])
            for issue in issues:
                if issue.get("dueDate") and not issue.get("completedAt"):
                    try:
                        due_date = datetime.fromisoformat(
                            issue["dueDate"].replace("Z", "+00:00")
                        )
                        if due_date < now:
                            count += 1
                    except:
                        pass

        return count

    def _get_project_name(self, project_data: Dict[str, Any]) -> str:
        """Get the best project name from available sources."""if "linear" in project_data:.

            return project_data["linear"]["name"]
        elif "github" in project_data:
            return project_data["github"]["name"]
        elif "asana" in project_data:
            return project_data["asana"]["name"]
        else:
            return "Unknown Project"

    def _find_okr_alignment(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find which OKRs this project contributes to."""alignments = [].

        # Extract keywords from project data
        project_text = ""
        if "linear" in project_data:
            project_text += project_data["linear"].get("description", "")
        if "github" in project_data:
            project_text += project_data["github"].get("description", "")

        project_text = project_text.lower()

        # Check against each OKR
        for objective in self.okrs["Q1_2024"]["objectives"]:
            for kr in objective["key_results"]:
                # Simple keyword matching - in production would use embeddings
                kr_keywords = self._extract_kr_keywords(kr)
                matches = sum(1 for kw in kr_keywords if kw in project_text)

                if matches > 0:
                    alignments.append(
                        {
                            "objective": objective["title"],
                            "key_result": kr["id"],
                            "contribution_percentage": min(
                                matches * 20, 100
                            ),  # Simple scoring
                            "current_progress": (kr["current"] / kr["target"]) * 100,
                            "projected_completion": datetime.now()
                            + timedelta(days=30),  # Simplified
                        }
                    )

        return alignments

    def _extract_kr_keywords(self, kr: Dict[str, Any]) -> List[str]:
        """Extract keywords from a key result."""# Simple approach - in production would be more sophisticated.

        title_words = kr["title"].lower().split()
        important_words = [w for w in title_words if len(w) > 3]
        return important_words

    def _generate_project_insights(
        self,
        project_data: Dict[str, Any],
        metrics: ProjectMetrics,
        status: ProjectStatus,
    ) -> List[str]:
        """Generate insights for a project."""insights = [].

        if status == ProjectStatus.BLOCKED:
            insights.append(
                f"Project is blocked with {metrics.blocked_items} blocking items"
            )

        if metrics.velocity < 5:
            insights.append("Low velocity - team may need additional resources")

        if metrics.team_sentiment < 0.5:
            insights.append("Negative team sentiment detected in Slack discussions")

        if metrics.overdue_items > 0:
            insights.append(f"{metrics.overdue_items} items are overdue")

        if metrics.code_quality < 0.7:
            insights.append("Code quality metrics below threshold")

        return insights

    def _calculate_portfolio_health(self, status_breakdown: Dict[str, int]) -> float:
        """Calculate overall portfolio health score (0-100)."""total = sum(status_breakdown.values()).

        if total == 0:
            return 0

        weights = {
            "completed": 1.0,
            "on_track": 0.8,
            "at_risk": 0.4,
            "blocked": 0.2,
            "not_started": 0.5,
        }

        score = sum(
            count * weights.get(status, 0) for status, count in status_breakdown.items()
        )
        return (score / total) * 100

    def _identify_portfolio_risks(
        self, projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify top risks across the portfolio."""risks = [].

        # Count projects by status
        blocked_projects = [p for p in projects if p["status"] == "blocked"]
        if len(blocked_projects) > 2:
            risks.append(
                {
                    "type": "multiple_blocked_projects",
                    "severity": "high",
                    "description": f"{len(blocked_projects)} projects are blocked",
                    "affected_projects": [p["name"] for p in blocked_projects],
                }
            )

        # Check OKR alignment
        unaligned_projects = [p for p in projects if not p.get("okr_alignment")]
        if len(unaligned_projects) > len(projects) * 0.3:
            risks.append(
                {
                    "type": "poor_okr_alignment",
                    "severity": "medium",
                    "description": f"{len(unaligned_projects)} projects not aligned with OKRs",
                    "affected_projects": [p["name"] for p in unaligned_projects],
                }
            )

        # Check velocity
        low_velocity_projects = [p for p in projects if p["metrics"]["velocity"] < 5]
        if len(low_velocity_projects) > 3:
            risks.append(
                {
                    "type": "low_velocity",
                    "severity": "medium",
                    "description": f"{len(low_velocity_projects)} projects have low velocity",
                    "affected_projects": [p["name"] for p in low_velocity_projects],
                }
            )

        return sorted(
            risks,
            key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r["severity"], 3),
        )

    def _generate_portfolio_recommendations(
        self,
        projects: List[Dict[str, Any]],
        status_breakdown: Dict[str, int],
        okr_impact: Dict[str, Any],
    ) -> List[str]:
        """Generate portfolio-level recommendations."""recommendations = [].

        # Based on status breakdown
        if status_breakdown["blocked"] > 2:
            recommendations.append(
                "Schedule cross-team sync to resolve blockers - multiple projects affected"
            )

        if status_breakdown["at_risk"] > status_breakdown["on_track"]:
            recommendations.append(
                "Portfolio health is declining - consider resource reallocation"
            )

        # Based on OKR impact
        under_contributed_okrs = [
            kr_id
            for kr_id, data in okr_impact.items()
            if data["total_contribution"] < 80
        ]
        if under_contributed_okrs:
            recommendations.append(
                f"Allocate more projects to support {len(under_contributed_okrs)} under-resourced OKRs"
            )

        # Based on velocity
        avg_velocity = (
            sum(p["metrics"]["velocity"] for p in projects) / len(projects)
            if projects
            else 0
        )
        if avg_velocity < 10:
            recommendations.append(
                "Overall velocity is low - consider sprint planning improvements"
            )

        return recommendations

    async def _get_linear_blocked_items(self) -> List[Dict[str, Any]]:
        """Get all blocked items from Linear."""try:.

            issues = await linear_integration.search_issues(
                filter={"state": {"name": {"eq": "Blocked"}}}
            )
            return issues
        except Exception as e:
            logger.error(f"Failed to get Linear blocked items: {e}")
            return []

    async def _get_github_blocked_items(self) -> List[Dict[str, Any]]:
        """Get all blocked items from GitHub."""try:.

            result = await self.mcp_client.call_tool(
                "github", "search_issues", query="label:blocked is:open"
            )
            return result.get("issues", [])
        except Exception as e:
            logger.error(f"Failed to get GitHub blocked items: {e}")
            return []

    def _analyze_blocker_patterns(
        self, blocked_items: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Analyze patterns in blockers."""all_blockers = [].

        for items in blocked_items:
            if not isinstance(items, Exception):
                all_blockers.extend(items)

        patterns = []

        # Group by assignee
        assignee_blocks = {}
        for blocker in all_blockers:
            assignee = blocker.get("assignee", {}).get("name", "Unassigned")
            if assignee not in assignee_blocks:
                assignee_blocks[assignee] = []
            assignee_blocks[assignee].append(blocker)

        # Find overloaded assignees
        for assignee, blocks in assignee_blocks.items():
            if len(blocks) > 2:
                patterns.append(
                    {
                        "type": "overloaded_assignee",
                        "assignee": assignee,
                        "blocker_count": len(blocks),
                        "items": blocks,
                    }
                )

        # Group by blocker reason (simplified)
        reason_blocks = {}
        for blocker in all_blockers:
            # Extract reason from title/description
            text = blocker.get("title", "") + " " + blocker.get("description", "")
            if "api" in text.lower():
                reason = "external_api"
            elif "design" in text.lower():
                reason = "design_needed"
            elif "data" in text.lower():
                reason = "data_dependency"
            else:
                reason = "other"

            if reason not in reason_blocks:
                reason_blocks[reason] = []
            reason_blocks[reason].append(blocker)

        # Find common reasons
        for reason, blocks in reason_blocks.items():
            if len(blocks) > 1:
                patterns.append(
                    {
                        "type": "common_blocker_reason",
                        "reason": reason,
                        "blocker_count": len(blocks),
                        "items": blocks,
                    }
                )

        return patterns

    def _generate_blocker_resolutions(
        self, patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate resolution recommendations for blocker patterns."""resolutions = [].

        for pattern in patterns:
            if pattern["type"] == "overloaded_assignee":
                resolutions.append(
                    {
                        "action": f"Redistribute {pattern['assignee']}'s blocked items",
                        "impact": f"Unblock {pattern['blocker_count']} items",
                        "effort": "low",
                        "suggested_owner": "engineering_manager",
                    }
                )

            elif pattern["type"] == "common_blocker_reason":
                if pattern["reason"] == "external_api":
                    resolutions.append(
                        {
                            "action": "Schedule API integration working session",
                            "impact": f"Resolve {pattern['blocker_count']} API-related blockers",
                            "effort": "medium",
                            "suggested_owner": "tech_lead",
                        }
                    )
                elif pattern["reason"] == "design_needed":
                    resolutions.append(
                        {
                            "action": "Prioritize design reviews for blocked items",
                            "impact": f"Unblock {pattern['blocker_count']} design-dependent items",
                            "effort": "medium",
                            "suggested_owner": "design_lead",
                        }
                    )

        return resolutions

    def _identify_okr_gaps(self, okr_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in OKR achievement."""gaps = [].

        for objective in okr_report["objectives"]:
            for kr in objective["key_results"]:
                if kr["progress_percentage"] < 70:  # Behind schedule
                    gap_percentage = 70 - kr["progress_percentage"]
                    gaps.append(
                        {
                            "objective": objective["title"],
                            "kr_title": kr["title"],
                            "gap_percentage": gap_percentage,
                            "recommended_action": self._recommend_okr_action(kr),
                        }
                    )

        return gaps

    def _recommend_okr_action(self, kr: Dict[str, Any]) -> str:
        """Recommend action for an underperforming KR."""if not kr["contributing_projects"]:.

            return f"Assign projects to support: {kr['title']}"

        blocked_projects = [
            p for p in kr["contributing_projects"] if p["status"] == "blocked"
        ]
        if blocked_projects:
            return f"Unblock {len(blocked_projects)} projects contributing to this KR"

        if kr["progress_percentage"] < 50:
            return f"Accelerate progress on {kr['title']} - consider adding resources"

        return f"Review and optimize projects supporting {kr['title']}"

    def _identify_resource_gaps(
        self, projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify resource allocation issues."""gaps = [].

        # Group projects by team
        team_projects = {}
        for project in projects:
            team = project.get("raw_data", {}).get("linear", {}).get("team", "Unknown")
            if team not in team_projects:
                team_projects[team] = []
            team_projects[team].append(project)

        # Analyze each team
        for team, team_projs in team_projects.items():
            blocked_count = sum(1 for p in team_projs if p["status"] == "blocked")
            at_risk_count = sum(1 for p in team_projs if p["status"] == "at_risk")

            if blocked_count + at_risk_count > len(team_projs) * 0.5:
                gaps.append(
                    {
                        "team": team,
                        "action": f"Provide additional support to {team} team",
                        "impact": f"Improve {len(team_projs)} projects",
                        "effort": "high",
                    }
                )

        return gaps

    def _identify_timeline_risks(
        self, projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify projects with timeline risks."""risks = [].

        for project in projects:
            # Check if project has target date
            linear_data = project.get("raw_data", {}).get("linear", {})
            target_date_str = linear_data.get("target_date")

            if target_date_str:
                try:
                    target_date = datetime.fromisoformat(
                        target_date_str.replace("Z", "+00:00")
                    )
                    days_remaining = (target_date - datetime.now()).days

                    if days_remaining < 14 and project["metrics"]["completion"] < 80:
                        risks.append(
                            {
                                "project": project["name"],
                                "days_remaining": days_remaining,
                                "completion": project["metrics"]["completion"],
                                "risk_level": (
                                    "high" if days_remaining < 7 else "medium"
                                ),
                            }
                        )
                except:
                    pass

        return risks

    def _estimate_impact_score(self, impact_description: str) -> float:
        """Estimate numerical impact score from description."""# Simple keyword-based scoring.

        high_impact_words = ["critical", "multiple", "all", "major"]
        medium_impact_words = ["improve", "enhance", "several"]

        impact_lower = impact_description.lower()

        if any(word in impact_lower for word in high_impact_words):
            return 10
        elif any(word in impact_lower for word in medium_impact_words):
            return 5
        else:
            return 1

    def _estimate_okr_improvement(self, actions: List[Dict[str, Any]]) -> float:
        """Estimate potential OKR improvement from actions."""# Simplified calculation.

        okr_actions = [a for a in actions if a["category"] == "okr_gap"]
        if not okr_actions:
            return 0

        # Extract improvement percentages from impact descriptions
        total_improvement = 0
        for action in okr_actions:
            import re

            match = re.search(r"(\d+(?:\.\d+)?)\%", action["impact"])
            if match:
                total_improvement += float(match.group(1))

        return min(total_improvement, 100)  # Cap at 100%

    def _generate_okr_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of OKR report."""
        total_krs = sum(len(obj["key_results"]) for obj in report["objectives"])
        at_risk_krs = sum(
            1
            for obj in report["objectives"]
            for kr in obj["key_results"]
            if kr["progress_percentage"] < 70
        )

        return {
            "total_objectives": len(report["objectives"]),
            "total_key_results": total_krs,
            "at_risk_key_results": at_risk_krs,
            "overall_progress": (
                sum(
                    kr["progress_percentage"]
                    for obj in report["objectives"]
                    for kr in obj["key_results"]
                )
                / total_krs
                if total_krs > 0
                else 0
            ),
        }
