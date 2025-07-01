#!/usr/bin/env python3
"""
Lambda Labs Infrastructure Provisioner
Comprehensive deployment automation for Sophia AI Platform
Handles instance creation, SSH setup, and service deployment
"""

import asyncio
import base64
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import asyncio
import paramiko

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LambdaLabsConfig:
    """Lambda Labs API configuration"""
    api_key: str
    base_url: str = "https://cloud.lambda.ai/api/v1"
    ssh_key_name: str = "cherry-ai-collaboration-20250604"
    region: str = "us-west-1"
    instance_type: str = "gpu_1x_a10"

@dataclass
class InstanceSpec:
    """Instance specification for deployment"""
    name: str
    instance_type: str
    region: str
    ssh_key_names: List[str]
    file_system_names: List[str] = None
    quantity: int = 1

@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""
    name: str = "sophia_staging"
    version: str = "15"
    port: int = 5432
    max_connections: int = 200
    shared_buffers: str = "512MB"
    effective_cache_size: str = "2GB"
    work_mem: str = "16MB"
    maintenance_work_mem: str = "256MB"

@dataclass
class RedisConfig:
    """Redis cache configuration"""
    port: int = 6379
    max_memory: str = "4gb"
    max_memory_policy: str = "allkeys-lru"
    save_config: str = "900 1 300 10 60 10000"
    tcp_keepalive: int = 300

