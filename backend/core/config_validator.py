"""
Configuration Validator

Utility module for validating critical configurations at application startup.
This ensures that all required services are accessible and properly configured
before the application begins processing requests.

Key Features:
- Gong API credentials validation
- Snowflake connection testing
- HubSpot Secure Data Share accessibility
- Fast-fail startup with clear error messages
- Comprehensive service health checks
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

import snowflake.connector
import aiohttp

from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status of configuration validation"""
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a configuration validation check"""
    service: str
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ConfigurationValidator:
    """
    Validates critical configurations at application startup
    
    This class performs comprehensive validation of all required services
    and configurations to ensure the application can operate properly.
    """
    
    def __init__(self):
        self.validation_results: List[ValidationResult] = []
        self.critical_failures: List[str] = []
        
    async def validate_all_configurations(self, fail_fast: bool = True) -> Dict[str, Any]:
        """
        Validate all critical configurations
        
        Args:
            fail_fast: Whether to stop on first critical failure
            
        Returns:
            Comprehensive validation report
        """
        logger.info("🔍 Starting comprehensive configuration validation...")
        
        validation_tasks = [
            self._validate_gong_api_credentials(),
            self._validate_snowflake_connection(),
            self._validate_hubspot_data_share(),
            self._validate_openai_api_key(),
            self._validate_pinecone_credentials(),
            self._validate_essential_config_values()
        ]
        
        # Run validations concurrently for speed
        validation_results = await asyncio.gather(
            *validation_tasks,
            return_exceptions=True
        )
        
        # Process results
        for result in validation_results:
            if isinstance(result, Exception):
                self.validation_results.append(ValidationResult(
                    service="unknown",
                    status=ValidationStatus.FAILURE,
                    message=f"Validation error: {str(result)}"
                ))
                self.critical_failures.append(str(result))
            elif isinstance(result, ValidationResult):
                self.validation_results.append(result)
                if result.status == ValidationStatus.FAILURE:
                    self.critical_failures.append(f"{result.service}: {result.message}")
        
        # Generate summary report
        report = self._generate_validation_report()
        
        # Fail fast if requested and critical failures exist
        if fail_fast and self.critical_failures:
            logger.error("❌ Critical configuration failures detected - application cannot start")
            for failure in self.critical_failures:
                logger.error(f"  • {failure}")
            raise RuntimeError(f"Configuration validation failed: {len(self.critical_failures)} critical errors")
        
        return report
    
    async def _validate_gong_api_credentials(self) -> ValidationResult:
        """Validate Gong API credentials and connectivity"""
        service = "Gong API"
        
        try:
            # Get credentials from config
            gong_access_key = config.get("gong_access_key")
            gong_secret_key = config.get("gong_secret_key")
            
            if not gong_access_key or not gong_secret_key:
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.FAILURE,
                    message="Gong API credentials not found in configuration",
                    details={"missing_keys": ["gong_access_key", "gong_secret_key"]}
                )
            
            # Test API connectivity with a simple request
            auth = aiohttp.BasicAuth(gong_access_key, gong_secret_key)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.gong.io/v2/users",
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ValidationResult(
                            service=service,
                            status=ValidationStatus.SUCCESS,
                            message="Gong API credentials validated successfully",
                            details={
                                "users_count": len(data.get("users", [])),
                                "api_version": "v2"
                            }
                        )
                    else:
                        return ValidationResult(
                            service=service,
                            status=ValidationStatus.FAILURE,
                            message=f"Gong API authentication failed (HTTP {response.status})",
                            details={"status_code": response.status}
                        )
        
        except asyncio.TimeoutError:
            return ValidationResult(
                service=service,
                status=ValidationStatus.WARNING,
                message="Gong API request timed out - may indicate network issues",
                details={"timeout_seconds": 10}
            )
        except Exception as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.FAILURE,
                message=f"Gong API validation error: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    async def _validate_snowflake_connection(self) -> ValidationResult:
        """Validate Snowflake connection and basic functionality"""
        service = "Snowflake"
        
        try:
            # Get Snowflake credentials
            snowflake_user = config.get("snowflake_user")
            snowflake_password = config.get("snowflake_password")
            snowflake_account = config.get("snowflake_account")
            
            if not all([snowflake_user, snowflake_password, snowflake_account]):
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.FAILURE,
                    message="Snowflake credentials incomplete",
                    details={
                        "missing_configs": [
                            k for k, v in {
                                "snowflake_user": snowflake_user,
                                "snowflake_password": snowflake_password,
                                "snowflake_account": snowflake_account
                            }.items() if not v
                        ]
                    }
                )
            
            # Test connection
            connection = snowflake.connector.connect(
                user=snowflake_user,
                password=snowflake_password,
                account=snowflake_account,
                warehouse=config.get("snowflake_warehouse", "COMPUTE_WH"),
                database=config.get("snowflake_database", "SOPHIA_AI"),
                role=config.get("snowflake_role", "ACCOUNTADMIN"),
                login_timeout=10
            )
            
            # Test basic query
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT CURRENT_VERSION(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
                result = cursor.fetchone()
                
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.SUCCESS,
                    message="Snowflake connection validated successfully",
                    details={
                        "version": result[0] if result else "unknown",
                        "warehouse": result[1] if result else "unknown",
                        "database": result[2] if result else "unknown"
                    }
                )
            finally:
                cursor.close()
                connection.close()
        
        except snowflake.connector.errors.DatabaseError as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.FAILURE,
                message=f"Snowflake authentication failed: {str(e)}",
                details={"error_code": getattr(e, 'errno', None)}
            )
        except Exception as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.FAILURE,
                message=f"Snowflake connection error: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    async def _validate_hubspot_data_share(self) -> ValidationResult:
        """Validate HubSpot Secure Data Share accessibility"""
        service = "HubSpot Secure Data Share"
        
        try:
            # Get Snowflake connection (reuse validation logic)
            snowflake_user = config.get("snowflake_user")
            snowflake_password = config.get("snowflake_password") 
            snowflake_account = config.get("snowflake_account")
            
            if not all([snowflake_user, snowflake_password, snowflake_account]):
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.SKIPPED,
                    message="Skipped - Snowflake credentials not available"
                )
            
            connection = snowflake.connector.connect(
                user=snowflake_user,
                password=snowflake_password,
                account=snowflake_account,
                warehouse=config.get("snowflake_warehouse", "COMPUTE_WH"),
                role=config.get("snowflake_role", "ACCOUNTADMIN"),
                login_timeout=10
            )
            
            cursor = connection.cursor()
            try:
                # Test if HubSpot share exists and is accessible
                cursor.execute("SHOW SHARES LIKE 'HUBSPOT%'")
                shares = cursor.fetchall()
                
                if not shares:
                    return ValidationResult(
                        service=service,
                        status=ValidationStatus.WARNING,
                        message="No HubSpot data shares found - may need to be configured",
                        details={"shares_found": 0}
                    )
                
                # Try to access a basic HubSpot table (this will fail if share not properly configured)
                try:
                    cursor.execute("SELECT COUNT(*) FROM HUBSPOT_SECURE_SHARE.PUBLIC.CONTACTS LIMIT 1")
                    result = cursor.fetchone()
                    
                    return ValidationResult(
                        service=service,
                        status=ValidationStatus.SUCCESS,
                        message="HubSpot Secure Data Share accessible",
                        details={
                            "shares_found": len(shares),
                            "test_query": "successful"
                        }
                    )
                except Exception:
                    return ValidationResult(
                        service=service,
                        status=ValidationStatus.WARNING,
                        message="HubSpot shares found but not accessible - may need configuration",
                        details={"shares_found": len(shares)}
                    )
            
            finally:
                cursor.close()
                connection.close()
        
        except Exception as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.WARNING,
                message=f"Could not validate HubSpot data share: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    async def _validate_openai_api_key(self) -> ValidationResult:
        """Validate OpenAI API key"""
        service = "OpenAI API"
        
        try:
            openai_api_key = config.get("openai_api_key")
            
            if not openai_api_key:
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.WARNING,
                    message="OpenAI API key not configured - AI features may be limited"
                )
            
            # Test API key with a simple request
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ValidationResult(
                            service=service,
                            status=ValidationStatus.SUCCESS,
                            message="OpenAI API key validated successfully",
                            details={"models_available": len(data.get("data", []))}
                        )
                    else:
                        return ValidationResult(
                            service=service,
                            status=ValidationStatus.FAILURE,
                            message=f"OpenAI API key validation failed (HTTP {response.status})"
                        )
        
        except Exception as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.WARNING,
                message=f"OpenAI API validation error: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    async def _validate_pinecone_credentials(self) -> ValidationResult:
        """Validate Pinecone credentials"""
        service = "Pinecone"
        
        try:
            pinecone_api_key = config.get("pinecone_api_key")
            
            if not pinecone_api_key:
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.WARNING,
                    message="Pinecone API key not configured - vector search may be limited"
                )
            
            # Test Pinecone API
            headers = {
                "Api-Key": pinecone_api_key,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://controller.pinecone.io/actions/whoami",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ValidationResult(
                            service=service,
                            status=ValidationStatus.SUCCESS,
                            message="Pinecone API key validated successfully",
                            details={"user_info": data}
                        )
                    else:
                        return ValidationResult(
                            service=service,
                            status=ValidationStatus.FAILURE,
                            message=f"Pinecone API key validation failed (HTTP {response.status})"
                        )
        
        except Exception as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.WARNING,
                message=f"Pinecone API validation error: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    async def _validate_essential_config_values(self) -> ValidationResult:
        """Validate essential configuration values"""
        service = "Essential Configuration"
        
        try:
            essential_configs = {
                "snowflake_database": config.get("snowflake_database"),
                "snowflake_warehouse": config.get("snowflake_warehouse"),
                "snowflake_schema": config.get("snowflake_schema")
            }
            
            missing_configs = [k for k, v in essential_configs.items() if not v]
            
            if missing_configs:
                return ValidationResult(
                    service=service,
                    status=ValidationStatus.WARNING,
                    message=f"Some essential configurations missing: {', '.join(missing_configs)}",
                    details={"missing_configs": missing_configs}
                )
            
            return ValidationResult(
                service=service,
                status=ValidationStatus.SUCCESS,
                message="All essential configurations present",
                details=essential_configs
            )
        
        except Exception as e:
            return ValidationResult(
                service=service,
                status=ValidationStatus.FAILURE,
                message=f"Configuration validation error: {str(e)}"
            )
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Count results by status
        status_counts = {}
        for status in ValidationStatus:
            status_counts[status.value] = sum(
                1 for result in self.validation_results 
                if result.status == status
            )
        
        # Determine overall status
        if self.critical_failures:
            overall_status = "FAILED"
        elif status_counts.get("failure", 0) > 0:
            overall_status = "DEGRADED"
        elif status_counts.get("warning", 0) > 0:
            overall_status = "WARNING"
        else:
            overall_status = "HEALTHY"
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "total_checks": len(self.validation_results),
                "successful": status_counts.get("success", 0),
                "warnings": status_counts.get("warning", 0),
                "failures": status_counts.get("failure", 0),
                "skipped": status_counts.get("skipped", 0)
            },
            "critical_failures": self.critical_failures,
            "detailed_results": [
                {
                    "service": result.service,
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.validation_results
            ]
        }
        
        # Log summary
        logger.info(f"🔍 Configuration validation complete: {overall_status}")
        logger.info(f"  ✅ {status_counts.get('success', 0)} successful")
        logger.info(f"  ⚠️  {status_counts.get('warning', 0)} warnings")
        logger.info(f"  ❌ {status_counts.get('failure', 0)} failures")
        logger.info(f"  ⏭️  {status_counts.get('skipped', 0)} skipped")
        
        return report


# Global validator instance
config_validator = ConfigurationValidator()


async def validate_startup_configuration(fail_fast: bool = True) -> Dict[str, Any]:
    """
    Validate all critical configurations at startup
    
    Args:
        fail_fast: Whether to raise exception on critical failures
        
    Returns:
        Validation report
        
    Raises:
        RuntimeError: If fail_fast=True and critical failures detected
    """
    return await config_validator.validate_all_configurations(fail_fast=fail_fast)


async def quick_health_check() -> bool:
    """
    Perform a quick health check of critical services
    
    Returns:
        True if all critical services are healthy
    """
    try:
        report = await validate_startup_configuration(fail_fast=False)
        return report["overall_status"] in ["HEALTHY", "WARNING"]
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False 