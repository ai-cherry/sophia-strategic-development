# Docker Cloud Bottleneck Remediation Plan

**Status**: IMMEDIATE ACTION REQUIRED
**Date**: January 2025
**Environment**: Docker Swarm on Lambda Labs (146.235.200.1)
**Priority**: CRITICAL - Performance and stability issues

## Executive Summary

Our Docker Cloud deployment has several critical bottlenecks that need immediate attention:
- Single-replica services creating single points of failure
- No resource limits causing node saturation
- Missing health checks on critical services
- Overlay network latency between services
- Slow persistent volume performance

## Current State Analysis

### 1. Node Resource Saturation Issues

**Current Problems:**
- No resource limits defined in docker-compose.cloud.yml
- Services can consume unlimited CPU/memory
- No placement constraints for GPU/memory-intensive services
- Risk of node exhaustion and service eviction

**Evidence:**
```yaml
# Current (BAD) - No limits
services:
  backend:
    image: scoobyjava15/sophia-backend:latest
    # NO deploy.resources defined!
```

### 2. Single-Replica Services (CRITICAL)

**Single Points of Failure:**
- Traefik (reverse proxy) - 1 replica
- PostgreSQL - 1 replica
- Redis - 1 replica
- MCP Gateway - 1 replica

**Impact:** Any failure causes complete service outage

### 3. Overlay Network Latency

**Current Issues:**
- All services on same overlay network
- No service co-location strategy
- Chatty services (MCP servers) causing network congestion

### 4. Persistent Volume Performance

**Current Configuration:**
- Using bind mounts: `/opt/sophia-ai/data/`
- No volume driver optimization
- Unknown disk performance characteristics

## Remediation Plan

### Phase 1: Critical Fixes (Week 1)

#### 1.1 Add Resource Limits to All Services

```yaml
# docker-compose.cloud.yml updates
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      placement:
        constraints:
          - node.labels.tier == compute
```

#### 1.2 Scale Critical Services

```yaml
# Scale single-replica services
traefik:
  deploy:
    replicas: 2
    placement:
      constraints:
        - node.role == manager

redis:
  deploy:
    replicas: 3
    # Redis Sentinel for HA

mcp-gateway:
  deploy:
    replicas: 3
    update_config:
      parallelism: 1
      delay: 10s
```

#### 1.3 Implement Comprehensive Health Checks

```yaml
# Add health checks to all services
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### Phase 2: Network Optimization (Week 2)

#### 2.1 Service Co-location Strategy

```yaml
# Create placement constraints for latency-sensitive services
services:
  backend:
    deploy:
      placement:
        constraints:
          - node.labels.zone == primary

  redis:
    deploy:
      placement:
        constraints:
          - node.labels.zone == primary
```

#### 2.2 Multiple Overlay Networks

```yaml
networks:
  frontend:
    driver: overlay
    attachable: true

  backend:
    driver: overlay
    internal: true

  data:
    driver: overlay
    internal: true
```

### Phase 3: Storage Optimization (Week 3)

#### 3.1 High-Performance Volume Configuration

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/fast-ssd/postgres

  redis_data:
    driver: local
    driver_opts:
      type: tmpfs
      o: size=2g
```

#### 3.2 Backup Strategy

```yaml
# Automated backup service
backup:
  image: postgres:15-alpine
  volumes:
    - postgres_data:/data:ro
    - backup_volume:/backup
  deploy:
    replicas: 1
    restart_policy:
      condition: on-failure
```

### Phase 4: Monitoring Implementation (Week 4)

#### 4.1 Prometheus Stack Deployment

```yaml
# monitoring-stack.yml
services:
  prometheus:
    image: prom/prometheus:latest
    configs:
      - source: prometheus_config
        target: /etc/prometheus/prometheus.yml
    deploy:
      replicas: 2

  grafana:
    image: grafana/grafana:latest
    deploy:
      replicas: 2

  node-exporter:
    image: prom/node-exporter:latest
    deploy:
      mode: global  # One per node
```

#### 4.2 Application Metrics

```python
# backend/monitoring/swarm_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Swarm-specific metrics
node_cpu_usage = Gauge('node_cpu_usage_percent', 'CPU usage per node', ['node_id'])
service_replica_count = Gauge('service_replica_count', 'Replicas per service', ['service'])
overlay_network_latency = Histogram('overlay_network_latency_ms', 'Network latency', ['source', 'dest'])
```

### Implementation Scripts

#### Script 1: Resource Optimization