class LambdaLabsProvisioner:
    """Comprehensive Lambda Labs infrastructure provisioner"""
    
    def __init__(self, config: LambdaLabsConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.instance_id: Optional[str] = None
        self.instance_ip: Optional[str] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for Lambda Labs API"""
        credentials = f"{self.config.api_key}:"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Lambda Labs API"""
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_text = await response.text()
                logger.info(f"{method} {endpoint} - Status: {response.status}")
                
                if response.status >= 400:
                    logger.error(f"API Error: {response.status} - {response_text}")
                    response.raise_for_status()
                
                return json.loads(response_text) if response_text else {}
                
        except Exception as e:
            logger.error(f"Request failed for {method} {endpoint}: {e}")
            raise
    
    async def list_instance_types(self) -> List[Dict]:
        """List available instance types"""
        logger.info("Fetching available instance types...")
        response = await self._make_request("GET", "/instance-types")
        return response.get("data", [])
    
    async def list_ssh_keys(self) -> List[Dict]:
        """List SSH keys in account"""
        logger.info("Fetching SSH keys...")
        response = await self._make_request("GET", "/ssh-keys")
        return response.get("data", [])
    
    async def create_ssh_key(self, name: str, public_key: str) -> Dict:
        """Create SSH key in Lambda Labs account"""
        logger.info(f"Creating SSH key: {name}")
        data = {
            "name": name,
            "public_key": public_key
        }
        return await self._make_request("POST", "/ssh-keys", data)
    
    async def launch_instance(self, spec: InstanceSpec) -> Dict:
        """Launch Lambda Labs instance"""
        logger.info(f"Launching instance: {spec.name}")
        
        data = {
            "region_name": spec.region,
            "instance_type_name": spec.instance_type,
            "ssh_key_names": spec.ssh_key_names,
            "quantity": spec.quantity,
            "name": spec.name
        }
        
        if spec.file_system_names:
            data["file_system_names"] = spec.file_system_names
        
        response = await self._make_request("POST", "/instance-operations/launch", data)
        
        if "data" in response and "instance_ids" in response["data"]:
            self.instance_id = response["data"]["instance_ids"][0]
            logger.info(f"Instance launched with ID: {self.instance_id}")
        
        return response
    
    async def get_instance_status(self, instance_id: str) -> Dict:
        """Get instance status and details"""
        response = await self._make_request("GET", f"/instances/{instance_id}")
        return response.get("data", {})
    
    async def wait_for_instance_ready(self, instance_id: str, timeout: int = 600) -> str:
        """Wait for instance to be ready and return IP address"""
        logger.info(f"Waiting for instance {instance_id} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = await self.get_instance_status(instance_id)
                instance_status = status.get("status")
                
                logger.info(f"Instance status: {instance_status}")
                
                if instance_status == "active":
                    ip_address = status.get("ip")
                    if ip_address:
                        logger.info(f"Instance ready! IP: {ip_address}")
                        self.instance_ip = ip_address
                        return ip_address
                
                elif instance_status in ["terminated", "error"]:
                    raise Exception(f"Instance failed with status: {instance_status}")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.warning(f"Error checking instance status: {e}")
                await asyncio.sleep(30)
        
        raise TimeoutError(f"Instance {instance_id} not ready after {timeout} seconds")
    
    def _create_ssh_client(self, ip_address: str, private_key_path: str) -> paramiko.SSHClient:
        """Create SSH client connection"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(
                hostname=ip_address,
                username="ubuntu",
                key_filename=private_key_path,
                timeout=30,
                banner_timeout=30
            )
            return ssh
        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            raise
    
    async def execute_ssh_command(self, ssh: paramiko.SSHClient, command: str) -> Tuple[str, str, int]:
        """Execute command via SSH and return stdout, stderr, exit_code"""
        logger.info(f"Executing: {command}")
        
        try:
            stdin, stdout, stderr = ssh.exec_command(command, timeout=300)
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            
            if exit_code != 0:
                logger.warning(f"Command failed with exit code {exit_code}: {stderr_text}")
            
            return stdout_text, stderr_text, exit_code
            
        except Exception as e:
            logger.error(f"SSH command execution failed: {e}")
            raise
    
    async def setup_base_system(self, ssh: paramiko.SSHClient):
        """Set up base system packages and configuration"""
        logger.info("Setting up base system...")
        
        commands = [
            "sudo apt-get update -y",
            "sudo apt-get upgrade -y",
            "sudo apt-get install -y curl wget git htop vim nginx fail2ban ufw",
            "sudo apt-get install -y python3-pip python3-venv python3-dev",
            "sudo apt-get install -y build-essential libssl-dev libffi-dev",
            "sudo systemctl enable nginx",
            "sudo systemctl enable fail2ban",
            "sudo ufw --force enable",
            "sudo ufw allow ssh",
            "sudo ufw allow 80",
            "sudo ufw allow 443",
            "sudo ufw allow 5432",  # PostgreSQL
            "sudo ufw allow 6379",  # Redis
            "sudo ufw allow 8080",  # Health monitoring
        ]
        
        for command in commands:
            stdout, stderr, exit_code = await self.execute_ssh_command(ssh, command)
            if exit_code != 0 and "ufw" not in command:  # UFW commands may have non-zero exit codes
                raise Exception(f"Base system setup failed: {stderr}")
    
    async def install_docker(self, ssh: paramiko.SSHClient):
        """Install Docker and Docker Compose"""
        logger.info("Installing Docker...")
        
        commands = [
            "curl -fsSL https://get.docker.com -o get-docker.sh",
            "sudo sh get-docker.sh",
            "sudo usermod -aG docker ubuntu",
            "sudo systemctl enable docker",
            "sudo systemctl start docker",
            "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
            "sudo chmod +x /usr/local/bin/docker-compose",
        ]
        
        for command in commands:
            stdout, stderr, exit_code = await self.execute_ssh_command(ssh, command)
            if exit_code != 0:
                raise Exception(f"Docker installation failed: {stderr}")
    
    async def install_postgresql(self, ssh: paramiko.SSHClient, config: DatabaseConfig):
        """Install and configure PostgreSQL"""
        logger.info("Installing PostgreSQL...")
        
        # Installation commands
        install_commands = [
            "sudo apt-get install -y postgresql postgresql-contrib postgresql-client",
            "sudo systemctl enable postgresql",
            "sudo systemctl start postgresql",
        ]
        
        for command in install_commands:
            stdout, stderr, exit_code = await self.execute_ssh_command(ssh, command)
            if exit_code != 0:
                raise Exception(f"PostgreSQL installation failed: {stderr}")
        
        # Configuration commands
        config_commands = [
            f"sudo -u postgres createdb {config.name}",
            "sudo -u postgres psql -c \"CREATE USER sophia WITH ENCRYPTED PASSWORD 'sophia_secure_password_2024';\"",
            f"sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE {config.name} TO sophia;\"",
            f"sudo -u postgres psql -c \"ALTER USER sophia CREATEDB;\"",
        ]
        
        for command in config_commands:
            stdout, stderr, exit_code = await self.execute_ssh_command(ssh, command)
            # Some commands may fail if already executed, which is okay
            if exit_code != 0:
                logger.warning(f"PostgreSQL config command warning: {stderr}")
        
        # Optimize PostgreSQL configuration
        pg_config = f"""
# Sophia AI PostgreSQL Optimization
max_connections = {config.max_connections}
shared_buffers = {config.shared_buffers}
effective_cache_size = {config.effective_cache_size}
work_mem = {config.work_mem}
maintenance_work_mem = {config.maintenance_work_mem}
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
"""
        
        # Write optimized configuration
        await self.execute_ssh_command(ssh, f"echo '{pg_config}' | sudo tee -a /etc/postgresql/15/main/postgresql.conf")
        await self.execute_ssh_command(ssh, "sudo systemctl restart postgresql")
    
    async def install_redis(self, ssh: paramiko.SSHClient, config: RedisConfig):
        """Install and configure Redis"""
        logger.info("Installing Redis...")
        
        # Installation commands
        install_commands = [
            "sudo apt-get install -y redis-server",
            "sudo systemctl enable redis-server",
        ]
        
        for command in install_commands:
            stdout, stderr, exit_code = await self.execute_ssh_command(ssh, command)
            if exit_code != 0:
                raise Exception(f"Redis installation failed: {stderr}")
        
        # Redis configuration
        redis_config = f"""
# Sophia AI Redis Configuration
port {config.port}
bind 127.0.0.1 0.0.0.0
maxmemory {config.max_memory}
maxmemory-policy {config.max_memory_policy}
save {config.save_config}
tcp-keepalive {config.tcp_keepalive}
timeout 300
tcp-backlog 511
databases 16
"""
        
        # Write Redis configuration
        await self.execute_ssh_command(ssh, f"echo '{redis_config}' | sudo tee /etc/redis/redis.conf")
        await self.execute_ssh_command(ssh, "sudo systemctl restart redis-server")
    
    async def setup_monitoring(self, ssh: paramiko.SSHClient):
        """Set up health monitoring service"""
        logger.info("Setting up monitoring service...")
        
        monitoring_script = """#!/usr/bin/env python3
import json
import psutil
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy',
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'services': self.check_services()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def check_services(self):
        services = {}
        for service in ['postgresql', 'redis-server', 'nginx']:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True)
                services[service] = result.stdout.strip() == 'active'
            except:
                services[service] = False
        return services

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    server.serve_forever()
"""
        
        # Create monitoring service
        await self.execute_ssh_command(ssh, f"echo '{monitoring_script}' | sudo tee /opt/health_monitor.py")
        await self.execute_ssh_command(ssh, "sudo chmod +x /opt/health_monitor.py")
        await self.execute_ssh_command(ssh, "sudo pip3 install psutil")
        
        # Create systemd service
        service_config = """[Unit]
Description=Sophia AI Health Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/python3 /opt/health_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        await self.execute_ssh_command(ssh, f"echo '{service_config}' | sudo tee /etc/systemd/system/sophia-health.service")
        await self.execute_ssh_command(ssh, "sudo systemctl daemon-reload")
        await self.execute_ssh_command(ssh, "sudo systemctl enable sophia-health")
        await self.execute_ssh_command(ssh, "sudo systemctl start sophia-health")
    
    async def deploy_complete_infrastructure(self, private_key_path: str) -> Dict[str, Any]:
        """Deploy complete infrastructure stack"""
        logger.info("Starting complete infrastructure deployment...")
        
        try:
            # 1. Ensure SSH key exists
            ssh_keys = await self.list_ssh_keys()
            key_exists = any(key["name"] == self.config.ssh_key_name for key in ssh_keys)
            
            if not key_exists:
                logger.info("SSH key not found, creating...")
                # Read public key from environment or file
                public_key = os.getenv('LAMBDA_LABS_SSH_PUBLIC_KEY')
                if not public_key:
                    with open(f"{private_key_path}.pub", 'r') as f:
                        public_key = f.read().strip()
                
                await self.create_ssh_key(self.config.ssh_key_name, public_key)
            
            # 2. Launch instance
            instance_spec = InstanceSpec(
                name="sophia-ai-production",
                instance_type=self.config.instance_type,
                region=self.config.region,
                ssh_key_names=[self.config.ssh_key_name]
            )
            
            launch_response = await self.launch_instance(instance_spec)
            
            if not self.instance_id:
                raise Exception("Failed to get instance ID from launch response")
            
            # 3. Wait for instance to be ready
            ip_address = await self.wait_for_instance_ready(self.instance_id)
            
            # 4. Wait additional time for SSH to be ready
            logger.info("Waiting for SSH service to be ready...")
            await asyncio.sleep(60)
            
            # 5. Connect via SSH and deploy services
            ssh = self._create_ssh_client(ip_address, private_key_path)
            
            try:
                # Deploy all services
                await self.setup_base_system(ssh)
                await self.install_docker(ssh)
                await self.install_postgresql(ssh, DatabaseConfig())
                await self.install_redis(ssh, RedisConfig())
                await self.setup_monitoring(ssh)
                
                logger.info("Infrastructure deployment completed successfully!")
                
                return {
                    "status": "success",
                    "instance_id": self.instance_id,
                    "ip_address": ip_address,
                    "services": {
                        "postgresql": {"port": 5432, "database": "sophia_staging"},
                        "redis": {"port": 6379},
                        "nginx": {"port": 80},
                        "health_monitor": {"port": 8080}
                    },
                    "connection_strings": {
                        "postgresql": f"postgresql://sophia:sophia_secure_password_2024@{ip_address}:5432/sophia_staging",
                        "redis": f"redis://{ip_address}:6379/0"
                    }
                }
                
            finally:
                ssh.close()
        
        except Exception as e:
            logger.error(f"Infrastructure deployment failed: {e}")
            raise

async def main():
    """Main deployment function"""
    # Load configuration from environment
    api_key = os.getenv('LAMBDA_LABS_API_KEY')
    private_key_path = os.getenv('LAMBDA_LABS_SSH_PRIVATE_KEY_PATH', '/tmp/lambda_labs_key')
    
    if not api_key:
        raise ValueError("LAMBDA_LABS_API_KEY environment variable required")
    
    # Create private key file if provided via environment
    private_key_content = os.getenv('LAMBDA_LABS_SSH_PRIVATE_KEY')
    if private_key_content:
        with open(private_key_path, 'w') as f:
            f.write(private_key_content)
        os.chmod(private_key_path, 0o600)
    
    config = LambdaLabsConfig(api_key=api_key)
    
    async with LambdaLabsProvisioner(config) as provisioner:
        result = await provisioner.deploy_complete_infrastructure(private_key_path)
        
        print("\n" + "="*60)
        print("🎉 LAMBDA LABS DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        print(f"Instance ID: {result['instance_id']}")
        print(f"IP Address: {result['ip_address']}")
        print(f"PostgreSQL: {result['connection_strings']['postgresql']}")
        print(f"Redis: {result['connection_strings']['redis']}")
        print(f"Health Monitor: http://{result['ip_address']}:8080/health")
        print("="*60)
        
        return result

if __name__ == "__main__":
    asyncio.run(main())

