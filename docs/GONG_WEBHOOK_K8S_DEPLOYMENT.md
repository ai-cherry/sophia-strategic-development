---
title: Gong Webhook Service - Kubernetes Deployment Guide
description: 
tags: security, gong, kubernetes, monitoring, database, docker
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Gong Webhook Service - Kubernetes Deployment Guide


## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
  - [Components Deployed](#components-deployed)
- [Prerequisites](#prerequisites)
  - [Required Tools](#required-tools)
  - [Required Access](#required-access)
  - [Required Infrastructure](#required-infrastructure)
- [Configuration](#configuration)
  - [Environment Variables (ConfigMap)](#environment-variables-(configmap))
  - [Secrets (Kubernetes Secret)](#secrets-(kubernetes-secret))
- [Deployment](#deployment)
  - [Quick Deployment](#quick-deployment)
  - [Step-by-Step Deployment](#step-by-step-deployment)
- [Resource Specifications](#resource-specifications)
  - [Pod Resources](#pod-resources)
  - [Auto-scaling](#auto-scaling)
  - [High Availability](#high-availability)
- [Security Features](#security-features)
  - [Container Security](#container-security)
  - [Network Security](#network-security)
  - [Secret Management](#secret-management)
- [Monitoring and Observability](#monitoring-and-observability)
  - [Health Endpoints](#health-endpoints)
  - [Prometheus Metrics](#prometheus-metrics)
  - [Logging](#logging)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging Commands](#debugging-commands)
- [Maintenance](#maintenance)
  - [Updates](#updates)
  - [Scaling](#scaling)
  - [Secret Rotation](#secret-rotation)
- [Performance Optimization](#performance-optimization)
  - [Tuning Parameters](#tuning-parameters)
  - [Monitoring Metrics](#monitoring-metrics)
- [Integration Points](#integration-points)
  - [Upstream Services](#upstream-services)
  - [Downstream Services](#downstream-services)
- [Disaster Recovery](#disaster-recovery)
  - [Backup Strategy](#backup-strategy)
  - [Recovery Procedures](#recovery-procedures)
- [Support and Documentation](#support-and-documentation)
  - [Additional Resources](#additional-resources)
  - [Contact Information](#contact-information)

## Overview

The Gong Webhook Service is a production-ready FastAPI application that processes Gong webhooks in real-time, enhances data via API calls, and stores processed data in Snowflake. This guide covers the Kubernetes deployment of the service within the Sophia AI platform.

## Architecture

```python
# Example usage:
python
```python

### Components Deployed

1. **Namespace**: `sophia-ai` - Isolated environment for Sophia AI services
2. **Deployment**: 3-replica deployment with rolling updates
3. **Service**: ClusterIP service for internal communication
4. **Ingress**: NGINX ingress with TLS termination
5. **ConfigMap**: Non-sensitive configuration values
6. **Secret**: Sensitive credentials from Pulumi ESC
7. **HPA**: Horizontal Pod Autoscaler (3-10 replicas)
8. **ServiceMonitor**: Prometheus monitoring configuration
9. **NetworkPolicy**: Security policies for network traffic
10. **PodDisruptionBudget**: High availability guarantees

## Prerequisites

### Required Tools
- `kubectl` - Kubernetes CLI
- `docker` - Container management
- `pulumi` - Infrastructure as Code and secret management
- `curl` - API testing

### Required Access
- Kubernetes cluster admin access
- Pulumi ESC environment access (`sophia-ai-production`)
- Docker registry access (for image pushing)

### Required Infrastructure
- Kubernetes cluster (1.21+)
- NGINX Ingress Controller
- Prometheus Operator (for monitoring)
- cert-manager (for TLS certificates)

## Configuration

### Environment Variables (ConfigMap)
```yaml
# Example usage:
yaml
```python

### Secrets (Kubernetes Secret)
Managed by Pulumi ESC and automatically injected:
- `GONG_API_KEY` - Gong API authentication
- `GONG_WEBHOOK_SECRETS` - JWT verification secrets
- `SNOWFLAKE_ACCOUNT` - Snowflake account identifier
- `SNOWFLAKE_USER` - Snowflake username
- `SNOWFLAKE_PASSWORD` - Snowflake password

## Deployment

### Quick Deployment
```bash
# Example usage:
bash
```python

### Step-by-Step Deployment

1. **Prepare Environment**
   ```bash
# Example usage:
bash
```yaml
requests:
  memory: "512Mi"
  cpu: "250m"
  ephemeral-storage: "1Gi"
limits:
  memory: "2Gi"
  cpu: "1000m"
  ephemeral-storage: "2Gi"
```python
# Example usage:
python
```bash
# View all resources
kubectl get all -l app=gong-webhook-service -n sophia-ai

# Check pod events
kubectl get events --field-selector involvedObject.name=<pod-name> -n sophia-ai

# Access pod shell
kubectl exec -it deployment/gong-webhook-service -n sophia-ai -- /bin/bash

# View configuration
kubectl get configmap gong-webhook-config -n sophia-ai -o yaml

# Check ingress
kubectl describe ingress gong-webhook-ingress -n sophia-ai
```python
# Example usage:
python
```bash
# Update image
kubectl set image deployment/gong-webhook-service \
  gong-webhook=sophia-ai/gong-webhook-service:v1.1.0 \
  -n sophia-ai

# Monitor rollout
kubectl rollout status deployment/gong-webhook-service -n sophia-ai
```python
# Example usage:
python
```bash
# Manual scaling
kubectl scale deployment gong-webhook-service --replicas=5 -n sophia-ai

# Update HPA
kubectl patch hpa gong-webhook-hpa -n sophia-ai -p '{"spec":{"maxReplicas":15}}'
```python
# Example usage:
python
```bash
# Rotate secrets via Pulumi ESC
pulumi env set scoobyjava-org/default/sophia-ai-production GONG_ACCESS_KEY new-value

# Restart deployment to pick up new secrets
kubectl rollout restart deployment/gong-webhook-service -n sophia-ai
```python

## Performance Optimization

### Tuning Parameters
- **Worker processes**: Adjust based on CPU cores
- **Connection pooling**: Optimize database connections
- **Rate limiting**: Tune based on Gong API limits
- **Caching**: Configure Redis appropriately

### Monitoring Metrics
- Response time percentiles
- Request rate
- Error rates
- Resource utilization
- Queue depth

## Integration Points

### Upstream Services
- **Gong API**: External webhook source
- **Load balancer**: Traffic distribution

### Downstream Services
- **Snowflake**: Data storage
- **Redis**: Background task queue
- **Prometheus**: Metrics collection
- **Slack**: Notification delivery

## Disaster Recovery

### Backup Strategy
- Configuration stored in Git
- Secrets managed by Pulumi ESC
- Data backed up in Snowflake
- Container images in registry

### Recovery Procedures
1. Restore from Git repository
2. Apply Kubernetes manifests
3. Inject secrets from ESC
4. Verify service functionality
5. Resume traffic routing

## Support and Documentation

### Additional Resources
- [Gong API Documentation](https://us-66463.app.gong.io/settings/api/documentation)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Pulumi ESC Documentation](https://www.pulumi.com/docs/esc/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

### Contact Information
- **Team**: Sophia AI Platform Team
- **Repository**: `sophia-main`
- **Monitoring**: Grafana dashboards
- **Alerts**: Prometheus AlertManager 