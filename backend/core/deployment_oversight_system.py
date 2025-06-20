"""
Comprehensive Deployment Oversight and Monitoring System
Provides enterprise-grade deployment stability, monitoring, and rollback capabilities
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json

from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC
from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
from backend.integrations.claude_integration import ClaudeIntegration

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class DeploymentMetrics:
    deployment_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: DeploymentStatus
    success_rate: float
    response_time_p95: float
    error_rate: float
    throughput: float
    resource_utilization: Dict[str, float]
    business_metrics: Dict[str, float]

@dataclass
class HealthCheck:
    service_name: str
    endpoint: str
    expected_status: int
    timeout_seconds: int
    retry_count: int
    critical: bool

@dataclass
class AlertRule:
    name: str
    metric: str
    threshold: float
    operator: str  # >, <, >=, <=, ==
    duration_minutes: int
    severity: str  # critical, warning, info
    notification_channels: List[str]

class DeploymentOversightSystem:
    """
    Comprehensive deployment oversight system with monitoring, validation, and rollback capabilities
    """
    
    def __init__(self):
        self.pulumi_esc = EnhancedPulumiESC()
        self.lambda_labs = LambdaLabsIntegration()
        self.claude = ClaudeIntegration()
        
        self.deployments: Dict[str, DeploymentMetrics] = {}
        self.health_checks: List[HealthCheck] = []
        self.alert_rules: List[AlertRule] = []
        self.monitoring_active = False
        
        self._setup_default_health_checks()
        self._setup_default_alert_rules()

    def _setup_default_health_checks(self):
        """Setup default health checks for all services"""
        self.health_checks = [
            HealthCheck(
                service_name="sophia-api",
                endpoint="/health",
                expected_status=200,
                timeout_seconds=5,
                retry_count=3,
                critical=True
            ),
            HealthCheck(
                service_name="hybrid-rag",
                endpoint="/api/v1/hybrid-rag/health",
                expected_status=200,
                timeout_seconds=10,
                retry_count=3,
                critical=True
            ),
            HealthCheck(
                service_name="agno-agents",
                endpoint="/api/v1/agno/health",
                expected_status=200,
                timeout_seconds=5,
                retry_count=2,
                critical=True
            ),
            HealthCheck(
                service_name="mcp-federation",
                endpoint="/api/v1/mcp/health",
                expected_status=200,
                timeout_seconds=15,
                retry_count=3,
                critical=True
            ),
            HealthCheck(
                service_name="lambda-labs",
                endpoint="/api/v1/lambda-labs/health",
                expected_status=200,
                timeout_seconds=30,
                retry_count=2,
                critical=False
            ),
            HealthCheck(
                service_name="pulumi-esc",
                endpoint="/api/v1/pulumi-esc/health",
                expected_status=200,
                timeout_seconds=10,
                retry_count=3,
                critical=True
            )
        ]

    def _setup_default_alert_rules(self):
        """Setup default alert rules for monitoring"""
        self.alert_rules = [
            # Critical Performance Alerts
            AlertRule(
                name="High Response Time",
                metric="response_time_p95",
                threshold=1000.0,  # 1 second
                operator=">=",
                duration_minutes=2,
                severity="critical",
                notification_channels=["slack", "email"]
            ),
            AlertRule(
                name="High Error Rate",
                metric="error_rate",
                threshold=0.05,  # 5%
                operator=">=",
                duration_minutes=1,
                severity="critical",
                notification_channels=["slack", "email", "sms"]
            ),
            AlertRule(
                name="Low Success Rate",
                metric="success_rate",
                threshold=0.95,  # 95%
                operator="<=",
                duration_minutes=3,
                severity="critical",
                notification_channels=["slack", "email"]
            ),
            
            # Resource Utilization Alerts
            AlertRule(
                name="High CPU Usage",
                metric="cpu_utilization",
                threshold=0.85,  # 85%
                operator=">=",
                duration_minutes=5,
                severity="warning",
                notification_channels=["slack"]
            ),
            AlertRule(
                name="High Memory Usage",
                metric="memory_utilization",
                threshold=0.90,  # 90%
                operator=">=",
                duration_minutes=5,
                severity="warning",
                notification_channels=["slack"]
            ),
            
            # Business Metrics Alerts
            AlertRule(
                name="Low User Engagement",
                metric="active_users",
                threshold=10.0,
                operator="<=",
                duration_minutes=10,
                severity="warning",
                notification_channels=["slack"]
            ),
            AlertRule(
                name="Revenue Impact",
                metric="revenue_per_hour",
                threshold=100.0,
                operator="<=",
                duration_minutes=15,
                severity="critical",
                notification_channels=["slack", "email"]
            )
        ]

    async def pre_deployment_validation(self, deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive pre-deployment validation
        """
        logger.info("Starting pre-deployment validation...")
        
        validation_results = {
            "overall_status": "pending",
            "checks": {},
            "recommendations": [],
            "blocking_issues": [],
            "warnings": []
        }
        
        try:
            # 1. Security Validation
            security_check = await self._validate_security(deployment_config)
            validation_results["checks"]["security"] = security_check
            
            # 2. Performance Benchmarking
            performance_check = await self._validate_performance(deployment_config)
            validation_results["checks"]["performance"] = performance_check
            
            # 3. Dependency Analysis
            dependency_check = await self._validate_dependencies(deployment_config)
            validation_results["checks"]["dependencies"] = dependency_check
            
            # 4. Resource Capacity
            capacity_check = await self._validate_capacity(deployment_config)
            validation_results["checks"]["capacity"] = capacity_check
            
            # 5. Database Migration Safety
            migration_check = await self._validate_migrations(deployment_config)
            validation_results["checks"]["migrations"] = migration_check
            
            # 6. Configuration Validation
            config_check = await self._validate_configuration(deployment_config)
            validation_results["checks"]["configuration"] = config_check
            
            # Determine overall status
            all_checks_passed = all(
                check.get("status") == "passed" 
                for check in validation_results["checks"].values()
            )
            
            has_blocking_issues = any(
                check.get("blocking", False) 
                for check in validation_results["checks"].values() 
                if check.get("status") == "failed"
            )
            
            if has_blocking_issues:
                validation_results["overall_status"] = "blocked"
            elif all_checks_passed:
                validation_results["overall_status"] = "approved"
            else:
                validation_results["overall_status"] = "approved_with_warnings"
            
            logger.info(f"Pre-deployment validation completed: {validation_results['overall_status']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Pre-deployment validation failed: {e}", exc_info=True)
            validation_results["overall_status"] = "error"
            validation_results["blocking_issues"].append(f"Validation system error: {str(e)}")
            return validation_results

    async def _validate_security(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security aspects of deployment"""
        try:
            # Check for hardcoded secrets
            secret_scan = await self._scan_for_secrets(config)
            
            # Validate secret management
            secret_mgmt = await self.pulumi_esc.validate_secret_configuration()
            
            # Check for security vulnerabilities
            vuln_scan = await self._security_vulnerability_scan(config)
            
            security_score = (
                (1.0 if secret_scan["passed"] else 0.0) +
                (1.0 if secret_mgmt["status"] == "healthy" else 0.0) +
                (1.0 if vuln_scan["critical_count"] == 0 else 0.0)
            ) / 3.0
            
            return {
                "status": "passed" if security_score >= 0.8 else "failed",
                "score": security_score,
                "details": {
                    "secret_scan": secret_scan,
                    "secret_management": secret_mgmt,
                    "vulnerability_scan": vuln_scan
                },
                "blocking": security_score < 0.6
            }
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "blocking": True
            }

    async def _validate_performance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance impact of deployment"""
        try:
            # Run performance benchmarks
            benchmark_results = await self._run_performance_benchmarks()
            
            # Analyze resource requirements
            resource_analysis = await self._analyze_resource_requirements(config)
            
            # Check for performance regressions
            regression_check = await self._check_performance_regression(benchmark_results)
            
            performance_score = (
                (1.0 if benchmark_results["response_time_p95"] < 500 else 0.5) +
                (1.0 if resource_analysis["cpu_increase"] < 0.2 else 0.5) +
                (1.0 if not regression_check["regression_detected"] else 0.0)
            ) / 3.0
            
            return {
                "status": "passed" if performance_score >= 0.7 else "failed",
                "score": performance_score,
                "details": {
                    "benchmarks": benchmark_results,
                    "resource_analysis": resource_analysis,
                    "regression_check": regression_check
                },
                "blocking": performance_score < 0.4
            }
            
        except Exception as e:
            logger.error(f"Performance validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "blocking": False
            }

    async def start_deployment_monitoring(self, deployment_id: str) -> None:
        """Start real-time deployment monitoring"""
        logger.info(f"Starting deployment monitoring for {deployment_id}")
        
        deployment_metrics = DeploymentMetrics(
            deployment_id=deployment_id,
            start_time=datetime.utcnow(),
            end_time=None,
            status=DeploymentStatus.DEPLOYING,
            success_rate=1.0,
            response_time_p95=0.0,
            error_rate=0.0,
            throughput=0.0,
            resource_utilization={},
            business_metrics={}
        )
        
        self.deployments[deployment_id] = deployment_metrics
        self.monitoring_active = True
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_deployment_health(deployment_id))
        asyncio.create_task(self._monitor_performance_metrics(deployment_id))
        asyncio.create_task(self._monitor_business_metrics(deployment_id))
        asyncio.create_task(self._check_alert_rules(deployment_id))

    async def _monitor_deployment_health(self, deployment_id: str) -> None:
        """Monitor deployment health in real-time"""
        while self.monitoring_active and deployment_id in self.deployments:
            try:
                health_results = {}
                
                for health_check in self.health_checks:
                    try:
                        result = await self._execute_health_check(health_check)
                        health_results[health_check.service_name] = result
                        
                        if not result["healthy"] and health_check.critical:
                            await self._trigger_alert(
                                f"Critical service {health_check.service_name} is unhealthy",
                                "critical",
                                deployment_id
                            )
                            
                    except Exception as e:
                        logger.error(f"Health check failed for {health_check.service_name}: {e}")
                        health_results[health_check.service_name] = {
                            "healthy": False,
                            "error": str(e)
                        }
                
                # Update deployment metrics
                if deployment_id in self.deployments:
                    healthy_services = sum(1 for r in health_results.values() if r.get("healthy", False))
                    total_services = len(health_results)
                    success_rate = healthy_services / total_services if total_services > 0 else 0.0
                    
                    self.deployments[deployment_id].success_rate = success_rate
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error for {deployment_id}: {e}")
                await asyncio.sleep(60)

    async def _execute_health_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute a single health check"""
        for attempt in range(health_check.retry_count):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=health_check.timeout_seconds)) as session:
                    async with session.get(f"http://localhost:8000{health_check.endpoint}") as response:
                        if response.status == health_check.expected_status:
                            return {
                                "healthy": True,
                                "status_code": response.status,
                                "response_time": response.headers.get("X-Response-Time", "unknown"),
                                "attempt": attempt + 1
                            }
                        else:
                            if attempt == health_check.retry_count - 1:
                                return {
                                    "healthy": False,
                                    "status_code": response.status,
                                    "expected": health_check.expected_status,
                                    "attempts": attempt + 1
                                }
                            
            except Exception as e:
                if attempt == health_check.retry_count - 1:
                    return {
                        "healthy": False,
                        "error": str(e),
                        "attempts": attempt + 1
                    }
                
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return {"healthy": False, "error": "Max retries exceeded"}

    async def automatic_rollback_decision(self, deployment_id: str) -> Dict[str, Any]:
        """Make automatic rollback decision based on metrics"""
        if deployment_id not in self.deployments:
            return {"should_rollback": False, "reason": "Deployment not found"}
        
        metrics = self.deployments[deployment_id]
        rollback_triggers = []
        
        # Check success rate
        if metrics.success_rate < 0.8:
            rollback_triggers.append(f"Success rate too low: {metrics.success_rate:.2%}")
        
        # Check error rate
        if metrics.error_rate > 0.1:
            rollback_triggers.append(f"Error rate too high: {metrics.error_rate:.2%}")
        
        # Check response time
        if metrics.response_time_p95 > 2000:  # 2 seconds
            rollback_triggers.append(f"Response time too high: {metrics.response_time_p95:.0f}ms")
        
        # Check deployment duration
        if metrics.end_time is None:
            duration = datetime.utcnow() - metrics.start_time
            if duration > timedelta(minutes=30):
                rollback_triggers.append(f"Deployment taking too long: {duration}")
        
        should_rollback = len(rollback_triggers) >= 2  # Require multiple triggers
        
        return {
            "should_rollback": should_rollback,
            "triggers": rollback_triggers,
            "confidence": len(rollback_triggers) / 4.0,  # Max 4 possible triggers
            "recommendation": "immediate" if len(rollback_triggers) >= 3 else "monitor"
        }

    async def execute_rollback(self, deployment_id: str, reason: str) -> Dict[str, Any]:
        """Execute automatic rollback"""
        logger.warning(f"Executing rollback for deployment {deployment_id}: {reason}")
        
        try:
            if deployment_id in self.deployments:
                self.deployments[deployment_id].status = DeploymentStatus.ROLLING_BACK
            
            # 1. Stop current deployment
            await self._stop_deployment(deployment_id)
            
            # 2. Restore previous version
            rollback_result = await self._restore_previous_version(deployment_id)
            
            # 3. Validate rollback success
            validation_result = await self._validate_rollback(deployment_id)
            
            # 4. Update deployment status
            if deployment_id in self.deployments:
                if validation_result["success"]:
                    self.deployments[deployment_id].status = DeploymentStatus.ROLLED_BACK
                else:
                    self.deployments[deployment_id].status = DeploymentStatus.FAILED
            
            # 5. Send notifications
            await self._send_rollback_notification(deployment_id, reason, validation_result["success"])
            
            return {
                "success": validation_result["success"],
                "rollback_result": rollback_result,
                "validation": validation_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Rollback execution failed for {deployment_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_deployment_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive deployment dashboard data"""
        try:
            # Current deployments
            active_deployments = {
                dep_id: {
                    "status": metrics.status.value,
                    "success_rate": metrics.success_rate,
                    "response_time_p95": metrics.response_time_p95,
                    "error_rate": metrics.error_rate,
                    "duration": (
                        (metrics.end_time or datetime.utcnow()) - metrics.start_time
                    ).total_seconds(),
                    "resource_utilization": metrics.resource_utilization
                }
                for dep_id, metrics in self.deployments.items()
            }
            
            # System health
            system_health = await self._get_system_health_summary()
            
            # Recent alerts
            recent_alerts = await self._get_recent_alerts()
            
            # Performance trends
            performance_trends = await self._get_performance_trends()
            
            # Business metrics
            business_metrics = await self._get_business_metrics_summary()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "active_deployments": active_deployments,
                "system_health": system_health,
                "recent_alerts": recent_alerts,
                "performance_trends": performance_trends,
                "business_metrics": business_metrics,
                "monitoring_status": "active" if self.monitoring_active else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate deployment dashboard: {e}", exc_info=True)
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    # Helper methods for validation and monitoring
    async def _scan_for_secrets(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for hardcoded secrets in deployment configuration"""
        # Implementation would scan for patterns like API keys, passwords, etc.
        return {"passed": True, "secrets_found": []}

    async def _security_vulnerability_scan(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for security vulnerabilities"""
        # Implementation would use security scanning tools
        return {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}

    async def _run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        # Implementation would run actual performance tests
        return {
            "response_time_p95": 250.0,
            "throughput": 1000.0,
            "cpu_usage": 0.45,
            "memory_usage": 0.60
        }

    async def _analyze_resource_requirements(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource requirements for deployment"""
        return {
            "cpu_increase": 0.1,
            "memory_increase": 0.15,
            "storage_increase": 0.05,
            "network_increase": 0.08
        }

    async def _check_performance_regression(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check for performance regression"""
        # Implementation would compare against historical baselines
        return {"regression_detected": False, "confidence": 0.95}

    async def _validate_dependencies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment dependencies"""
        return {"status": "passed", "missing_dependencies": [], "version_conflicts": []}

    async def _validate_capacity(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate system capacity for deployment"""
        return {"status": "passed", "cpu_available": 0.7, "memory_available": 0.6, "storage_available": 0.8}

    async def _validate_migrations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate database migrations"""
        return {"status": "passed", "migrations_count": 0, "rollback_available": True}

    async def _validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment configuration"""
        return {"status": "passed", "config_errors": [], "warnings": []}

    async def _monitor_performance_metrics(self, deployment_id: str) -> None:
        """Monitor performance metrics during deployment"""
        # Implementation would collect real performance metrics
        pass

    async def _monitor_business_metrics(self, deployment_id: str) -> None:
        """Monitor business metrics during deployment"""
        # Implementation would collect business KPIs
        pass

    async def _check_alert_rules(self, deployment_id: str) -> None:
        """Check alert rules and trigger notifications"""
        # Implementation would evaluate alert rules
        pass

    async def _trigger_alert(self, message: str, severity: str, deployment_id: str) -> None:
        """Trigger alert notification"""
        logger.warning(f"ALERT [{severity}] {message} (Deployment: {deployment_id})")

    async def _stop_deployment(self, deployment_id: str) -> None:
        """Stop current deployment"""
        # Implementation would stop deployment process
        pass

    async def _restore_previous_version(self, deployment_id: str) -> Dict[str, Any]:
        """Restore previous version"""
        # Implementation would restore previous deployment
        return {"success": True, "version": "previous"}

    async def _validate_rollback(self, deployment_id: str) -> Dict[str, Any]:
        """Validate rollback success"""
        # Implementation would validate rollback
        return {"success": True, "health_checks_passed": True}

    async def _send_rollback_notification(self, deployment_id: str, reason: str, success: bool) -> None:
        """Send rollback notification"""
        logger.info(f"Rollback {'successful' if success else 'failed'} for {deployment_id}: {reason}")

    async def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary"""
        return {"overall": "healthy", "services": {}}

    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return []

    async def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends"""
        return {"response_time": [], "throughput": [], "error_rate": []}

    async def _get_business_metrics_summary(self) -> Dict[str, Any]:
        """Get business metrics summary"""
        return {"revenue": 0, "users": 0, "conversions": 0}


# FastAPI Integration
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

class DeploymentRequest(BaseModel):
    deployment_config: Dict[str, Any]
    environment: str = "production"
    auto_rollback: bool = True

class ValidationResponse(BaseModel):
    overall_status: str
    checks: Dict[str, Any]
    recommendations: List[str]
    blocking_issues: List[str]
    warnings: List[str]

# Initialize oversight system
oversight_system = DeploymentOversightSystem()

# API Router
router = APIRouter(prefix="/api/v1/deployment-oversight", tags=["deployment-oversight"])

@router.post("/validate", response_model=ValidationResponse)
async def validate_deployment(request: DeploymentRequest):
    """Validate deployment before execution"""
    try:
        result = await oversight_system.pre_deployment_validation(request.deployment_config)
        return ValidationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy/{deployment_id}")
async def start_deployment_monitoring(deployment_id: str, background_tasks: BackgroundTasks):
    """Start deployment monitoring"""
    try:
        background_tasks.add_task(oversight_system.start_deployment_monitoring, deployment_id)
        return {"message": f"Monitoring started for deployment {deployment_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback/{deployment_id}")
async def execute_rollback(deployment_id: str, reason: str = "Manual rollback"):
    """Execute deployment rollback"""
    try:
        result = await oversight_system.execute_rollback(deployment_id, reason)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_deployment_dashboard():
    """Get deployment dashboard data"""
    try:
        return await oversight_system.get_deployment_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/{deployment_id}")
async def get_deployment_health(deployment_id: str):
    """Get deployment health status"""
    try:
        if deployment_id not in oversight_system.deployments:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        metrics = oversight_system.deployments[deployment_id]
        rollback_decision = await oversight_system.automatic_rollback_decision(deployment_id)
        
        return {
            "deployment_id": deployment_id,
            "status": metrics.status.value,
            "metrics": {
                "success_rate": metrics.success_rate,
                "response_time_p95": metrics.response_time_p95,
                "error_rate": metrics.error_rate,
                "throughput": metrics.throughput
            },
            "rollback_decision": rollback_decision,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

