# Sophia AI Distributed Architecture Implementation Plan
## Comprehensive Conflict Resolution & Dependency Management

**Document Version**: 2.0  
**Date**: July 15, 2025  
**Status**: Implementation Ready  
**Target**: Transform sophia-main repository for distributed Lambda Labs infrastructure

---

## 🎯 Executive Summary

This plan addresses the complete transformation of the Sophia AI repository from localhost deployment to a distributed architecture across 4 Lambda Labs GPU instances, with comprehensive conflict resolution and dependency management.

### Infrastructure Target
```yaml
Lambda Labs Instances:
  sophia-ai-core:        # 192.222.58.232 - GH200 96GB - Primary K3s cluster
  sophia-mcp-orchestrator: # 104.171.202.117 - A6000 48GB - MCP servers  
  sophia-data-pipeline:   # 104.171.202.134 - A100 40GB - Data processing
  sophia-development:     # 155.248.194.183 - A10 24GB - Development/testing
```

---

## 📋 Phase 1: Dependency Resolution & Environment Setup

### 1.1 Python Environment Conflicts

**IDENTIFIED CONFLICTS:**
- ❌ Type checker cannot resolve `uvicorn`, `fastapi` imports
- ❌ Missing distributed architecture dependencies  
- ❌ Inconsistent Python path management
- ❌ Environment variable conflicts between instances

**RESOLUTION STRATEGY:**

#### A. Update requirements.txt with distributed dependencies
```bash
# Add to requirements.txt
tenacity>=8.2.0          # Retry logic for distributed calls
httpx>=0.24.0           # Async HTTP client for inter-service communication
consul-python>=1.1.0    # Service discovery (optional)
etcd3>=0.12.0          # Distributed configuration (optional)
paramiko>=3.0.0        # SSH connectivity to instances
fabric>=3.0.0          # Deployment automation
prometheus-client>=0.16.0  # Metrics collection
structlog>=22.3.0      # Structured logging
```

#### B. Fix Python path and import issues
```python
# In main.py and api/main.py
import sys
from pathlib import Path

# Ensure project root is in Python path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

#### C. Environment variable standardization
```bash
# .env.distributed (new file)
# Core Infrastructure
ENVIRONMENT=production
SOPHIA_DISTRIBUTED_MODE=true

# Instance Detection
CURRENT_INSTANCE_IP=${INSTANCE_IP}
INSTANCE_NAME=${INSTANCE_NAME}
INSTANCE_ROLE=${INSTANCE_ROLE}

# Lambda Labs Infrastructure  
LAMBDA_AI_CORE_IP=192.222.58.232
LAMBDA_MCP_ORCHESTRATOR_IP=104.171.202.117
LAMBDA_DATA_PIPELINE_IP=104.171.202.134
LAMBDA_DEVELOPMENT_IP=155.248.194.183

# Qdrant Cluster
QDRANT_URL=https://a2a5dc3b-bf37-4907-9398-d49f5c6813ed.us-west-2-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.dolvYDuCiLIegw30HhFR9wXWWO3wn8ArOHr0ORj9U2Y

# Service Discovery
SERVICE_DISCOVERY_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# Database (Primary instance only)
DATABASE_URL=postgresql://sophia:sophia2025@192.222.58.232:5432/sophia_ai
REDIS_URL=redis://192.222.58.232:6379

# Domain Configuration
DOMAIN=sophia-intel.ai
API_DOMAIN=api.sophia-intel.ai
APP_DOMAIN=app.sophia-intel.ai
```

### 1.2 Configuration Management Conflicts

**IDENTIFIED CONFLICTS:**
- ❌ Hardcoded localhost references throughout codebase
- ❌ Single-instance assumptions in service initialization
- ❌ Port conflicts between services
- ❌ Missing instance-specific configuration

**RESOLUTION STRATEGY:**

#### A. Create centralized configuration system
```python
# config/distributed_config.py (new file)
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os

class DeploymentMode(Enum):
    SINGLE_INSTANCE = "single"
    DISTRIBUTED = "distributed"
    DEVELOPMENT = "development"

