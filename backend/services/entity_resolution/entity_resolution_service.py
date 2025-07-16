"""
Cross-Platform Entity Resolution Service
Main orchestrator for entity matching and resolution across platforms
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict

from backend.services.entity_resolution.core_entity_matcher import AdvancedEntityMatcher, MatchResult
from backend.database.database_service import DatabaseService
from backend.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

class EntityResolutionService:
    """Main service for cross-platform entity resolution"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.entity_matcher = AdvancedEntityMatcher()
        self.openai_service = OpenAIService()
        
        # Resolution thresholds
        self.auto_merge_threshold = 0.95
        self.manual_review_threshold = 0.50
        self.conflict_threshold = 0.30
        
        # Batch processing settings
        self.batch_size = 100
        self.max_concurrent_matches = 10
        
        # Check if advanced matching is available
        self.use_basic_matching = not hasattr(self.entity_matcher, 'use_advanced_matching') or not self.entity_matcher.use_advanced_matching
        
    async def resolve_employee_across_platforms(
        self, 
        employee_data: Dict[str, Any],
        target_platforms: List[str],
        force_reprocessing: bool = False
    ) -> Dict[str, Any]:
        """
        Resolve a single employee across multiple platforms
        
        Args:
            employee_data: Employee information to resolve
            target_platforms: List of platforms to search ('lattice', 'salesforce', 'hubspot', etc.)
            force_reprocessing: Whether to bypass cache and force reprocessing
            
        Returns:
            Resolution result with matches, conflicts, and recommendations
        """
        start_time = datetime.now()
        employee_id = employee_data.get('employee_id', str(uuid.uuid4()))
        
        logger.info(f"Starting cross-platform resolution for employee {employee_data.get('name', 'Unknown')} across {len(target_platforms)} platforms")
        
        resolution_result = {
            "employee_id": employee_id,
            "employee_data": employee_data,
            "platforms_searched": target_platforms,
            "matches_found": {},
            "conflicts_detected": [],
            "auto_merge_candidates": [],
            "manual_review_required": [],
            "master_entity_id": None,
            "confidence_scores": {},
            "processing_time_ms": 0,
            "recommendations": [],
            "created_at": start_time.isoformat()
        }
        
        try:
            # Check if employee already has master entity
            existing_master = await self._get_existing_master_entity(employee_data)
            if existing_master and not force_reprocessing:
                resolution_result["master_entity_id"] = existing_master["master_entity_id"]
                logger.info(f"Found existing master entity: {existing_master['master_entity_id']}")
            
            # Process each platform
            for platform in target_platforms:
                try:
                    platform_matches = await self._resolve_against_platform(
                        employee_data, platform, force_reprocessing
                    )
                    
                    if platform_matches:
                        resolution_result["matches_found"][platform] = platform_matches
                        resolution_result["confidence_scores"][platform] = [
                            match.confidence_score for match in platform_matches
                        ]
                        
                        # Categorize matches
                        await self._categorize_matches(platform_matches, resolution_result)
                
                except Exception as e:
                    logger.error(f"Error resolving against platform {platform}: {e}")
                    continue
            
            # Create or update master entity
            if not resolution_result["master_entity_id"]:
                resolution_result["master_entity_id"] = await self._create_master_entity(
                    employee_data, resolution_result["matches_found"]
                )
            
            # Detect and handle conflicts
            conflicts = await self._detect_conflicts(resolution_result)
            if conflicts:
                resolution_result["conflicts_detected"] = conflicts
                await self._create_conflict_records(conflicts, resolution_result["master_entity_id"])
            
            # Generate recommendations
            recommendations = await self._generate_resolution_recommendations(resolution_result)
            resolution_result["recommendations"] = recommendations
            
            # Store resolution result
            await self._store_resolution_result(resolution_result)
            
        except Exception as e:
            logger.error(f"Error in cross-platform resolution: {e}", exc_info=True)
            resolution_result["error"] = str(e)
        
        finally:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            resolution_result["processing_time_ms"] = processing_time
            
            logger.info(f"Cross-platform resolution completed in {processing_time}ms. "
                       f"Found {sum(len(matches) for matches in resolution_result['matches_found'].values())} total matches")
        
        return resolution_result
    
    async def bulk_resolve_employees(
        self, 
        employees: List[Dict[str, Any]], 
        target_platforms: List[str],
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Resolve multiple employees in bulk with progress tracking
        """
        logger.info(f"Starting bulk resolution for {len(employees)} employees across {len(target_platforms)} platforms")
        
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent_matches)
        
        async def resolve_single(employee_data: Dict[str, Any], index: int) -> Dict[str, Any]:
            async with semaphore:
                try:
                    result = await self.resolve_employee_across_platforms(employee_data, target_platforms)
                    if progress_callback:
                        await progress_callback(index + 1, len(employees), result)
                    return result
                except Exception as e:
                    logger.error(f"Error resolving employee {employee_data.get('name', 'Unknown')}: {e}")
                    return {"error": str(e), "employee_data": employee_data}
        
        # Process in batches
        for i in range(0, len(employees), self.batch_size):
            batch = employees[i:i + self.batch_size]
            batch_tasks = [
                resolve_single(employee, i + j) 
                for j, employee in enumerate(batch)
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Brief pause between batches to prevent overwhelming
            await asyncio.sleep(0.1)
        
        logger.info(f"Bulk resolution completed. Processed {len(results)} employees")
        return results
    
    async def get_entity_conflicts_for_review(
        self, 
        priority_filter: Optional[str] = None,
        assigned_reviewer: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get entity resolution conflicts that require manual review
        """
        query = """
        SELECT 
            conflict_id,
            entity_type,
            conflicting_entities,
            conflict_type,
            confidence_scores,
            priority,
            assigned_reviewer,
            created_at,
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - created_at))/3600 as hours_pending
        FROM FOUNDATIONAL_KNOWLEDGE.ENTITY_RESOLUTION_CONFLICTS
        WHERE resolution_status = 'pending'
        """
        
        params = []
        
        if priority_filter:
            query += " AND priority = %s"
            params.append(priority_filter)
        
        if assigned_reviewer:
            query += " AND assigned_reviewer = %s"
            params.append(assigned_reviewer)
        
        query += " ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, created_at LIMIT %s"
        params.append(limit)
        
        return await self.db_service.execute_query(query, params)
    
    async def resolve_conflict_manually(
        self, 
        conflict_id: str, 
        resolution_decision: Dict[str, Any],
        resolved_by: str
    ) -> bool:
        """
        Manually resolve an entity conflict
        """
        try:
            # Update conflict record
            update_query = """
            UPDATE FOUNDATIONAL_KNOWLEDGE.ENTITY_RESOLUTION_CONFLICTS
            SET 
                resolution_status = 'resolved',
                resolution_decision = %s,
                resolved_by = %s,
                resolved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE conflict_id = %s
            """
            
            await self.db_service.execute_update(
                update_query, 
                [json.dumps(resolution_decision), resolved_by, conflict_id]
            )
            
            # Apply the resolution decision
            await self._apply_resolution_decision(resolution_decision)
            
            # Store as training data for ML improvement
            await self._store_resolution_training_data(conflict_id, resolution_decision, resolved_by)
            
            logger.info(f"Conflict {conflict_id} resolved by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {e}")
            return False
    
    async def get_entity_mapping_summary(self) -> Dict[str, Any]:
        """
        Get summary of cross-platform entity mappings
        """
        query = """
        SELECT * FROM FOUNDATIONAL_KNOWLEDGE.V_CROSS_PLATFORM_MAPPING_SUMMARY
        ORDER BY entity_type, platform_name
        """
        
        mappings = await self.db_service.execute_query(query)
        
        # Aggregate statistics
        total_entities = sum(row['total_mappings'] for row in mappings)
        total_verified = sum(row['verified_mappings'] for row in mappings)
        total_pending_review = sum(row['pending_review'] for row in mappings)
        
        platform_coverage = {}
        for row in mappings:
            platform = row['platform_name']
            if platform not in platform_coverage:
                platform_coverage[platform] = {'entities': 0, 'verified': 0}
            platform_coverage[platform]['entities'] += row['total_mappings']
            platform_coverage[platform]['verified'] += row['verified_mappings']
        
        return {
            "total_entities": total_entities,
            "total_verified": total_verified,
            "total_pending_review": total_pending_review,
            "verification_rate": (total_verified / total_entities) if total_entities > 0 else 0,
            "platform_coverage": platform_coverage,
            "detailed_mappings": mappings,
            "last_updated": datetime.now().isoformat()
        }
    
    # Private helper methods
    
    async def _get_existing_master_entity(self, employee_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if employee already has a master entity"""
        # Try by email first (most reliable)
        email = employee_data.get('email', '').lower().strip()
        if email:
            query = """
            SELECT master_entity_id, canonical_name, canonical_email, confidence_score
            FROM FOUNDATIONAL_KNOWLEDGE.ENTITY_MASTER_REGISTRY
            WHERE entity_type = 'employee' AND LOWER(canonical_email) = %s
            """
            result = await self.db_service.execute_query(query, [email])
            if result:
                return result[0]
        
        # Try by name if no email match
        name = employee_data.get('name', '') or f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}".strip()
        if name:
            query = """
            SELECT master_entity_id, canonical_name, canonical_email, confidence_score
            FROM FOUNDATIONAL_KNOWLEDGE.ENTITY_MASTER_REGISTRY
            WHERE entity_type = 'employee' AND canonical_name ILIKE %s
            """
            result = await self.db_service.execute_query(query, [f"%{name}%"])
            if result:
                return result[0]
        
        return None
    
    async def _resolve_against_platform(
        self, 
        employee_data: Dict[str, Any], 
        platform: str,
        force_reprocessing: bool = False
    ) -> List[MatchResult]:
        """Resolve employee against a specific platform"""
        # Get platform data (this would integrate with actual platform APIs)
        platform_records = await self._get_platform_records(platform, employee_data)
        
        if not platform_records:
            logger.debug(f"No records found in platform {platform}")
            return []
        
        # Use the entity matcher to find matches
        matches = await self.entity_matcher.match_employee_across_platforms(
            employee_data, platform, platform_records
        )
        
        return matches
    
    async def _get_platform_records(self, platform: str, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get records from a specific platform for matching
        This is a placeholder - in production this would call actual platform APIs
        """
        # For now, return mock data based on platform
        if platform == "lattice":
            return await self._get_lattice_records(search_criteria)
        elif platform == "salesforce":
            return await self._get_salesforce_records(search_criteria)
        elif platform == "hubspot":
            return await self._get_hubspot_records(search_criteria)
        elif platform == "slack":
            return await self._get_slack_records(search_criteria)
        else:
            return []
    
    async def _get_lattice_records(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get Lattice employee records (placeholder)"""
        # This would integrate with Lattice API
        return [
            {
                "person_id": "lattice_123",
                "name": "John Smith",
                "email": "john.smith@payready.com",
                "title": "Software Engineer",
                "department": "Engineering",
                "manager": "Jane Doe",
                "start_date": "2023-01-15"
            }
        ]
    
    async def _get_salesforce_records(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get Salesforce contact records (placeholder)"""
        return []
    
    async def _get_hubspot_records(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get HubSpot contact records (placeholder)"""
        return []
    
    async def _get_slack_records(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get Slack user records (placeholder)"""
        return []
    
    async def _categorize_matches(self, matches: List[MatchResult], resolution_result: Dict[str, Any]):
        """Categorize matches based on confidence scores"""
        for match in matches:
            if match.confidence_score >= self.auto_merge_threshold:
                resolution_result["auto_merge_candidates"].append(asdict(match))
            elif match.confidence_score >= self.manual_review_threshold:
                resolution_result["manual_review_required"].append(asdict(match))
    
    async def _create_master_entity(
        self, 
        employee_data: Dict[str, Any], 
        platform_matches: Dict[str, List[MatchResult]]
    ) -> str:
        """Create a new master entity record"""
        master_entity_id = f"entity_{uuid.uuid4().hex[:12]}"
        
        # Extract canonical information from employee data and matches
        canonical_name = employee_data.get('name', '') or f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}".strip()
        canonical_email = employee_data.get('email', '').lower().strip()
        canonical_title = employee_data.get('title', '')
        canonical_phone = employee_data.get('phone', '')
        
        # Calculate confidence score based on data completeness
        confidence_score = self._calculate_entity_confidence(employee_data, platform_matches)
        
        insert_query = """
        INSERT INTO FOUNDATIONAL_KNOWLEDGE.ENTITY_MASTER_REGISTRY
        (master_entity_id, entity_type, canonical_name, canonical_email, canonical_title, 
         canonical_phone, confidence_score, verification_status, metadata, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        metadata = {
            "source_platform": employee_data.get('source_platform', 'manual'),
            "platforms_matched": list(platform_matches.keys()),
            "creation_method": "automated_resolution"
        }
        
        await self.db_service.execute_query(insert_query, [
            master_entity_id, 'employee', canonical_name, canonical_email, canonical_title,
            canonical_phone, confidence_score, 'pending', json.dumps(metadata), 'entity_resolution_service'
        ])
        
        logger.info(f"Created master entity {master_entity_id} for {canonical_name}")
        return master_entity_id
    
    def _calculate_entity_confidence(
        self, 
        employee_data: Dict[str, Any], 
        platform_matches: Dict[str, List[MatchResult]]
    ) -> float:
        """Calculate confidence score for master entity"""
        score = 0.0
        
        # Base score from data completeness
        if employee_data.get('email'):
            score += 0.3
        if employee_data.get('name') or (employee_data.get('first_name') and employee_data.get('last_name')):
            score += 0.3
        if employee_data.get('title'):
            score += 0.2
        if employee_data.get('phone'):
            score += 0.1
        
        # Bonus for platform matches
        if platform_matches:
            max_platform_confidence = max(
                max(match.confidence_score for match in matches) if matches else 0
                for matches in platform_matches.values()
            )
            score += max_platform_confidence * 0.1
        
        return min(score, 1.0)
    
    async def _detect_conflicts(self, resolution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts that require manual resolution"""
        conflicts = []
        
        # Check for multiple high-confidence matches in the same platform
        for platform, matches in resolution_result["matches_found"].items():
            high_confidence_matches = [
                match for match in matches 
                if match.confidence_score >= self.manual_review_threshold
            ]
            
            if len(high_confidence_matches) > 1:
                conflicts.append({
                    "conflict_type": "multiple_high_confidence_matches",
                    "platform": platform,
                    "matches": high_confidence_matches,
                    "priority": "high"
                })
        
        # Check for conflicting data across platforms
        # (Implementation would compare field values across matches)
        
        return conflicts
    
    async def _create_conflict_records(self, conflicts: List[Dict[str, Any]], master_entity_id: str):
        """Create conflict records in the database"""
        for conflict in conflicts:
            conflict_id = f"conflict_{uuid.uuid4().hex[:12]}"
            
            insert_query = """
            INSERT INTO FOUNDATIONAL_KNOWLEDGE.ENTITY_RESOLUTION_CONFLICTS
            (conflict_id, entity_type, conflicting_entities, conflict_type, confidence_scores, 
             resolution_status, priority, auto_resolution_attempted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await self.db_service.execute_query(insert_query, [
                conflict_id, 'employee', json.dumps(conflict), conflict["conflict_type"],
                json.dumps({}), 'pending', conflict.get("priority", "medium"), False
            ])
    
    async def _generate_resolution_recommendations(self, resolution_result: Dict[str, Any]) -> List[str]:
        """Generate AI-powered recommendations for resolution"""
        recommendations = []
        
        # Analyze patterns and suggest actions
        total_matches = sum(len(matches) for matches in resolution_result["matches_found"].values())
        
        if total_matches == 0:
            recommendations.append("No matches found. Consider manually verifying employee data or adding to platforms.")
        elif len(resolution_result["auto_merge_candidates"]) > 0:
            recommendations.append(f"Found {len(resolution_result['auto_merge_candidates'])} high-confidence matches ready for automatic merging.")
        
        if len(resolution_result["manual_review_required"]) > 0:
            recommendations.append(f"{len(resolution_result['manual_review_required'])} matches require manual review due to medium confidence scores.")
        
        if len(resolution_result["conflicts_detected"]) > 0:
            recommendations.append(f"Detected {len(resolution_result['conflicts_detected'])} conflicts that need immediate attention.")
        
        return recommendations
    
    async def _store_resolution_result(self, resolution_result: Dict[str, Any]):
        """Store the resolution result for audit and analytics"""
        # This would store the complete resolution result in a separate audit table
        pass
    
    async def _apply_resolution_decision(self, resolution_decision: Dict[str, Any]):
        """Apply a manual resolution decision"""
        # Implementation would update entity mappings based on the decision
        pass
    
    async def _store_resolution_training_data(self, conflict_id: str, resolution_decision: Dict[str, Any], resolved_by: str):
        """Store resolution as training data for ML improvement"""
        f"training_{uuid.uuid4().hex[:12]}"
        
        
        # Extract training data from resolution decision
        # (Implementation would depend on decision structure)
        pass
    
    async def basic_employee_resolution(self, employee_data: Dict[str, Any], target_platforms: List[str]) -> Dict[str, Any]:
        """
        Basic employee resolution when advanced libraries aren't available
        Returns a simplified resolution result
        """
        logger.info(f"Using basic resolution for employee {employee_data.get('full_name', 'Unknown')}")
        
        return {
            "employee_id": employee_data.get('employee_id', str(uuid.uuid4())),
            "employee_data": employee_data,
            "platforms_searched": target_platforms,
            "matches_found": 0,  # Basic implementation doesn't search other platforms
            "conflicts_detected": [],
            "auto_merge_candidates": [],
            "manual_review_required": [],
            "master_entity_id": employee_data.get('employee_id'),
            "confidence_scores": {"basic_match": 1.0},
            "processing_time_ms": 1,
            "recommendations": ["Advanced entity matching not available - using basic resolution"],
            "resolution_method": "basic",
            "created_at": datetime.now().isoformat()
        }

import json
