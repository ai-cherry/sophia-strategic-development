from backend.services.knowledge_service import KnowledgeService
"""
Foundational Knowledge Service
Manages Pay Ready's foundational business information and integrates it with the existing knowledge base
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.core.logger import logger

# logger = logging.getLogger(__name__)


class FoundationalDataType(Enum):
    """Types of foundational knowledge data"""

    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    PRODUCT = "product"
    COMPETITOR = "competitor"
    PROCESS = "business_process"
    VALUE = "organizational_value"
    ARTICLE = "knowledge_article"


@dataclass
class FoundationalRecord:
    """Represents a foundational knowledge record"""

    record_id: str
    data_type: FoundationalDataType
    title: str
    description: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    last_updated: Optional[datetime] = None


class FoundationalKnowledgeService:
    """Service for managing foundational Pay Ready knowledge"""

    def __init__(self):
        self.cortex_service = SnowflakeCortexService()
        self.knowledge_service = KnowledgeService()
        self.schema = "FOUNDATIONAL_KNOWLEDGE"

    async def sync_foundational_data_to_knowledge_base(self) -> Dict[str, Any]:
        """
        Sync all foundational data from Snowflake to the knowledge base system

        Returns:
            Summary of sync operation
        """
        try:
            logger.info("Starting foundational knowledge sync to knowledge base")

            sync_results = {
                "total_records": 0,
                "synced_records": 0,
                "failed_records": 0,
                "data_types": {},
                "errors": [],
            }

            # Sync each data type
            for data_type in FoundationalDataType:
                try:
                    result = await self._sync_data_type(data_type)
                    sync_results["data_types"][data_type.value] = result
                    sync_results["total_records"] += result["total"]
                    sync_results["synced_records"] += result["synced"]
                    sync_results["failed_records"] += result["failed"]
                except Exception as e:
                    error_msg = f"Failed to sync {data_type.value}: {str(e)}"
                    logger.error(error_msg)
                    sync_results["errors"].append(error_msg)

            logger.info(
                f"Foundational knowledge sync completed: {sync_results['synced_records']}/{sync_results['total_records']} records synced"
            )
            return sync_results

        except Exception as e:
            logger.error(f"Foundational knowledge sync failed: {str(e)}")
            raise

    async def _sync_data_type(self, data_type: FoundationalDataType) -> Dict[str, int]:
        """Sync a specific data type to knowledge base"""

        # Get records from Snowflake
        records = await self._get_foundational_records(data_type)

        result = {"total": len(records), "synced": 0, "failed": 0}

        for record in records:
            try:
                # Convert to knowledge base document format
                document = await self._convert_to_knowledge_document(record)

                # Add to knowledge base through existing service
                await self.knowledge_service.add_document_to_knowledge_base(document)

                result["synced"] += 1

            except Exception as e:
                logger.error(f"Failed to sync record {record.record_id}: {str(e)}")
                result["failed"] += 1

        return result

    async def _get_foundational_records(
        self, data_type: FoundationalDataType
    ) -> List[FoundationalRecord]:
        """Get foundational records from Snowflake by type"""

        queries = {
            FoundationalDataType.EMPLOYEE: """
                SELECT 
                    EMPLOYEE_ID as record_id,
                    FULL_NAME as title,
                    (DEPARTMENT || ' - ' || JOB_TITLE || ' - ' || COALESCE(ARRAY_TO_STRING(PRIMARY_SKILLS, ', '), '')) as description,
                    OBJECT_CONSTRUCT(
                        'department', DEPARTMENT,
                        'job_title', JOB_TITLE,
                        'email', EMAIL_ADDRESS,
                        'skills', PRIMARY_SKILLS,
                        'location', LOCATION,
                        'hire_date', HIRE_DATE
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
                WHERE EMPLOYMENT_STATUS = 'Active'
            """,
            FoundationalDataType.CUSTOMER: """
                SELECT 
                    CUSTOMER_ID as record_id,
                    COMPANY_NAME as title,
                    (INDUSTRY || ' - ' || CUSTOMER_SEGMENT || ' - ' || BUSINESS_MODEL) as description,
                    OBJECT_CONSTRUCT(
                        'industry', INDUSTRY,
                        'segment', CUSTOMER_SEGMENT,
                        'business_model', BUSINESS_MODEL,
                        'tier', CUSTOMER_TIER,
                        'website', COMPANY_WEBSITE,
                        'size', COMPANY_SIZE,
                        'revenue_range', ANNUAL_REVENUE_RANGE
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.CUSTOMERS
                WHERE CUSTOMER_STATUS = 'Active'
            """,
            FoundationalDataType.PRODUCT: """
                SELECT 
                    PRODUCT_ID as record_id,
                    PRODUCT_NAME as title,
                    (PRODUCT_DESCRIPTION || ' - ' || PRODUCT_CATEGORY || ' - ' || PRICING_MODEL) as description,
                    OBJECT_CONSTRUCT(
                        'category', PRODUCT_CATEGORY,
                        'type', PRODUCT_TYPE,
                        'pricing_model', PRICING_MODEL,
                        'value_proposition', VALUE_PROPOSITION,
                        'benefits', KEY_BENEFITS,
                        'target_segment', TARGET_CUSTOMER_SEGMENT
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.PRODUCTS_SERVICES
                WHERE PRODUCT_STATUS = 'Active'
            """,
            FoundationalDataType.COMPETITOR: """
                SELECT 
                    COMPETITOR_ID as record_id,
                    COMPANY_NAME as title,
                    (COMPANY_DESCRIPTION || ' - ' || MARKET_SEGMENT || ' - Threat: ' || THREAT_LEVEL) as description,
                    OBJECT_CONSTRUCT(
                        'market_segment', MARKET_SEGMENT,
                        'threat_level', THREAT_LEVEL,
                        'competitive_tier', COMPETITIVE_TIER,
                        'strengths', STRENGTHS,
                        'weaknesses', WEAKNESSES,
                        'website', COMPANY_WEBSITE,
                        'win_rate', WIN_RATE
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.COMPETITORS
            """,
            FoundationalDataType.PROCESS: """
                SELECT 
                    PROCESS_ID as record_id,
                    PROCESS_NAME as title,
                    (PROCESS_DESCRIPTION || ' - ' || PROCESS_CATEGORY) as description,
                    OBJECT_CONSTRUCT(
                        'category', PROCESS_CATEGORY,
                        'type', PROCESS_TYPE,
                        'owner', PROCESS_OWNER_EMPLOYEE_ID,
                        'steps', PROCESS_STEPS,
                        'tools', REQUIRED_TOOLS,
                        'skills', REQUIRED_SKILLS,
                        'documentation_url', PROCESS_DOCUMENTATION_URL
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.BUSINESS_PROCESSES
                WHERE PROCESS_STATUS = 'Active'
            """,
            FoundationalDataType.VALUE: """
                SELECT 
                    VALUE_ID as record_id,
                    VALUE_NAME as title,
                    (VALUE_STATEMENT || ' - ' || VALUE_TYPE) as description,
                    OBJECT_CONSTRUCT(
                        'type', VALUE_TYPE,
                        'statement', VALUE_STATEMENT,
                        'description', VALUE_DESCRIPTION,
                        'contexts', APPLICABLE_CONTEXTS,
                        'examples', BEHAVIORAL_EXAMPLES,
                        'priority', PRIORITY_LEVEL
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.ORGANIZATIONAL_VALUES
                WHERE IS_ACTIVE = TRUE
            """,
            FoundationalDataType.ARTICLE: """
                SELECT 
                    ARTICLE_ID as record_id,
                    ARTICLE_TITLE as title,
                    COALESCE(ARTICLE_SUMMARY, SUBSTR(ARTICLE_CONTENT, 1, 500)) as description,
                    OBJECT_CONSTRUCT(
                        'category', ARTICLE_CATEGORY,
                        'type', ARTICLE_TYPE,
                        'author', AUTHOR_EMPLOYEE_ID,
                        'keywords', KEYWORDS,
                        'tags', TAGS,
                        'visibility', VISIBILITY_LEVEL,
                        'content_format', CONTENT_FORMAT,
                        'view_count', VIEW_COUNT
                    ) as metadata,
                    AI_MEMORY_EMBEDDING as embedding,
                    UPDATED_AT as last_updated
                FROM FOUNDATIONAL_KNOWLEDGE.KNOWLEDGE_ARTICLES
                WHERE CONTENT_STATUS = 'Published'
            """,
        }

        query = queries.get(data_type)
        if not query:
            return []

        try:
            # Execute query through Cortex service
            result = await self.cortex_service.execute_query(query)

            records = []
            for row in result:
                record = FoundationalRecord(
                    record_id=row[0],
                    data_type=data_type,
                    title=row[1],
                    description=row[2],
                    metadata=json.loads(row[3]) if row[3] else {},
                    embedding=row[4] if row[4] else None,
                    last_updated=row[5] if row[5] else None,
                )
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"Failed to fetch {data_type.value} records: {str(e)}")
            return []

    async def _convert_to_knowledge_document(
        self, record: FoundationalRecord
    ) -> Dict[str, Any]:
        """Convert foundational record to knowledge base document format"""

        return {
            "id": f"foundational_{record.data_type.value}_{record.record_id}",
            "title": record.title,
            "content": record.description,
            "source": "foundational_knowledge",
            "source_type": record.data_type.value,
            "metadata": {
                **record.metadata,
                "foundational_type": record.data_type.value,
                "source_id": record.record_id,
                "last_updated": (
                    record.last_updated.isoformat() if record.last_updated else None
                ),
            },
            "embedding": record.embedding,
            "tags": [
                record.data_type.value,
                "foundational",
                "payready",
                record.metadata.get("category", ""),
                record.metadata.get("department", ""),
                record.metadata.get("type", ""),
            ],
            "category": f"foundational_{record.data_type.value}",
            "importance_score": self._calculate_importance_score(record),
            "auto_detected": False,
        }

    def _calculate_importance_score(self, record: FoundationalRecord) -> float:
        """Calculate importance score based on record type and metadata"""

        base_scores = {
            FoundationalDataType.EMPLOYEE: 0.7,
            FoundationalDataType.CUSTOMER: 0.9,  # High importance for customer data
            FoundationalDataType.PRODUCT: 0.8,  # High importance for product data
            FoundationalDataType.COMPETITOR: 0.8,  # High importance for competitive intel
            FoundationalDataType.PROCESS: 0.6,
            FoundationalDataType.VALUE: 0.5,
            FoundationalDataType.ARTICLE: 0.6,
        }

        base_score = base_scores.get(record.data_type, 0.5)

        # Adjust based on metadata
        if record.data_type == FoundationalDataType.CUSTOMER:
            tier = record.metadata.get("tier", "").lower()
            if tier == "strategic":
                base_score = 0.95
            elif tier == "key":
                base_score = 0.9

        elif record.data_type == FoundationalDataType.COMPETITOR:
            threat = record.metadata.get("threat_level", "").lower()
            if threat == "high":
                base_score = 0.9
            elif threat == "medium":
                base_score = 0.7

        elif record.data_type == FoundationalDataType.EMPLOYEE:
            level = record.metadata.get("job_title", "").lower()
            if any(title in level for title in ["ceo", "vp", "director"]):
                base_score = 0.8

        return min(base_score, 1.0)

    async def search_foundational_knowledge(
        self,
        query: str,
        data_types: Optional[List[FoundationalDataType]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search foundational knowledge using semantic search

        Args:
            query: Search query
            data_types: Optional filter by data types
            limit: Maximum results to return

        Returns:
            List of matching foundational knowledge records
        """
        try:
            # Use existing knowledge service search with foundational filters
            search_filters = {"source": "foundational_knowledge"}

            if data_types:
                search_filters["source_type"] = [dt.value for dt in data_types]

            results = await self.knowledge_service.semantic_search(
                query=query, filters=search_filters, limit=limit
            )

            return results

        except Exception as e:
            logger.error(f"Foundational knowledge search failed: {str(e)}")
            return []

    async def get_foundational_stats(self) -> Dict[str, Any]:
        """Get statistics about foundational knowledge in the knowledge base"""

        try:
            stats_query = """
            SELECT 
                metadata:foundational_type::string as data_type,
                COUNT(*) as count,
                AVG(importance_score) as avg_importance,
                MAX(last_updated) as last_updated
            FROM knowledge_base_documents
            WHERE source = 'foundational_knowledge'
            GROUP BY metadata:foundational_type::string
            """

            result = await self.cortex_service.execute_query(stats_query)

            stats = {
                "total_foundational_records": 0,
                "data_types": {},
                "last_sync": None,
            }

            for row in result:
                data_type = row[0]
                count = row[1]
                avg_importance = row[2]
                last_updated = row[3]

                stats["data_types"][data_type] = {
                    "count": count,
                    "avg_importance": float(avg_importance) if avg_importance else 0.0,
                    "last_updated": last_updated,
                }
                stats["total_foundational_records"] += count

                if last_updated and (
                    not stats["last_sync"] or last_updated > stats["last_sync"]
                ):
                    stats["last_sync"] = last_updated

            return stats

        except Exception as e:
            logger.error(f"Failed to get foundational stats: {str(e)}")
            return {
                "total_foundational_records": 0,
                "data_types": {},
                "last_sync": None,
            }

    async def update_foundational_record(
        self, record_id: str, data_type: FoundationalDataType, updates: Dict[str, Any]
    ) -> bool:
        """
        Update a foundational record in both Snowflake and knowledge base

        Args:
            record_id: ID of the record to update
            data_type: Type of foundational data
            updates: Dictionary of field updates

        Returns:
            True if update successful, False otherwise
        """
        try:
            # Update in Snowflake first
            table_map = {
                FoundationalDataType.EMPLOYEE: "EMPLOYEES",
                FoundationalDataType.CUSTOMER: "CUSTOMERS",
                FoundationalDataType.PRODUCT: "PRODUCTS_SERVICES",
                FoundationalDataType.COMPETITOR: "COMPETITORS",
                FoundationalDataType.PROCESS: "BUSINESS_PROCESSES",
                FoundationalDataType.VALUE: "ORGANIZATIONAL_VALUES",
                FoundationalDataType.ARTICLE: "KNOWLEDGE_ARTICLES",
            }

            table_name = table_map.get(data_type)
            if not table_name:
                return False

            # Build update query
            set_clauses = []
            for field, value in updates.items():
                if isinstance(value, str):
                    set_clauses.append(f"{field} = '{value}'")
                else:
                    set_clauses.append(f"{field} = {value}")

            update_query = f"""
            UPDATE FOUNDATIONAL_KNOWLEDGE.{table_name}
            SET {', '.join(set_clauses)}, UPDATED_AT = CURRENT_TIMESTAMP()
            WHERE {self._get_primary_key_field(data_type)} = '{record_id}'
            """

            await self.cortex_service.execute_query(update_query)

            # Re-sync this record to knowledge base
            records = await self._get_foundational_records(data_type)
            updated_record = next(
                (r for r in records if r.record_id == record_id), None
            )

            if updated_record:
                document = await self._convert_to_knowledge_document(updated_record)
                await self.knowledge_service.update_document_in_knowledge_base(document)

            logger.info(f"Updated foundational record {record_id} ({data_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to update foundational record {record_id}: {str(e)}")
            return False

    def _get_primary_key_field(self, data_type: FoundationalDataType) -> str:
        """Get the primary key field name for a data type"""

        key_map = {
            FoundationalDataType.EMPLOYEE: "EMPLOYEE_ID",
            FoundationalDataType.CUSTOMER: "CUSTOMER_ID",
            FoundationalDataType.PRODUCT: "PRODUCT_ID",
            FoundationalDataType.COMPETITOR: "COMPETITOR_ID",
            FoundationalDataType.PROCESS: "PROCESS_ID",
            FoundationalDataType.VALUE: "VALUE_ID",
            FoundationalDataType.ARTICLE: "ARTICLE_ID",
        }

        return key_map.get(data_type, "ID")

    async def generate_foundational_insights(self) -> Dict[str, Any]:
        """
        Generate insights about foundational knowledge using Snowflake Cortex

        Returns:
            Dictionary containing various insights about the foundational knowledge
        """
        try:
            insights = {}

            # Employee insights
            employee_insights_query = """
            SELECT 
                DEPARTMENT,
                COUNT(*) as employee_count,
                ARRAY_AGG(DISTINCT JOB_TITLE) as job_titles,
                AVG(DATEDIFF('year', HIRE_DATE, CURRENT_DATE())) as avg_tenure_years
            FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
            WHERE EMPLOYMENT_STATUS = 'Active'
            GROUP BY DEPARTMENT
            ORDER BY employee_count DESC
            """

            employee_result = await self.cortex_service.execute_query(
                employee_insights_query
            )
            insights["departments"] = [
                {
                    "department": row[0],
                    "employee_count": row[1],
                    "job_titles": row[2],
                    "avg_tenure_years": float(row[3]) if row[3] else 0.0,
                }
                for row in employee_result
            ]

            # Customer insights
            customer_insights_query = """
            SELECT 
                CUSTOMER_SEGMENT,
                COUNT(*) as customer_count,
                AVG(PAYMENT_PROCESSING_VOLUME_MONTHLY) as avg_monthly_volume,
                COUNT(DISTINCT INDUSTRY) as industry_diversity
            FROM FOUNDATIONAL_KNOWLEDGE.CUSTOMERS
            WHERE CUSTOMER_STATUS = 'Active'
            GROUP BY CUSTOMER_SEGMENT
            ORDER BY customer_count DESC
            """

            customer_result = await self.cortex_service.execute_query(
                customer_insights_query
            )
            insights["customer_segments"] = [
                {
                    "segment": row[0],
                    "customer_count": row[1],
                    "avg_monthly_volume": float(row[2]) if row[2] else 0.0,
                    "industry_diversity": row[3],
                }
                for row in customer_result
            ]

            # Competitive landscape
            competitive_query = """
            SELECT 
                THREAT_LEVEL,
                COUNT(*) as competitor_count,
                AVG(WIN_RATE) as avg_win_rate_against_us,
                ARRAY_AGG(COMPANY_NAME) as competitors
            FROM FOUNDATIONAL_KNOWLEDGE.COMPETITORS
            GROUP BY THREAT_LEVEL
            ORDER BY 
                CASE THREAT_LEVEL 
                    WHEN 'High' THEN 1 
                    WHEN 'Medium' THEN 2 
                    WHEN 'Low' THEN 3 
                END
            """

            competitive_result = await self.cortex_service.execute_query(
                competitive_query
            )
            insights["competitive_landscape"] = [
                {
                    "threat_level": row[0],
                    "competitor_count": row[1],
                    "avg_win_rate_against_us": float(row[2]) if row[2] else 0.0,
                    "competitors": row[3],
                }
                for row in competitive_result
            ]

            # Product portfolio
            product_query = """
            SELECT 
                PRODUCT_CATEGORY,
                COUNT(*) as product_count,
                SUM(MONTHLY_RECURRING_REVENUE) as total_mrr,
                AVG(CUSTOMER_SATISFACTION_SCORE) as avg_satisfaction
            FROM FOUNDATIONAL_KNOWLEDGE.PRODUCTS_SERVICES
            WHERE PRODUCT_STATUS = 'Active'
            GROUP BY PRODUCT_CATEGORY
            ORDER BY total_mrr DESC
            """

            product_result = await self.cortex_service.execute_query(product_query)
            insights["product_portfolio"] = [
                {
                    "category": row[0],
                    "product_count": row[1],
                    "total_mrr": float(row[2]) if row[2] else 0.0,
                    "avg_satisfaction": float(row[3]) if row[3] else 0.0,
                }
                for row in product_result
            ]

            return insights

        except Exception as e:
            logger.error(f"Failed to generate foundational insights: {str(e)}")
            return {}