@dataclass
class DistributedConfig:
    mode: DeploymentMode
    current_instance: Optional[str] = None
    service_discovery_enabled: bool = True
    health_monitoring_enabled: bool = True
    
    @classmethod
    def from_environment(cls) -> 'DistributedConfig':
        mode_str = os.getenv('SOPHIA_DISTRIBUTED_MODE', 'false').lower()
        mode = DeploymentMode.DISTRIBUTED if mode_str == 'true' else DeploymentMode.SINGLE_INSTANCE
        
        return cls(
            mode=mode,
            current_instance=os.getenv('INSTANCE_NAME'),
            service_discovery_enabled=os.getenv('SERVICE_DISCOVERY_ENABLED', 'true').lower() == 'true',
            health_monitoring_enabled=os.getenv('HEALTH_MONITORING_ENABLED', 'true').lower() == 'true'
        )
```

#### B. Port allocation strategy
```python
# In config/infrastructure.py
PORT_ALLOCATION = {
    "sophia-ai-core": {
        "primary": 8000,
        "health": 8001,
        "metrics": 8002,
        "admin": 8003
    },
    "sophia-mcp-orchestrator": {
        "primary": 8100,
        "health": 8101,
        "metrics": 8102,
        "mcp_gateway": 8103
    },
    "sophia-data-pipeline": {
        "primary": 8200,
        "health": 8201,
        "metrics": 8202,
        "ml_api": 8203
    },
    "sophia-development": {
        "primary": 8300,
        "health": 8301,
        "metrics": 8302,
        "debug": 8303
    }
}
```

---

## 📋 Phase 2: Service Architecture Conflicts

### 2.1 Service Discovery Integration

**IDENTIFIED CONFLICTS:**
- ❌ Services assume localhost availability
- ❌ No mechanism for inter-service communication
- ❌ Missing health check coordination
- ❌ Race conditions during startup

**RESOLUTION STRATEGY:**

#### A. Implement service registry pattern
```python
# services/distributed_orchestrator.py (new file)
import asyncio
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ServiceEndpoint:
    name: str
    url: str
    instance: str
    health_status: bool = False
    last_check: datetime = field(default_factory=datetime.now)
    
class DistributedOrchestrator:
    def __init__(self):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def register_service(self, name: str, url: str, instance: str):
        """Register a service endpoint"""
        self.services[name] = ServiceEndpoint(
            name=name,
            url=url,
            instance=instance
        )
        
    async def route_request(self, service_name: str, request_data: Dict) -> Dict:
        """Route request to appropriate service"""
        service = self.services.get(service_name)
        if not service or not service.health_status:
            raise ServiceUnavailableError(f"Service {service_name} not available")
            
        async with self.session.post(f"{service.url}/process", json=request_data) as response:
            return await response.json()
```

#### B. Startup coordination mechanism
```python
# utils/startup_coordinator.py (new file)
import asyncio
from typing import List, Dict, Callable
from enum import Enum

class StartupPhase(Enum):
    INFRASTRUCTURE = 1
    SERVICES = 2
    HEALTH_CHECKS = 3
    READY = 4

class StartupCoordinator:
    def __init__(self):
        self.current_phase = StartupPhase.INFRASTRUCTURE
        self.phase_callbacks: Dict[StartupPhase, List[Callable]] = {
            phase: [] for phase in StartupPhase
        }
        
    async def execute_startup_sequence(self):
        """Execute coordinated startup across all phases"""
        for phase in StartupPhase:
            await self._execute_phase(phase)
            
    async def _execute_phase(self, phase: StartupPhase):
        """Execute all callbacks for a specific phase"""
        callbacks = self.phase_callbacks.get(phase, [])
        if callbacks:
            await asyncio.gather(*[callback() for callback in callbacks])
        self.current_phase = phase
```

### 2.2 Database Connection Management

**IDENTIFIED CONFLICTS:**
- ❌ All instances trying to connect to database
- ❌ Connection pool exhaustion
- ❌ Database migrations running multiple times
- ❌ Redis connection conflicts

**RESOLUTION STRATEGY:**

#### A. Database access patterns by role
```python
# database/distributed_manager.py (new file)
from config.infrastructure import InstanceRole
import asyncpg
import redis

