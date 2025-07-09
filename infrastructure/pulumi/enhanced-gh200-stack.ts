import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import * as docker from "@pulumi/docker";

// Configuration
const config = new pulumi.Config();
const lambdaLabsKubeconfig = config.requireSecret("lambdaLabsKubeconfig");
const dockerRegistry = config.require("dockerRegistry");

// Lambda Labs Kubernetes provider with H200 optimization
const lambdaLabsProvider = new k8s.Provider("lambda-labs-h200", {
    kubeconfig: lambdaLabsKubeconfig,
});

// Namespace with enhanced labeling
const namespace = new k8s.core.v1.Namespace("sophia-ai-enhanced", {
    metadata: {
        name: "sophia-ai-enhanced",
        labels: {
            "sophia.ai/gpu-tier": "h200",
            "sophia.ai/memory-architecture": "6-tier",
            "sophia.ai/snowflake-integration": "enabled",
        },
    },
}, { provider: lambdaLabsProvider });

// Enhanced Docker image for GGH200 GPU optimization
const sophiaEnhancedImage = new docker.Image("sophia-h200-optimized", {
    imageName: pulumi.interpolate`${dockerRegistry}/sophia-ai:h200-optimized`,
    build: {
        context: "../../",
        dockerfile: "../../Dockerfile.gh200",
        target: "production",
        args: {
            PYTHON_VERSION: "3.11",
            NODE_VERSION: "18",
            CUDA_VERSION: "12.3",
            GPU_ARCHITECTURE: "h200",
            GPU_MEMORY: "96GB",
        },
        cacheFrom: {
            images: [`${dockerRegistry}/sophia-ai:h200-cache`],
        },
    },
    registry: {
        server: dockerRegistry,
        username: config.require("dockerUsername"),
        password: config.requireSecret("dockerToken"),
    },
});

// Enhanced secrets configuration
const sophiaEnhancedSecrets = new k8s.core.v1.Secret("sophia-enhanced-secrets", {
    metadata: {
        name: "sophia-enhanced-secrets",
        namespace: namespace.metadata.name,
    },
    stringData: {
        // AI/LLM APIs
        "OPENAI_API_KEY": config.requireSecret("openaiApiKey"),
        "ANTHROPIC_API_KEY": config.requireSecret("anthropicApiKey"),
        "PORTKEY_API_KEY": config.requireSecret("portkeyApiKey"),
        "OPENROUTER_API_KEY": config.requireSecret("openrouterApiKey"),

        // Business Intelligence
        "GONG_ACCESS_KEY": config.requireSecret("gongAccessKey"),
        "GONG_ACCESS_KEY_SECRET": config.requireSecret("gongAccessKeySecret"),
        "HUBSPOT_ACCESS_TOKEN": config.requireSecret("hubspotAccessToken"),
        "SLACK_BOT_TOKEN": config.requireSecret("slackBotToken"),
        "LINEAR_API_KEY": config.requireSecret("linearApiKey"),

        // Infrastructure
        "LAMBDA_LABS_API_KEY": config.requireSecret("lambdaLabsApiKey"),
        "PINECONE_API_KEY": config.requireSecret("pineconeApiKey"),
        "PULUMI_ACCESS_TOKEN": config.requireSecret("pulumiAccessToken"),

        // Enhanced GPU configuration
        "GPU_MEMORY_POOL_SIZE": "96GB",
        "GPU_INFERENCE_CACHE_SIZE": "40GB",
        "GPU_MODEL_CACHE_SIZE": "60GB",
        "GPU_VECTOR_CACHE_SIZE": "30GB",
    },
}, { provider: lambdaLabsProvider });

// Snowflake secrets with enhanced configuration
const snowflakeEnhancedSecrets = new k8s.core.v1.Secret("sophia-snowflake-enhanced", {
    metadata: {
        name: "sophia-snowflake-enhanced",
        namespace: namespace.metadata.name,
    },
    stringData: {
        "account": config.requireSecret("snowflakeAccount"),
        "username": config.requireSecret("snowflakeUsername"),
        "password": config.requireSecret("snowflakePassword"),
        "warehouse": "SOPHIA_AI_COMPUTE_WH",
        "database": "SOPHIA_AI_PRODUCTION",
        "schema": "PRODUCTION",
        "role": "SOPHIA_AI_ROLE",
        // Enhanced Cortex configuration
        "cortex_warehouse": "SOPHIA_AI_CORTEX_WH",
        "cortex_compute_tier": "MEDIUM",
        "gpu_acceleration": "true",
        "lambda_labs_integration": "enabled",
    },
}, { provider: lambdaLabsProvider });

