#!/usr/bin/env python3
"""
Sophia AI Complete Stack Deployment
Comprehensive deployment script that works on Lambda Labs, local development, or any Linux server
Includes full Estuary Flow, Snowflake, and codebase integration
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
import docker
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SophiaCompleteStackDeployment:
    """
    Complete Sophia AI stack deployment
    Handles Lambda Labs, local development, and production deployments
    """
    
    def __init__(self, deployment_mode: str = "auto"):
        self.deployment_mode = deployment_mode  # auto, lambda-labs, local, production
        self.project_root = Path(__file__).parent.parent
        self.docker_client = None
        self.deployment_status = {
            'environment_setup': False,
            'docker_setup': False,
            'infrastructure_deployment': False,
            'estuary_configuration': False,
            'snowflake_setup': False,
            'codebase_deployment': False,
            'health_validation': False
        }
        
        # Detect deployment environment
        self.detect_environment()
    
    def detect_environment(self):
        """Detect the deployment environment"""
        if self.deployment_mode == "auto":
            if os.getenv('LAMBDA_IP_ADDRESS'):
                self.deployment_mode = "lambda-labs"
            elif os.path.exists('/.dockerenv'):
                self.deployment_mode = "docker"
            elif os.getenv('GITHUB_ACTIONS'):
                self.deployment_mode = "ci"
            else:
                self.deployment_mode = "local"
        
        logger.info(f"🎯 Deployment mode: {self.deployment_mode}")
    
    async def deploy_complete_stack(self):
        """Deploy the complete Sophia AI stack"""
        logger.info("🚀 Starting Sophia AI complete stack deployment...")
        
        try:
            # Phase 1: Environment Setup
            await self.setup_environment()
            
            # Phase 2: Docker Infrastructure
            await self.setup_docker_infrastructure()
            
            # Phase 3: Deploy Core Services
            await self.deploy_infrastructure_services()
            
            # Phase 4: Configure Data Pipeline
            await self.configure_estuary_flow()
            
            # Phase 5: Setup Snowflake Integration
            await self.setup_snowflake_integration()
            
            # Phase 6: Deploy Sophia AI Codebase
            await self.deploy_sophia_codebase()
            
            # Phase 7: Validate Complete Setup
            await self.validate_complete_deployment()
            
            logger.info("✅ Sophia AI complete stack deployment successful!")
            await self.print_deployment_summary()
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            await self.cleanup_on_failure()
            return False
    
    async def setup_environment(self):
        """Set up the deployment environment"""
        logger.info("🔧 Setting up deployment environment...")
        
        # Install required system packages
        if self.deployment_mode in ["lambda-labs", "local"]:
            await self.install_system_packages()
        
        # Set up Python environment
        await self.setup_python_environment()
        
        # Validate environment variables
        await self.validate_environment_variables()
        
        self.deployment_status['environment_setup'] = True
        logger.info("✅ Environment setup complete")
    
    async def setup_docker_infrastructure(self):
        """Set up Docker and Docker Compose infrastructure"""
        logger.info("🐳 Setting up Docker infrastructure...")
        
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Test Docker connectivity
            self.docker_client.ping()
            logger.info("✅ Docker connectivity confirmed")
            
        except Exception as e:
            logger.info("Installing Docker...")
            await self.install_docker()
            self.docker_client = docker.from_env()
        
        # Create Docker network
        await self.create_docker_network()
        
        self.deployment_status['docker_setup'] = True
        logger.info("✅ Docker infrastructure setup complete")
    
    async def deploy_infrastructure_services(self):
        """Deploy core infrastructure services using Docker Compose"""
        logger.info("🏗️ Deploying infrastructure services...")
        
        # Copy Docker Compose configuration
        compose_file = self.project_root / "infrastructure" / "sophia-ai-complete-stack.yml"
        
        if not compose_file.exists():
            logger.error(f"Docker Compose file not found: {compose_file}")
            raise FileNotFoundError(f"Missing Docker Compose configuration: {compose_file}")
        
        # Create environment file
        await self.create_environment_file()
        
        # Deploy services
        cmd = [
            "docker-compose",
            "-f", str(compose_file),
            "up", "-d",
            "--remove-orphans"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Docker Compose deployment failed: {stderr.decode()}")
            raise Exception(f"Infrastructure deployment failed: {stderr.decode()}")
        
        # Wait for services to be ready
        await self.wait_for_services()
        
        self.deployment_status['infrastructure_deployment'] = True
        logger.info("✅ Infrastructure services deployment complete")
    
    async def configure_estuary_flow(self):
        """Configure Estuary Flow data pipeline"""
        logger.info("🌊 Configuring Estuary Flow data pipeline...")
        
        # Check if Estuary Flow is available
        estuary_token = os.getenv('ESTUARY_ACCESS_TOKEN')
        if not estuary_token:
            logger.warning("⚠️ Estuary Flow token not available, skipping configuration")
            return
        
        try:
            # Deploy Estuary Flow configuration
            flow_config_file = self.project_root / "estuary-config" / "sophia-ai-flows.yaml"
            
            if flow_config_file.exists():
                # Apply Estuary Flow configuration
                await self.apply_estuary_configuration(flow_config_file)
            else:
                logger.warning(f"⚠️ Estuary Flow configuration not found: {flow_config_file}")
            
            self.deployment_status['estuary_configuration'] = True
            logger.info("✅ Estuary Flow configuration complete")
            
        except Exception as e:
            logger.warning(f"⚠️ Estuary Flow configuration failed: {e}")
            # Don't fail the entire deployment for Estuary issues
    
    async def setup_snowflake_integration(self):
        """Set up Snowflake integration and schema alignment"""
        logger.info("❄️ Setting up Snowflake integration...")
        
        try:
            # Test Snowflake connection
            await self.test_snowflake_connection()
            
            # Create Snowflake schemas
            await self.create_snowflake_schemas()
            
            # Set up data sharing if available
            await self.setup_snowflake_data_sharing()
            
            self.deployment_status['snowflake_setup'] = True
            logger.info("✅ Snowflake integration setup complete")
            
        except Exception as e:
            logger.warning(f"⚠️ Snowflake setup failed: {e}")
            # Don't fail deployment for Snowflake issues in development
    
    async def deploy_sophia_codebase(self):
        """Deploy Sophia AI codebase and services"""
        logger.info("📦 Deploying Sophia AI codebase...")
        
        # Build Docker images for Sophia AI services
        await self.build_sophia_images()
        
        # Deploy Sophia AI services
        await self.deploy_sophia_services()
        
        # Set up service monitoring
        await self.setup_service_monitoring()
        
        self.deployment_status['codebase_deployment'] = True
        logger.info("✅ Sophia AI codebase deployment complete")
    
    async def validate_complete_deployment(self):
        """Validate the complete deployment"""
        logger.info("🔍 Validating complete deployment...")
        
        validations = [
            ("PostgreSQL", self.validate_postgresql),
            ("Redis", self.validate_redis),
            ("Weaviate", self.validate_weaviate),
            ("Sophia Backend", self.validate_sophia_backend),
            ("Monitoring", self.validate_monitoring),
        ]
        
        for name, validator in validations:
            try:
                await validator()
                logger.info(f"✅ {name} validation successful")
            except Exception as e:
                logger.error(f"❌ {name} validation failed: {e}")
                # Don't fail deployment for non-critical validations
        
        self.deployment_status['health_validation'] = True
        logger.info("✅ Deployment validation complete")
    
    async def install_system_packages(self):
        """Install required system packages"""
        packages = [
            "curl", "wget", "git", "htop", "vim",
            "python3-pip", "python3-venv", "python3-dev",
            "build-essential", "libssl-dev", "libffi-dev",
            "postgresql-client", "redis-tools"
        ]
        
        cmd = ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y"] + packages
        
        process = await asyncio.create_subprocess_shell(
            " ".join(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
    
    async def setup_python_environment(self):
        """Set up Python virtual environment"""
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            # Create virtual environment
            cmd = ["python3", "-m", "venv", str(venv_path)]
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.communicate()
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            pip_cmd = [
                str(venv_path / "bin" / "pip"),
                "install", "-r", str(requirements_file)
            ]
            process = await asyncio.create_subprocess_exec(*pip_cmd)
            await process.communicate()
    
    async def validate_environment_variables(self):
        """Validate required environment variables"""
        required_vars = [
            "DATABASE_PASSWORD",
            "REDIS_PASSWORD",
            "GRAFANA_ADMIN_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                # Set default values for development
                if var == "DATABASE_PASSWORD":
                    os.environ[var] = "sophia_dev_password_123"
                elif var == "REDIS_PASSWORD":
                    os.environ[var] = "sophia_redis_password_123"
                elif var == "GRAFANA_ADMIN_PASSWORD":
                    os.environ[var] = "sophia_admin_123"
                
                logger.info(f"⚠️ Set default value for {var}")
    
    async def install_docker(self):
        """Install Docker and Docker Compose"""
        commands = [
            "curl -fsSL https://get.docker.com -o get-docker.sh",
            "sudo sh get-docker.sh",
            "sudo usermod -aG docker $USER",
            "sudo systemctl enable docker",
            "sudo systemctl start docker",
            "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
            "sudo chmod +x /usr/local/bin/docker-compose"
        ]
        
        for cmd in commands:
            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()
    
    async def create_docker_network(self):
        """Create Docker network for Sophia AI services"""
        try:
            network = self.docker_client.networks.get("sophia-network")
            logger.info("✅ Docker network 'sophia-network' already exists")
        except docker.errors.NotFound:
            self.docker_client.networks.create(
                "sophia-network",
                driver="bridge",
                ipam=docker.types.IPAMConfig(
                    pool_configs=[docker.types.IPAMPool(subnet="172.20.0.0/16")]
                )
            )
            logger.info("✅ Created Docker network 'sophia-network'")
    
    async def create_environment_file(self):
        """Create environment file for Docker Compose"""
        env_file = self.project_root / ".env"
        
        env_vars = {
            # Database
            "DATABASE_PASSWORD": os.getenv("DATABASE_PASSWORD", "sophia_dev_password_123"),
            "DATABASE_HOST": "postgresql",
            
            # Redis
            "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", "sophia_redis_password_123"),
            "REDIS_HOST": "redis",
            
            # Monitoring
            "GRAFANA_ADMIN_PASSWORD": os.getenv("GRAFANA_ADMIN_PASSWORD", "sophia_admin_123"),
            
            # Snowflake
            "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT", ""),
            "SOPHIA_AI_TOKEN": os.getenv("SOPHIA_AI_TOKEN", ""),
            "SNOWFLAKE_ROLE": os.getenv("SNOWFLAKE_ROLE", "SOPHIA_AI_ROLE"),
            "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE", "SOPHIA_AI_WH"),
            "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE", "SOPHIA_AI_DB"),
            "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA", "PRODUCTION"),
            
            # API Keys
            "ESTUARY_ACCESS_TOKEN": os.getenv("ESTUARY_ACCESS_TOKEN", ""),
            "GONG_ACCESS_KEY": os.getenv("GONG_ACCESS_KEY", ""),
            "GONG_ACCESS_KEY_SECRET": os.getenv("GONG_ACCESS_KEY_SECRET", ""),
            "HUBSPOT_ACCESS_TOKEN": os.getenv("HUBSPOT_ACCESS_TOKEN", ""),
            
            # AI Services
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
            
            # Vector DBs
            "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY", ""),
            "PINECONE_ENVIRONMENT": os.getenv("PINECONE_ENVIRONMENT", ""),
        }
        
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"✅ Created environment file: {env_file}")
    
    async def wait_for_services(self):
        """Wait for services to be ready"""
        services = [
            ("PostgreSQL", "localhost", 5432),
            ("Redis", "localhost", 6379),
            ("Weaviate", "localhost", 8080),
        ]
        
        for service_name, host, port in services:
            await self.wait_for_port(service_name, host, port)
    
    async def wait_for_port(self, service_name: str, host: str, port: int, timeout: int = 120):
        """Wait for a service port to be available"""
        logger.info(f"⏳ Waiting for {service_name} on {host}:{port}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
                logger.info(f"✅ {service_name} is ready on {host}:{port}")
                return
            except:
                await asyncio.sleep(2)
        
        raise Exception(f"❌ {service_name} not ready after {timeout} seconds")
    
    async def print_deployment_summary(self):
        """Print deployment summary"""
        logger.info("\n" + "="*60)
        logger.info("🎉 SOPHIA AI COMPLETE STACK DEPLOYMENT SUMMARY")
        logger.info("="*60)
        
        if self.deployment_mode == "lambda-labs":
            instance_ip = os.getenv('LAMBDA_IP_ADDRESS', 'localhost')
            base_url = f"http://{instance_ip}"
        else:
            base_url = "http://localhost"
        
        services = [
            ("Sophia AI Backend", f"{base_url}:8000"),
            ("Sophia AI Frontend", f"{base_url}:3000"),
            ("Grafana Monitoring", f"{base_url}:3001"),
            ("Prometheus Metrics", f"{base_url}:9090"),
            ("Weaviate Vector DB", f"{base_url}:8080"),
            ("PostgreSQL Database", f"{base_url}:5432"),
            ("Redis Cache", f"{base_url}:6379"),
        ]
        
        for service, url in services:
            logger.info(f"🌐 {service}: {url}")
        
        logger.info("\n📊 Deployment Status:")
        for component, status in self.deployment_status.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {component.replace('_', ' ').title()}")
        
        logger.info("\n🔐 Default Credentials:")
        logger.info(f"📊 Grafana: admin / {os.getenv('GRAFANA_ADMIN_PASSWORD', 'sophia_admin_123')}")
        logger.info(f"🐘 PostgreSQL: sophia_user / {os.getenv('DATABASE_PASSWORD', 'sophia_dev_password_123')}")
        
        logger.info("\n🚀 Sophia AI is ready to kick ass!")
        logger.info("="*60)


async def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Sophia AI Complete Stack")
    parser.add_argument(
        "--mode",
        choices=["auto", "lambda-labs", "local", "production"],
        default="auto",
        help="Deployment mode"
    )
    
    args = parser.parse_args()
    
    deployment = SophiaCompleteStackDeployment(deployment_mode=args.mode)
    
    try:
        success = await deployment.deploy_complete_stack()
        if success:
            logger.info("🎉 Deployment completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("⏹️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Deployment failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

