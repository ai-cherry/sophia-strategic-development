#!/usr/bin/env python3
"""
Lambda Labs Complete Infrastructure Setup
Comprehensive setup script for Lambda Labs instance with full data pipeline integration
Includes: Estuary Flow, Snowflake, PostgreSQL, Redis, Vector DBs, and codebase alignment
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
import asyncpg
import redis
import snowflake.connector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LambdaLabsCompleteSetup:
    """
    Complete Lambda Labs infrastructure setup
    Integrates all data pipeline components for Sophia AI
    """
    
    def __init__(self):
        self.instance_ip = os.getenv('LAMBDA_IP_ADDRESS')
        self.ssh_key_path = '/tmp/lambda_ssh_key'
        self.setup_status = {
            'system_setup': False,
            'docker_setup': False,
            'postgresql_setup': False,
            'redis_setup': False,
            'snowflake_setup': False,
            'estuary_setup': False,
            'codebase_deployment': False,
            'vector_db_setup': False,
            'monitoring_setup': False
        }
    
    async def run_complete_setup(self):
        """Execute complete infrastructure setup"""
        logger.info("🚀 Starting Lambda Labs complete infrastructure setup...")
        
        try:
            # Phase 1: System and Docker Setup
            await self.setup_system_environment()
            await self.setup_docker_environment()
            
            # Phase 2: Database Infrastructure
            await self.setup_postgresql()
            await self.setup_redis()
            await self.setup_vector_databases()
            
            # Phase 3: Data Pipeline Integration
            await self.setup_snowflake_connection()
            await self.setup_estuary_flow()
            
            # Phase 4: Codebase Deployment
            await self.deploy_sophia_codebase()
            
            # Phase 5: Monitoring and Validation
            await self.setup_monitoring()
            await self.validate_complete_setup()
            
            logger.info("✅ Lambda Labs complete infrastructure setup successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            await self.cleanup_on_failure()
            return False
    
    async def setup_system_environment(self):
        """Set up system environment and dependencies"""
        logger.info("🔧 Setting up system environment...")
        
        commands = [
            # System updates
            "sudo apt-get update && sudo apt-get upgrade -y",
            
            # Essential packages
            "sudo apt-get install -y python3-pip python3-venv git curl wget htop nvtop",
            
            # NVIDIA drivers and CUDA (for GPU instances)
            "sudo apt-get install -y nvidia-driver-535 nvidia-cuda-toolkit",
            
            # Development tools
            "sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev",
            
            # Database clients
            "sudo apt-get install -y postgresql-client redis-tools",
            
            # Monitoring tools
            "sudo apt-get install -y prometheus-node-exporter",
        ]
        
        for cmd in commands:
            await self.run_ssh_command(cmd)
        
        self.setup_status['system_setup'] = True
        logger.info("✅ System environment setup complete")
    
    async def setup_docker_environment(self):
        """Set up Docker and Docker Compose"""
        logger.info("🐳 Setting up Docker environment...")
        
        commands = [
            # Install Docker
            "curl -fsSL https://get.docker.com -o get-docker.sh",
            "sudo sh get-docker.sh",
            "sudo usermod -aG docker ubuntu",
            
            # Install Docker Compose
            "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
            "sudo chmod +x /usr/local/bin/docker-compose",
            
            # Start Docker service
            "sudo systemctl enable docker",
            "sudo systemctl start docker",
        ]
        
        for cmd in commands:
            await self.run_ssh_command(cmd)
        
        self.setup_status['docker_setup'] = True
        logger.info("✅ Docker environment setup complete")
    
    async def setup_postgresql(self):
        """Set up PostgreSQL for structured data storage"""
        logger.info("🐘 Setting up PostgreSQL...")
        
        # Create PostgreSQL Docker Compose configuration
        postgres_config = {
            'version': '3.8',
            'services': {
                'postgresql': {
                    'image': 'postgres:15',
                    'environment': {
                        'POSTGRES_DB': 'sophia_ai',
                        'POSTGRES_USER': 'sophia_user',
                        'POSTGRES_PASSWORD': os.getenv('DATABASE_PASSWORD', 'secure_password_123'),
                    },
                    'ports': ['5432:5432'],
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './init-scripts:/docker-entrypoint-initdb.d'
                    ],
                    'restart': 'unless-stopped'
                }
            },
            'volumes': {
                'postgres_data': {}
            }
        }
        
        # Deploy PostgreSQL
        await self.deploy_docker_service('postgresql', postgres_config)
        
        # Create database schemas
        await self.create_postgresql_schemas()
        
        self.setup_status['postgresql_setup'] = True
        logger.info("✅ PostgreSQL setup complete")
    
    async def setup_redis(self):
        """Set up Redis for caching and real-time data"""
        logger.info("🔴 Setting up Redis...")
        
        redis_config = {
            'version': '3.8',
            'services': {
                'redis': {
                    'image': 'redis:7-alpine',
                    'ports': ['6379:6379'],
                    'volumes': ['redis_data:/data'],
                    'restart': 'unless-stopped',
                    'command': 'redis-server --appendonly yes'
                }
            },
            'volumes': {
                'redis_data': {}
            }
        }
        
        await self.deploy_docker_service('redis', redis_config)
        
        self.setup_status['redis_setup'] = True
        logger.info("✅ Redis setup complete")
    
    async def setup_vector_databases(self):
        """Set up Pinecone and Weaviate for vector search"""
        logger.info("🔍 Setting up vector databases...")
        
        # Weaviate setup
        weaviate_config = {
            'version': '3.8',
            'services': {
                'weaviate': {
                    'image': 'semitechnologies/weaviate:1.22.4',
                    'ports': ['8080:8080'],
                    'environment': {
                        'QUERY_DEFAULTS_LIMIT': '25',
                        'AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED': 'true',
                        'PERSISTENCE_DATA_PATH': '/var/lib/weaviate',
                        'DEFAULT_VECTORIZER_MODULE': 'none',
                        'ENABLE_MODULES': 'text2vec-openai,text2vec-cohere,text2vec-huggingface',
                        'CLUSTER_HOSTNAME': 'node1'
                    },
                    'volumes': ['weaviate_data:/var/lib/weaviate'],
                    'restart': 'unless-stopped'
                }
            },
            'volumes': {
                'weaviate_data': {}
            }
        }
        
        await self.deploy_docker_service('weaviate', weaviate_config)
        
        # Pinecone configuration (API-based, no local deployment needed)
        await self.configure_pinecone_connection()
        
        self.setup_status['vector_db_setup'] = True
        logger.info("✅ Vector databases setup complete")
    
    async def setup_snowflake_connection(self):
        """Set up Snowflake connection and schema alignment"""
        logger.info("❄️ Setting up Snowflake connection...")
        
        try:
            # Test Snowflake connection
            conn = snowflake.connector.connect(
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                user='PROGRAMMATIC_SERVICE_USER',
                password=os.getenv('SOPHIA_AI_TOKEN'),
                role=os.getenv('SNOWFLAKE_ROLE', 'SOPHIA_AI_ROLE'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'SOPHIA_AI_WH'),
                database=os.getenv('SNOWFLAKE_DATABASE', 'SOPHIA_AI_DB'),
                schema=os.getenv('SNOWFLAKE_SCHEMA', 'PRODUCTION')
            )
            
            # Create foundational schemas
            await self.create_snowflake_schemas(conn)
            
            # Set up data sharing connections
            await self.setup_gong_data_share(conn)
            
            conn.close()
            
            self.setup_status['snowflake_setup'] = True
            logger.info("✅ Snowflake connection setup complete")
            
        except Exception as e:
            logger.error(f"❌ Snowflake setup failed: {e}")
            raise
    
    async def setup_estuary_flow(self):
        """Set up Estuary Flow data pipeline"""
        logger.info("🌊 Setting up Estuary Flow integration...")
        
        # Create Estuary Flow configuration
        estuary_config = {
            'captures': {
                'hubspot-capture': {
                    'endpoint': {
                        'connector': {
                            'image': 'ghcr.io/estuary/source-hubspot:dev',
                            'config': {
                                'credentials': {
                                    'credentials_title': 'Private App Credentials',
                                    'access_token': os.getenv('HUBSPOT_ACCESS_TOKEN')
                                },
                                'start_date': '2024-01-01T00:00:00Z'
                            }
                        }
                    },
                    'bindings': [
                        {
                            'resource': {
                                'stream': 'contacts',
                                'syncMode': 'incremental'
                            },
                            'target': 'sophia-ai/hubspot/contacts'
                        },
                        {
                            'resource': {
                                'stream': 'deals',
                                'syncMode': 'incremental'
                            },
                            'target': 'sophia-ai/hubspot/deals'
                        }
                    ]
                },
                'gong-capture': {
                    'endpoint': {
                        'connector': {
                            'image': 'ghcr.io/estuary/source-gong:dev',
                            'config': {
                                'access_key': os.getenv('GONG_ACCESS_KEY'),
                                'access_key_secret': os.getenv('GONG_ACCESS_KEY_SECRET'),
                                'start_date': '2024-01-01T00:00:00Z'
                            }
                        }
                    },
                    'bindings': [
                        {
                            'resource': {
                                'stream': 'calls',
                                'syncMode': 'incremental'
                            },
                            'target': 'sophia-ai/gong/calls'
                        }
                    ]
                }
            },
            'materializations': {
                'postgresql-materialization': {
                    'endpoint': {
                        'connector': {
                            'image': 'ghcr.io/estuary/materialize-postgres:dev',
                            'config': {
                                'address': f'{self.instance_ip}:5432',
                                'database': 'sophia_ai',
                                'user': 'sophia_user',
                                'password': os.getenv('DATABASE_PASSWORD'),
                                'schema': 'estuary_staging'
                            }
                        }
                    },
                    'bindings': [
                        {
                            'source': 'sophia-ai/hubspot/contacts',
                            'resource': {
                                'table': 'hubspot_contacts'
                            }
                        },
                        {
                            'source': 'sophia-ai/hubspot/deals',
                            'resource': {
                                'table': 'hubspot_deals'
                            }
                        },
                        {
                            'source': 'sophia-ai/gong/calls',
                            'resource': {
                                'table': 'gong_calls'
                            }
                        }
                    ]
                }
            }
        }
        
        # Deploy Estuary Flow configuration
        await self.deploy_estuary_configuration(estuary_config)
        
        self.setup_status['estuary_setup'] = True
        logger.info("✅ Estuary Flow setup complete")
    
    async def deploy_sophia_codebase(self):
        """Deploy Sophia AI codebase to Lambda Labs instance"""
        logger.info("📦 Deploying Sophia AI codebase...")
        
        commands = [
            # Clone repository
            "cd /home/ubuntu && git clone https://github.com/ai-cherry/sophia-main.git",
            "cd /home/ubuntu/sophia-main",
            
            # Set up Python environment
            "python3 -m venv venv",
            "source venv/bin/activate && pip install --upgrade pip",
            "source venv/bin/activate && pip install -r requirements.txt",
            
            # Set up environment variables
            f"echo 'export LAMBDA_IP_ADDRESS={self.instance_ip}' >> ~/.bashrc",
            f"echo 'export DATABASE_HOST={self.instance_ip}' >> ~/.bashrc",
            f"echo 'export REDIS_HOST={self.instance_ip}' >> ~/.bashrc",
            f"echo 'export WEAVIATE_HOST={self.instance_ip}' >> ~/.bashrc",
            
            # Create systemd service for Sophia AI
            "sudo cp deployment/sophia-ai.service /etc/systemd/system/",
            "sudo systemctl enable sophia-ai",
            "sudo systemctl start sophia-ai",
        ]
        
        for cmd in commands:
            await self.run_ssh_command(cmd)
        
        self.setup_status['codebase_deployment'] = True
        logger.info("✅ Sophia AI codebase deployment complete")
    
    async def setup_monitoring(self):
        """Set up monitoring and health checks"""
        logger.info("📊 Setting up monitoring...")
        
        monitoring_config = {
            'version': '3.8',
            'services': {
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './prometheus.yml:/etc/prometheus/prometheus.yml',
                        'prometheus_data:/prometheus'
                    ],
                    'restart': 'unless-stopped'
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'ports': ['3000:3000'],
                    'environment': {
                        'GF_SECURITY_ADMIN_PASSWORD': 'sophia_admin_123'
                    },
                    'volumes': ['grafana_data:/var/lib/grafana'],
                    'restart': 'unless-stopped'
                }
            },
            'volumes': {
                'prometheus_data': {},
                'grafana_data': {}
            }
        }
        
        await self.deploy_docker_service('monitoring', monitoring_config)
        
        self.setup_status['monitoring_setup'] = True
        logger.info("✅ Monitoring setup complete")
    
    async def validate_complete_setup(self):
        """Validate all components are working correctly"""
        logger.info("🔍 Validating complete setup...")
        
        validations = [
            ('PostgreSQL', self.validate_postgresql),
            ('Redis', self.validate_redis),
            ('Snowflake', self.validate_snowflake),
            ('Weaviate', self.validate_weaviate),
            ('Estuary Flow', self.validate_estuary_flow),
            ('Sophia AI Service', self.validate_sophia_service),
        ]
        
        for name, validator in validations:
            try:
                await validator()
                logger.info(f"✅ {name} validation successful")
            except Exception as e:
                logger.error(f"❌ {name} validation failed: {e}")
                raise
        
        logger.info("✅ Complete setup validation successful!")
    
    async def run_ssh_command(self, command: str) -> str:
        """Execute command on Lambda Labs instance via SSH"""
        ssh_cmd = [
            'ssh', '-i', self.ssh_key_path,
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            f'ubuntu@{self.instance_ip}',
            command
        ]
        
        process = await asyncio.create_subprocess_exec(
            *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"SSH command failed: {command}")
            logger.error(f"Error: {stderr.decode()}")
            raise Exception(f"SSH command failed: {stderr.decode()}")
        
        return stdout.decode()
    
    async def deploy_docker_service(self, service_name: str, config: Dict):
        """Deploy a Docker service using Docker Compose"""
        config_path = f'/tmp/{service_name}-docker-compose.yml'
        
        # Write config to file
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)
        
        # Copy to instance and deploy
        await self.run_ssh_command(f'mkdir -p /home/ubuntu/{service_name}')
        
        scp_cmd = [
            'scp', '-i', self.ssh_key_path,
            '-o', 'StrictHostKeyChecking=no',
            config_path,
            f'ubuntu@{self.instance_ip}:/home/ubuntu/{service_name}/docker-compose.yml'
        ]
        
        process = await asyncio.create_subprocess_exec(*scp_cmd)
        await process.communicate()
        
        # Deploy service
        await self.run_ssh_command(
            f'cd /home/ubuntu/{service_name} && docker-compose up -d'
        )
    
    async def create_postgresql_schemas(self):
        """Create PostgreSQL database schemas"""
        schema_sql = """
        CREATE SCHEMA IF NOT EXISTS estuary_staging;
        CREATE SCHEMA IF NOT EXISTS processed_data;
        CREATE SCHEMA IF NOT EXISTS analytics;
        
        -- Create tables for Estuary Flow staging
        CREATE TABLE IF NOT EXISTS estuary_staging.hubspot_contacts (
            id SERIAL PRIMARY KEY,
            contact_id VARCHAR(255) UNIQUE,
            email VARCHAR(255),
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            company VARCHAR(255),
            created_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS estuary_staging.gong_calls (
            id SERIAL PRIMARY KEY,
            call_id VARCHAR(255) UNIQUE,
            title VARCHAR(500),
            duration INTEGER,
            participants JSONB,
            transcript TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        await self.run_ssh_command(
            f'echo "{schema_sql}" | docker exec -i postgresql_postgresql_1 psql -U sophia_user -d sophia_ai'
        )
    
    async def create_snowflake_schemas(self, conn):
        """Create Snowflake database schemas"""
        cursor = conn.cursor()
        
        schemas = [
            "CREATE SCHEMA IF NOT EXISTS RAW_DATA",
            "CREATE SCHEMA IF NOT EXISTS PROCESSED_DATA", 
            "CREATE SCHEMA IF NOT EXISTS ANALYTICS",
            "CREATE SCHEMA IF NOT EXISTS GONG_DATA_SHARE",
        ]
        
        for schema in schemas:
            cursor.execute(schema)
        
        cursor.close()
    
    async def cleanup_on_failure(self):
        """Clean up resources on setup failure"""
        logger.info("🧹 Cleaning up on failure...")
        # Implementation for cleanup
        pass


async def main():
    """Main execution function"""
    setup = LambdaLabsCompleteSetup()
    
    try:
        success = await setup.run_complete_setup()
        if success:
            print("🎉 Lambda Labs complete infrastructure setup successful!")
            print(f"🌐 Instance IP: {setup.instance_ip}")
            print("📊 Access Grafana: http://{setup.instance_ip}:3000")
            print("🔍 Access Weaviate: http://{setup.instance_ip}:8080")
            sys.exit(0)
        else:
            print("❌ Setup failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