// Enhanced ConfigMap with 6-tier memory architecture
const enhancedConfigMap = new k8s.core.v1.ConfigMap("sophia-enhanced-config", {
    metadata: {
        name: "sophia-enhanced-config",
        namespace: namespace.metadata.name,
    },
    data: {
        "app_config.yaml": `
# Enhanced Sophia AI Configuration - GGH200 GPU Optimization
server:
  host: "0.0.0.0"
  port: 8000
  workers: 6  # Increased for H200 capabilities

# Snowflake Cortex Configuration
snowflake:
  warehouse: "SOPHIA_AI_COMPUTE_WH"
  cortex_warehouse: "SOPHIA_AI_CORTEX_WH"
  role: "SOPHIA_AI_ROLE"
  schema: "PRODUCTION"
  cortex_integration: true
  gpu_acceleration: true

# 6-Tier Memory Architecture
memory_architecture:
  l0_gpu_memory:
    size: "96GB"
    latency: "<10ms"
    type: "HBM3e"
    pools:
      active_models: "60GB"
      inference_cache: "40GB"
      vector_cache: "30GB"
      buffer: "11GB"

  l1_session_cache:
    size: "16GB"
    latency: "<50ms"
    type: "Redis"
    eviction_policy: "allkeys-lru"

  l2_cortex_cache:
    size: "unlimited"
    latency: "<100ms"
    type: "Snowflake"
    gpu_acceleration: true

  l3_persistent_memory:
    size: "unlimited"
    latency: "<200ms"
    type: "Snowflake"
    tables: ["SOPHIA_AI_MEMORY.MEMORY_RECORDS"]

  l4_knowledge_graph:
    size: "unlimited"
    latency: "<300ms"
    type: "Snowflake"
    vector_search: true

  l5_workflow_memory:
    size: "unlimited"
    latency: "<400ms"
    type: "Snowflake"
    long_term_storage: true

# LLM Routing Configuration
llm_routing:
  sensitive_data_route: "lambda_labs_local"
  complex_reasoning_route: "external_api"
  simple_tasks_route: "snowflake_cortex"
  cost_optimization: true

# GPU Optimization
gpu:
  type: "H200"
  memory: "96GB"
  bandwidth: "4.8TB/s"
  compute_capability: "9.0"
  tensor_cores: true
  multi_instance: true

# Portkey AI Gateway
portkey:
  base_url: "https://api.portkey.ai/v1"
  default_model: "gpt-4"
  cost_tracking: true
  fallback_enabled: true

# Estuary Flow Integration
estuary:
  connector: "sophia-ai-production-enhanced"
  parallel_processing: true
  gpu_acceleration: true

# Machine Learning Configuration
ml:
  model_cache_dir: "/app/models"
  enable_gpu: true
  batch_size: 64  # Increased for H200
  mixed_precision: true
  tensor_parallel: true
  gpu_memory_fraction: 0.9
`,
    },
}, { provider: lambdaLabsProvider });

// Enhanced PersistentVolumeClaim for model cache
const enhancedModelCachePVC = new k8s.core.v1.PersistentVolumeClaim("sophia-model-cache-enhanced", {
    metadata: {
        name: "sophia-model-cache-enhanced",
        namespace: namespace.metadata.name,
    },
    spec: {
        accessModes: ["ReadWriteMany"],
        resources: {
            requests: {
                storage: "200Gi",  // Increased for H200 models
            },
        },
        storageClassName: "lambda-labs-nvme",  // Enhanced SSD storage
    },
}, { provider: lambdaLabsProvider });

// GPU Memory PersistentVolumeClaim for L0 tier
const gpuMemoryPVC = new k8s.core.v1.PersistentVolumeClaim("sophia-gpu-memory", {
    metadata: {
        name: "sophia-gpu-memory",
        namespace: namespace.metadata.name,
    },
    spec: {
        accessModes: ["ReadWriteOnce"],
        resources: {
            requests: {
                storage: "100Gi",  // Local NVMe for GPU memory overflow
            },
        },
        storageClassName: "lambda-labs-local-nvme",
    },
}, { provider: lambdaLabsProvider });

