#!/usr/bin/env python3
"""
Lambda Labs Infrastructure Deployment for Sophia AI
Deploys PostgreSQL staging database and Redis cache on Lambda Labs instances
Integrates with Pulumi ESC for secure credential management
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any

import requests

from core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


@dataclass
class LambdaLabsConfig:
    """Configuration for Lambda Labs deployment"""

    api_key: str
    ssh_private_key: str
    region: str = "us-west-1"
    instance_type: str = "gpu_1x_a10"


@dataclass
class DatabaseConfig:
    """Configuration for PostgreSQL database"""

    name: str = "sophia_staging"
    version: str = "15"
    port: int = 5432
    max_connections: int = 100
    shared_buffers: str = "256MB"
    effective_cache_size: str = "1GB"


@dataclass
class RedisConfig:
    """Configuration for Redis cache"""

    port: int = 6379
    max_memory: str = "2gb"
    max_memory_policy: str = "allkeys-lru"
    save_config: str = "900 1 300 10 60 10000"


class LambdaLabsDeployer:
    """
    Deploys PostgreSQL and Redis infrastructure on Lambda Labs
    Manages instance lifecycle and configuration
    """

    def __init__(self):
        self.config = LambdaLabsConfig(
            api_key=get_config_value("lambda_api_key"),
            ssh_private_key=get_config_value("lambda_ssh_private_key"),
            region=get_config_value("lambda_region", "us-west-1"),
            instance_type=get_config_value("lambda_instance_type", "gpu_1x_a10"),
        )
        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        self._validate_config()

    def _validate_config(self):
        """Validate Lambda Labs configuration"""
        if not self.config.api_key:
            raise ValueError("Lambda Labs API key not configured in Pulumi ESC")

        if not self.config.ssh_private_key:
            raise ValueError("Lambda Labs SSH private key not configured in Pulumi ESC")

        logger.info(
            f"Lambda Labs deployer initialized for region: {self.config.region}"
        )

    def _make_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Make authenticated request to Lambda Labs API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, headers=self.headers, json=data, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Lambda Labs API request failed: {e}")
            raise

    def list_instance_types(self) -> list[dict[str, Any]]:
        """List available instance types"""
        return self._make_request("GET", "instance-types")

    def launch_database_instance(self) -> dict[str, Any]:
        """
        Launch Lambda Labs instance for PostgreSQL and Redis

        Returns:
            Instance information including IP address and ID
        """
        # Get available instance types
        instance_types = self.list_instance_types()
        available_types = [t["name"] for t in instance_types["data"]]

        if self.config.instance_type not in available_types:
            logger.warning(
                f"Instance type {self.config.instance_type} not available, using first available"
            )
            self.config.instance_type = available_types[0]

        # Launch instance
        launch_data = {
            "region_name": self.config.region,
            "instance_type_name": self.config.instance_type,
            "ssh_key_names": ["sophia-ai-key"],  # Assumes SSH key is already uploaded
            "file_system_names": [],
            "quantity": 1,
            "name": "sophia-ai-database-server",
        }

        logger.info(f"Launching Lambda Labs instance: {self.config.instance_type}")
        result = self._make_request("POST", "instance-operations/launch", launch_data)

        instance_ids = result["data"]["instance_ids"]
        if not instance_ids:
            raise RuntimeError("Failed to launch Lambda Labs instance")

        instance_id = instance_ids[0]
        logger.info(f"Instance launched successfully: {instance_id}")

        # Wait for instance to be running
        instance_info = self._wait_for_instance_running(instance_id)

        return {
            "instance_id": instance_id,
            "ip_address": instance_info["ip"],
            "status": instance_info["status"],
            "instance_type": self.config.instance_type,
        }

    def _wait_for_instance_running(
        self, instance_id: str, timeout: int = 300
    ) -> dict[str, Any]:
        """Wait for instance to be in running state"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            instances = self._make_request("GET", "instances")

            for instance in instances["data"]:
                if instance["id"] == instance_id:
                    if instance["status"] == "running":
                        logger.info(
                            f"Instance {instance_id} is running at {instance['ip']}"
                        )
                        return instance
                    elif instance["status"] == "unhealthy":
                        raise RuntimeError(f"Instance {instance_id} is unhealthy")

            logger.info(f"Waiting for instance {instance_id} to be running...")
            time.sleep(10)

        raise TimeoutError(
            f"Instance {instance_id} did not start within {timeout} seconds"
        )

    def setup_database_server(self, ip_address: str) -> dict[str, Any]:
        """
        Set up PostgreSQL and Redis on the Lambda Labs instance

        Args:
            ip_address: IP address of the Lambda Labs instance

        Returns:
            Configuration details for the deployed services
        """
        logger.info(f"Setting up database server on {ip_address}")

        # Create setup script
        setup_script = self._generate_setup_script()

        # Execute setup via SSH
        self._execute_remote_setup(ip_address, setup_script)

        # Generate configuration
        db_config = DatabaseConfig()
        redis_config = RedisConfig()

        return {
            "postgresql": {
                "host": ip_address,
                "port": db_config.port,
                "database": db_config.name,
                "username": "sophia_user",
                "connection_string": f"postgresql://sophia_user:{{password}}@{ip_address}:{db_config.port}/{db_config.name}",
            },
            "redis": {
                "host": ip_address,
                "port": redis_config.port,
                "url": f"redis://{ip_address}:{redis_config.port}",
            },
            "monitoring": {
                "health_check_url": f"http://{ip_address}:8080/health",
                "metrics_url": f"http://{ip_address}:9090/metrics",
            },
        }

    def _generate_setup_script(self) -> str:
        """Generate setup script for PostgreSQL and Redis installation"""
        db_config = DatabaseConfig()
        redis_config = RedisConfig()

        # Generate secure password for PostgreSQL
        postgres_password = (
            get_config_value("postgresql_password") or "sophia_secure_2025"
        )

        return f"""#!/bin/bash
set -e

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install PostgreSQL {db_config.version}
sudo apt-get install -y postgresql-{db_config.version} postgresql-contrib-{db_config.version}

# Configure PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE {db_config.name};"
sudo -u postgres psql -c "CREATE USER sophia_user WITH ENCRYPTED PASSWORD '{postgres_password}';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE {db_config.name} TO sophia_user;"
sudo -u postgres psql -c "ALTER USER sophia_user CREATEDB;"

# Configure PostgreSQL for remote connections
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/{db_config.version}/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" | sudo tee -a /etc/postgresql/{db_config.version}/main/pg_hba.conf

# Optimize PostgreSQL configuration
sudo sed -i "s/#max_connections = 100/max_connections = {db_config.max_connections}/" /etc/postgresql/{db_config.version}/main/postgresql.conf
sudo sed -i "s/#shared_buffers = 128MB/shared_buffers = {db_config.shared_buffers}/" /etc/postgresql/{db_config.version}/main/postgresql.conf
sudo sed -i "s/#effective_cache_size = 4GB/effective_cache_size = {db_config.effective_cache_size}/" /etc/postgresql/{db_config.version}/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

# Install Redis
sudo apt-get install -y redis-server

# Configure Redis
sudo sed -i "s/bind 127.0.0.1 ::1/bind 0.0.0.0/" /etc/redis/redis.conf
sudo sed -i "s/# maxmemory <bytes>/maxmemory {redis_config.max_memory}/" /etc/redis/redis.conf
sudo sed -i "s/# maxmemory-policy noeviction/maxmemory-policy {redis_config.max_memory_policy}/" /etc/redis/redis.conf
sudo sed -i "s/save 900 1/save {redis_config.save_config}/" /etc/redis/redis.conf

# Enable Redis persistence
sudo sed -i "s/# requirepass foobared/requirepass sophia_redis_2025/" /etc/redis/redis.conf

# Start and enable Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

# Install Python and dependencies for health checks
sudo apt-get install -y python3 python3-pip
pip3 install psycopg2-binary redis flask

# Create health check service
cat > /tmp/health_check.py << 'EOF'
#!/usr/bin/env python3
import json
import psycopg2
import redis
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    status = {{"status": "healthy", "services": {{}}}}

    # Check PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="{db_config.name}",
            user="sophia_user",
            password="{postgres_password}"
        )
        conn.close()
        status["services"]["postgresql"] = "healthy"
    except Exception as e:
        status["services"]["postgresql"] = f"unhealthy: {{e}}"
        status["status"] = "unhealthy"

    # Check Redis
    try:
        r = redis.Redis(host="localhost", port={redis_config.port}, password="sophia_redis_2025")
        r.ping()
        status["services"]["redis"] = "healthy"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {{e}}"
        status["status"] = "unhealthy"

    return jsonify(status)

if __name__ == '__main__':
    app.run(host="127.0.0.1"  # Changed from 0.0.0.0 for security. Use environment variable for production, port=8080)
EOF

sudo mv /tmp/health_check.py /opt/health_check.py
sudo chmod +x /opt/health_check.py

# Create systemd service for health check
sudo tee /etc/systemd/system/sophia-health.service > /dev/null << EOF
[Unit]
Description=Sophia AI Health Check Service
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 /opt/health_check.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable sophia-health
sudo systemctl start sophia-health

# Configure firewall
sudo ufw allow {db_config.port}/tcp  # PostgreSQL
sudo ufw allow {redis_config.port}/tcp  # Redis
sudo ufw allow 8080/tcp  # Health check
sudo ufw allow 22/tcp    # SSH
sudo ufw --force enable

echo "Database server setup complete!"
echo "PostgreSQL: localhost:{db_config.port}/{db_config.name}"
echo "Redis: localhost:{redis_config.port}"
echo "Health check: http://localhost:8080/health"
"""

    def _execute_remote_setup(self, ip_address: str, setup_script: str):
        """Execute setup script on remote Lambda Labs instance"""
        # Save SSH key to temporary file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pem", delete=False
        ) as key_file:
            key_file.write(self.config.ssh_private_key)
            key_file_path = key_file.name

        try:
            # Set proper permissions on SSH key
            os.chmod(key_file_path, 0o600)

            # Save setup script to temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".sh", delete=False
            ) as script_file:
                script_file.write(setup_script)
                script_file_path = script_file.name

            # Copy script to remote server
            scp_cmd = [
                "scp",
                "-i",
                key_file_path,
                "-o",
                "StrictHostKeyChecking=no",
                script_file_path,
                f"ubuntu@{ip_address}:/tmp/setup.sh",
            ]

            logger.info("Copying setup script to remote server...")
            subprocess.run(scp_cmd, check=True, capture_output=True)

            # Execute script on remote server
            ssh_cmd = [
                "ssh",
                "-i",
                key_file_path,
                "-o",
                "StrictHostKeyChecking=no",
                f"ubuntu@{ip_address}",
                "chmod +x /tmp/setup.sh && /tmp/setup.sh",
            ]

            logger.info("Executing setup script on remote server...")
            result = subprocess.run(ssh_cmd, check=True, capture_output=True, text=True)

            logger.info("Setup script executed successfully")
            logger.debug(f"Setup output: {result.stdout}")

        finally:
            # Clean up temporary files
            os.unlink(key_file_path)
            os.unlink(script_file_path)

    def update_pulumi_esc_config(self, database_config: dict[str, Any]):
        """
        Update Pulumi ESC configuration with database connection details

        Args:
            database_config: Database configuration from setup
        """
        logger.info("Updating Pulumi ESC configuration with database details")

        # Create ESC configuration update
        esc_updates = {
            "postgresql_host": database_config["postgresql"]["host"],
            "postgresql_port": str(database_config["postgresql"]["port"]),
            "postgresql_database": database_config["postgresql"]["database"],
            "postgresql_user": database_config["postgresql"]["username"],
            "postgresql_password": get_config_value(
                "postgresql_password", "sophia_secure_2025"
            ),
            "redis_host": database_config["redis"]["host"],
            "redis_port": str(database_config["redis"]["port"]),
            "redis_password": "sophia_redis_2025",
            "redis_url": f"redis://:{database_config['redis']['host']}:{database_config['redis']['port']}",
        }

        # Update ESC environment (this would typically use Pulumi ESC CLI)
        logger.info("Database configuration ready for Pulumi ESC update:")
        for key, value in esc_updates.items():
            logger.info(f"  {key}: {value}")

        return esc_updates

    def deploy_complete_infrastructure(self) -> dict[str, Any]:
        """
        Deploy complete database infrastructure on Lambda Labs

        Returns:
            Complete deployment configuration
        """
        logger.info("Starting complete infrastructure deployment...")

        # Launch instance
        instance_info = self.launch_database_instance()

        # Set up database server
        database_config = self.setup_database_server(instance_info["ip_address"])

        # Update Pulumi ESC
        esc_updates = self.update_pulumi_esc_config(database_config)

        # Complete deployment info
        deployment_info = {
            "instance": instance_info,
            "database": database_config,
            "esc_updates": esc_updates,
            "deployment_time": time.time(),
            "status": "deployed",
        }

        logger.info("Infrastructure deployment completed successfully!")
        return deployment_info


def deploy_lambda_labs_infrastructure():
    """Convenience function to deploy Lambda Labs infrastructure"""
    deployer = LambdaLabsDeployer()
    return deployer.deploy_complete_infrastructure()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        deployment = deploy_lambda_labs_infrastructure()

    except Exception:
        raise
