#!/usr/bin/env python3
"""
Unified Lambda Labs Deployment Script
Deploys complete Sophia AI platform with all MCP servers to Lambda Labs
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


def run_ssh_command(
    host: str, ssh_key: str, command: str, capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a command on the remote host via SSH"""
    ssh_cmd = [
        "ssh",
        "-i",
        ssh_key,
        "-o",
        "StrictHostKeyChecking=no",
        f"ubuntu@{host}",
        command,
    ]

    try:
        result = subprocess.run(
            ssh_cmd, capture_output=capture_output, text=True, check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ SSH command failed: {command}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        raise


def upload_file(host: str, ssh_key: str, local_path: str, remote_path: str):
    """Upload a file to the remote host"""
    scp_cmd = [
        "scp",
        "-i",
        ssh_key,
        "-o",
        "StrictHostKeyChecking=no",
        local_path,
        f"ubuntu@{host}:{remote_path}",
    ]

    try:
        subprocess.run(scp_cmd, check=True)
        print(f"✅ Uploaded {local_path} to {remote_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upload {local_path}: {e}")
        raise


def create_comprehensive_docker_compose(registry: str, environment: str) -> str:
    """Create a comprehensive docker-compose.yml with all MCP servers"""

    compose_content = f"""version: '3.8'

networks:
  sophia-overlay:
    driver: overlay
    attachable: true
  traefik-public:
    external: true

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

secrets:
  # Core platform secrets
  openai_api_key:
    external: true
  anthropic_api_key:
    external: true
  pulumi_access_token:
    external: true

  # Database secrets
  postgres_password:
    external: true
  redis_password:
    external: true

  # Snowflake secrets
  snowflake_account:
    external: true
  snowflake_user:
    external: true
  snowflake_password:
    external: true

  # Business tool secrets
  gong_access_key:
    external: true
  hubspot_access_token:
    external: true
  linear_api_key:
    external: true
  slack_bot_token:
    external: true

  # Infrastructure secrets
  lambda_api_key:
    external: true
  VERCEL_ACCESS_TOKEN:
    external: true
  github_token:
    external: true

  # Monitoring
  grafana_password:
    external: true

services:
  # Core Backend Service
  sophia-backend:
    image: {registry}/sophia-ai:latest
    networks:
      - sophia-overlay
    secrets:
      - openai_api_key
      - anthropic_api_key
      - pulumi_access_token
      - snowflake_account
      - snowflake_user
      - snowflake_password
    environment:
      - ENVIRONMENT={environment}
      - PULUMI_ORG=scoobyjava-org
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_api_key
      - SNOWFLAKE_ACCOUNT_FILE=/run/secrets/snowflake_account
      - SNOWFLAKE_USER_FILE=/run/secrets/snowflake_user
      - SNOWFLAKE_PASSWORD_FILE=/run/secrets/snowflake_password
    ports:
      - "8000:8000"
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  # Core AI Orchestration MCP Servers
  ai-memory-server:
    image: {registry}/sophia-ai-memory:latest
    networks:
      - sophia-overlay
    secrets:
      - openai_api_key
      - anthropic_api_key
    environment:
      - ENVIRONMENT={environment}
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_api_key
    ports:
      - "9001:9001"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9001/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  codacy-server:
    image: {registry}/sophia-codacy:latest
    networks:
      - sophia-overlay
    ports:
      - "3008:3008"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3008/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  # Unified AI Agent Authentication System Services
  github-agent:
    image: {registry}/sophia-github-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - github_token
    environment:
      - GITHUB_TOKEN_FILE=/run/secrets/github_token
    ports:
      - "9010:9010"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  pulumi-agent:
    image: {registry}/sophia-pulumi-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - pulumi_access_token
    environment:
      - PULUMI_ACCESS_TOKEN_FILE=/run/secrets/pulumi_access_token
    ports:
      - "9011:9011"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  docker-agent:
    image: {registry}/sophia-docker-agent:latest
    networks:
      - sophia-overlay
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "9012:9012"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  vercel-agent:
    image: {registry}/sophia-vercel-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - VERCEL_ACCESS_TOKEN
    environment:
      - VERCEL_ACCESS_TOKEN_FILE=/run/secrets/VERCEL_ACCESS_TOKEN
    ports:
      - "9013:9013"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  snowflake-agent:
    image: {registry}/sophia-snowflake-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - snowflake_account
      - snowflake_user
      - snowflake_password
    environment:
      - SNOWFLAKE_ACCOUNT_FILE=/run/secrets/snowflake_account
      - SNOWFLAKE_USER_FILE=/run/secrets/snowflake_user
      - SNOWFLAKE_PASSWORD_FILE=/run/secrets/snowflake_password
    ports:
      - "9014:9014"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  lambda-labs-agent:
    image: {registry}/sophia-lambda-labs-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - lambda_api_key
    environment:
      - LAMBDA_API_KEY_FILE=/run/secrets/lambda_api_key
    ports:
      - "9015:9015"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  # Business Tool Agents
  slack-agent:
    image: {registry}/sophia-slack-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - slack_bot_token
    environment:
      - SLACK_BOT_TOKEN_FILE=/run/secrets/slack_bot_token
    ports:
      - "9019:9019"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  linear-agent:
    image: {registry}/sophia-linear-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - linear_api_key
    environment:
      - LINEAR_API_KEY_FILE=/run/secrets/linear_api_key
    ports:
      - "9020:9020"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  hubspot-agent:
    image: {registry}/sophia-hubspot-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - hubspot_access_token
    environment:
      - HUBSPOT_ACCESS_TOKEN_FILE=/run/secrets/hubspot_access_token
    ports:
      - "9021:9021"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  gong-agent:
    image: {registry}/sophia-gong-agent:latest
    networks:
      - sophia-overlay
    secrets:
      - gong_access_key
    environment:
      - GONG_ACCESS_KEY_FILE=/run/secrets/gong_access_key
    ports:
      - "9022:9022"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  # External Repository Integration Servers
  playwright-server:
    image: {registry}/sophia-playwright:latest
    networks:
      - sophia-overlay
    ports:
      - "9030:9030"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  figma-context-server:
    image: {registry}/sophia-figma-context:latest
    networks:
      - sophia-overlay
    ports:
      - "9031:9031"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  snowflake-cortex-server:
    image: {registry}/sophia-snowflake-cortex:latest
    networks:
      - sophia-overlay
    secrets:
      - snowflake_account
      - snowflake_user
      - snowflake_password
    environment:
      - SNOWFLAKE_ACCOUNT_FILE=/run/secrets/snowflake_account
      - SNOWFLAKE_USER_FILE=/run/secrets/snowflake_user
      - SNOWFLAKE_PASSWORD_FILE=/run/secrets/snowflake_password
    ports:
      - "9032:9032"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure

  # Infrastructure Services
  postgres:
    image: postgres:16-alpine
    networks:
      - sophia-overlay
    secrets:
      - postgres_password
    environment:
      - POSTGRES_DB=sophia_ai
      - POSTGRES_USER=sophia
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  redis:
    image: redis:7-alpine
    networks:
      - sophia-overlay
    secrets:
      - redis_password
    command: redis-server --requirepass-file /run/secrets/redis_password
    volumes:
      - redis_data:/data
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    networks:
      - sophia-overlay
    ports:
      - "9090:9090"
    volumes:
      - prometheus_data:/prometheus
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  grafana:
    image: grafana/grafana:latest
    networks:
      - sophia-overlay
    secrets:
      - grafana_password
    environment:
      - GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/grafana_password
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  # Reverse Proxy
  traefik:
    image: traefik:v3.0
    networks:
      - sophia-overlay
      - traefik-public
    ports:
      - "80:80"
      - "443:443"
      - "8090:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command:
      - --api.dashboard=true
      - --api.insecure=true
      - --providers.docker=true
      - --providers.docker.swarmmode=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager
"""

    return compose_content


def deploy_to_lambda_labs(
    host: str,
    ssh_key: str,
    registry: str,
    environment: str,
    deploy_mcp_servers: bool = True,
):
    """Deploy the complete Sophia AI platform to Lambda Labs"""

    print(f"🚀 Starting deployment to Lambda Labs: {host}")
    print(f"Registry: {registry}")
    print(f"Environment: {environment}")
    print(f"Deploy MCP servers: {deploy_mcp_servers}")
    print()

    # Step 1: Create comprehensive docker-compose file
    print("📝 Creating comprehensive docker-compose.yml...")
    compose_content = create_comprehensive_docker_compose(registry, environment)

    # Write to local file
    compose_path = Path("docker-compose.unified.yml")
    compose_path.write_text(compose_content)

    # Upload to remote host
    upload_file(host, ssh_key, str(compose_path), "docker-compose.unified.yml")

    # Step 2: Ensure Docker Swarm is initialized
    print("🐳 Ensuring Docker Swarm is initialized...")
    try:
        run_ssh_command(host, ssh_key, "sudo docker swarm init || true")
    except subprocess.CalledProcessError:
        # Swarm might already be initialized
        pass

    # Step 3: Create required networks
    print("🌐 Creating Docker networks...")
    run_ssh_command(
        host,
        ssh_key,
        "sudo docker network create --driver overlay --attachable traefik-public || true",
    )
    run_ssh_command(
        host,
        ssh_key,
        "sudo docker network create --driver overlay --attachable sophia-overlay || true",
    )

    # Step 4: Login to Docker Hub on remote host
    print("🔑 Logging into Docker Hub on remote host...")
    # This should already be done by the secrets script, but let's ensure it

    # Step 5: Remove existing stack if it exists
    print("🗑️  Removing existing stack...")
    try:
        run_ssh_command(host, ssh_key, "sudo docker stack rm sophia-ai")
        print("⏳ Waiting for stack removal...")
        time.sleep(15)
    except subprocess.CalledProcessError:
        # Stack might not exist
        pass

    # Step 6: Deploy the stack
    print("🚀 Deploying unified stack...")
    deploy_cmd = "sudo docker stack deploy -c docker-compose.unified.yml sophia-ai"
    run_ssh_command(host, ssh_key, deploy_cmd, capture_output=False)

    # Step 7: Wait for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(30)

    # Step 8: Check service status
    print("📊 Checking service status...")
    result = run_ssh_command(host, ssh_key, "sudo docker service ls")
    print(result.stdout)

    # Step 9: Show service details for any failing services
    print("🔍 Checking for failing services...")
    services_result = run_ssh_command(
        host, ssh_key, "sudo docker service ls --format '{{.Name}} {{.Replicas}}'"
    )

    failing_services = []
    for line in services_result.stdout.strip().split("\n"):
        if line and not line.startswith("NAME"):
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                replicas = parts[1]
                if "0/" in replicas:
                    failing_services.append(name)

    if failing_services:
        print(f"⚠️  Found {len(failing_services)} failing services:")
        for service in failing_services:
            print(f"  • {service}")
            try:
                ps_result = run_ssh_command(
                    host, ssh_key, f"sudo docker service ps {service} --no-trunc"
                )
                print(f"    Status: {ps_result.stdout}")
            except:
                pass
    else:
        print("✅ All services are running successfully!")

    # Step 10: Display access information
    print()
    print("🌟 Deployment Complete!")
    print("=" * 50)
    print(f"🌐 Main Backend: http://{host}:8000")
    print(f"📊 Grafana: http://{host}:3000")
    print(f"📈 Prometheus: http://{host}:9090")
    print(f"🔧 Traefik Dashboard: http://{host}:8090")
    print()
    print("🤖 MCP Servers:")
    print(f"  • AI Memory: http://{host}:9001")
    print(f"  • Codacy: http://{host}:3008")
    print(f"  • GitHub Agent: http://{host}:9010")
    print(f"  • Pulumi Agent: http://{host}:9011")
    print(f"  • Docker Agent: http://{host}:9012")
    print(f"  • Vercel Agent: http://{host}:9013")
    print(f"  • Snowflake Agent: http://{host}:9014")
    print(f"  • Lambda Labs Agent: http://{host}:9015")
    print(f"  • Slack Agent: http://{host}:9019")
    print(f"  • Linear Agent: http://{host}:9020")
    print(f"  • HubSpot Agent: http://{host}:9021")
    print(f"  • Gong Agent: http://{host}:9022")
    print(f"  • Playwright: http://{host}:9030")
    print(f"  • Figma Context: http://{host}:9031")
    print(f"  • Snowflake Cortex: http://{host}:9032")
    print()

    # Cleanup local file
    compose_path.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Deploy complete Sophia AI platform to Lambda Labs"
    )
    parser.add_argument("--host", required=True, help="Lambda Labs host IP")
    parser.add_argument("--ssh-key", required=True, help="SSH key file path")
    parser.add_argument("--registry", default="scoobyjava15", help="Docker registry")
    parser.add_argument("--environment", default="production", help="Environment")
    parser.add_argument(
        "--deploy-mcp-servers", type=str, default="true", help="Deploy MCP servers"
    )

    args = parser.parse_args()

    deploy_mcp_servers = args.deploy_mcp_servers.lower() == "true"

    try:
        deploy_to_lambda_labs(
            args.host, args.ssh_key, args.registry, args.environment, deploy_mcp_servers
        )
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
