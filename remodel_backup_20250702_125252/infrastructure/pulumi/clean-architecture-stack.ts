import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import * as docker from "@pulumi/docker";

// Configuration
const config = new pulumi.Config();
const lambdaLabsKubeconfig = config.requireSecret("lambdaLabsKubeconfig");
const dockerRegistry = config.require("dockerRegistry");

// Lambda Labs Kubernetes provider
const lambdaLabsProvider = new k8s.Provider("lambda-labs", {
    kubeconfig: lambdaLabsKubeconfig,
});

// Namespace
const namespace = new k8s.core.v1.Namespace("sophia-ai", {
    metadata: {
        name: "sophia-ai",
    },
}, { provider: lambdaLabsProvider });

// Docker image for Clean Architecture
const sophiaImage = new docker.Image("sophia-clean-arch", {
    imageName: pulumi.interpolate`${dockerRegistry}/sophia-ai:clean-arch-optimized`,
    build: {
        context: "../../",
        dockerfile: "../../Dockerfile.optimized",
        target: "production",
        args: {
            PYTHON_VERSION: "3.11",
            NODE_VERSION: "18",
        },
        cacheFrom: {
            images: [`${dockerRegistry}/sophia-ai:cache`],
        },
    },
    registry: {
        server: dockerRegistry,
        username: config.require("dockerUsername"),
        password: config.requireSecret("dockerPassword"),
    },
});

// Secrets from Pulumi ESC
const sophiaSecrets = new k8s.core.v1.Secret("sophia-api-secrets", {
    metadata: {
        name: "sophia-api-secrets",
        namespace: namespace.metadata.name,
    },
    stringData: {
        "OPENAI_API_KEY": config.requireSecret("openaiApiKey"),
        "ANTHROPIC_API_KEY": config.requireSecret("anthropicApiKey"),
        "PORTKEY_API_KEY": config.requireSecret("portkeyApiKey"),
        "OPENROUTER_API_KEY": config.requireSecret("openrouterApiKey"),
        "GONG_ACCESS_KEY": config.requireSecret("gongAccessKey"),
        "GONG_ACCESS_KEY_SECRET": config.requireSecret("gongAccessKeySecret"),
        "HUBSPOT_ACCESS_TOKEN": config.requireSecret("hubspotAccessToken"),
        "PINECONE_API_KEY": config.requireSecret("pineconeApiKey"),
        "PULUMI_ACCESS_TOKEN": config.requireSecret("pulumiAccessToken"),
    },
}, { provider: lambdaLabsProvider });

// Snowflake secrets
const snowflakeSecrets = new k8s.core.v1.Secret("sophia-snowflake-secrets", {
    metadata: {
        name: "sophia-snowflake-secrets",
        namespace: namespace.metadata.name,
    },
    stringData: {
        "account": config.requireSecret("snowflakeAccount"),
        "username": config.requireSecret("snowflakeUsername"),
        "password": config.requireSecret("snowflakePassword"),
        "warehouse": "SOPHIA_AI_WH",
        "database": "SOPHIA_AI_PROD",
        "schema": "PRODUCTION",
    },
}, { provider: lambdaLabsProvider });

// ConfigMap for application configuration
const configMap = new k8s.core.v1.ConfigMap("sophia-api-config", {
    metadata: {
        name: "sophia-api-config",
        namespace: namespace.metadata.name,
    },
    data: {
        "app_config.yaml": `
# Clean Architecture Configuration
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  
snowflake:
  warehouse: "SOPHIA_AI_WH"
  role: "SOPHIA_AI_ROLE"
  schema: "PRODUCTION"
  
portkey:
  base_url: "https://api.portkey.ai/v1"
  default_model: "gpt-4"
  
estuary:
  connector: "sophia-ai-production"
  
ml:
  model_cache_dir: "/app/models"
  enable_gpu: true
  batch_size: 32
`,
    },
}, { provider: lambdaLabsProvider });

// PersistentVolumeClaim for model cache
const modelCachePVC = new k8s.core.v1.PersistentVolumeClaim("sophia-model-cache", {
    metadata: {
        name: "sophia-model-cache",
        namespace: namespace.metadata.name,
    },
    spec: {
        accessModes: ["ReadWriteMany"],
        resources: {
            requests: {
                storage: "50Gi",
            },
        },
        storageClassName: "lambda-labs-ssd",
    },
}, { provider: lambdaLabsProvider });

// Service Account
const serviceAccount = new k8s.core.v1.ServiceAccount("sophia-api", {
    metadata: {
        name: "sophia-api",
        namespace: namespace.metadata.name,
    },
}, { provider: lambdaLabsProvider });

