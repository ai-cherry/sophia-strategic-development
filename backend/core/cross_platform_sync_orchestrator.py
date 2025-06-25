"""
Sophia AI - Cross-Platform Sync Orchestrator
Orchestrates data synchronization across all MCP servers with priority-based scheduling
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from backend.mcp.base.standardized_mcp_server import SyncPriority, MCPServerConfig
from backend.utils.enhanced_snowflake_cortex_service import EnhancedSnowflakeCortexService

logger = logging.getLogger(__name__)

class SyncPriority(Enum):
    """Data synchronization priority levels."""
    REAL_TIME = "real_time"    # <1 minute
    HIGH = "high"              # <5 minutes  
    MEDIUM = "medium"          # <30 minutes
    LOW = "low"                # <24 hours

class SyncStatus(Enum):
    """Synchronization status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    CONFLICTED = "conflicted"
    SKIPPED = "skipped"

class ConflictType(Enum):
    """Data conflict type enumeration."""
    DUPLICATE_RECORD = "duplicate_record"
    DATA_MISMATCH = "data_mismatch"
    TIMESTAMP_CONFLICT = "timestamp_conflict"
    REFERENCE_CONFLICT = "reference_conflict"
    BUSINESS_RULE_CONFLICT = "business_rule_conflict"

@dataclass
class SyncConfiguration:
    """Configuration for data synchronization."""
    platform: str
    data_type: str
    priority: SyncPriority
    sync_interval_minutes: int
    batch_size: int = 100
    retry_attempts: int = 3
    timeout_seconds: int = 300
    enable_ai_processing: bool = True
    enable_conflict_detection: bool = True
    sync_dependencies: List[str] = field(default_factory=list)

@dataclass
class SyncResult:
    """Result from a synchronization operation."""
    platform: str
    data_type: str
    status: SyncStatus
    records_synced: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    conflicts_detected: int = 0
    sync_duration_ms: float = 0
    ai_processing_duration_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataConflict:
    """Data conflict detected during synchronization."""
    conflict_id: str
    conflict_type: ConflictType
    platforms: List[str]
    identifier: str
    conflicting_data: Dict[str, Any]
    detected_at: datetime = field(default_factory=datetime.utcnow)
    severity: str = "medium"  # low, medium, high, critical
    resolution_strategy: Optional[str] = None
    resolved: bool = False

@dataclass
class SyncMetrics:
    """Synchronization metrics and statistics."""
    total_syncs: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    total_records: int = 0
    total_conflicts: int = 0
    average_sync_time_ms: float = 0
    last_sync_time: Optional[datetime] = None
    sync_success_rate: float = 0.0

