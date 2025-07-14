"""
Enhanced Semantic Layer Service with Fuzzy Text Matching
Implements entity resolution and fuzzy joins for Sophia AI
"""

import logging
import re
from typing import Any, Optional

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class EnhancedSemanticLayerService:
    """Enhanced semantic layer with entity resolution and fuzzy matching capabilities"""

    def __init__(self):
        self.connection = None
        self.entity_resolution_enabled = True
        self.fuzzy_threshold = 0.75

    async def _get_connection(self):
        """Get ModernStack connection with entity resolution schema"""
        if not self.connection:
            # REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3

            self.connection = self.modern_stack_connection(
                user=get_config_value("modern_stack_user"),
                password=get_config_value("postgres_password"),
                account=get_config_value("postgres_host"),
                warehouse=get_config_value("postgres_database"),
                database=get_config_value("postgres_database"),
                schema="SOPHIA_ENTITY_RESOLUTION",  # Default to entity resolution schema
            )
        return self.connection

    async def generate_fuzzy_join_sql(
        self,
        base_table: str,
        join_table: str,
        base_column: str,
        join_column: str,
        join_type: str = "LEFT",
        threshold: float = 0.75,
    ) -> str:
        """Generate SQL for fuzzy text matching joins"""

        if join_type == "FUZZY_TEXT_MATCH":
            # Generate entity-aware fuzzy join
            fuzzy_sql = f"""
            {join_type.replace('FUZZY_TEXT_MATCH', 'LEFT')} JOIN (
                -- Entity-aware fuzzy matching with confidence scoring
                SELECT DISTINCT
                    j.*,
                    fm.entity_id as resolved_entity_id,
                    fm.similarity_score,
                    fm.match_reason
                FROM {join_table} j
                CROSS JOIN TABLE(
                    SOPHIA_ENTITY_RESOLUTION.FIND_ENTITY_MATCHES(
                        j.{join_column}::STRING,
                        NULL, -- entity_type (let it auto-detect)
                        {threshold}
                    )
                ) fm
                WHERE fm.similarity_score >= {threshold}
            ) resolved_entities ON (
                -- Match base table entities to resolved entities
                EXISTS (
                    SELECT 1 FROM TABLE(
                        SOPHIA_ENTITY_RESOLUTION.FIND_ENTITY_MATCHES(
                            {base_table}.{base_column}::STRING,
                            NULL,
                            {threshold}
                        )
                    ) base_match
                    WHERE base_match.entity_id = resolved_entities.resolved_entity_id
                )
            )
            """
        else:
            # Standard join
            fuzzy_sql = f"{join_type} JOIN {join_table} ON {base_table}.{base_column} = {join_table}.{join_column}"

        return fuzzy_sql

    async def build_semantic_query(self, entity_config: dict[str, Any]) -> str:
        """Build semantic query with fuzzy matching support"""

        base_table = entity_config["base_table"]
        entity_name = entity_config["name"]

        # Start building the query
        select_parts = [f"base.{entity_config['primary_key']} as entity_id"]
        from_clause = f"{base_table} base"
        join_clauses = []

        # Process enrichment sources
        for i, source in enumerate(entity_config.get("enrichment_sources", [])):
            source_alias = f"enrich_{i}"
            source_table = source["source_table"]
            join_config = source["join_on"]
            join_type = source.get("join_type", "LEFT")

            # Generate join clause based on type
            if join_type == "FUZZY_TEXT_MATCH":
                join_sql = await self.generate_fuzzy_join_sql(
                    "base",
                    source_table,
                    join_config["from_column"],
                    join_config["to_column"],
                    join_type,
                    self.fuzzy_threshold,
                )
                # Update alias for fuzzy joins
                join_sql = join_sql.replace(") resolved_entities", f") {source_alias}")
            else:
                join_sql = f"""
                {join_type} JOIN {source_table} {source_alias}
                ON base.{join_config['from_column']} = {source_alias}.{join_config['to_column']}
                """

            join_clauses.append(join_sql)

            # Add metrics from this source
            for metric in source.get("metrics", []):
                metric_sql = metric["agg"].replace(
                    "DISTINCT ", f"DISTINCT {source_alias}."
                )
                select_parts.append(f"{metric_sql} as {metric['name']}")

        # Combine all parts
        full_query = f"""
        SELECT
            {', '.join(select_parts)}
        FROM {from_clause}
        {' '.join(join_clauses)}
        GROUP BY base.{entity_config['primary_key']}
        """

        return full_query

    async def execute_entity_resolution_query(
        self,
        query_text: str,
        entity_type: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute query with entity resolution and disambiguation"""

        try:
            # Extract potential entity names from the query
            entities_in_query = await self._extract_entities_from_query(query_text)

            # Find potential matches for each entity
            entity_matches = {}
            needs_clarification = False

            for entity_text in entities_in_query:
                matches = await self._find_entity_matches(entity_text, entity_type)

                if len(matches) > 1:
                    # Multiple matches found - needs clarification
                    entity_matches[entity_text] = {
                        "candidates": matches,
                        "needs_clarification": True,
                    }
                    needs_clarification = True
                elif len(matches) == 1:
                    # Single match found - auto-resolve
                    entity_matches[entity_text] = {
                        "resolved_entity": matches[0],
                        "needs_clarification": False,
                    }
                else:
                    # No matches found - might be new entity
                    entity_matches[entity_text] = {
                        "candidates": [],
                        "needs_clarification": False,
                        "suggestion": "new_entity",
                    }

            # If clarification needed, return clarification request
            if needs_clarification:
                return {
                    "type": "clarification_needed",
                    "query": query_text,
                    "entity_matches": entity_matches,
                    "clarification_message": self._generate_clarification_message(
                        entity_matches
                    ),
                }

            # Execute query with resolved entities
            resolved_query = await self._substitute_resolved_entities(
                query_text, entity_matches
            )
            results = await self._execute_resolved_query(resolved_query)

            # Log the resolution event
            await self._log_resolution_event(
                query_text, entity_matches, user_id, "automatic"
            )

            return {
                "type": "query_result",
                "query": resolved_query,
                "results": results,
                "entity_resolutions": entity_matches,
            }

        except Exception as e:
            logger.error(f"Entity resolution query failed: {e}")
            return {"type": "error", "message": str(e), "query": query_text}

    async def _extract_entities_from_query(self, query_text: str) -> list[str]:
        """Extract potential entity names from natural language query"""

        # Simple entity extraction patterns
        # In production, this would use NLP libraries or AI services
        entity_patterns = [
            r"\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+(?:Properties|Management|Company|Corp|LLC|Inc))?",  # Company names
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Person names
            r"\b\w+(?:\s+\w+)?\s+(?:Apartments|Properties|Complex|Community)\b",  # Property names
        ]

        entities = []
        for pattern in entity_patterns:
            matches = re.findall(pattern, query_text, re.IGNORECASE)
            entities.extend(matches)

        # Remove duplicates and clean up
        unique_entities = list(set([e.strip() for e in entities if len(e.strip()) > 3]))

        return unique_entities

    async def _find_entity_matches(
        self, entity_text: str, entity_type: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Find matching entities using the entity resolution system"""

        conn = await self._get_connection()
        cursor = conn.cursor()

        try:
            # Use our entity resolution function
            if entity_type:
                query = """
                SELECT entity_id, canonical_name, similarity_score, match_reason, aliases
                FROM TABLE(SOPHIA_ENTITY_RESOLUTION.FIND_ENTITY_MATCHES(?, ?, ?))
                ORDER BY similarity_score DESC
                """
                cursor.execute(query, [entity_text, entity_type, self.fuzzy_threshold])
            else:
                query = """
                SELECT entity_id, canonical_name, similarity_score, match_reason, aliases
                FROM TABLE(SOPHIA_ENTITY_RESOLUTION.FIND_ENTITY_MATCHES(?, NULL, ?))
                ORDER BY similarity_score DESC
                """
                cursor.execute(query, [entity_text, self.fuzzy_threshold])

            results = cursor.fetchall()

            matches = []
            for row in results:
                matches.append(
                    {
                        "entity_id": row[0],
                        "canonical_name": row[1],
                        "similarity_score": row[2],
                        "match_reason": row[3],
                        "aliases": row[4],
                    }
                )

            return matches

        finally:
            cursor.close()

    def _generate_clarification_message(self, entity_matches: dict[str, Any]) -> str:
        """Generate user-friendly clarification message"""

        clarification_parts = []

        for entity_text, match_info in entity_matches.items():
            if match_info.get("needs_clarification"):
                candidates = match_info["candidates"]

                if len(candidates) <= 3:
                    # Show all candidates
                    options = ", ".join(
                        [f"'{c['canonical_name']}'" for c in candidates]
                    )
                    clarification_parts.append(
                        f"Did you mean {options} when you mentioned '{entity_text}'?"
                    )
                else:
                    # Show top 3 candidates
                    top_candidates = candidates[:3]
                    options = ", ".join(
                        [f"'{c['canonical_name']}'" for c in top_candidates]
                    )
                    clarification_parts.append(
                        f"Did you mean {options} or something else when you mentioned '{entity_text}'?"
                    )

        if clarification_parts:
            return "I found multiple possible matches. " + " ".join(clarification_parts)
        else:
            return "Please clarify which specific entities you're referring to."

    async def _substitute_resolved_entities(
        self, original_query: str, entity_matches: dict[str, Any]
    ) -> str:
        """Substitute resolved entities in the query"""

        resolved_query = original_query

        for entity_text, match_info in entity_matches.items():
            if (
                not match_info.get("needs_clarification")
                and "resolved_entity" in match_info
            ):
                resolved_entity = match_info["resolved_entity"]
                canonical_name = resolved_entity["canonical_name"]

                # Replace entity text with canonical name
                resolved_query = resolved_query.replace(entity_text, canonical_name)

        return resolved_query

    async def _execute_resolved_query(self, query: str) -> list[dict[str, Any]]:
        """Execute the resolved query against the semantic layer"""

        # This would integrate with existing query execution logic
        # For now, return a placeholder
        return [{"message": f"Executed resolved query: {query}"}]

    async def _log_resolution_event(
        self,
        original_query: str,
        entity_matches: dict[str, Any],
        user_id: Optional[str],
        resolution_method: str,
    ):
        """Log entity resolution event for learning and analytics"""

        conn = await self._get_connection()
        cursor = conn.cursor()

        try:
            event_id = f"EVT_{int(__import__('time').time() * 1000)}"

            # Convert entity matches to array format
            candidates = []
            for entity_text, match_info in entity_matches.items():
                if "candidates" in match_info:
                    candidates.extend(match_info["candidates"])
                elif "resolved_entity" in match_info:
                    candidates.append(match_info["resolved_entity"])

            cursor.execute(
                """
                INSERT INTO SOPHIA_ENTITY_RESOLUTION.ENTITY_RESOLUTION_EVENTS (
                    event_id, user_query, entity_candidates, suggestions_count,
                    model_confidence, resolution_method, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    event_id,
                    original_query,
                    candidates,  # ModernStack will handle the array conversion
                    len(candidates),
                    sum(c.get("similarity_score", 0) for c in candidates)
                    / max(len(candidates), 1),
                    resolution_method,
                    user_id,
                ],
            )

            conn.commit()

        except Exception as e:
            logger.error(f"Failed to log resolution event: {e}")
        finally:
            cursor.close()

    async def learn_from_user_selection(
        self, event_id: str, selected_entity_id: str, user_query: str, user_id: str
    ) -> dict[str, Any]:
        """Learn from user entity selection"""

        conn = await self._get_connection()
        cursor = conn.cursor()

        try:
            # Call the learning procedure
            cursor.execute(
                """
                CALL SOPHIA_ENTITY_RESOLUTION.LEARN_FROM_USER_FEEDBACK(?, ?, ?, ?)
            """,
                [event_id, selected_entity_id, user_query, user_id],
            )

            result = cursor.fetchone()
            conn.commit()

            return {
                "status": "success",
                "message": "Learning feedback processed",
                "result": result[0] if result else "SUCCESS",
            }

        except Exception as e:
            logger.error(f"Failed to process learning feedback: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()

    async def get_entity_resolution_analytics(self) -> dict[str, Any]:
        """Get analytics on entity resolution performance"""

        conn = await self._get_connection()
        cursor = conn.cursor()

        try:
            # Get resolution metrics
            cursor.execute(
                """
                SELECT * FROM SOPHIA_ENTITY_RESOLUTION.ENTITY_RESOLUTION_METRICS
                ORDER BY resolution_date DESC LIMIT 30
            """
            )
            metrics = [
                dict(zip([col[0] for col in cursor.description], row, strict=False))
                for row in cursor.fetchall()
            ]

            # Get ambiguous entities
            cursor.execute(
                """
                SELECT * FROM SOPHIA_ENTITY_RESOLUTION.AMBIGUOUS_ENTITIES
                LIMIT 20
            """
            )
            ambiguous = [
                dict(zip([col[0] for col in cursor.description], row, strict=False))
                for row in cursor.fetchall()
            ]

            # Get usage analytics
            cursor.execute(
                """
                SELECT * FROM SOPHIA_ENTITY_RESOLUTION.ENTITY_USAGE_ANALYTICS
            """
            )
            usage = [
                dict(zip([col[0] for col in cursor.description], row, strict=False))
                for row in cursor.fetchall()
            ]

            return {
                "resolution_metrics": metrics,
                "ambiguous_entities": ambiguous,
                "usage_analytics": usage,
                "total_entities": sum(row["entity_count"] for row in usage),
            }

        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}
        finally:
            cursor.close()

    async def health_check(self) -> dict[str, Any]:
        """Enhanced health check including entity resolution system"""

        try:
            conn = await self._get_connection()
            cursor = conn.cursor()

            # Test basic connectivity
            cursor.execute("SELECT 1")
            basic_health = cursor.fetchone()[0] == 1

            # Test entity resolution system
            cursor.execute(
                """
                SELECT COUNT(*) FROM SOPHIA_ENTITY_RESOLUTION.ENTITY_CANONICAL
            """
            )
            entity_count = cursor.fetchone()[0]

            # Test fuzzy matching function
            cursor.execute(
                """
                SELECT SOPHIA_ENTITY_RESOLUTION.SIMILARITY_JW('Test Company', 'Test Corp')
            """
            )
            fuzzy_test = cursor.fetchone()[0] > 0

            cursor.close()
            conn.close()

            return {
                "status": "healthy" if basic_health and fuzzy_test else "degraded",
                "entity_resolution_enabled": self.entity_resolution_enabled,
                "total_entities": entity_count,
                "fuzzy_matching": fuzzy_test,
                "message": "Entity resolution system operational",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "message": str(e),
                "entity_resolution_enabled": False,
            }