// Deployment
const deployment = new k8s.apps.v1.Deployment("sophia-api-clean-arch", {
    metadata: {
        name: "sophia-api-clean-arch",
        namespace: namespace.metadata.name,
        labels: {
            app: "sophia-api",
            architecture: "clean",
            environment: "production",
        },
    },
    spec: {
        replicas: 3,
        selector: {
            matchLabels: {
                app: "sophia-api",
                architecture: "clean",
            },
        },
        template: {
            metadata: {
                labels: {
                    app: "sophia-api",
                    architecture: "clean",
                    environment: "production",
                },
            },
            spec: {
                serviceAccountName: serviceAccount.metadata.name,
                nodeSelector: {
                    "lambdalabs.com/gpu-type": "rtx-4090",
                },
                containers: [{
                    name: "sophia-api",
                    image: sophiaImage.imageName,
                    ports: [{
                        containerPort: 8000,
                        name: "http",
                    }],
                    envFrom: [{
                        secretRef: {
                            name: sophiaSecrets.metadata.name,
                        },
                    }],
                    env: [
                        { name: "ENVIRONMENT", value: "prod" },
                        { name: "PULUMI_ORG", value: "scoobyjava-org" },
                        {
                            name: "SNOWFLAKE_ACCOUNT",
                            valueFrom: {
                                secretKeyRef: {
                                    name: snowflakeSecrets.metadata.name,
                                    key: "account",
                                },
                            },
                        },
                        { name: "SNOWFLAKE_DATABASE", value: "SOPHIA_AI_PROD" },
                    ],
                    resources: {
                        requests: {
                            memory: "4Gi",
                            cpu: "2",
                            "nvidia.com/gpu": "1",
                        },
                        limits: {
                            memory: "8Gi",
                            cpu: "4",
                            "nvidia.com/gpu": "1",
                        },
                    },
                    livenessProbe: {
                        httpGet: {
                            path: "/health",
                            port: "http",
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 10,
                    },
                    readinessProbe: {
                        httpGet: {
                            path: "/ready",
                            port: "http",
                        },
                        initialDelaySeconds: 20,
                        periodSeconds: 5,
                    },
                    volumeMounts: [
                        {
                            name: "model-cache",
                            mountPath: "/app/models",
                        },
                        {
                            name: "config",
                            mountPath: "/app/config",
                            readOnly: true,
                        },
                    ],
                }],
                volumes: [
                    {
                        name: "model-cache",
                        persistentVolumeClaim: {
                            claimName: modelCachePVC.metadata.name,
                        },
                    },
                    {
                        name: "config",
                        configMap: {
                            name: configMap.metadata.name,
                        },
                    },
                ],
            },
        },
    },
}, { provider: lambdaLabsProvider });

// Service
const service = new k8s.core.v1.Service("sophia-api-service", {
    metadata: {
        name: "sophia-api-service",
        namespace: namespace.metadata.name,
        labels: {
            app: "sophia-api",
            architecture: "clean",
        },
    },
    spec: {
        type: "ClusterIP",
        ports: [{
            port: 80,
            targetPort: 8000,
            protocol: "TCP",
            name: "http",
        }],
        selector: {
            app: "sophia-api",
            architecture: "clean",
        },
    },
}, { provider: lambdaLabsProvider });

// HorizontalPodAutoscaler
const hpa = new k8s.autoscaling.v2.HorizontalPodAutoscaler("sophia-api-hpa", {
    metadata: {
        name: "sophia-api-hpa",
        namespace: namespace.metadata.name,
    },
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "Deployment",
            name: deployment.metadata.name,
        },
        minReplicas: 3,
        maxReplicas: 10,
        metrics: [
            {
                type: "Resource",
                resource: {
                    name: "cpu",
                    target: {
                        type: "Utilization",
                        averageUtilization: 70,
                    },
                },
            },
            {
                type: "Resource",
                resource: {
                    name: "memory",
                    target: {
                        type: "Utilization",
                        averageUtilization: 80,
                    },
                },
            },
        ],
    },
}, { provider: lambdaLabsProvider });

// Exports
export const namespaceName = namespace.metadata.name;
export const deploymentName = deployment.metadata.name;
export const serviceName = service.metadata.name;
export const serviceEndpoint = pulumi.interpolate`http://${service.metadata.name}.${namespace.metadata.name}.svc.cluster.local`;
export const imageUri = sophiaImage.imageName; 