class DataConflictResolver:
    """Resolves data conflicts between platforms."""
    
    def __init__(self, cortex_service: EnhancedSnowflakeCortexService):
        self.cortex_service = cortex_service
        
    async def resolve_conflict(self, conflict: DataConflict) -> Dict[str, Any]:
        """Resolve a data conflict using business rules and AI assistance."""
        try:
            logger.info(f"🔧 Resolving conflict {conflict.conflict_id}: {conflict.conflict_type.value}")
            
            # Apply resolution strategy based on conflict type
            if conflict.conflict_type == ConflictType.DUPLICATE_RECORD:
                return await self._resolve_duplicate_record(conflict)
            elif conflict.conflict_type == ConflictType.DATA_MISMATCH:
                return await self._resolve_data_mismatch(conflict)
            elif conflict.conflict_type == ConflictType.TIMESTAMP_CONFLICT:
                return await self._resolve_timestamp_conflict(conflict)
            elif conflict.conflict_type == ConflictType.REFERENCE_CONFLICT:
                return await self._resolve_reference_conflict(conflict)
            else:
                return await self._resolve_with_ai(conflict)
                
        except Exception as e:
            logger.error(f"❌ Failed to resolve conflict {conflict.conflict_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "resolution": "manual_review_required"
            }
    
    async def _resolve_duplicate_record(self, conflict: DataConflict) -> Dict[str, Any]:
        """Resolve duplicate record conflicts."""
        # Strategy: Use most recent record, merge complementary data
        platforms_data = conflict.conflicting_data
        
        # Find the most recent record
        latest_record = None
        latest_timestamp = None
        
        for platform, data in platforms_data.items():
            record_timestamp = data.get('updated_at') or data.get('modified_at') or data.get('created_at')
            if record_timestamp and (not latest_timestamp or record_timestamp > latest_timestamp):
                latest_timestamp = record_timestamp
                latest_record = data
                latest_record['source_platform'] = platform
        
        if latest_record:
            return {
                "status": "resolved",
                "resolution": "use_latest_record",
                "resolved_data": latest_record,
                "strategy": "timestamp_priority"
            }
        else:
            return {
                "status": "unresolved",
                "resolution": "manual_review_required",
                "reason": "no_timestamp_available"
            }
    
    async def _resolve_data_mismatch(self, conflict: DataConflict) -> Dict[str, Any]:
        """Resolve data mismatch conflicts using AI analysis."""
        try:
            # Use AI to analyze data quality and suggest resolution
            ai_analysis = await self.cortex_service.generate_ai_insights(
                conflict.conflicting_data,
                insight_type="data_quality"
            )
            
            # Extract insights for resolution
            confidence_scores = {}
            for platform, data in conflict.conflicting_data.items():
                # Score data quality based on completeness, consistency, etc.
                score = self._calculate_data_quality_score(data)
                confidence_scores[platform] = score
            
            # Choose highest quality data
            best_platform = max(confidence_scores.items(), key=lambda x: x[1])
            
            return {
                "status": "resolved",
                "resolution": "use_highest_quality",
                "resolved_data": conflict.conflicting_data[best_platform[0]],
                "strategy": "data_quality_priority",
                "quality_scores": confidence_scores,
                "ai_insights": [insight.content for insight in ai_analysis[:3]]
            }
            
        except Exception as e:
            logger.error(f"Data mismatch resolution failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _resolve_timestamp_conflict(self, conflict: DataConflict) -> Dict[str, Any]:
        """Resolve timestamp-based conflicts."""
        # Strategy: Always use the most recent timestamp
        return await self._resolve_duplicate_record(conflict)
    
    async def _resolve_reference_conflict(self, conflict: DataConflict) -> Dict[str, Any]:
        """Resolve reference conflicts (e.g., broken foreign keys)."""
        # Strategy: Validate references and update broken ones
        return {
            "status": "deferred",
            "resolution": "reference_validation_required",
            "action": "validate_and_update_references"
        }
    
    async def _resolve_with_ai(self, conflict: DataConflict) -> Dict[str, Any]:
        """Use AI to resolve complex conflicts."""
        try:
            prompt_data = {
                "conflict_type": conflict.conflict_type.value,
                "platforms": conflict.platforms,
                "conflicting_data": conflict.conflicting_data,
                "identifier": conflict.identifier
            }
            
            ai_resolution = await self.cortex_service.generate_ai_insights(
                prompt_data,
                insight_type="conflict_resolution"
            )
            
            if ai_resolution:
                return {
                    "status": "ai_resolved",
                    "resolution": ai_resolution[0].content,
                    "confidence": ai_resolution[0].confidence_score,
                    "strategy": "ai_analysis"
                }
            else:
                return {
                    "status": "unresolved",
                    "resolution": "manual_review_required",
                    "reason": "ai_analysis_failed"
                }
                
        except Exception as e:
            logger.error(f"AI conflict resolution failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score based on completeness and consistency."""
        if not data:
            return 0.0
        
        score = 0.0
        total_fields = len(data)
        
        # Completeness score (weight: 50%)
        non_empty_fields = sum(1 for v in data.values() if v is not None and str(v).strip())
        completeness = non_empty_fields / total_fields if total_fields > 0 else 0
        score += completeness * 0.5
        
        # Consistency score (weight: 30%)
        # Check for consistent data types and formats
        consistency = 0.8  # Assume good consistency for now
        score += consistency * 0.3
        
        # Freshness score (weight: 20%)
        # Check for recent timestamps
        timestamp_fields = ['updated_at', 'modified_at', 'last_seen', 'created_at']
        freshness = 0.5  # Default freshness
        
        for field in timestamp_fields:
            if field in data and data[field]:
                try:
                    # Simple freshness calculation
                    freshness = 0.9
                    break
                except:
                    pass
        
        score += freshness * 0.2
        
        return min(score, 1.0)

class CrossPlatformSyncOrchestrator:
    """
    Orchestrates data synchronization across all MCP server platforms.
    
    Features:
    - Priority-based sync scheduling
    - Hybrid sync strategy (real-time + batch)
    - Intelligent conflict detection and resolution
    - Performance monitoring and optimization
    - AI-enhanced data processing
    """
    
    def __init__(self, cortex_service: Optional[EnhancedSnowflakeCortexService] = None):
        self.cortex_service = cortex_service or EnhancedSnowflakeCortexService()
        self.sync_configs = self._load_sync_configurations()
        self.conflict_resolver = DataConflictResolver(self.cortex_service)
        
        # Tracking and metrics
        self.sync_status_tracker: Dict[str, SyncResult] = {}
        self.sync_metrics: Dict[str, SyncMetrics] = defaultdict(SyncMetrics)
        self.active_conflicts: Dict[str, DataConflict] = {}
        self.mcp_servers: Dict[str, Any] = {}
        
        # Sync coordination
        self.sync_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.dependency_graph: Dict[str, List[str]] = {}
        
    def _load_sync_configurations(self) -> List[SyncConfiguration]:
        """Load synchronization configurations for all platforms."""
        return [
            # Real-time sync for critical business data
            SyncConfiguration(
                platform="linear", 
                data_type="issues", 
                priority=SyncPriority.REAL_TIME,
                sync_interval_minutes=1,
                batch_size=50,
                enable_ai_processing=True
            ),
            SyncConfiguration(
                platform="asana", 
                data_type="tasks", 
                priority=SyncPriority.REAL_TIME,
                sync_interval_minutes=1,
                batch_size=50,
                enable_ai_processing=True
            ),
            SyncConfiguration(
                platform="gong", 
                data_type="calls", 
                priority=SyncPriority.REAL_TIME,
                sync_interval_minutes=2,
                batch_size=25,
                enable_ai_processing=True
            ),
            SyncConfiguration(
                platform="hubspot", 
                data_type="deals", 
                priority=SyncPriority.REAL_TIME,
                sync_interval_minutes=2,
                batch_size=25,
                enable_ai_processing=True
            ),
            
            # High priority sync
            SyncConfiguration(
                platform="linear", 
                data_type="projects", 
                priority=SyncPriority.HIGH,
                sync_interval_minutes=5,
                batch_size=100,
                sync_dependencies=["linear_issues"]
            ),
            SyncConfiguration(
                platform="asana", 
                data_type="projects", 
                priority=SyncPriority.HIGH,
                sync_interval_minutes=5,
                batch_size=100,
                sync_dependencies=["asana_tasks"]
            ),
            SyncConfiguration(
                platform="hubspot", 
                data_type="contacts", 
                priority=SyncPriority.HIGH,
                sync_interval_minutes=10,
                batch_size=200
            ),
            SyncConfiguration(
                platform="gong", 
                data_type="transcripts", 
                priority=SyncPriority.HIGH,
                sync_interval_minutes=5,
                batch_size=50,
                sync_dependencies=["gong_calls"],
                enable_ai_processing=True
            ),
            
            # Medium priority sync
            SyncConfiguration(
                platform="linear", 
                data_type="teams", 
                priority=SyncPriority.MEDIUM,
                sync_interval_minutes=30,
                batch_size=50
            ),
            SyncConfiguration(
                platform="asana", 
                data_type="teams", 
                priority=SyncPriority.MEDIUM,
                sync_interval_minutes=30,
                batch_size=50
            ),
            SyncConfiguration(
                platform="notion", 
                data_type="pages", 
                priority=SyncPriority.MEDIUM,
                sync_interval_minutes=60,
                batch_size=100,
                enable_ai_processing=True
            ),
            
            # Low priority sync
            SyncConfiguration(
                platform="codacy", 
                data_type="metrics", 
                priority=SyncPriority.LOW,
                sync_interval_minutes=1440,  # Daily
                batch_size=1000
            ),
            SyncConfiguration(
                platform="snowflake_admin", 
                data_type="query_history", 
                priority=SyncPriority.LOW,
                sync_interval_minutes=720,  # 12 hours
                batch_size=500
            ),
        ]
    
    def register_mcp_server(self, platform: str, server_instance: Any) -> None:
        """Register an MCP server for sync orchestration."""
        self.mcp_servers[platform] = server_instance
        logger.info(f"✅ Registered MCP server: {platform}")
    
    async def orchestrate_sync(self, force_sync: bool = False) -> Dict[str, Any]:
        """
        Orchestrate synchronization across all platforms with priority-based scheduling.
        
        Args:
            force_sync: Force sync regardless of intervals
            
        Returns:
            Comprehensive sync results
        """
        start_time = time.time()
        orchestration_result = {
            "status": "started",
            "timestamp": datetime.utcnow().isoformat(),
            "sync_results": {},
            "conflicts_detected": [],
            "metrics": {}
        }
        
        try:
            logger.info("🚀 Starting cross-platform sync orchestration")
            
            # Initialize Cortex service if needed
            if not hasattr(self.cortex_service, 'connection') or not self.cortex_service.connection:
                await self.cortex_service.initialize()
            
            # Group configurations by priority
            priority_groups = self._group_configs_by_priority()
            
            # Execute syncs by priority (real-time first, then high, medium, low)
            for priority in [SyncPriority.REAL_TIME, SyncPriority.HIGH, SyncPriority.MEDIUM, SyncPriority.LOW]:
                if priority in priority_groups:
                    priority_results = await self._execute_priority_group(
                        priority_groups[priority], 
                        force_sync
                    )
                    orchestration_result["sync_results"][priority.value] = priority_results
            
            # Detect and resolve conflicts
            conflicts = await self._detect_cross_platform_conflicts()
            if conflicts:
                resolution_results = await self._resolve_conflicts(conflicts)
                orchestration_result["conflicts_detected"] = conflicts
                orchestration_result["conflict_resolutions"] = resolution_results
            
            # Update metrics
            await self._update_orchestration_metrics()
            orchestration_result["metrics"] = await self._get_sync_metrics_summary()
            
            # Calculate overall status
            total_duration = time.time() - start_time
            orchestration_result.update({
                "status": "completed",
                "total_duration_ms": total_duration * 1000,
                "platforms_synced": len(self.mcp_servers),
                "total_conflicts": len(conflicts)
            })
            
            logger.info(f"✅ Sync orchestration completed in {total_duration:.2f}s")
            return orchestration_result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Sync orchestration failed: {error_msg}")
            
            orchestration_result.update({
                "status": "failed",
                "error": error_msg,
                "total_duration_ms": (time.time() - start_time) * 1000
            })
            
            return orchestration_result
    
    def _group_configs_by_priority(self) -> Dict[SyncPriority, List[SyncConfiguration]]:
        """Group sync configurations by priority."""
        priority_groups = defaultdict(list)
        for config in self.sync_configs:
            priority_groups[config.priority].append(config)
        return priority_groups
    
    async def _execute_priority_group(
        self, 
        configs: List[SyncConfiguration], 
        force_sync: bool
    ) -> List[SyncResult]:
        """Execute sync for a priority group."""
        # Filter configs that need syncing
        configs_to_sync = []
        for config in configs:
            if force_sync or self._should_sync(config):
                configs_to_sync.append(config)
        
        if not configs_to_sync:
            return []
        
        # For real-time and high priority, run in parallel
        # For medium and low priority, run with limited concurrency
        if configs[0].priority in [SyncPriority.REAL_TIME, SyncPriority.HIGH]:
            # Run all in parallel for speed
            tasks = [self._sync_platform_data(config) for config in configs_to_sync]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run with limited concurrency to avoid overload
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent syncs
            async def limited_sync(config):
                async with semaphore:
                    return await self._sync_platform_data(config)
            
            tasks = [limited_sync(config) for config in configs_to_sync]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        sync_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Convert exception to failed sync result
                config = configs_to_sync[i]
                sync_result = SyncResult(
                    platform=config.platform,
                    data_type=config.data_type,
                    status=SyncStatus.FAILED,
                    error_message=str(result)
                )
                sync_results.append(sync_result)
            else:
                sync_results.append(result)
        
        return sync_results
    
    def _should_sync(self, config: SyncConfiguration) -> bool:
        """Determine if sync should run based on interval and dependencies."""
        sync_key = f"{config.platform}_{config.data_type}"
        
        # Check last sync time
        last_sync = self.sync_status_tracker.get(sync_key)
        if not last_sync:
            return True
        
        time_since_sync = datetime.utcnow() - last_sync.timestamp
        interval_threshold = timedelta(minutes=config.sync_interval_minutes)
        
        if time_since_sync < interval_threshold:
            return False
        
        # Check dependencies
        if config.sync_dependencies:
            for dependency in config.sync_dependencies:
                if dependency not in self.sync_status_tracker:
                    logger.warning(f"Dependency {dependency} not found for {sync_key}")
                    continue
                
                dep_sync = self.sync_status_tracker[dependency]
                if dep_sync.status != SyncStatus.SUCCESS:
                    logger.info(f"Skipping {sync_key} due to failed dependency {dependency}")
                    return False
        
        return True
    
    async def _sync_platform_data(self, config: SyncConfiguration) -> SyncResult:
        """Sync data for a specific platform and data type."""
        sync_key = f"{config.platform}_{config.data_type}"
        start_time = time.time()
        
        # Use lock to prevent concurrent syncs of the same data
        async with self.sync_locks[sync_key]:
            try:
                logger.info(f"🔄 Syncing {sync_key}")
                
                # Get MCP server for platform
                mcp_server = self.mcp_servers.get(config.platform)
                if not mcp_server:
                    return SyncResult(
                        platform=config.platform,
                        data_type=config.data_type,
                        status=SyncStatus.FAILED,
                        error_message=f"MCP server not found for {config.platform}"
                    )
                
                # Execute sync via MCP server
                sync_result_data = await mcp_server.sync_and_process_data()
                
                # Convert to SyncResult
                sync_result = SyncResult(
                    platform=config.platform,
                    data_type=config.data_type,
                    status=SyncStatus.SUCCESS if sync_result_data.get("status") == "completed" else SyncStatus.FAILED,
                    records_synced=sync_result_data.get("records_synced", 0),
                    sync_duration_ms=(time.time() - start_time) * 1000,
                    ai_processing_duration_ms=sync_result_data.get("ai_duration", 0) * 1000,
                    metadata=sync_result_data
                )
                
                # Store result for tracking
                self.sync_status_tracker[sync_key] = sync_result
                
                # Update metrics
                metrics = self.sync_metrics[sync_key]
                metrics.total_syncs += 1
                if sync_result.status == SyncStatus.SUCCESS:
                    metrics.successful_syncs += 1
                else:
                    metrics.failed_syncs += 1
                
                metrics.total_records += sync_result.records_synced
                metrics.last_sync_time = sync_result.timestamp
                metrics.sync_success_rate = metrics.successful_syncs / metrics.total_syncs
                
                logger.info(f"✅ Sync completed for {sync_key}: {sync_result.records_synced} records")
                return sync_result
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Sync failed for {sync_key}: {error_msg}")
                
                sync_result = SyncResult(
                    platform=config.platform,
                    data_type=config.data_type,
                    status=SyncStatus.FAILED,
                    sync_duration_ms=(time.time() - start_time) * 1000,
                    error_message=error_msg
                )
                
                self.sync_status_tracker[sync_key] = sync_result
                
                # Update metrics
                metrics = self.sync_metrics[sync_key]
                metrics.total_syncs += 1
                metrics.failed_syncs += 1
                metrics.sync_success_rate = metrics.successful_syncs / metrics.total_syncs
                
                return sync_result
    
    async def _detect_cross_platform_conflicts(self) -> List[DataConflict]:
        """Detect data conflicts across platforms."""
        conflicts = []
        
        try:
            # Example: Detect duplicate contacts across platforms
            # This would be implemented with actual Snowflake queries
            logger.info("🔍 Detecting cross-platform conflicts")
            
            # Placeholder for actual conflict detection
            # In real implementation, this would query Snowflake for duplicates
            
            return conflicts
            
        except Exception as e:
            logger.error(f"❌ Conflict detection failed: {e}")
            return []
    
    async def _resolve_conflicts(self, conflicts: List[DataConflict]) -> Dict[str, Any]:
        """Resolve detected conflicts."""
        resolution_results = {
            "total_conflicts": len(conflicts),
            "resolved": 0,
            "failed": 0,
            "deferred": 0,
            "resolutions": []
        }
        
        for conflict in conflicts:
            try:
                resolution = await self.conflict_resolver.resolve_conflict(conflict)
                resolution_results["resolutions"].append({
                    "conflict_id": conflict.conflict_id,
                    "resolution": resolution
                })
                
                if resolution["status"] == "resolved":
                    resolution_results["resolved"] += 1
                    conflict.resolved = True
                elif resolution["status"] == "deferred":
                    resolution_results["deferred"] += 1
                else:
                    resolution_results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to resolve conflict {conflict.conflict_id}: {e}")
                resolution_results["failed"] += 1
        
        return resolution_results
    
    async def _update_orchestration_metrics(self) -> None:
        """Update orchestration-level metrics."""
        try:
            # Calculate averages and totals across all syncs
            total_syncs = sum(m.total_syncs for m in self.sync_metrics.values())
            successful_syncs = sum(m.successful_syncs for m in self.sync_metrics.values())
            total_records = sum(m.total_records for m in self.sync_metrics.values())
            
            # Store metrics for historical tracking
            metrics_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_syncs": total_syncs,
                "successful_syncs": successful_syncs,
                "total_records": total_records,
                "overall_success_rate": successful_syncs / total_syncs if total_syncs > 0 else 0,
                "platforms_active": len(self.mcp_servers)
            }
            
            logger.info(f"📊 Orchestration metrics: {metrics_data}")
            
        except Exception as e:
            logger.error(f"Failed to update orchestration metrics: {e}")
    
    async def _get_sync_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of sync metrics."""
        return {
            "total_platforms": len(self.mcp_servers),
            "total_sync_configs": len(self.sync_configs),
            "active_conflicts": len(self.active_conflicts),
            "platform_metrics": {
                key: {
                    "total_syncs": metrics.total_syncs,
                    "success_rate": metrics.sync_success_rate,
                    "total_records": metrics.total_records,
                    "last_sync": metrics.last_sync_time.isoformat() if metrics.last_sync_time else None
                }
                for key, metrics in self.sync_metrics.items()
            }
        }
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status across all platforms."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "sync_results": {key: {
                "platform": result.platform,
                "data_type": result.data_type,
                "status": result.status.value,
                "last_sync": result.timestamp.isoformat(),
                "records_synced": result.records_synced
            } for key, result in self.sync_status_tracker.items()},
            "metrics": await self._get_sync_metrics_summary(),
            "active_conflicts": len(self.active_conflicts)
        } 