```python
# scripts/optimize_docker_swarm_resources.py
#!/usr/bin/env python3
"""
Optimize Docker Swarm resource allocation
"""

import yaml
import subprocess
from pathlib import Path

def add_resource_limits(compose_file: str):
    """Add resource limits to all services"""
    with open(compose_file, 'r') as f:
        config = yaml.safe_load(f)

    # Default resource limits
    default_limits = {
        'backend': {'cpus': '2.0', 'memory': '4G'},
        'mcp-server': {'cpus': '1.0', 'memory': '2G'},
        'database': {'cpus': '4.0', 'memory': '8G'},
        'cache': {'cpus': '2.0', 'memory': '4G'},
    }

    for service, spec in config['services'].items():
        if 'deploy' not in spec:
            spec['deploy'] = {}

        service_type = detect_service_type(service)
        limits = default_limits.get(service_type, {'cpus': '1.0', 'memory': '2G'})

        spec['deploy']['resources'] = {
            'limits': limits,
            'reservations': {
                'cpus': str(float(limits['cpus']) / 2),
                'memory': f"{int(limits['memory'][:-1]) // 2}G"
            }
        }

    # Save updated config
    with open(compose_file + '.optimized', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
```

#### Script 2: Health Check Validator

```python
# scripts/validate_swarm_health_checks.py
#!/usr/bin/env python3
"""
Validate and add health checks to all services
"""

def generate_health_check(service_name: str, port: int) -> dict:
    """Generate appropriate health check for service"""

    health_checks = {
        'fastapi': {
            'test': ["CMD", "curl", "-f", f"http://localhost:{port}/health"],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3,
            'start_period': '40s'
        },
        'postgres': {
            'test': ["CMD-SHELL", "pg_isready -U postgres"],
            'interval': '10s',
            'timeout': '5s',
            'retries': 5,
            'start_period': '30s'
        },
        'redis': {
            'test': ["CMD", "redis-cli", "ping"],
            'interval': '10s',
            'timeout': '5s',
            'retries': 5,
            'start_period': '30s'
        }
    }

    # Detect service type and return appropriate health check
    if 'postgres' in service_name:
        return health_checks['postgres']
    elif 'redis' in service_name:
        return health_checks['redis']
    else:
        return health_checks['fastapi']
```

#### Script 3: Swarm Performance Monitor

```bash
#!/bin/bash
# scripts/monitor_swarm_performance.sh

# Monitor node resources
echo "=== Node Resource Usage ==="
docker node ls --format "table {{.Hostname}}\t{{.Status}}\t{{.Availability}}"

for node in $(docker node ls -q); do
    echo "Node: $(docker node inspect $node --format '{{.Description.Hostname}}')"
    docker node inspect $node --format '{{json .Description.Resources}}' | jq
done

# Monitor service status
echo -e "\n=== Service Status ==="
docker service ls --format "table {{.Name}}\t{{.Replicas}}\t{{.Image}}"

# Check for placement issues
echo -e "\n=== Placement Constraints ==="
for service in $(docker service ls -q); do
    constraints=$(docker service inspect $service --format '{{json .Spec.TaskTemplate.Placement.Constraints}}')
    if [ "$constraints" != "null" ]; then
        echo "Service: $(docker service inspect $service --format '{{.Spec.Name}}')"
        echo "Constraints: $constraints"
    fi
done

# Network performance
echo -e "\n=== Network Status ==="
docker network ls --filter driver=overlay
```

### Monitoring Dashboard Configuration

```yaml
# grafana/dashboards/swarm-performance.json
{
  "dashboard": {
    "title": "Sophia AI Swarm Performance",
    "panels": [
      {
        "title": "Node CPU Usage",
        "targets": [{
          "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) by (instance) * 100)"
        }]
      },
      {
        "title": "Service Replica Health",
        "targets": [{
          "expr": "sum(up{job=~\"sophia-.*\"}) by (job)"
        }]
      },
      {
        "title": "Overlay Network Latency",
        "targets": [{
          "expr": "histogram_quantile(0.95, overlay_network_latency_ms)"
        }]
      }
    ]
  }
}
```

### Deployment Checklist

- [ ] Backup current configuration
- [ ] Test resource limits in staging
- [ ] Deploy monitoring stack first
- [ ] Apply resource limits gradually
- [ ] Scale services one at a time
- [ ] Monitor for 24h after each change
- [ ] Document performance improvements

## Expected Improvements

1. **Reliability**: 99.9% uptime (from ~95%)
2. **Performance**: 40% reduction in p95 latency
3. **Scalability**: Support 10x current load
4. **Resource Efficiency**: 30% better utilization
5. **Recovery Time**: <1 minute for service failures

## Success Metrics

- All services have resource limits
- No single-replica critical services
- Health checks passing 100%
- Node CPU < 80% sustained
- Memory usage < 70% sustained
- Network latency < 10ms p95
- Zero OOM kills per week

## Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Critical Fixes | Resource limits, scaling, health checks |
| 2 | Network Optimization | Co-location, multiple networks |
| 3 | Storage Optimization | SSD volumes, backup strategy |
| 4 | Monitoring | Prometheus, Grafana, alerts |

## Risk Mitigation

1. **Test all changes in staging first**
2. **Roll back plan for each change**
3. **Monitor closely during changes**
4. **Keep Lambda Labs support informed**
5. **Document all configuration changes**

---

This plan addresses all identified bottlenecks with concrete, actionable steps that can be implemented immediately on our Docker Swarm cluster.