// Enhanced Service Account with additional permissions
const enhancedServiceAccount = new k8s.core.v1.ServiceAccount("sophia-enhanced-sa", {
    metadata: {
        name: "sophia-enhanced-sa",
        namespace: namespace.metadata.name,
        annotations: {
            "sophia.ai/gpu-access": "enabled",
            "sophia.ai/snowflake-integration": "enabled",
        },
    },
}, { provider: lambdaLabsProvider });

// Enhanced Deployment with H200 optimization
const enhancedDeployment = new k8s.apps.v1.Deployment("sophia-enhanced-deployment", {
    metadata: {
        name: "sophia-enhanced-deployment",
        namespace: namespace.metadata.name,
        labels: {
            app: "sophia-ai-enhanced",
            "sophia.ai/gpu-tier": "h200",
            "sophia.ai/memory-architecture": "6-tier",
            environment: "production",
        },
    },
    spec: {
        replicas: 3,
        selector: {
            matchLabels: {
                app: "sophia-ai-enhanced",
                "sophia.ai/gpu-tier": "h200",
            },
        },
        template: {
            metadata: {
                labels: {
                    app: "sophia-ai-enhanced",
                    "sophia.ai/gpu-tier": "h200",
                    "sophia.ai/memory-architecture": "6-tier",
                    environment: "production",
                },
            },
            spec: {
                serviceAccountName: enhancedServiceAccount.metadata.name,
                nodeSelector: {
                    "lambdalabs.com/gpu-type": "h200",
                    "lambdalabs.com/gpu-memory": "96GB",
                },
                tolerations: [{
                    key: "nvidia.com/gpu",
                    operator: "Equal",
                    value: "h200",
                    effect: "NoSchedule",
                }],
                containers: [{
                    name: "sophia-ai-enhanced",
                    image: sophiaEnhancedImage.imageName,
                    ports: [{
                        containerPort: 8000,
                        name: "http",
                    }, {
                        containerPort: 8001,
                        name: "gpu-metrics",
                    }],
                    envFrom: [{
                        secretRef: {
                            name: sophiaEnhancedSecrets.metadata.name,
                        },
                    }],
                    env: [
                        { name: "ENVIRONMENT", value: "prod" },
                        { name: "PULUMI_ORG", value: "scoobyjava-org" },
                        { name: "GPU_TIER", value: "h200" },
                        { name: "MEMORY_ARCHITECTURE", value: "6-tier" },
                        {
                            name: "SNOWFLAKE_ACCOUNT",
                            valueFrom: {
                                secretKeyRef: {
                                    name: snowflakeEnhancedSecrets.metadata.name,
                                    key: "account",
                                },
                            },
                        },
                        {
                            name: "SNOWFLAKE_DATABASE",
                            valueFrom: {
                                secretKeyRef: {
                                    name: snowflakeEnhancedSecrets.metadata.name,
                                    key: "database",
                                },
                            },
                        },
                        {
                            name: "SNOWFLAKE_WAREHOUSE",
                            valueFrom: {
                                secretKeyRef: {
                                    name: snowflakeEnhancedSecrets.metadata.name,
                                    key: "warehouse",
                                },
                            },
                        },
                        {
                            name: "SNOWFLAKE_CORTEX_WAREHOUSE",
                            valueFrom: {
                                secretKeyRef: {
                                    name: snowflakeEnhancedSecrets.metadata.name,
                                    key: "cortex_warehouse",
                                },
                            },
                        },
                    ],
                    resources: {
                        requests: {
                            memory: "32Gi",  // Increased for H200 workloads
                            cpu: "8",        // Increased CPU allocation
                            "nvidia.com/gpu": "1",
                        },
                        limits: {
                            memory: "64Gi",  // Increased memory limit
                            cpu: "16",       // Increased CPU limit
                            "nvidia.com/gpu": "1",
                        },
                    },
                    livenessProbe: {
                        httpGet: {
                            path: "/health",
                            port: "http",
                        },
                        initialDelaySeconds: 60,  // Increased for GPU initialization
                        periodSeconds: 15,
                        timeoutSeconds: 10,
                        failureThreshold: 3,
                    },
                    readinessProbe: {
                        httpGet: {
                            path: "/ready",
                            port: "http",
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 10,
                        timeoutSeconds: 5,
                        failureThreshold: 2,
                    },
                    volumeMounts: [
                        {
                            name: "model-cache",
                            mountPath: "/app/models",
                        },
                        {
                            name: "gpu-memory",
                            mountPath: "/app/gpu-memory",
                        },
                        {
                            name: "config",
                            mountPath: "/app/config",
                            readOnly: true,
                        },
                        {
                            name: "dev-shm",
                            mountPath: "/dev/shm",
                        },
                    ],
                }],
                volumes: [
                    {
                        name: "model-cache",
                        persistentVolumeClaim: {
                            claimName: enhancedModelCachePVC.metadata.name,
                        },
                    },
                    {
                        name: "gpu-memory",
                        persistentVolumeClaim: {
                            claimName: gpuMemoryPVC.metadata.name,
                        },
                    },
                    {
                        name: "config",
                        configMap: {
                            name: enhancedConfigMap.metadata.name,
                        },
                    },
                    {
                        name: "dev-shm",
                        emptyDir: {
                            medium: "Memory",
                            sizeLimit: "16Gi",
                        },
                    },
                ],
            },
        },
    },
}, { provider: lambdaLabsProvider });

// Enhanced Service with GPU metrics
const enhancedService = new k8s.core.v1.Service("sophia-enhanced-service", {
    metadata: {
        name: "sophia-enhanced-service",
        namespace: namespace.metadata.name,
        labels: {
            app: "sophia-ai-enhanced",
            "sophia.ai/gpu-tier": "h200",
        },
    },
    spec: {
        type: "ClusterIP",
        ports: [{
            port: 80,
            targetPort: 8000,
            protocol: "TCP",
            name: "http",
        }, {
            port: 8001,
            targetPort: 8001,
            protocol: "TCP",
            name: "gpu-metrics",
        }],
        selector: {
            app: "sophia-ai-enhanced",
            "sophia.ai/gpu-tier": "h200",
        },
    },
}, { provider: lambdaLabsProvider });

// Enhanced HorizontalPodAutoscaler with GPU metrics
const enhancedHPA = new k8s.autoscaling.v2.HorizontalPodAutoscaler("sophia-enhanced-hpa", {
    metadata: {
        name: "sophia-enhanced-hpa",
        namespace: namespace.metadata.name,
    },
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "Deployment",
            name: enhancedDeployment.metadata.name,
        },
        minReplicas: 3,
        maxReplicas: 16,  // Increased for H200 scaling
        metrics: [
            {
                type: "Resource",
                resource: {
                    name: "cpu",
                    target: {
                        type: "Utilization",
                        averageUtilization: 60,  // Lower threshold for GPU workloads
                    },
                },
            },
            {
                type: "Resource",
                resource: {
                    name: "memory",
                    target: {
                        type: "Utilization",
                        averageUtilization: 70,  // Adjusted for larger memory allocation
                    },
                },
            },
        ],
        behavior: {
            scaleUp: {
                stabilizationWindowSeconds: 300,
                policies: [{
                    type: "Percent",
                    value: 100,
                    periodSeconds: 60,
                }],
            },
            scaleDown: {
                stabilizationWindowSeconds: 600,
                policies: [{
                    type: "Percent",
                    value: 50,
                    periodSeconds: 60,
                }],
            },
        },
    },
}, { provider: lambdaLabsProvider });

// GPU monitoring service
const gpuMonitoringService = new k8s.core.v1.Service("gpu-monitoring-service", {
    metadata: {
        name: "gpu-monitoring-service",
        namespace: namespace.metadata.name,
        labels: {
            app: "gpu-monitoring",
        },
    },
    spec: {
        type: "ClusterIP",
        ports: [{
            port: 9090,
            targetPort: 9090,
            protocol: "TCP",
            name: "metrics",
        }],
        selector: {
            app: "sophia-ai-enhanced",
        },
    },
}, { provider: lambdaLabsProvider });

// Exports
export const namespaceName = namespace.metadata.name;
export const enhancedDeploymentName = enhancedDeployment.metadata.name;
export const enhancedServiceName = enhancedService.metadata.name;
export const enhancedServiceEndpoint = pulumi.interpolate`http://${enhancedService.metadata.name}.${namespace.metadata.name}.svc.cluster.local`;
export const enhancedImageUri = sophiaEnhancedImage.imageName;
export const gpuTier = "h200";
export const memoryArchitecture = "6-tier";
export const gpuMemorySize = "96GB";
export const snowflakeIntegration = "enabled";
