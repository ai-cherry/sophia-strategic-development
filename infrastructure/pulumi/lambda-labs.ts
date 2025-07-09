import * as pulumi from "@pulumi/pulumi";
import * as command from "@pulumi/command";
import * as random from "@pulumi/random";

// Configuration
const config = new pulumi.Config();
const lambdaCloudApiKey = config.requireSecret("lambdaCloudApiKey");
const lambdaApiKey = config.requireSecret("lambdaApiKey");
const dockerHubUsername = config.require("dockerHubUsername");
const dockerHubPassword = config.requireSecret("dockerHubPassword");

// Lambda Labs instance configuration
interface LambdaInstance {
    name: string;
    ip: string;
    type: string;
    region: string;
    role: string;
}

const instances: LambdaInstance[] = [
    {
        name: "sophia-production-instance",
        ip: "104.171.202.103",
        type: "gpu_1x_rtx6000",
        region: "us-south-1",
        role: "production"
    },
    {
        name: "sophia-ai-core",
        ip: "192.222.58.232",
        type: "gpu_1x_gh200",
        region: "us-east-3",
        role: "ai-core"
    },
    {
        name: "sophia-mcp-orchestrator",
        ip: "104.171.202.117",
        type: "gpu_1x_a6000",
        region: "us-south-1",
        role: "mcp-orchestrator"
    },
    {
        name: "sophia-data-pipeline",
        ip: "104.171.202.134",
        type: "gpu_1x_a100",
        region: "us-south-1",
        role: "data-pipeline"
    },
    {
        name: "sophia-development",
        ip: "155.248.194.183",
        type: "gpu_1x_a10",
        region: "us-west-1",
        role: "development"
    }
];

// SSH key for Lambda Labs
const sshPrivateKey = `-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAsctiuxhwWHR6Vw2MCEKFQTo0fDd0cDE4G2S7AexGvQZvTyqy
Vl/bBqVE8k3ToTO1VzVynbX4UIv4jmtZ+f85uAkCfkW9xIhfrdMGLVIoMs7UN0rS
iuFdyUD7pf41RDGah35+FfpxQWq+gL0ac9LCFwhE66YyeB2MzG6hrabsKVAAK7Tv
GSYH2ApULQdSowZP0niIshBEy9Sq3px1Vylyon7RsY3UWwEgcrEpQens4s3aJDMe
o/du4cUhbtMJf3RqcDrva9aL3ub0n1Xq5o57lju7umtqlfsJXP776Vyg2oobviaf
LeLg3ZkRHNFgkUz6nWXSZkEyeeM0nSaKIbBoawIDAQABAoIBABvsIbbZeTdjH52R
Wpcnf08FqZ2Chg5ipHmk4bvFFDz2iD+qKHTpO/g4t3HIaD6uZMHr+nKrU/KucNxJ
Hsnk2/c7rwEOyeVWN5SQii1O9FI6ali+rv8xsq17P6pLmKj7k1XJN1sTSHsqHP4R
9NgQ1vuQCGbr5Iw5s9WdYFXp27gG/cwCPcRmtbDwxWypNqBJXCuzryTcj12mXWxx
KXyR1D2i64kYJvfX4XpdO2fHqCwy9OQe6XXCgfO8EmY16GEBA9OYFz7TWD05g/ag
e4C3PhO/OJ8wdd6EUA8/DS8ycN8iAxrqJJ4O8ZRKhPWVTIWG++2b9AJlc+vy+lCo
4PbAWKECgYEA4SZhKQnDAHzt6xuHkVZCxcFGDQPtEhdPc3B23SIFgRtCCss4h5NC
20WoxjsULv+CWG6rlTxNojUS3dKwS/xZs7RZRVleV6Rd3nWikuRDTZTDXQBsxRfr
mgrfdnRKhCkqBfvxEsiRz/dewUL4owkZYyr3B8T6NRDXuCNeWKHHlgsCgYEAyifp
VmQ9aCS3PrZTVo9CwCz7vh0NHjrZ1LQpJzGWld/BKzwmqZeOe3EKlNI0BaYH43sb
38uTq5A0TnjfD16hqeWhy7oIgAabnKUU894PkMZNt4xjk9iRFKvsJiCZxv4vN5MY
MraJRj61jH/9BtXnLAhqsnH7tJYN2uAzufjB0yECgYAyalipStFKg672zWRO7ATp
qTyZX36vZV7aF53WKG8ZGNRx/E19NkFrPi7rrID5gSdby/RJ54Xuw3mlCC+H5Erl
zYWL3NYeQ+TtEmREBi736U7RvW2duJx+Et809BdXfqw1SNQTg6v66IZkOi3YvAne
Rdmo+LeaOFpFlk3jBN7fPwKBgAhMLxWus56Ms0DNtwn8g17j+clJ4/nzrHFAm9fR
/z5TmtgtdeDMKbsDXs3Q+vWoZPZ/XRuIfZ0zJBJ8f5tf5P7WQBfeoO6wVr7NP9jq
qnTkztfT2Vp+LyZMEDtYZzd1w3ZigUHDoErT1BvaPQaEzSJPjiGY8B3vcs4jGbxu
a3ZBAoGARVeKJRgiPHQTxguouBYLSpKr5kuF+sYp0TB3XvOPlMPjKMLIryOajRpd
3ot+NheIx7IOO8nbRBjcdr1CsxvKVrC6K1iEyV1cOwrGo2JednJr5cY92oE3Q3BZ
Si02dEz1jsNZT5IObnR+EZU3x3tUPVwobDfLiVIhf5iOHg48b/w=
-----END RSA PRIVATE KEY-----`;

