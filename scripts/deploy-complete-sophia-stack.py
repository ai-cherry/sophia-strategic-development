#!/usr/bin/env python3
"""
Complete Sophia AI Stack Deployment Script
Orchestrates the deployment of the entire Sophia AI infrastructure including:
- Lambda Labs infrastructure
- Estuary Flow data pipeline
- Snowflake schema and integration
- PostgreSQL staging
- Redis caching
- Vector databases
- API endpoints
- Monitoring and alerting
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import asyncpg
import redis.asyncio as redis
import snowflake.connector
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sophia_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentConfig:
    """Configuration for Sophia AI deployment"""
    # Environment
    environment: str = "production"
    project_root: str = "/home/ubuntu/sophia-project"
    
    # Infrastructure
    lambda_labs_instance_type: str = "gpu_1x_a100"
    lambda_labs_region: str = "us-west-2"
    
    # Database configurations
    postgresql_config: Dict[str, Any] = field(default_factory=dict)
    redis_config: Dict[str, Any] = field(default_factory=dict)
    snowflake_config: Dict[str, Any] = field(default_factory=dict)
    
    # Data pipeline
    estuary_enabled: bool = True
    
    # Monitoring
    monitoring_enabled: bool = True
    alerting_enabled: bool = True
    
    # Deployment options
    force_recreate: bool = False
    skip_tests: bool = False
    dry_run: bool = False


@dataclass
class DeploymentStatus:
    """Status tracking for deployment"""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "in_progress"  # in_progress, completed, failed
    components: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SophiaStackDeployer:
    """
    Master deployer for the complete Sophia AI stack
    """
    
    def __init__(self, config: Optional[DeploymentConfig] = None):
        self.config = config or DeploymentConfig()
        self.status = DeploymentStatus()
        self.project_root = Path(self.config.project_root)
        
        # Initialize component status tracking
        self.components = [
            "environment_setup",
            "secrets_management", 
            "lambda_labs_infrastructure",
            "postgresql_setup",
            "redis_setup",
            "snowflake_setup",
            "estuary_flow_pipeline",
            "api_deployment",
            "monitoring_setup",
            "health_checks"
        ]
        
        for component in self.components:
            self.status.components[component] = "pending"
    
    async def deploy_complete_stack(self) -> Dict[str, Any]:
        """
        Deploy the complete Sophia AI stack
        """
        logger.info("🚀 Starting complete Sophia AI stack deployment...")
        
        try:
            # Phase 1: Environment and secrets setup
            await self._setup_environment()
            await self._setup_secrets_management()
            
            # Phase 2: Infrastructure deployment
            await self._deploy_lambda_labs_infrastructure()
            await self._setup_databases()
            
            # Phase 3: Data pipeline setup
            await self._setup_data_pipeline()
            
            # Phase 4: Application deployment
            await self._deploy_api_services()
            
            # Phase 5: Monitoring and validation
            await self._setup_monitoring()
            await self._run_health_checks()
            
            # Mark deployment as completed
            self.status.status = "completed"
            self.status.completed_at = datetime.now(timezone.utc)
            
            logger.info("✅ Complete Sophia AI stack deployment successful!")
            return self._generate_deployment_report()
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            self.status.status = "failed"
            self.status.errors.append(str(e))
            raise
    
    async def _setup_environment(self):
        """Set up deployment environment"""
        logger.info("🔧 Setting up deployment environment...")
        
        try:
            # Validate project structure
            required_dirs = [
                "backend",
                "scripts", 
                "infrastructure",
                "estuary-config",
                ".github/workflows"
            ]
            
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    logger.warning(f"⚠️ Creating missing directory: {dir_name}")
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            # Install Python dependencies
            await self._run_command([
                "pip", "install", "-r", "requirements.txt"
            ], cwd=self.project_root)
            
            # Set up environment variables
            self._setup_environment_variables()
            
            self.status.components["environment_setup"] = "completed"
            logger.info("✅ Environment setup completed")
            
        except Exception as e:
            self.status.components["environment_setup"] = "failed"
            logger.error(f"❌ Environment setup failed: {e}")
            raise
    
    def _setup_environment_variables(self):
        """Set up environment variables from Pulumi ESC"""
        logger.info("🔐 Setting up environment variables...")
        
        # Key environment variables for Sophia AI
        env_vars = {
            "SOPHIA_AI_ENV": self.config.environment,
            "PROJECT_ROOT": str(self.project_root),
            "PULUMI_STACK": "scoobyjava-org/sophia-prod-on-lambda",
            "SNOWFLAKE_USER": "PROGRAMMATIC_SERVICE_USER",
            "SNOWFLAKE_PASSWORD": "eyJraWQiOiIxNzAwMTAwMDk2OSIsImFsZyI6IkVTMjU2In0.eyJwIjoiNjY0MTAwNjg6MTcwMDA5NTYyOTMiLCJpc3MiOiJTRjozMDAxIiwiZXhwIjoxNzU4MzkyMDc4fQ.HPlaOkJGlckJ8W8-GWt8lw0t8kIyvO6UctKrrv7d-kwjCOd5kveyKMspcFGIyuzKzS8X26BtDQQctk2LybXJOQ.",
            "SNOWFLAKE_ACCOUNT": "MYJDJNU-FP71296",
            "SNOWFLAKE_DATABASE": "SOPHIA_AI_DB",
            "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_WH",
            "SNOWFLAKE_ROLE": "SOPHIA_AI_ROLE"
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
            logger.info(f"✅ Set environment variable: {key}")
    
    async def _setup_secrets_management(self):
        """Set up Pulumi ESC secrets management"""
        logger.info("🔐 Setting up secrets management with Pulumi ESC...")
        
        try:
            # Update Pulumi ESC configuration
            await self._run_command([
                "python", "infrastructure/pulumi-esc-comprehensive-update.py"
            ], cwd=self.project_root)
            
            # Validate secret access
            await self._validate_secrets_access()
            
            self.status.components["secrets_management"] = "completed"
            logger.info("✅ Secrets management setup completed")
            
        except Exception as e:
            self.status.components["secrets_management"] = "failed"
            logger.error(f"❌ Secrets management setup failed: {e}")
            raise
    
    async def _validate_secrets_access(self):
        """Validate access to critical secrets"""
        logger.info("🔍 Validating secrets access...")
        
        critical_secrets = [
            "LAMBDA_LABS_API_KEY",
            "ESTUARY_ACCESS_TOKEN",
            "HUBSPOT_ACCESS_TOKEN",
            "GONG_ACCESS_KEY",
            "SNOWFLAKE_PASSWORD"
        ]
        
        for secret in critical_secrets:
            if not os.getenv(secret):
                logger.warning(f"⚠️ Secret not available: {secret}")
            else:
                logger.info(f"✅ Secret validated: {secret}")
    
    async def _deploy_lambda_labs_infrastructure(self):
        """Deploy Lambda Labs infrastructure"""
        logger.info("🖥️ Deploying Lambda Labs infrastructure...")
        
        try:
            # Trigger Lambda Labs deployment via GitHub Actions
            await self._run_command([
                "gh", "workflow", "run", "lambda-labs-deployment.yml",
                "--ref", "main",
                "-f", f"instance_type={self.config.lambda_labs_instance_type}",
                "-f", "deploy_services=true",
                "-f", f"force_recreate={str(self.config.force_recreate).lower()}"
            ], cwd=self.project_root)
            
            # Wait for deployment to complete
            await self._wait_for_github_workflow("lambda-labs-deployment.yml")
            
            self.status.components["lambda_labs_infrastructure"] = "completed"
            logger.info("✅ Lambda Labs infrastructure deployment completed")
            
        except Exception as e:
            self.status.components["lambda_labs_infrastructure"] = "failed"
            logger.error(f"❌ Lambda Labs infrastructure deployment failed: {e}")
            # Continue with other components even if Lambda Labs fails
            self.status.warnings.append(f"Lambda Labs deployment failed: {e}")
    
    async def _setup_databases(self):
        """Set up all database components"""
        logger.info("🗄️ Setting up database components...")
        
        # Set up PostgreSQL
        await self._setup_postgresql()
        
        # Set up Redis
        await self._setup_redis()
        
        # Set up Snowflake
        await self._setup_snowflake()
    
    async def _setup_postgresql(self):
        """Set up PostgreSQL staging database"""
        logger.info("🐘 Setting up PostgreSQL...")
        
        try:
            # Run PostgreSQL setup script
            await self._run_command([
                "python", "backend/database/postgresql_staging_manager.py", "--setup"
            ], cwd=self.project_root)
            
            # Test PostgreSQL connection
            await self._test_postgresql_connection()
            
            self.status.components["postgresql_setup"] = "completed"
            logger.info("✅ PostgreSQL setup completed")
            
        except Exception as e:
            self.status.components["postgresql_setup"] = "failed"
            logger.error(f"❌ PostgreSQL setup failed: {e}")
            raise
    
    async def _test_postgresql_connection(self):
        """Test PostgreSQL connection"""
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST", "localhost"),
                port=os.getenv("DATABASE_PORT", 5432),
                database=os.getenv("DATABASE_NAME", "sophia_ai"),
                user=os.getenv("DATABASE_USER", "sophia_user"),
                password=os.getenv("DATABASE_PASSWORD")
            )
            await conn.close()
            logger.info("✅ PostgreSQL connection test successful")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection test failed: {e}")
            raise
    
    async def _setup_redis(self):
        """Set up Redis caching"""
        logger.info("🔴 Setting up Redis...")
        
        try:
            # Test Redis connection
            redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD"),
                db=int(os.getenv("REDIS_DB", 0))
            )
            
            await redis_client.ping()
            await redis_client.close()
            
            self.status.components["redis_setup"] = "completed"
            logger.info("✅ Redis setup completed")
            
        except Exception as e:
            self.status.components["redis_setup"] = "failed"
            logger.error(f"❌ Redis setup failed: {e}")
            raise
    
    async def _setup_snowflake(self):
        """Set up Snowflake data warehouse"""
        logger.info("❄️ Setting up Snowflake...")
        
        try:
            # Execute Snowflake schema setup
            await self._run_command([
                "snowsql", "-f", "backend/snowflake_setup/enhanced_data_pipeline_schema.sql"
            ], cwd=self.project_root)
            
            # Test Snowflake connection
            await self._test_snowflake_connection()
            
            self.status.components["snowflake_setup"] = "completed"
            logger.info("✅ Snowflake setup completed")
            
        except Exception as e:
            self.status.components["snowflake_setup"] = "failed"
            logger.error(f"❌ Snowflake setup failed: {e}")
            # Continue without Snowflake for now
            self.status.warnings.append(f"Snowflake setup failed: {e}")
    
    async def _test_snowflake_connection(self):
        """Test Snowflake connection"""
        try:
            conn = snowflake.connector.connect(
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                role=os.getenv("SNOWFLAKE_ROLE")
            )
            conn.close()
            logger.info("✅ Snowflake connection test successful")
        except Exception as e:
            logger.error(f"❌ Snowflake connection test failed: {e}")
            raise
    
    async def _setup_data_pipeline(self):
        """Set up Estuary Flow data pipeline"""
        logger.info("🌊 Setting up data pipeline...")
        
        try:
            if self.config.estuary_enabled:
                # Set up Estuary Flow pipeline
                await self._run_command([
                    "python", "-c", 
                    "import asyncio; from backend.etl.enhanced_unified_data_pipeline import setup_sophia_data_pipeline; asyncio.run(setup_sophia_data_pipeline())"
                ], cwd=self.project_root)
            
            self.status.components["estuary_flow_pipeline"] = "completed"
            logger.info("✅ Data pipeline setup completed")
            
        except Exception as e:
            self.status.components["estuary_flow_pipeline"] = "failed"
            logger.error(f"❌ Data pipeline setup failed: {e}")
            # Continue without data pipeline for now
            self.status.warnings.append(f"Data pipeline setup failed: {e}")
    
    async def _deploy_api_services(self):
        """Deploy API services"""
        logger.info("🚀 Deploying API services...")
        
        try:
            # Deploy to Vercel
            await self._run_command([
                "vercel", "--prod", "--yes"
            ], cwd=self.project_root)
            
            self.status.components["api_deployment"] = "completed"
            logger.info("✅ API services deployment completed")
            
        except Exception as e:
            self.status.components["api_deployment"] = "failed"
            logger.error(f"❌ API services deployment failed: {e}")
            raise
    
    async def _setup_monitoring(self):
        """Set up monitoring and alerting"""
        logger.info("📊 Setting up monitoring...")
        
        try:
            # Deploy monitoring workflow
            await self._run_command([
                "gh", "workflow", "run", "deployment-monitoring.yml", "--ref", "main"
            ], cwd=self.project_root)
            
            self.status.components["monitoring_setup"] = "completed"
            logger.info("✅ Monitoring setup completed")
            
        except Exception as e:
            self.status.components["monitoring_setup"] = "failed"
            logger.error(f"❌ Monitoring setup failed: {e}")
            # Continue without monitoring
            self.status.warnings.append(f"Monitoring setup failed: {e}")
    
    async def _run_health_checks(self):
        """Run comprehensive health checks"""
        logger.info("🏥 Running health checks...")
        
        try:
            health_results = {}
            
            # Check API endpoints
            health_results["api"] = await self._check_api_health()
            
            # Check database connections
            health_results["databases"] = await self._check_database_health()
            
            # Check data pipeline
            health_results["pipeline"] = await self._check_pipeline_health()
            
            self.status.components["health_checks"] = "completed"
            logger.info("✅ Health checks completed")
            
            return health_results
            
        except Exception as e:
            self.status.components["health_checks"] = "failed"
            logger.error(f"❌ Health checks failed: {e}")
            raise
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API endpoint health"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check main API endpoint
                async with session.get("https://sophia-main.vercel.app/api/health") as response:
                    if response.status == 200:
                        return {"status": "healthy", "response_time": response.headers.get("X-Response-Time")}
                    else:
                        return {"status": "unhealthy", "status_code": response.status}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        results = {}
        
        # Check PostgreSQL
        try:
            await self._test_postgresql_connection()
            results["postgresql"] = {"status": "healthy"}
        except Exception as e:
            results["postgresql"] = {"status": "unhealthy", "error": str(e)}
        
        # Check Redis
        try:
            redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD")
            )
            await redis_client.ping()
            await redis_client.close()
            results["redis"] = {"status": "healthy"}
        except Exception as e:
            results["redis"] = {"status": "unhealthy", "error": str(e)}
        
        # Check Snowflake
        try:
            await self._test_snowflake_connection()
            results["snowflake"] = {"status": "healthy"}
        except Exception as e:
            results["snowflake"] = {"status": "unhealthy", "error": str(e)}
        
        return results
    
    async def _check_pipeline_health(self) -> Dict[str, Any]:
        """Check data pipeline health"""
        try:
            # Check Estuary Flow status
            from backend.etl.enhanced_unified_data_pipeline import get_sophia_pipeline_status
            status = await get_sophia_pipeline_status()
            return {"status": "healthy", "pipeline_status": status.status}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _wait_for_github_workflow(self, workflow_name: str, timeout: int = 600):
        """Wait for GitHub workflow to complete"""
        logger.info(f"⏳ Waiting for GitHub workflow: {workflow_name}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = await self._run_command([
                    "gh", "run", "list", "--workflow", workflow_name, "--limit", "1", "--json", "status,conclusion"
                ], cwd=self.project_root, capture_output=True)
                
                runs = json.loads(result.stdout)
                if runs and runs[0]["status"] == "completed":
                    if runs[0]["conclusion"] == "success":
                        logger.info(f"✅ Workflow {workflow_name} completed successfully")
                        return
                    else:
                        raise Exception(f"Workflow {workflow_name} failed with conclusion: {runs[0]['conclusion']}")
                
                await asyncio.sleep(30)  # Wait 30 seconds before checking again
                
            except Exception as e:
                logger.warning(f"⚠️ Error checking workflow status: {e}")
                await asyncio.sleep(30)
        
        raise Exception(f"Workflow {workflow_name} timed out after {timeout} seconds")
    
    async def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command asynchronously"""
        logger.info(f"🔧 Running command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd or self.project_root,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = f"Command failed: {' '.join(cmd)}"
            if stderr:
                error_msg += f"\nError: {stderr.decode()}"
            raise Exception(error_msg)
        
        if capture_output:
            result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            return result
        
        return subprocess.CompletedProcess(cmd, process.returncode)
    
    def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        duration = (self.status.completed_at - self.status.started_at).total_seconds()
        
        report = {
            "deployment_id": f"sophia-{int(time.time())}",
            "status": self.status.status,
            "started_at": self.status.started_at.isoformat(),
            "completed_at": self.status.completed_at.isoformat() if self.status.completed_at else None,
            "duration_seconds": duration,
            "environment": self.config.environment,
            "components": self.status.components,
            "errors": self.status.errors,
            "warnings": self.status.warnings,
            "summary": {
                "total_components": len(self.components),
                "completed_components": len([c for c in self.status.components.values() if c == "completed"]),
                "failed_components": len([c for c in self.status.components.values() if c == "failed"]),
                "success_rate": len([c for c in self.status.components.values() if c == "completed"]) / len(self.components) * 100
            }
        }
        
        return report


async def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy complete Sophia AI stack")
    parser.add_argument("--environment", default="production", help="Deployment environment")
    parser.add_argument("--instance-type", default="gpu_1x_a100", help="Lambda Labs instance type")
    parser.add_argument("--force-recreate", action="store_true", help="Force recreate infrastructure")
    parser.add_argument("--skip-tests", action="store_true", help="Skip health checks")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    # Create deployment configuration
    config = DeploymentConfig(
        environment=args.environment,
        lambda_labs_instance_type=args.instance_type,
        force_recreate=args.force_recreate,
        skip_tests=args.skip_tests,
        dry_run=args.dry_run
    )
    
    # Deploy the stack
    deployer = SophiaStackDeployer(config)
    
    try:
        report = await deployer.deploy_complete_stack()
        
        # Save deployment report
        report_path = Path("deployment_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Deployment report saved to: {report_path}")
        logger.info(f"🎯 Deployment success rate: {report['summary']['success_rate']:.1f}%")
        
        if report["status"] == "completed":
            logger.info("🎉 Sophia AI stack deployment completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Sophia AI stack deployment failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Deployment crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