class DistributedDatabaseManager:
    def __init__(self, instance_role: InstanceRole):
        self.instance_role = instance_role
        self.db_pool = None
        self.redis_client = None
        
    async def initialize(self):
        """Initialize database connections based on role"""
        if self.instance_role == InstanceRole.PRIMARY:
            # Primary instance manages main database
            self.db_pool = await asyncpg.create_pool(
                os.getenv('DATABASE_URL'),
                min_size=5,
                max_size=20
            )
            self.redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))
            
        elif self.instance_role in [InstanceRole.MCP_ORCHESTRATOR, InstanceRole.DATA_PIPELINE]:
            # These instances need read-only database access
            self.db_pool = await asyncpg.create_pool(
                os.getenv('DATABASE_URL'),
                min_size=2,
                max_size=5,
                command_timeout=10
            )
            
        # Development instance uses minimal connections
        elif self.instance_role == InstanceRole.DEVELOPMENT:
            self.db_pool = await asyncpg.create_pool(
                os.getenv('DATABASE_URL'),
                min_size=1,
                max_size=3
            )
```

#### B. Database migration coordination
```python
# database/migration_coordinator.py (new file)
import asyncio
import os
from typing import List
from config.infrastructure import InstanceRole

class MigrationCoordinator:
    def __init__(self, instance_role: InstanceRole):
        self.instance_role = instance_role
        
    async def handle_migrations(self):
        """Only primary instance runs migrations"""
        if self.instance_role != InstanceRole.PRIMARY:
            # Non-primary instances wait for migrations to complete
            await self._wait_for_migrations()
            return
            
        # Primary instance runs migrations
        await self._run_migrations()
        await self._signal_migration_complete()
        
    async def _wait_for_migrations(self):
        """Wait for primary instance to complete migrations"""
        # Implementation would check migration status
        pass
        
    async def _run_migrations(self):
        """Run database migrations"""
        # Implementation would run Alembic migrations
        pass
```

---

## 📋 Phase 3: Network & Communication Conflicts

### 3.1 Inter-Service Communication

**IDENTIFIED CONFLICTS:**
- ❌ Services cannot communicate across instances
- ❌ No load balancing or failover
- ❌ Timeouts not configured for distributed calls
- ❌ No circuit breaker pattern

**RESOLUTION STRATEGY:**

#### A. HTTP client with retry logic
```python
# utils/distributed_client.py (new file)
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any, Optional