// Create deployment script for each instance
const deploymentScript = `#!/bin/bash
set -e

echo "🚀 Deploying Sophia AI to Lambda Labs..."

# Install Docker and dependencies
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git curl jq
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Create deployment directory
mkdir -p /home/ubuntu/sophia-ai
cd /home/ubuntu/sophia-ai

# Login to Docker Hub
echo "${dockerHubPassword}" | docker login -u ${dockerHubUsername} --password-stdin

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sophia_db
      POSTGRES_USER: sophia_user
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-sophia_secure_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sophia_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ${dockerHubUsername}/sophia-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://sophia_user:\${POSTGRES_PASSWORD:-sophia_secure_password}@postgres:5432/sophia_db
      - REDIS_URL=redis://redis:6379
      - PULUMI_ORG=\${PULUMI_ORG}
      - PULUMI_STACK=\${PULUMI_STACK}
      - PULUMI_ACCESS_TOKEN=\${PULUMI_ACCESS_TOKEN}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - sophia-network
    volumes:
      - ./config:/app/config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  mcp-servers:
    image: ${dockerHubUsername}/sophia-mcp-servers:latest
    ports:
      - "9000-9100:9000-9100"
    environment:
      - ENVIRONMENT=production
      - PULUMI_ORG=\${PULUMI_ORG}
      - PULUMI_STACK=\${PULUMI_STACK}
      - PULUMI_ACCESS_TOKEN=\${PULUMI_ACCESS_TOKEN}
    networks:
      - sophia-network
    volumes:
      - ./config:/app/config
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - sophia-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_PASSWORD:-sophia_admin}
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/var/lib/grafana/dashboards
    networks:
      - sophia-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - mcp-servers
    networks:
      - sophia-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  sophia-network:
    driver: bridge
EOF

# Create Prometheus configuration
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'sophia-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'mcp-servers'
    static_configs:
      - targets:
        - 'mcp-servers:9001'
        - 'mcp-servers:9002'
        - 'mcp-servers:9003'
        - 'mcp-servers:9004'
        - 'mcp-servers:9005'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF

# Create nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream mcp {
        server mcp-servers:9001;
        server mcp-servers:9002;
        server mcp-servers:9003;
    }

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /mcp/ {
            proxy_pass http://mcp/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }

        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF

# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 60

# Check service status
docker-compose ps

# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

echo "✅ Deployment complete!"
`;

// Deploy to each Lambda Labs instance
instances.forEach(instance => {
    const deployment = new command.remote.Command(`deploy-${instance.name}`, {
        connection: {
            host: instance.ip,
            user: "ubuntu",
            privateKey: sshPrivateKey,
        },
        create: deploymentScript,
    });

    // Export deployment status
    pulumi.export(`${instance.name}-deployment`, {
        name: instance.name,
        ip: instance.ip,
        type: instance.type,
        region: instance.region,
        role: instance.role,
        deploymentId: deployment.id,
    });
});

// Create monitoring dashboard configuration
const monitoringConfig = {
    instances: instances.map(i => ({
        name: i.name,
        ip: i.ip,
        endpoints: {
            backend: `http://${i.ip}:8000`,
            mcp: `http://${i.ip}:9001`,
            prometheus: `http://${i.ip}:9090`,
            grafana: `http://${i.ip}:3000`,
        }
    }))
};

// Export monitoring configuration
pulumi.export("monitoring", monitoringConfig);

// Create health check command
const healthCheckScript = `
#!/bin/bash
echo "🏥 Health Check Report"
echo "===================="

# Check Docker services
echo "Docker Services:"
docker-compose ps

# Check system resources
echo -e "\nSystem Resources:"
df -h | grep -E "^/dev"
free -h
uptime

# Check service endpoints
echo -e "\nService Health:"
curl -s http://localhost:8000/health || echo "Backend: ❌"
curl -s http://localhost:9001/health || echo "MCP-9001: ❌"
curl -s http://localhost:9090/-/healthy || echo "Prometheus: ❌"
curl -s http://localhost:3000/api/health || echo "Grafana: ❌"
`;

// Create health check for each instance
instances.forEach(instance => {
    const healthCheck = new command.remote.Command(`health-check-${instance.name}`, {
        connection: {
            host: instance.ip,
            user: "ubuntu",
            privateKey: sshPrivateKey,
        },
        create: healthCheckScript,
    });
});

// Export summary
pulumi.export("deployment-summary", {
    instances: instances.length,
    totalGPUs: instances.length,
    regions: [...new Set(instances.map(i => i.region))],
    endpoints: {
        production: `http://${instances.find(i => i.role === "production")?.ip}`,
        development: `http://${instances.find(i => i.role === "development")?.ip}`,
    }
});
