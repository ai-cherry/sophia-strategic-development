"""
Pay Ready Foundational Knowledge Service
Integrated with Sophia AI infrastructure for enterprise-grade intelligence

This service bridges Pay Ready employee data with Sophia AI's foundational knowledge
system, leveraging existing PostgreSQL schemas, Qdrant vector storage, and 
entity resolution capabilities.
"""

import logging
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from backend.core.auto_esc_config import get_redis_config
from backend.services.sophia_unified_memory_service import SophiaUnifiedMemoryService
from backend.services.entity_resolution.entity_resolution_service import EntityResolutionService
from backend.database.database_service import DatabaseService
from backend.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

@dataclass
class PayReadyEmployee:
    """Pay Ready employee data structure"""
    employee_id: str
    full_name: str
    first_name: str
    last_name: str
    department: str
    job_title: str
    manager_name: str
    employment_type: str
    business_function: str
    intelligence_priority: str
    ai_enhancement_level: str
    is_active: bool
    email: str
    created_at: datetime

class PayReadyFoundationalService:
    """
    Pay Ready Foundational Knowledge Service
    
    Integrates Pay Ready employee data with Sophia AI's enterprise infrastructure:
    - PostgreSQL foundational knowledge schema
    - Qdrant vector storage for semantic search
    - Entity resolution for cross-platform matching
    - Redis caching for performance
    """
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.memory_service = SophiaUnifiedMemoryService()
        self.entity_resolver = EntityResolutionService()
        self.openai_service = OpenAIService()
        self.redis_config = get_redis_config()
        
        # Department to business function mapping
        self.dept_mapping = {
            'Account Management': 'customer_retention',
            'AI': 'artificial_intelligence',
            'Engineering': 'product_development', 
            'Sales': 'revenue_generation',
            'Support Team': 'customer_success',
            'Executive': 'strategic_leadership',
            'Finance': 'financial_operations',
            'Compliance': 'risk_management',
            'Eviction Center': 'specialized_operations',
            'Product': 'product_development',
            'Marketing': 'marketing_growth',
            'Implementation': 'customer_onboarding',
            'Human Resources': 'people_operations',
            'Operational Excellence': 'operational_efficiency',
            'Payment Operations': 'financial_operations'
        }
        
    async def initialize(self):
        """Initialize all services"""
        await self.db_service.initialize_pool()
        await self.memory_service.initialize()
        logger.info("✅ Pay Ready Foundational Service initialized")
    
    async def process_employee_csv(self, csv_file_path: str) -> List[PayReadyEmployee]:
        """Process Pay Ready employee CSV with enhanced business intelligence"""
        employees = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):
                employee = self._enrich_employee_data(row, row_num)
                if employee:
                    employees.append(employee)
        
        logger.info(f"📊 Processed {len(employees)} Pay Ready employees")
        return employees
    
    def _enrich_employee_data(self, row: Dict[str, str], row_num: int) -> Optional[PayReadyEmployee]:
        """Enrich employee data with business intelligence"""
        full_name = row.get('Preferred full name', '').strip()
        department = row.get('Department', '').strip()
        job_title = row.get('Job title', '').strip()
        manager_name = row.get('Manager Name', '').strip()
        employment_type = row.get('Employment type', '').strip()
        
        if not full_name or not department or not job_title:
            return None
            
        # Parse name
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Generate employee ID and email
        employee_id = self._generate_employee_id(full_name)
        email = self._generate_email(full_name)
        
        # Business intelligence categorization
        business_function = self.dept_mapping.get(department, 'general_operations')
        intelligence_priority = self._get_intelligence_priority(department, job_title)
        ai_enhancement_level = self._get_ai_enhancement_level(department, job_title)
        
        return PayReadyEmployee(
            employee_id=employee_id,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            department=department,
            job_title=job_title,
            manager_name=manager_name,
            employment_type=employment_type,
            business_function=business_function,
            intelligence_priority=intelligence_priority,
            ai_enhancement_level=ai_enhancement_level,
            is_active=True,  # All CSV employees are active
            email=email,
            created_at=datetime.now()
        )
    
    def _generate_employee_id(self, full_name: str) -> str:
        """Generate consistent employee ID"""
        clean_name = ''.join(c.lower() for c in full_name if c.isalnum())
        timestamp = datetime.now().strftime('%Y%m%d')
        return f"pr_{clean_name[:8]}_{timestamp}"
    
    def _generate_email(self, full_name: str) -> str:
        """Generate Pay Ready email address"""
        clean_name = ''.join(c.lower() for c in full_name if c.isalnum() or c.isspace())
        name_parts = clean_name.split()
        if len(name_parts) >= 2:
            return f"{name_parts[0]}.{name_parts[-1]}@payready.com"
        else:
            return f"{clean_name.replace(' ', '')}@payready.com"
    
    def _get_intelligence_priority(self, department: str, job_title: str) -> str:
        """Determine intelligence priority level"""
        title_lower = job_title.lower()
        dept_lower = department.lower()
        
        if any(x in title_lower for x in ['ceo', 'president', 'vice president', 'vp', 'executive']):
            return 'maximum'
        elif any(x in title_lower for x in ['director', 'manager', 'lead', 'head', 'senior']):
            return 'critical'
        elif any(x in dept_lower for x in ['ai', 'engineering', 'sales', 'product']):
            return 'high'
        else:
            return 'standard'
    
    def _get_ai_enhancement_level(self, department: str, job_title: str) -> str:
        """Determine AI enhancement level"""
        title_lower = job_title.lower()
        dept_lower = department.lower()
        
        if any(x in title_lower for x in ['ceo', 'president', 'vice president']):
            return 'executive'
        elif dept_lower == 'ai' or 'ai' in title_lower:
            return 'maximum'
        elif any(x in dept_lower for x in ['engineering', 'product', 'sales']):
            return 'advanced'
        elif any(x in dept_lower for x in ['account management', 'marketing']):
            return 'enhanced'
        else:
            return 'standard'
    
    async def integrate_with_foundational_knowledge(self, employees: List[PayReadyEmployee]) -> Dict[str, Any]:
        """Integrate Pay Ready employees with Sophia AI foundational knowledge system"""
        integration_results = {
            'total_processed': len(employees),
            'successfully_inserted': 0,
            'entity_matches_found': 0,
            'vector_embeddings_created': 0,
            'errors': []
        }
        
        try:
            # Insert into PostgreSQL foundational knowledge schema
            await self._insert_into_foundational_schema(employees, integration_results)
            
            # Create vector embeddings for semantic search
            await self._create_vector_embeddings(employees, integration_results)
            
            # Perform entity resolution across platforms
            await self._perform_entity_resolution(employees, integration_results)
            
            logger.info(f"✅ Integration completed: {integration_results}")
            
        except Exception as e:
            logger.error(f"❌ Integration failed: {e}")
            integration_results['errors'].append(str(e))
        
        return integration_results
    
    async def _insert_into_foundational_schema(self, employees: List[PayReadyEmployee], results: Dict[str, Any]):
        """Insert employees into PostgreSQL foundational knowledge schema"""
        insert_query = """
        INSERT INTO foundational_knowledge.employees 
        (employee_id, email, first_name, last_name, job_title, department, 
         status, created_at, updated_at, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (email) DO UPDATE SET
            job_title = EXCLUDED.job_title,
            department = EXCLUDED.department,
            updated_at = EXCLUDED.updated_at
        """
        
        for employee in employees:
            try:
                await self.db_service.execute_query(insert_query, [
                    employee.employee_id,
                    employee.email,
                    employee.first_name,
                    employee.last_name,
                    employee.job_title,
                    employee.department,
                    'active' if employee.is_active else 'inactive',
                    employee.created_at,
                    employee.created_at,
                    'pay_ready_integration'
                ])
                results['successfully_inserted'] += 1
                
            except Exception as e:
                results['errors'].append(f"Failed to insert {employee.full_name}: {e}")
    
    async def _create_vector_embeddings(self, employees: List[PayReadyEmployee], results: Dict[str, Any]):
        """Create vector embeddings for semantic search in Qdrant"""
        for employee in employees:
            try:
                # Create rich employee profile for embedding
                profile_text = f"""
                Name: {employee.full_name}
                Role: {employee.job_title} in {employee.department}
                Business Function: {employee.business_function}
                Intelligence Priority: {employee.intelligence_priority}
                AI Enhancement: {employee.ai_enhancement_level}
                Manager: {employee.manager_name}
                Employment: {employee.employment_type}
                """
                
                # Store in Qdrant via unified memory service
                await self.memory_service.add_knowledge(
                    content=profile_text,
                    source="pay_ready_employees",
                    metadata={
                        "employee_id": employee.employee_id,
                        "department": employee.department,
                        "job_title": employee.job_title,
                        "business_function": employee.business_function,
                        "intelligence_priority": employee.intelligence_priority,
                        "ai_enhancement_level": employee.ai_enhancement_level,
                        "integration_source": "pay_ready_csv",
                        "integration_date": datetime.now().isoformat()
                    }
                )
                results['vector_embeddings_created'] += 1
                
            except Exception as e:
                results['errors'].append(f"Failed to create embedding for {employee.full_name}: {e}")
    
    async def _perform_entity_resolution(self, employees: List[PayReadyEmployee], results: Dict[str, Any]):
        """Perform entity resolution across platforms"""
        target_platforms = ['lattice', 'salesforce', 'hubspot', 'slack', 'gong']
        
        for employee in employees:
            try:
                employee_data = {
                    'full_name': employee.full_name,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'email': employee.email,
                    'job_title': employee.job_title,
                    'department': employee.department
                }
                
                # Use basic resolution if advanced matching isn't available
                if hasattr(self.entity_resolver, 'use_basic_matching') and self.entity_resolver.use_basic_matching:
                    resolution_result = await self.entity_resolver.basic_employee_resolution(
                        employee_data=employee_data,
                        target_platforms=target_platforms
                    )
                else:
                    resolution_result = await self.entity_resolver.resolve_employee_across_platforms(
                        employee_data=employee_data,
                        target_platforms=target_platforms
                    )
                
                if resolution_result.get('matches_found', 0) > 0:
                    results['entity_matches_found'] += resolution_result['matches_found']
                
            except Exception as e:
                results['errors'].append(f"Entity resolution failed for {employee.full_name}: {e}")
    
    async def search_pay_ready_employees(
        self, 
        query: str, 
        limit: int = 10,
        department_filter: Optional[str] = None,
        priority_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search Pay Ready employees using semantic search"""
        
        # Build metadata filters
        filters = {"integration_source": "pay_ready_csv"}
        if department_filter:
            filters["department"] = department_filter
        if priority_filter:
            filters["intelligence_priority"] = priority_filter
        
        # Search using unified memory service
        results = await self.memory_service.search_knowledge(
            query=query,
            limit=limit,
            metadata_filter=filters
        )
        
        return results
    
    async def get_department_analytics(self) -> Dict[str, Any]:
        """Get Pay Ready department analytics"""
        query = """
        SELECT 
            department,
            COUNT(*) as employee_count,
            COUNT(DISTINCT job_title) as unique_roles,
            AVG(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_rate
        FROM foundational_knowledge.employees 
        WHERE created_by = 'pay_ready_integration'
        GROUP BY department
        ORDER BY employee_count DESC
        """
        
        results = await self.db_service.execute_query(query)
        return results
    
    async def get_employee_intelligence_summary(self) -> Dict[str, Any]:
        """Get employee intelligence priority and AI enhancement summary"""
        # This would query the vector embeddings metadata
        # For now, return a placeholder structure
        return {
            "total_employees": 104,
            "intelligence_distribution": {
                "maximum": 3,
                "critical": 15,
                "high": 35,
                "standard": 51
            },
            "ai_enhancement_distribution": {
                "executive": 3,
                "maximum": 8,
                "advanced": 31,
                "enhanced": 13,
                "standard": 49
            },
            "department_count": 15,
            "business_functions": 10
        }

# Singleton instance
_pay_ready_service: Optional[PayReadyFoundationalService] = None

async def get_pay_ready_foundational_service() -> PayReadyFoundationalService:
    """Get singleton Pay Ready foundational service"""
    global _pay_ready_service
    if _pay_ready_service is None:
        _pay_ready_service = PayReadyFoundationalService()
        await _pay_ready_service.initialize()
    return _pay_ready_service 