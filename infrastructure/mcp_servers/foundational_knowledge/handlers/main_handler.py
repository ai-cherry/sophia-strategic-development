"""
Foundational Knowledge MCP Server Handler
Simple CRUD operations for foundational knowledge entities
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.auto_esc_config import get_config_value
from shared.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)

class FoundationalKnowledgeHandler:
    """Handler for foundational knowledge operations"""

    def __init__(self):
        self.cortex_service = SnowflakeCortexService()
        self.schema = "FOUNDATIONAL_KNOWLEDGE"

    async def initialize(self):
        """Initialize the handler"""
        await self.cortex_service.initialize()
        logger.info("Foundational Knowledge handler initialized")

    # Employee Operations
    async def create_employee(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new employee record"""
        try:
            # Validate required fields
            required = ['email', 'first_name', 'last_name']
            missing = [f for f in required if f not in data]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            # Build insert query
            columns = list(data.keys())
            values = [f":{col}" for col in columns]

            query = f"""
            INSERT INTO {self.schema}.EMPLOYEES ({', '.join(columns)})
            VALUES ({', '.join(values)})
            """

            await self.cortex_service.execute_query(query, data)

            # Get the created employee
            employee = await self.get_employee_by_email(data['email'])

            return {
                "success": True,
                "employee": employee
            }

        except Exception as e:
            logger.error(f"Failed to create employee: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_employee(self, employee_id: str) -> dict[str, Any] | None:
        """Get employee by ID"""
        try:
            query = f"""
            SELECT * FROM {self.schema}.EMPLOYEES
            WHERE EMPLOYEE_ID = :employee_id
            """

            result = await self.cortex_service.execute_query(
                query,
                {"employee_id": employee_id}
            )

            if result and len(result) > 0:
                return result[0]
            return None

        except Exception as e:
            logger.error(f"Failed to get employee: {e}")
            return None

    async def get_employee_by_email(self, email: str) -> dict[str, Any] | None:
        """Get employee by email"""
        try:
            query = f"""
            SELECT * FROM {self.schema}.EMPLOYEES
            WHERE EMAIL = :email
            """

            result = await self.cortex_service.execute_query(
                query,
                {"email": email}
            )

            if result and len(result) > 0:
                return result[0]
            return None

        except Exception as e:
            logger.error(f"Failed to get employee by email: {e}")
            return None

    async def update_employee(self, employee_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update employee record"""
        try:
            # Remove employee_id from data if present
            data = {k: v for k, v in data.items() if k != 'employee_id'}

            if not data:
                return {
                    "success": False,
                    "error": "No fields to update"
                }

            # Build update query
            set_clauses = [f"{col} = :{col}" for col in data.keys()]

            query = f"""
            UPDATE {self.schema}.EMPLOYEES
            SET {', '.join(set_clauses)}, UPDATED_AT = CURRENT_TIMESTAMP
            WHERE EMPLOYEE_ID = :employee_id
            """

            params = {**data, "employee_id": employee_id}
            await self.cortex_service.execute_query(query, params)

            # Get updated employee
            employee = await self.get_employee(employee_id)

            return {
                "success": True,
                "employee": employee
            }

        except Exception as e:
            logger.error(f"Failed to update employee: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def search_employees(self, search_term: str, limit: int = 50) -> list[dict[str, Any]]:
        """Search employees by name, email, or department"""
        try:
            query = f"""
            SELECT * FROM {self.schema}.EMPLOYEES
            WHERE STATUS = 'active'
              AND (
                LOWER(FIRST_NAME) LIKE LOWER(:search_pattern)
                OR LOWER(LAST_NAME) LIKE LOWER(:search_pattern)
                OR LOWER(EMAIL) LIKE LOWER(:search_pattern)
                OR LOWER(DEPARTMENT) LIKE LOWER(:search_pattern)
                OR LOWER(JOB_TITLE) LIKE LOWER(:search_pattern)
              )
            ORDER BY LAST_NAME, FIRST_NAME
            LIMIT :limit
            """

            params = {
                "search_pattern": f"%{search_term}%",
                "limit": limit
            }

            result = await self.cortex_service.execute_query(query, params)
            return result or []

        except Exception as e:
            logger.error(f"Failed to search employees: {e}")
            return []

    # Customer Operations
    async def create_customer(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new customer record"""
        try:
            # Validate required fields
            if 'company_name' not in data:
                raise ValueError("Missing required field: company_name")

            # Build insert query
            columns = list(data.keys())
            values = [f":{col}" for col in columns]

            query = f"""
            INSERT INTO {self.schema}.CUSTOMERS ({', '.join(columns)})
            VALUES ({', '.join(values)})
            """

            await self.cortex_service.execute_query(query, data)

            # Get the created customer
            customer_query = f"""
            SELECT * FROM {self.schema}.CUSTOMERS
            WHERE COMPANY_NAME = :company_name
            ORDER BY CREATED_AT DESC
            LIMIT 1
            """

            customers = await self.cortex_service.execute_query(
                customer_query,
                {"company_name": data['company_name']}
            )

            return {
                "success": True,
                "customer": customers[0] if customers else None
            }

        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        """Get customer by ID"""
        try:
            query = f"""
            SELECT c.*, e.FIRST_NAME || ' ' || e.LAST_NAME as SUCCESS_MANAGER_NAME
            FROM {self.schema}.CUSTOMERS c
            LEFT JOIN {self.schema}.EMPLOYEES e ON c.SUCCESS_MANAGER_ID = e.EMPLOYEE_ID
            WHERE c.CUSTOMER_ID = :customer_id
            """

            result = await self.cortex_service.execute_query(
                query,
                {"customer_id": customer_id}
            )

            if result and len(result) > 0:
                return result[0]
            return None

        except Exception as e:
            logger.error(f"Failed to get customer: {e}")
            return None

    async def search_customers(self, search_term: str, limit: int = 50) -> list[dict[str, Any]]:
        """Search customers by name or industry"""
        try:
            query = f"""
            SELECT c.*, e.FIRST_NAME || ' ' || e.LAST_NAME as SUCCESS_MANAGER_NAME
            FROM {self.schema}.CUSTOMERS c
            LEFT JOIN {self.schema}.EMPLOYEES e ON c.SUCCESS_MANAGER_ID = e.EMPLOYEE_ID
            WHERE c.STATUS IN ('active', 'prospect')
              AND (
                LOWER(c.COMPANY_NAME) LIKE LOWER(:search_pattern)
                OR LOWER(c.INDUSTRY) LIKE LOWER(:search_pattern)
              )
            ORDER BY c.COMPANY_NAME
            LIMIT :limit
            """

            params = {
                "search_pattern": f"%{search_term}%",
                "limit": limit
            }

            result = await self.cortex_service.execute_query(query, params)
            return result or []

        except Exception as e:
            logger.error(f"Failed to search customers: {e}")
            return []

    # Product Operations
    async def create_product(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new product record"""
        try:
            # Validate required fields
            if 'product_name' not in data:
                raise ValueError("Missing required field: product_name")

            # Build insert query
            columns = list(data.keys())
            values = [f":{col}" for col in columns]

            query = f"""
            INSERT INTO {self.schema}.PRODUCTS ({', '.join(columns)})
            VALUES ({', '.join(values)})
            """

            await self.cortex_service.execute_query(query, data)

            # Get the created product
            product_query = f"""
            SELECT * FROM {self.schema}.PRODUCTS
            WHERE PRODUCT_NAME = :product_name
            ORDER BY CREATED_AT DESC
            LIMIT 1
            """

            products = await self.cortex_service.execute_query(
                product_query,
                {"product_name": data['product_name']}
            )

            return {
                "success": True,
                "product": products[0] if products else None
            }

        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def search_products(self, search_term: str, limit: int = 50) -> list[dict[str, Any]]:
        """Search products by name or category"""
        try:
            query = f"""
            SELECT p.*, e.FIRST_NAME || ' ' || e.LAST_NAME as PRODUCT_MANAGER_NAME
            FROM {self.schema}.PRODUCTS p
            LEFT JOIN {self.schema}.EMPLOYEES e ON p.PRODUCT_MANAGER_ID = e.EMPLOYEE_ID
            WHERE p.STATUS = 'active'
              AND (
                LOWER(p.PRODUCT_NAME) LIKE LOWER(:search_pattern)
                OR LOWER(p.PRODUCT_CATEGORY) LIKE LOWER(:search_pattern)
                OR LOWER(p.DESCRIPTION) LIKE LOWER(:search_pattern)
              )
            ORDER BY p.PRODUCT_NAME
            LIMIT :limit
            """

            params = {
                "search_pattern": f"%{search_term}%",
                "limit": limit
            }

            result = await self.cortex_service.execute_query(query, params)
            return result or []

        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []

    # Competitor Operations
    async def create_competitor(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new competitor record"""
        try:
            # Validate required fields
            if 'company_name' not in data:
                raise ValueError("Missing required field: company_name")

            # Build insert query
            columns = list(data.keys())
            values = [f":{col}" for col in columns]

            query = f"""
            INSERT INTO {self.schema}.COMPETITORS ({', '.join(columns)})
            VALUES ({', '.join(values)})
            """

            await self.cortex_service.execute_query(query, data)

            # Get the created competitor
            competitor_query = f"""
            SELECT * FROM {self.schema}.COMPETITORS
            WHERE COMPANY_NAME = :company_name
            ORDER BY CREATED_AT DESC
            LIMIT 1
            """

            competitors = await self.cortex_service.execute_query(
                competitor_query,
                {"company_name": data['company_name']}
            )

            return {
                "success": True,
                "competitor": competitors[0] if competitors else None
            }

        except Exception as e:
            logger.error(f"Failed to create competitor: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Unified Search
    async def search_all(self, search_term: str, limit: int = 10) -> dict[str, list[dict[str, Any]]]:
        """Search across all entity types"""
        try:
            query = f"""
            CALL {self.schema}.SEARCH_KNOWLEDGE(:search_term)
            """

            result = await self.cortex_service.execute_query(
                query,
                {"search_term": search_term}
            )

            # Group results by entity type
            grouped = {
                "employees": [],
                "customers": [],
                "products": [],
                "competitors": []
            }

            for row in result or []:
                entity_type = row.get('ENTITY_TYPE', '').lower()
                if entity_type == 'employee':
                    grouped['employees'].append(row)
                elif entity_type == 'customer':
                    grouped['customers'].append(row)
                elif entity_type == 'product':
                    grouped['products'].append(row)
                elif entity_type == 'competitor':
                    grouped['competitors'].append(row)

            return grouped

        except Exception as e:
            logger.error(f"Failed to search all entities: {e}")
            return {
                "employees": [],
                "customers": [],
                "products": [],
                "competitors": []
            }

    # Bulk Import Operations
    async def bulk_import_employees(self, employees: list[dict[str, Any]]) -> dict[str, Any]:
        """Bulk import employees from CSV or other sources"""
        try:
            success_count = 0
            error_count = 0
            errors = []

            for emp in employees:
                result = await self.create_employee(emp)
                if result.get('success'):
                    success_count += 1
                else:
                    error_count += 1
                    errors.append({
                        "email": emp.get('email', 'unknown'),
                        "error": result.get('error', 'Unknown error')
                    })

            return {
                "success": True,
                "imported": success_count,
                "failed": error_count,
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Failed to bulk import employees: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Statistics and Health
    async def get_statistics(self) -> dict[str, Any]:
        """Get foundational knowledge statistics"""
        try:
            query = f"""
            SELECT
                (SELECT COUNT(*) FROM {self.schema}.EMPLOYEES WHERE STATUS = 'active') as active_employees,
                (SELECT COUNT(*) FROM {self.schema}.CUSTOMERS WHERE STATUS = 'active') as active_customers,
                (SELECT COUNT(*) FROM {self.schema}.PRODUCTS WHERE STATUS = 'active') as active_products,
                (SELECT COUNT(*) FROM {self.schema}.COMPETITORS) as competitors
            """

            result = await self.cortex_service.execute_query(query)

            if result and len(result) > 0:
                return result[0]

            return {
                "active_employees": 0,
                "active_customers": 0,
                "active_products": 0,
                "competitors": 0
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "active_employees": 0,
                "active_customers": 0,
                "active_products": 0,
                "competitors": 0
            }

# Singleton instance
handler = FoundationalKnowledgeHandler()