class DistributedHTTPClient:
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP POST with retry logic"""
        async with self.session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
```

#### B. Circuit breaker implementation
```python
# utils/circuit_breaker.py (new file)
import asyncio
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time < self.timeout:
                raise CircuitBreakerOpenError("Circuit breaker is open")
            else:
                self.state = CircuitState.HALF_OPEN
                
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
            
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### 3.2 Load Balancing & Failover

**IDENTIFIED CONFLICTS:**
- ❌ No load balancing between similar services
- ❌ Single point of failure for each service type
- ❌ No automatic failover mechanisms

**RESOLUTION STRATEGY:**

#### A. Service load balancer
```python
# services/load_balancer.py (new file)
import random
from typing import List, Dict, Optional
from services.service_discovery import ServiceDiscovery

class ServiceLoadBalancer:
    def __init__(self, service_discovery: ServiceDiscovery):
        self.service_discovery = service_discovery
        
    async def get_service_endpoint(self, service_type: str) -> Optional[str]:
        """Get endpoint for service with load balancing"""
        healthy_services = await self.service_discovery.get_healthy_services(service_type)
        
        if not healthy_services:
            return None
            
        # Simple round-robin for now, can be enhanced with weighted algorithms
        return random.choice(healthy_services)
        
    async def get_primary_fallback_endpoint(self, service_type: str) -> Optional[str]:
        """Get primary endpoint with fallback to secondary"""
        # Try primary instance first
        primary_endpoint = await self.get_service_endpoint(f"{service_type}_primary")
        if primary_endpoint:
            return primary_endpoint
            
        # Fallback to any healthy instance
        return await self.get_service_endpoint(service_type)
```

---

## 📋 Phase 4: Deployment & Orchestration Conflicts

### 4.1 Deployment Script Conflicts

**IDENTIFIED CONFLICTS:**
- ❌ Deployment assumes single instance
- ❌ No coordination between instance deployments
- ❌ Race conditions during deployment
- ❌ No rollback strategy for distributed deployment

**RESOLUTION STRATEGY:**

#### A. Orchestrated deployment script
```bash
#!/bin/bash
# scripts/deploy_distributed_coordinated.sh

set -e

# Configuration
DEPLOYMENT_ID=$(date +%Y%m%d_%H%M%S)
DEPLOYMENT_LOG="deployment_${DEPLOYMENT_ID}.log"
ROLLBACK_DATA="rollback_${DEPLOYMENT_ID}.json"

# Deployment order (critical for avoiding conflicts)
DEPLOYMENT_ORDER=(
    "sophia-ai-core:192.222.58.232:primary"
    "sophia-data-pipeline:104.171.202.134:data" 
    "sophia-mcp-orchestrator:104.171.202.117:mcp"
    "sophia-development:155.248.194.183:dev"
)

# Phase 1: Pre-deployment validation
echo "🔍 Phase 1: Pre-deployment validation"
for instance_info in "${DEPLOYMENT_ORDER[@]}"; do
    IFS=':' read -r name ip role <<< "$instance_info"
    
    # Check connectivity
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 ubuntu@$ip "echo 'SSH OK'"; then
        echo "❌ Cannot connect to $name ($ip)"
        exit 1
    fi
    
    # Check system resources
    ssh -i "$SSH_KEY" ubuntu@$ip "
        if [ \$(df / | tail -1 | awk '{print \$5}' | sed 's/%//') -gt 90 ]; then
            echo 'ERROR: Disk usage > 90%'
            exit 1
        fi
        if [ \$(free | grep Mem | awk '{print (\$3/\$2) * 100.0}' | cut -d. -f1) -gt 90 ]; then
            echo 'ERROR: Memory usage > 90%'
            exit 1
        fi
    " || {
        echo "❌ Resource check failed for $name"
        exit 1
    }
done

# Phase 2: Stop services in reverse order
echo "🛑 Phase 2: Stopping services"
for ((i=${#DEPLOYMENT_ORDER[@]}-1; i>=0; i--)); do
    instance_info="${DEPLOYMENT_ORDER[$i]}"
    IFS=':' read -r name ip role <<< "$instance_info"
    
    echo "Stopping services on $name..."
    ssh -i "$SSH_KEY" ubuntu@$ip "
        pkill -f 'uvicorn' || true
        pkill -f 'python.*main.py' || true
        sleep 5
    "
done

# Phase 3: Deploy in order
echo "🚀 Phase 3: Deploying services"
for instance_info in "${DEPLOYMENT_ORDER[@]}"; do
    IFS=':' read -r name ip role <<< "$instance_info"
    
    echo "Deploying to $name ($role)..."
    
    # Create deployment package
    tar -czf "/tmp/sophia-${name}-${DEPLOYMENT_ID}.tar.gz" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='deployment_*.log' \
        .
    
    # Deploy to instance
    scp -i "$SSH_KEY" "/tmp/sophia-${name}-${DEPLOYMENT_ID}.tar.gz" ubuntu@$ip:~/
    
    ssh -i "$SSH_KEY" ubuntu@$ip << EOF
        # Backup current deployment
        if [ -d sophia-main ]; then
            mv sophia-main sophia-main-backup-${DEPLOYMENT_ID}
        fi
        
        # Extract new deployment
        mkdir sophia-main
        cd sophia-main
        tar -xzf ~/sophia-${name}-${DEPLOYMENT_ID}.tar.gz
        rm ~/sophia-${name}-${DEPLOYMENT_ID}.tar.gz
        
        # Set up environment
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create instance-specific environment
        cat > .env << 'ENVFILE'
ENVIRONMENT=production
SOPHIA_DISTRIBUTED_MODE=true
CURRENT_INSTANCE_IP=$ip
INSTANCE_NAME=$name
INSTANCE_ROLE=$role
DEPLOYMENT_ID=${DEPLOYMENT_ID}

# Infrastructure endpoints
LAMBDA_AI_CORE_IP=192.222.58.232
LAMBDA_MCP_ORCHESTRATOR_IP=104.171.202.117
LAMBDA_DATA_PIPELINE_IP=104.171.202.134
LAMBDA_DEVELOPMENT_IP=155.248.194.183

# External services
QDRANT_URL=https://a2a5dc3b-bf37-4907-9398-d49f5c6813ed.us-west-2-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.dolvYDuCiLIegw30HhFR9wXWWO3wn8ArOHr0ORj9U2Y

# Service discovery
SERVICE_DISCOVERY_ENABLED=true
HEALTH_CHECK_INTERVAL=30
ENVFILE

        # Start service
        source venv/bin/activate
        mkdir -p ~/sophia-logs
        nohup python main.py > ~/sophia-logs/main-${DEPLOYMENT_ID}.log 2>&1 &
        echo \$! > ~/sophia-logs/main-${DEPLOYMENT_ID}.pid
        
        # Wait for service to start
        sleep 15
        
        # Verify service is running
        if curl -s http://localhost:8000/health | grep -q "healthy"; then
            echo "✅ Service started successfully on $name"
        else
            echo "❌ Service failed to start on $name"
            tail -20 ~/sophia-logs/main-${DEPLOYMENT_ID}.log
            exit 1
        fi
EOF
    
    # Clean up local deployment package
    rm "/tmp/sophia-${name}-${DEPLOYMENT_ID}.tar.gz"
    
    echo "✅ Deployment complete on $name"
done

# Phase 4: Verify distributed health
echo "🔍 Phase 4: Verifying distributed health"
sleep 30  # Allow time for service discovery

for instance_info in "${DEPLOYMENT_ORDER[@]}"; do
    IFS=':' read -r name ip role <<< "$instance_info"
    
    echo -n "Testing $name ($ip): "
    if curl -s --max-time 10 http://$ip:8000/health | grep -q "healthy"; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy - initiating rollback"
        # Rollback logic here
        exit 1
    fi
done

echo "🎉 Distributed deployment successful!"
echo "📊 Monitor health at:"
echo "   Primary: http://192.222.58.232:8000/health"
echo "   MCP: http://104.171.202.117:8000/health" 
echo "   Data: http://104.171.202.134:8000/health"
echo "   Dev: http://155.248.194.183:8000/health"
```

#### B. Rollback mechanism
```bash
# scripts/rollback_distributed.sh
#!/bin/bash

DEPLOYMENT_ID=$1
if [ -z "$DEPLOYMENT_ID" ]; then
    echo "Usage: $0 <deployment_id>"
    exit 1
fi

echo "🔄 Rolling back deployment $DEPLOYMENT_ID"

# Rollback in reverse order
ROLLBACK_ORDER=(
    "sophia-development:155.248.194.183:dev"
    "sophia-mcp-orchestrator:104.171.202.117:mcp"
    "sophia-data-pipeline:104.171.202.134:data"
    "sophia-ai-core:192.222.58.232:primary"
)

for instance_info in "${ROLLBACK_ORDER[@]}"; do
    IFS=':' read -r name ip role <<< "$instance_info"
    
    echo "Rolling back $name..."
    ssh -i "$SSH_KEY" ubuntu@$ip "
        # Stop current service
        if [ -f ~/sophia-logs/main-${DEPLOYMENT_ID}.pid ]; then
            kill \$(cat ~/sophia-logs/main-${DEPLOYMENT_ID}.pid) || true
        fi
        
        # Restore backup
        if [ -d sophia-main-backup-${DEPLOYMENT_ID} ]; then
            rm -rf sophia-main
            mv sophia-main-backup-${DEPLOYMENT_ID} sophia-main
            
            # Start backup service
            cd sophia-main
            source venv/bin/activate
            nohup python main.py > ~/sophia-logs/rollback.log 2>&1 &
            echo \$! > ~/sophia-logs/rollback.pid
        fi
    "
done

echo "✅ Rollback complete"
```

---

## 📋 Phase 5: Testing & Validation Strategy

### 5.1 Integration Test Suite

```python
# tests/test_distributed_architecture.py (new file)
import pytest
import asyncio
import aiohttp
from config.infrastructure import InfrastructureConfig

class TestDistributedArchitecture:
    
    @pytest.fixture
    async def infrastructure_config(self):
        return InfrastructureConfig()
    
    @pytest.fixture 
    async def http_session(self):
        async with aiohttp.ClientSession() as session:
            yield session
    
    async def test_all_instances_health(self, infrastructure_config, http_session):
        """Test that all instances respond to health checks"""
        for name, instance in infrastructure_config.INSTANCES.items():
            async with http_session.get(instance.health_endpoint) as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
                assert data["instance"]["name"] == name
    
    async def test_service_discovery(self, infrastructure_config, http_session):
        """Test service discovery functionality"""
        primary_instance = infrastructure_config.get_instance_by_role(InstanceRole.PRIMARY)
        
        async with http_session.get(f"{primary_instance.endpoint}/api/v1/instances") as response:
            assert response.status == 200
            data = await response.json()
            assert len(data["instances"]) == 4
            assert data["total_count"] == 4
    
    async def test_inter_service_communication(self, infrastructure_config, http_session):
        """Test communication between services"""
        primary_instance = infrastructure_config.get_instance_by_role(InstanceRole.PRIMARY)
        mcp_instance = infrastructure_config.get_instance_by_role(InstanceRole.MCP_ORCHESTRATOR)
        
        # Test orchestration from primary to MCP
        request_data = {
            "type": "mcp_request",
            "data": {"test": "inter_service_communication"}
        }
        
        async with http_session.post(
            f"{primary_instance.endpoint}/api/v1/orchestrate",
            json=request_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "orchestrated_by" in data
    
    async def test_load_balancing(self, infrastructure_config, http_session):
        """Test load balancing functionality"""
        # Multiple requests should be distributed across instances
        responses = []
        for i in range(10):
            async with http_session.get(f"{primary_instance.endpoint}/api/v1/status") as response:
                data = await response.json()
                responses.append(data["instance"]["name"])
        
        # Should have some distribution (not all same instance)
        unique_instances = set(responses)
        assert len(unique_instances) >= 1  # At minimum, should respond
    
    async def test_failure_handling(self, infrastructure_config, http_session):
        """Test system behavior when one instance fails"""
        # This would simulate instance failure and test failover
        pass
```

### 5.2 Performance Testing

```python
# tests/test_distributed_performance.py (new file)
import pytest
import asyncio
import aiohttp
import time
from statistics import mean, median

class TestDistributedPerformance:
    
    async def test_response_times(self, http_session):
        """Test response times across all instances"""
        instances = [
            "http://192.222.58.232:8000",
            "http://104.171.202.117:8000", 
            "http://104.171.202.134:8000",
            "http://155.248.194.183:8000"
        ]
        
        response_times = {}
        
        for instance_url in instances:
            times = []
            for _ in range(10):
                start_time = time.time()
                async with http_session.get(f"{instance_url}/health") as response:
                    await response.json()
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convert to ms
            
            response_times[instance_url] = {
                "mean": mean(times),
                "median": median(times),
                "max": max(times)
            }
        
        # Assert all response times are reasonable
        for url, stats in response_times.items():
            assert stats["mean"] < 200, f"{url} mean response time too high: {stats['mean']}ms"
            assert stats["max"] < 500, f"{url} max response time too high: {stats['max']}ms"
    
    async def test_concurrent_requests(self, http_session):
        """Test system under concurrent load"""
        instance_url = "http://192.222.58.232:8000"
        
        async def make_request():
            async with http_session.get(f"{instance_url}/health") as response:
                return response.status
        
        # Test 50 concurrent requests
        tasks =
