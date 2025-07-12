import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";

// Import deployment configurations
import * as weaviate from "./weaviate-deployment";
import * as redis from "./redis-deployment";
import * as postgresql from "./postgresql-deployment";

// Configuration
const config = new pulumi.Config();
const stack = pulumi.getStack();
const namespace = stack === "prod" ? "sophia-ai-prod" : `sophia-ai-${stack}`;

// Create namespace
const ns = new k8s.core.v1.Namespace("sophia-ai-namespace", {
    metadata: {
        name: namespace,
        labels: {
            environment: stack,
            "app.kubernetes.io/managed-by": "pulumi"
        }
    }
});

// Create secrets from Pulumi ESC
const weaviateAuthSecret = new k8s.core.v1.Secret("weaviate-auth", {
    metadata: { namespace },
    stringData: {
        "oidc-issuer": config.requireSecret("WEAVIATE_OIDC_ISSUER"),
        "client-id": config.requireSecret("WEAVIATE_CLIENT_ID"),
        "admin-users": config.requireSecret("WEAVIATE_ADMIN_USERS")
    }
});

const redisAuthSecret = new k8s.core.v1.Secret("redis-auth", {
    metadata: { namespace },
    stringData: {
        "password": config.requireSecret("REDIS_PASSWORD")
    }
});

const postgresqlAuthSecret = new k8s.core.v1.Secret("postgresql-auth", {
    metadata: { namespace },
    stringData: {
        "password": config.requireSecret("POSTGRESQL_PASSWORD")
    }
});

// Lambda Inference Service deployment
const lambdaInferenceDeployment = new k8s.apps.v1.Deployment("lambda-inference", {
    metadata: { namespace },
    spec: {
        replicas: 2,
        selector: { matchLabels: { app: "lambda-inference" } },
        template: {
            metadata: {
                labels: {
                    app: "lambda-inference",
                    component: "inference",
                    tier: "compute"
                }
            },
            spec: {
                nodeSelector: {
                    "beta.kubernetes.io/instance-type": "gpu",
                    "node.kubernetes.io/gpu-vendor": "nvidia"
                },
                tolerations: [{
                    key: "nvidia.com/gpu",
                    operator: "Exists",
                    effect: "NoSchedule"
                }],
                containers: [{
                    name: "inference",
                    image: "scoobyjava15/lambda-inference:latest",
                    resources: {
                        requests: {
                            "nvidia.com/gpu": "1",
                            cpu: "2",
                            memory: "8Gi"
                        },
                        limits: {
                            "nvidia.com/gpu": "1",
                            cpu: "4",
                            memory: "16Gi"
                        }
                    },
                    env: [
                        {
                            name: "PORTKEY_API_KEY",
                            valueFrom: {
                                secretKeyRef: {
                                    name: "portkey-auth",
                                    key: "api-key"
                                }
                            }
                        }
                    ],
                    ports: [
                        { name: "http", containerPort: 8080 }
                    ],
                    livenessProbe: {
                        httpGet: {
                            path: "/health",
                            port: 8080
                        },
                        initialDelaySeconds: 60,
                        periodSeconds: 10
                    },
                    readinessProbe: {
                        httpGet: {
                            path: "/health",
                            port: 8080
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 5
                    }
                }]
            }
        }
    }
});

const lambdaInferenceService = new k8s.core.v1.Service("lambda-inference-service", {
    metadata: { namespace },
    spec: {
        selector: { app: "lambda-inference" },
        type: "ClusterIP",
        ports: [
            { name: "http", port: 8080, targetPort: 8080 }
        ]
    }
});

// GPU Resource Quotas
const gpuResourceQuota = new k8s.core.v1.ResourceQuota("gpu-quota", {
    metadata: { namespace },
    spec: {
        hard: {
            "requests.nvidia.com/gpu": "8",  // Limit total GPU requests
            "limits.nvidia.com/gpu": "8"
        }
    }
});

// Monitoring Configuration
const prometheusConfig = new k8s.core.v1.ConfigMap("prometheus-config", {
    metadata: { namespace },
    data: {
        "prometheus.yml": `
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'weaviate'
    static_configs:
      - targets: ['weaviate-service:2112']
    
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
  
  - job_name: 'lambda-inference'
    static_configs:
      - targets: ['lambda-inference-service:8080']
    metrics_path: '/metrics'
`
    }
});

// Alert Rules
const alertRules = new k8s.core.v1.ConfigMap("prometheus-alerts", {
    metadata: { namespace },
    data: {
        "alerts.yml": `
groups:
  - name: sophia-ai-alerts
    interval: 30s
    rules:
      - alert: WeaviateHighQueryLatency
        expr: weaviate_query_seconds_sum > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Weaviate query latency is high"
          description: "Weaviate queries are taking longer than 50ms"
      
      - alert: ETLLatencyHigh
        expr: etl_pipeline_duration_seconds > 0.15
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ETL pipeline latency exceeds 150ms"
          description: "ETL processing is slower than expected target"
      
      - alert: GPUMemoryHigh
        expr: gpu_memory_allocated_gb / gpu_memory_reserved_gb > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "GPU memory usage is critically high"
          description: "GPU memory usage is above 90%"
`
    }
});

// Export stack outputs
export const weaviateEndpoint = pulumi.interpolate`http://${weaviate.weaviateService.metadata.name}.${namespace}.svc.cluster.local:8080`;
export const redisEndpoint = pulumi.interpolate`redis://${redis.redisService.metadata.name}.${namespace}.svc.cluster.local:6379`;
export const postgresqlEndpoint = pulumi.interpolate`postgresql://${postgresql.postgresqlService.metadata.name}.${namespace}.svc.cluster.local:5432/sophia_vectors`;
export const lambdaInferenceEndpoint = pulumi.interpolate`http://${lambdaInferenceService.metadata.name}.${namespace}.svc.cluster.local:8080`;

// Stack information
export const stackInfo = {
    namespace: namespace,
    stack: stack,
    deployments: {
        weaviate: weaviate.weaviateDeployment.metadata.name,
        redis: redis.redisStatefulSet.metadata.name,
        postgresql: postgresql.postgresqlDeployment.metadata.name,
        lambdaInference: lambdaInferenceDeployment.metadata.name
    },
    services: {
        weaviate: weaviate.weaviateService.metadata.name,
        redis: redis.redisService.metadata.name,
        postgresql: postgresql.postgresqlService.metadata.name,
        lambdaInference: lambdaInferenceService.metadata.name
    }
}; 