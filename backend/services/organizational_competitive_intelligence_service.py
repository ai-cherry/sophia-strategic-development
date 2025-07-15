from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

from backend.core.auto_esc_config import get_config_value
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService, FoundationalDataType
from backend.utils.logging import get_logger

logger = get_logger(__name__)

class ExecutiveRole(str, Enum):
    """Executive roles in Pay Ready"""
    CEO = "CEO"
    CPO = "CPO" 
    VP_STRATEGIC = "VP_Strategic"
    TEAM_MEMBER = "Team_Member"

class CompetitiveAssignmentType(str, Enum):
    """Types of competitive assignments"""
    PRIMARY_ANALYST = "primary_analyst"
    TERRITORY_OWNER = "territory_owner"
    PRODUCT_SPECIALIST = "product_specialist"
    MARKET_MONITOR = "market_monitor"

@dataclass
class PayReadyEmployee:
    """Enhanced employee data with competitive intelligence context"""
    employee_id: str
    full_name: str
    email: str
    job_title: str
    department: str
    manager_id: Optional[str] = None
    manager_name: Optional[str] = None
    hierarchy_level: int = 5
    executive_role: ExecutiveRole = ExecutiveRole.TEAM_MEMBER
    
    # Competitive intelligence fields
    competitive_focus_areas: List[str] = None
    market_segments: List[str] = None
    expertise_areas: List[str] = None
    customer_territories: List[str] = None
    competitive_win_rate: float = 0.0
    battle_card_access_level: str = "standard"
    last_competitive_training: Optional[datetime] = None
    
    # Calculated fields
    direct_reports_count: int = 0
    team_avg_win_rate: float = 0.0
    
    def __post_init__(self):
        if self.competitive_focus_areas is None:
            self.competitive_focus_areas = []
        if self.market_segments is None:
            self.market_segments = []
        if self.expertise_areas is None:
            self.expertise_areas = []
        if self.customer_territories is None:
            self.customer_territories = []

@dataclass
class CompetitorWithCoverage:
    """Competitor data enhanced with organizational coverage information"""
    competitor_id: str
    company_name: str
    website: Optional[str]
    industry: Optional[str]
    threat_level: str
    
    # Coverage information
    assigned_analysts: List[Dict[str, str]] = None
    coverage_strength: int = 0
    primary_analyst: Optional[str] = None
    
    def __post_init__(self):
        if self.assigned_analysts is None:
            self.assigned_analysts = []

@dataclass
class CompetitiveIntelligenceAlert:
    """Alert for competitive intelligence events"""
    alert_id: str
    alert_type: str  # 'new_threat', 'coverage_gap', 'win_rate_decline', 'training_due'
    priority: str    # 'high', 'medium', 'low'
    title: str
    description: str
    affected_employees: List[str]
    recommended_actions: List[str]
    created_at: datetime

class OrganizationalCompetitiveIntelligenceService:
    """Service for managing Pay Ready organizational data with competitive intelligence integration"""
    
    def __init__(self):
        self.foundational_service = FoundationalKnowledgeService()
        self.cortex_service = None  # Will be initialized when needed
        
    async def initialize(self):
        """Initialize the service with database connections"""
        # Initialize cortex service for SQL queries
        # This would connect to your Snowflake/Cortex instance
        pass
    
    # =====================================================================
    # ORGANIZATIONAL CHART OPERATIONS
    # =====================================================================
    
    async def get_pay_ready_org_chart(self, include_competitive_context: bool = True) -> List[PayReadyEmployee]:
        """Get complete Pay Ready organizational chart with competitive intelligence context"""
        try:
            query = """
            SELECT 
                EMPLOYEE_ID,
                FULL_NAME,
                EMAIL,
                JOB_TITLE,
                DEPARTMENT,
                MANAGER_ID,
                MANAGER_NAME,
                HIERARCHY_LEVEL,
                EXECUTIVE_ROLE,
                COMPETITIVE_FOCUS_AREAS,
                MARKET_SEGMENTS,
                EXPERTISE_AREAS,
                CUSTOMER_TERRITORIES,
                COMPETITIVE_WIN_RATE,
                BATTLE_CARD_ACCESS_LEVEL,
                LAST_COMPETITIVE_TRAINING,
                DIRECT_REPORTS_COUNT,
                TEAM_AVG_WIN_RATE
            FROM VW_PAY_READY_ORG_CHART
            ORDER BY HIERARCHY_LEVEL, DEPARTMENT, FULL_NAME
            """
            
            # Execute query via cortex service
            results = await self._execute_foundational_query(query)
            
            employees = []
            for row in results:
                employee = PayReadyEmployee(
                    employee_id=row[0],
                    full_name=row[1],
                    email=row[2],
                    job_title=row[3],
                    department=row[4],
                    manager_id=row[5],
                    manager_name=row[6],
                    hierarchy_level=row[7],
                    executive_role=ExecutiveRole(row[8]) if row[8] else ExecutiveRole.TEAM_MEMBER,
                    competitive_focus_areas=row[9] or [],
                    market_segments=row[10] or [],
                    expertise_areas=row[11] or [],
                    customer_territories=row[12] or [],
                    competitive_win_rate=float(row[13]) if row[13] else 0.0,
                    battle_card_access_level=row[14] or "standard",
                    last_competitive_training=row[15],
                    direct_reports_count=int(row[16]) if row[16] else 0,
                    team_avg_win_rate=float(row[17]) if row[17] else 0.0
                )
                employees.append(employee)
            
            logger.info(f"Retrieved {len(employees)} employees from Pay Ready org chart")
            return employees
            
        except Exception as e:
            logger.error(f"Error retrieving Pay Ready org chart: {e}")
            return []
    
    async def get_executive_team(self) -> List[PayReadyEmployee]:
        """Get Pay Ready executive team with competitive intelligence context"""
        all_employees = await self.get_pay_ready_org_chart()
        executives = [
            emp for emp in all_employees 
            if emp.executive_role in [ExecutiveRole.CEO, ExecutiveRole.CPO, ExecutiveRole.VP_STRATEGIC]
        ]
        return executives
    
    async def get_employees_by_competitive_focus(self, competitor_name: str) -> List[PayReadyEmployee]:
        """Get employees who focus on a specific competitor"""
        all_employees = await self.get_pay_ready_org_chart()
        focused_employees = [
            emp for emp in all_employees
            if competitor_name in emp.competitive_focus_areas
        ]
        return focused_employees
    
    async def get_department_competitive_analysis(self) -> List[Dict[str, Any]]:
        """Get competitive analysis by department"""
        try:
            query = """
            SELECT 
                DEPARTMENT,
                EMPLOYEE_COUNT,
                AVG_WIN_RATE,
                DEPT_COMPETITIVE_FOCUS,
                DEPT_MARKET_COVERAGE,
                DEPT_EXPERTISE,
                FULL_ACCESS_COUNT,
                RECENTLY_TRAINED_COUNT
            FROM VW_DEPARTMENT_COMPETITIVE_ANALYSIS
            ORDER BY AVG_WIN_RATE DESC
            """
            
            results = await self._execute_foundational_query(query)
            
            department_analysis = []
            for row in results:
                analysis = {
                    "department": row[0],
                    "employee_count": row[1],
                    "avg_win_rate": float(row[2]) if row[2] else 0.0,
                    "competitive_focus": row[3],
                    "market_coverage": row[4],
                    "expertise": row[5],
                    "full_access_count": row[6],
                    "recently_trained_count": row[7]
                }
                department_analysis.append(analysis)
            
            return department_analysis
            
        except Exception as e:
            logger.error(f"Error retrieving department competitive analysis: {e}")
            return []
    
    # =====================================================================
    # COMPETITIVE INTELLIGENCE WITH ORGANIZATIONAL CONTEXT
    # =====================================================================
    
    async def get_competitors_with_coverage(self) -> List[CompetitorWithCoverage]:
        """Get competitors with organizational coverage information"""
        try:
            query = """
            SELECT 
                c.COMPETITOR_ID,
                c.COMPANY_NAME,
                c.WEBSITE,
                c.INDUSTRY,
                c.THREAT_LEVEL,
                
                -- Coverage information
                ARRAY_AGG(
                    CASE WHEN cea.EMPLOYEE_ID IS NOT NULL THEN
                        OBJECT_CONSTRUCT(
                            'employee_id', cea.EMPLOYEE_ID,
                            'name', e.FULL_NAME,
                            'assignment_type', cea.ASSIGNMENT_TYPE,
                            'win_rate', cea.CURRENT_WIN_RATE
                        )
                    END
                ) as assigned_analysts,
                
                COUNT(cea.EMPLOYEE_ID) as coverage_strength,
                
                MAX(CASE WHEN cea.ASSIGNMENT_TYPE = 'primary_analyst' THEN e.FULL_NAME END) as primary_analyst
                
            FROM FOUNDATIONAL_KNOWLEDGE.COMPETITORS c
            LEFT JOIN FOUNDATIONAL_KNOWLEDGE.COMPETITIVE_EMPLOYEE_ASSIGNMENTS cea ON c.COMPETITOR_ID = cea.COMPETITOR_ID
            LEFT JOIN FOUNDATIONAL_KNOWLEDGE.EMPLOYEES e ON cea.EMPLOYEE_ID = e.EMPLOYEE_ID
            GROUP BY c.COMPETITOR_ID, c.COMPANY_NAME, c.WEBSITE, c.INDUSTRY, c.THREAT_LEVEL
            ORDER BY c.THREAT_LEVEL = 'high' DESC, coverage_strength ASC
            """
            
            results = await self._execute_foundational_query(query)
            
            competitors = []
            for row in results:
                competitor = CompetitorWithCoverage(
                    competitor_id=row[0],
                    company_name=row[1],
                    website=row[2],
                    industry=row[3],
                    threat_level=row[4],
                    assigned_analysts=row[5] or [],
                    coverage_strength=int(row[6]) if row[6] else 0,
                    primary_analyst=row[7]
                )
                competitors.append(competitor)
            
            logger.info(f"Retrieved {len(competitors)} competitors with coverage information")
            return competitors
            
        except Exception as e:
            logger.error(f"Error retrieving competitors with coverage: {e}")
            return []
    
    async def assign_competitive_responsibility(
        self, 
        employee_id: str, 
        competitor_id: str, 
        assignment_type: CompetitiveAssignmentType,
        responsibility_level: str = "lead"
    ) -> bool:
        """Assign competitive intelligence responsibility to an employee"""
        try:
            query = """
            INSERT INTO FOUNDATIONAL_KNOWLEDGE.COMPETITIVE_EMPLOYEE_ASSIGNMENTS (
                EMPLOYEE_ID, COMPETITOR_ID, ASSIGNMENT_TYPE, RESPONSIBILITY_LEVEL
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT (EMPLOYEE_ID, COMPETITOR_ID, ASSIGNMENT_TYPE) 
            DO UPDATE SET 
                RESPONSIBILITY_LEVEL = EXCLUDED.RESPONSIBILITY_LEVEL,
                UPDATED_AT = CURRENT_TIMESTAMP
            """
            
            await self._execute_foundational_query(
                query, 
                [employee_id, competitor_id, assignment_type.value, responsibility_level]
            )
            
            logger.info(f"Assigned {assignment_type.value} responsibility for {competitor_id} to {employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning competitive responsibility: {e}")
            return False
    
    # =====================================================================
    # SOPHIA AI NATURAL LANGUAGE QUERY INTERFACE
    # =====================================================================
    
    async def process_natural_language_org_query(self, query: str) -> Dict[str, Any]:
        """Process natural language queries about Pay Ready organization and competitive intelligence"""
        
        query_lower = query.lower()
        
        # Executive team queries
        if any(keyword in query_lower for keyword in ["executive", "ceo", "cpo", "vp", "leadership"]):
            executives = await self.get_executive_team()
            return {
                "query_type": "executive_team",
                "results": [emp.__dict__ for emp in executives],
                "summary": f"Found {len(executives)} executive team members"
            }
        
        # Competitive responsibility queries
        elif any(keyword in query_lower for keyword in ["owns", "responsible", "covers", "analyst"]):
            # Extract competitor name from query
            competitor_keywords = ["eliseai", "entrata", "yieldstar", "propertyradar", "rentspree"]
            competitor_found = None
            
            for keyword in competitor_keywords:
                if keyword in query_lower:
                    competitor_found = keyword
                    break
            
            if competitor_found:
                employees = await self.get_employees_by_competitive_focus(competitor_found.title())
                return {
                    "query_type": "competitive_responsibility",
                    "competitor": competitor_found,
                    "results": [emp.__dict__ for emp in employees],
                    "summary": f"Found {len(employees)} employees responsible for {competitor_found}"
                }
        
        # Department analysis queries
        elif any(keyword in query_lower for keyword in ["department", "team", "win rate", "performance"]):
            dept_analysis = await self.get_department_competitive_analysis()
            return {
                "query_type": "department_analysis",
                "results": dept_analysis,
                "summary": f"Analyzed competitive performance across {len(dept_analysis)} departments"
            }
        
        # Coverage gap queries
        elif any(keyword in query_lower for keyword in ["coverage", "gap", "unassigned", "threat"]):
            competitors = await self.get_competitors_with_coverage()
            uncovered = [comp for comp in competitors if comp.coverage_strength == 0]
            return {
                "query_type": "coverage_gaps",
                "results": [comp.__dict__ for comp in uncovered],
                "summary": f"Found {len(uncovered)} competitors without assigned coverage"
            }
        
        # Org chart queries
        else:
            org_chart = await self.get_pay_ready_org_chart()
            return {
                "query_type": "org_chart",
                "results": [emp.__dict__ for emp in org_chart[:10]],  # Limit to first 10
                "summary": f"Retrieved Pay Ready organizational chart with {len(org_chart)} employees"
            }
    
    # =====================================================================
    # COMPETITIVE INTELLIGENCE ALERTS
    # =====================================================================
    
    async def generate_competitive_intelligence_alerts(self) -> List[CompetitiveIntelligenceAlert]:
        """Generate alerts for competitive intelligence issues"""
        alerts = []
        
        # Coverage gap alerts
        competitors = await self.get_competitors_with_coverage()
        high_threat_uncovered = [
            comp for comp in competitors 
            if comp.threat_level == "high" and comp.coverage_strength == 0
        ]
        
        for competitor in high_threat_uncovered:
            alert = CompetitiveIntelligenceAlert(
                alert_id=f"coverage_gap_{competitor.competitor_id}",
                alert_type="coverage_gap",
                priority="high",
                title=f"High-threat competitor {competitor.company_name} has no assigned coverage",
                description=f"{competitor.company_name} is marked as high threat but has no assigned analysts or coverage team.",
                affected_employees=[],
                recommended_actions=[
                    f"Assign primary analyst to {competitor.company_name}",
                    "Review threat level assessment",
                    "Create battle cards for sales team"
                ],
                created_at=datetime.utcnow()
            )
            alerts.append(alert)
        
        # Training due alerts
        employees = await self.get_pay_ready_org_chart()
        training_due = [
            emp for emp in employees
            if emp.competitive_focus_areas and (
                emp.last_competitive_training is None or 
                emp.last_competitive_training < datetime.utcnow() - timedelta(days=90)
            )
        ]
        
        if training_due:
            alert = CompetitiveIntelligenceAlert(
                alert_id="training_due_competitive",
                alert_type="training_due",
                priority="medium",
                title=f"{len(training_due)} employees need competitive intelligence training",
                description="Employees with competitive responsibilities haven't had training in 90+ days",
                affected_employees=[emp.email for emp in training_due],
                recommended_actions=[
                    "Schedule competitive intelligence training session",
                    "Update battle cards and competitive materials",
                    "Review competitive win rates"
                ],
                created_at=datetime.utcnow()
            )
            alerts.append(alert)
        
        return alerts
    
    # =====================================================================
    # EXECUTIVE DASHBOARD INTEGRATION
    # =====================================================================
    
    async def get_executive_competitive_summary(self) -> Dict[str, Any]:
        """Get executive-level competitive intelligence summary"""
        try:
            executives = await self.get_executive_team()
            competitors = await self.get_competitors_with_coverage()
            dept_analysis = await self.get_department_competitive_analysis()
            alerts = await self.generate_competitive_intelligence_alerts()
            
            # Calculate summary metrics
            total_employees = len(await self.get_pay_ready_org_chart())
            high_threat_competitors = len([c for c in competitors if c.threat_level == "high"])
            coverage_gaps = len([c for c in competitors if c.coverage_strength == 0])
            avg_win_rate = sum(dept["avg_win_rate"] for dept in dept_analysis) / len(dept_analysis) if dept_analysis else 0
            
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "executive_team": {
                    "count": len(executives),
                    "members": [
                        {
                            "name": exec.full_name,
                            "role": exec.executive_role.value,
                            "competitive_focus": exec.competitive_focus_areas,
                            "win_rate": exec.competitive_win_rate
                        } for exec in executives
                    ]
                },
                "organizational_metrics": {
                    "total_employees": total_employees,
                    "departments": len(dept_analysis),
                    "avg_competitive_win_rate": avg_win_rate,
                    "employees_with_competitive_focus": len([
                        emp for emp in await self.get_pay_ready_org_chart() 
                        if emp.competitive_focus_areas
                    ])
                },
                "competitive_landscape": {
                    "total_competitors": len(competitors),
                    "high_threat_competitors": high_threat_competitors,
                    "coverage_gaps": coverage_gaps,
                    "avg_coverage_per_competitor": sum(c.coverage_strength for c in competitors) / len(competitors) if competitors else 0
                },
                "alerts": {
                    "total_alerts": len(alerts),
                    "high_priority": len([a for a in alerts if a.priority == "high"]),
                    "coverage_gaps": len([a for a in alerts if a.alert_type == "coverage_gap"]),
                    "training_due": len([a for a in alerts if a.alert_type == "training_due"])
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive competitive summary: {e}")
            return {}
    
    # =====================================================================
    # HELPER METHODS
    # =====================================================================
    
    async def _execute_foundational_query(self, query: str, parameters: List[Any] = None) -> List[Any]:
        """Execute SQL query against foundational knowledge database"""
        try:
            # This would use your actual Snowflake/Cortex connection
            # For now, return mock data structure
            logger.info(f"Executing foundational query: {query[:100]}...")
            
            # Mock implementation - replace with actual database connection
            if "VW_PAY_READY_ORG_CHART" in query:
                return [
                    # Mock data for executives
                    ["emp_lynn_musil", "Lynn Patrick Musil", "lynn@payready.com", "Chief Executive Officer", 
                     "Executive", None, None, 1, "CEO", ["EliseAI", "Entrata"], ["Multifamily"], 
                     ["Strategic Planning"], ["National"], 85.0, "full", None, 2, 78.5],
                    ["emp_tiffany_york", "Tiffany York", "tiffany@payready.com", "Chief Product Officer",
                     "Product", "emp_lynn_musil", "Lynn Patrick Musil", 2, "CPO", ["EliseAI"], 
                     ["Multifamily"], ["Product Strategy"], ["West Coast"], 82.0, "full", None, 5, 75.2],
                    ["emp_steve_gabel", "Steve Gabel", "steve@payready.com", "VP Strategic Initiatives",
                     "Strategy", "emp_lynn_musil", "Lynn Patrick Musil", 2, "VP_Strategic", 
                     ["Market Analysis"], ["All Segments"], ["Strategic Planning"], ["National"], 
                     78.0, "full", None, 3, 73.1]
                ]
            elif "VW_DEPARTMENT_COMPETITIVE_ANALYSIS" in query:
                return [
                    ["Executive", 3, 81.7, "EliseAI,Entrata", "Multifamily,Student Housing", "Strategic Planning", 3, 1],
                    ["Product", 8, 76.3, "EliseAI,PropertyRadar", "Multifamily", "Product Strategy", 5, 6],
                    ["Sales", 12, 74.8, "EliseAI,Entrata", "Multifamily", "Sales", 8, 9]
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error executing foundational query: {e}")
            return []
    
    # =====================================================================
    # INTEGRATION WITH EXISTING SOPHIA AI SERVICES
    # =====================================================================
    
    async def integrate_with_unified_dashboard(self) -> Dict[str, Any]:
        """Provide data for integration with the unified dashboard"""
        try:
            summary = await self.get_executive_competitive_summary()
            
            # Format for dashboard consumption
            dashboard_data = {
                "organizational_overview": {
                    "executive_team_health": {
                        "total_executives": summary["executive_team"]["count"],
                        "avg_win_rate": sum(
                            exec["win_rate"] for exec in summary["executive_team"]["members"]
                        ) / summary["executive_team"]["count"] if summary["executive_team"]["members"] else 0,
                        "competitive_coverage": "Full"
                    },
                    "department_performance": summary["organizational_metrics"],
                    "competitive_posture": summary["competitive_landscape"]
                },
                "alerts_summary": summary["alerts"],
                "recommended_actions": await self._generate_executive_recommendations(summary)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error integrating with unified dashboard: {e}")
            return {}
    
    async def _generate_executive_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate executive-level recommendations based on organizational and competitive data"""
        recommendations = []
        
        # Coverage gap recommendations
        if summary["competitive_landscape"]["coverage_gaps"] > 0:
            recommendations.append(
                f"Address {summary['competitive_landscape']['coverage_gaps']} competitor coverage gaps"
            )
        
        # Win rate recommendations
        avg_win_rate = summary["organizational_metrics"]["avg_competitive_win_rate"]
        if avg_win_rate < 75.0:
            recommendations.append(
                f"Improve competitive win rate from {avg_win_rate:.1f}% (target: 75%+)"
            )
        
        # Training recommendations
        if summary["alerts"]["training_due"] > 0:
            recommendations.append("Update competitive intelligence training program")
        
        return recommendations 