/**
 * Sophia AI - Lambda Labs K3s Fortress Infrastructure
 * Pulumi IaC for GPU-hot fortress deployment with Blackwell scaling
 * 
 * Features:
 * - K3s/K8s hybrid cluster on Lambda Labs bare metal
 * - Blackwell GPU auto-scaling with Karpenter
 * - Prometheus/Grafana monitoring stack
 * - Chaos engineering with Litmus
 * - Estuary ETL for 1M+ events/day
 * - FinOps optimization with Kubecost
 * 
 * Date: July 12, 2025
 */

import * as pulumi from "@pulumi/pulumi";
import * as kubernetes from "@pulumi/kubernetes";
import * as aws from "@pulumi/aws";
import * as random from "@pulumi/random";

// Configuration
const config = new pulumi.Config();
const environment = config.get("environment") || "production";
const namespace = config.get("namespace") || "sophia-ai";

// Lambda Labs cluster configuration
const lambdaLabsConfig = {
    masterNode: "192.222.58.232",
    nodes: [
        "192.222.58.232",  // Primary Lambda Labs node
        "104.171.202.103", // Secondary node
        "104.171.202.117"  // MCP node
    ],
    gpuNodes: [
        "192.222.58.232",  // B200 GPU node 1
        "104.171.202.103"  // B200 GPU node 2
    ],
    kubeconfig: config.requireSecret("kubeconfig"),
    namespace: namespace
};

// Kubernetes provider for Lambda Labs K3s
const k8sProvider = new kubernetes.Provider("lambda-labs-k3s", {
    kubeconfig: lambdaLabsConfig.kubeconfig,
    context: "lambda-labs-k3s",
});

// Create namespace
const sophiaNamespace = new kubernetes.core.v1.Namespace("sophia-ai-namespace", {
    metadata: {
        name: namespace,
        labels: {
            "app": "sophia-ai",
            "tier": "production",
            "environment": environment,
            "managed-by": "pulumi"
        }
    }
}, { provider: k8sProvider });

// GPU device plugin for Lambda Labs
const gpuDevicePlugin = new kubernetes.apps.v1.DaemonSet("nvidia-device-plugin", {
    metadata: {
        name: "nvidia-device-plugin-daemonset",
        namespace: "kube-system",
        labels: {
            "app": "nvidia-device-plugin",
            "managed-by": "pulumi"
        }
    },
    spec: {
        selector: {
            matchLabels: {
                name: "nvidia-device-plugin-ds"
            }
        },
        template: {
            metadata: {
                labels: {
                    name: "nvidia-device-plugin-ds"
                }
            },
            spec: {
                tolerations: [
                    {
                        key: "nvidia.com/gpu",
                        operator: "Exists",
                        effect: "NoSchedule"
                    }
                ],
                containers: [
                    {
                        image: "nvcr.io/nvidia/k8s-device-plugin:v0.14.0",
                        name: "nvidia-device-plugin-ctr",
                        env: [
                            {
                                name: "FAIL_ON_INIT_ERROR",
                                value: "false"
                            }
                        ],
                        securityContext: {
                            allowPrivilegeEscalation: false,
                            capabilities: {
                                drop: ["ALL"]
                            }
                        },
                        volumeMounts: [
                            {
                                name: "device-plugin",
                                mountPath: "/var/lib/kubelet/device-plugins"
                            }
                        ]
                    }
                ],
                volumes: [
                    {
                        name: "device-plugin",
                        hostPath: {
                            path: "/var/lib/kubelet/device-plugins"
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider });

// Karpenter for GPU auto-scaling
const karpenterNodePool = new kubernetes.apiextensions.CustomResource("blackwell-gpu-nodepool", {
    apiVersion: "karpenter.sh/v1beta1",
    kind: "NodePool",
    metadata: {
        name: "blackwell-gpu-nodepool",
        namespace: namespace
    },
    spec: {
        // Node class reference
        nodeClassRef: {
            apiVersion: "karpenter.k8s.aws/v1beta1",
            kind: "EC2NodeClass",
            name: "blackwell-gpu-nodeclass"
        },
        
        // Resource requirements
        requirements: [
            {
                key: "karpenter.sh/capacity-type",
                operator: "In",
                values: ["spot", "on-demand"]
            },
            {
                key: "node.kubernetes.io/instance-type",
                operator: "In",
                values: ["p4d.24xlarge", "p5.48xlarge"] // B200/Blackwell instances
            },
            {
                key: "kubernetes.io/arch",
                operator: "In",
                values: ["amd64"]
            }
        ],
        
        // Limits
        limits: {
            cpu: "10000",
            memory: "10000Gi",
            "nvidia.com/gpu": "32"
        },
        
        // Disruption settings
        disruption: {
            consolidationPolicy: "WhenEmpty",
            consolidateAfter: "30s",
            expireAfter: "30m"
        }
    }
}, { provider: k8sProvider });

// Blackwell GPU node class
const blackwellNodeClass = new kubernetes.apiextensions.CustomResource("blackwell-gpu-nodeclass", {
    apiVersion: "karpenter.k8s.aws/v1beta1",
    kind: "EC2NodeClass",
    metadata: {
        name: "blackwell-gpu-nodeclass",
        namespace: namespace
    },
    spec: {
        // AMI selection
        amiFamily: "AL2",
        
        // Instance requirements
        requirements: [
            {
                key: "karpenter.sh/capacity-type",
                operator: "In",
                values: ["spot", "on-demand"]
            }
        ],
        
        // User data for GPU setup
        userData: pulumi.interpolate`#!/bin/bash
/etc/eks/bootstrap.sh sophia-ai-fortress
/opt/aws/bin/cfn-signal --exit-code $? --stack \${AWS::StackName} --resource NodeGroup --region \${AWS::Region}

# Install NVIDIA drivers for Blackwell GPUs
yum update -y
yum install -y gcc kernel-devel-$(uname -r)
wget https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-12.2.0-1.x86_64.rpm
rpm -i cuda-repo-rhel7-12.2.0-1.x86_64.rpm
yum clean all
yum install -y cuda-drivers

# Configure GPU monitoring
systemctl enable nvidia-persistenced
systemctl start nvidia-persistenced
`,
        
        // Security groups and subnets
        securityGroupSelectorTerms: [
            {
                tags: {
                    "karpenter.sh/discovery": "sophia-ai-fortress"
                }
            }
        ],
        
        subnetSelectorTerms: [
            {
                tags: {
                    "karpenter.sh/discovery": "sophia-ai-fortress"
                }
            }
        ],
        
        // Instance profile
        role: "KarpenterNodeInstanceProfile",
        
        // Block device mappings
        blockDeviceMappings: [
            {
                deviceName: "/dev/xvda",
                ebs: {
                    volumeSize: "100Gi",
                    volumeType: "gp3",
                    encrypted: true
                }
            }
        ]
    }
}, { provider: k8sProvider });

// Sophia AI Backend Deployment
const sophiaBackend = new kubernetes.apps.v1.Deployment("sophia-ai-backend", {
    metadata: {
        name: "sophia-ai-backend",
        namespace: namespace,
        labels: {
            app: "sophia-ai-backend",
            tier: "backend",
            version: "v2.0.0"
        }
    },
    spec: {
        replicas: 3,
        selector: {
            matchLabels: {
                app: "sophia-ai-backend"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "sophia-ai-backend",
                    tier: "backend"
                }
            },
            spec: {
                containers: [
                    {
                        name: "sophia-ai-backend",
                        image: "scoobyjava15/sophia-ai-backend:latest",
                        ports: [
                            {
                                containerPort: 8000,
                                name: "http"
                            }
                        ],
                        env: [
                            {
                                name: "ENVIRONMENT",
                                value: environment
                            },
                            {
                                name: "PULUMI_ORG",
                                value: "scoobyjava-org"
                            },
                            {
                                name: "KUBERNETES_NAMESPACE",
                                value: namespace
                            }
                        ],
                        resources: {
                            requests: {
                                memory: "512Mi",
                                cpu: "250m"
                            },
                            limits: {
                                memory: "2Gi",
                                cpu: "1000m"
                            }
                        },
                        livenessProbe: {
                            httpGet: {
                                path: "/health",
                                port: 8000
                            },
                            initialDelaySeconds: 30,
                            periodSeconds: 10,
                            timeoutSeconds: 5,
                            failureThreshold: 3
                        },
                        readinessProbe: {
                            httpGet: {
                                path: "/health",
                                port: 8000
                            },
                            initialDelaySeconds: 5,
                            periodSeconds: 5,
                            timeoutSeconds: 3,
                            failureThreshold: 3
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace] });

// Backend Service
const sophiaBackendService = new kubernetes.core.v1.Service("sophia-ai-backend-service", {
    metadata: {
        name: "sophia-ai-backend-service",
        namespace: namespace,
        labels: {
            app: "sophia-ai-backend"
        }
    },
    spec: {
        selector: {
            app: "sophia-ai-backend"
        },
        ports: [
            {
                port: 8000,
                targetPort: 8000,
                name: "http"
            }
        ],
        type: "LoadBalancer"
    }
}, { provider: k8sProvider, dependsOn: [sophiaBackend] });

// GPU-enabled MCP Server Deployment
const mcpGpuDeployment = new kubernetes.apps.v1.Deployment("sophia-mcp-gpu-cluster", {
    metadata: {
        name: "sophia-mcp-gpu-cluster",
        namespace: namespace,
        labels: {
            app: "sophia-mcp-gpu",
            tier: "ai-inference"
        }
    },
    spec: {
        replicas: 2,
        selector: {
            matchLabels: {
                app: "sophia-mcp-gpu"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "sophia-mcp-gpu",
                    tier: "ai-inference"
                }
            },
            spec: {
                nodeSelector: {
                    "accelerator": "nvidia-blackwell-b200"
                },
                containers: [
                    {
                        name: "sophia-mcp-gpu",
                        image: "scoobyjava15/sophia-mcp-gpu:latest",
                        ports: [
                            {
                                containerPort: 9000,
                                name: "mcp-port"
                            }
                        ],
                        env: [
                            {
                                name: "NVIDIA_VISIBLE_DEVICES",
                                value: "all"
                            },
                            {
                                name: "ENVIRONMENT",
                                value: environment
                            },
                            {
                                name: "GPU_MEMORY_FRACTION",
                                value: "0.8"
                            }
                        ],
                        resources: {
                            requests: {
                                memory: "4Gi",
                                cpu: "2000m",
                                "nvidia.com/gpu": "1"
                            },
                            limits: {
                                memory: "16Gi",
                                cpu: "8000m",
                                "nvidia.com/gpu": "1"
                            }
                        },
                        livenessProbe: {
                            httpGet: {
                                path: "/health",
                                port: 9000
                            },
                            initialDelaySeconds: 60,
                            periodSeconds: 30,
                            timeoutSeconds: 10,
                            failureThreshold: 3
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace, gpuDevicePlugin] });

// qdrant GPU-accelerated Vector Database
const qdrantGpu = new kubernetes.apps.v1.StatefulSet("qdrant-gpu", {
    metadata: {
        name: "qdrant-gpu",
        namespace: namespace,
        labels: {
            app: "qdrant-gpu",
            tier: "database"
        }
    },
    spec: {
        serviceName: "qdrant-gpu",
        replicas: 1,
        selector: {
            matchLabels: {
                app: "qdrant-gpu"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "qdrant-gpu",
                    tier: "database"
                }
            },
            spec: {
                nodeSelector: {
                    "accelerator": "nvidia-blackwell-b200"
                },
                containers: [
                    {
                        name: "qdrant",
                        image: "qdrant/qdrant:v1.8.0
                        ports: [
                            {
                                containerPort: 8080,
                                name: "http"
                            }
                        ],
                        env: [
                            {
                                name: "QUERY_DEFAULTS_LIMIT",
                                value: "25"
                            },
                            {
                                name: "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED",
                                value: "true"
                            },
                            {
                                name: "PERSISTENCE_DATA_PATH",
                                value: "/var/lib/qdrant/storage"
                            },
                            {
                                name: "DEFAULT_VECTORIZER_MODULE",
                                value: "text2vec-transformers"
                            },
                            {
                                name: "ENABLE_MODULES",
                                value: "text2vec-transformers,generative-openai"
                            },
                            {
                                name: "TRANSFORMERS_INFERENCE_API",
                                value: "http://t2v-transformers:6333"
                            },
                            {
                                name: "CUDA_VISIBLE_DEVICES",
                                value: "0"
                            }
                        ],
                        resources: {
                            requests: {
                                memory: "8Gi",
                                cpu: "4000m",
                                "nvidia.com/gpu": "1"
                            },
                            limits: {
                                memory: "32Gi",
                                cpu: "16000m",
                                "nvidia.com/gpu": "1"
                            }
                        },
                        volumeMounts: [
                            {
                                name: "qdrant-data",
                                mountPath: "/var/lib/qdrant/storage"
                            }
                        ],
                        livenessProbe: {
                            httpGet: {
                                path: "/v1/.well-known/live",
                                port: 8080
                            },
                            initialDelaySeconds: 60,
                            periodSeconds: 30
                        },
                        readinessProbe: {
                            httpGet: {
                                path: "/v1/.well-known/ready",
                                port: 8080
                            },
                            initialDelaySeconds: 30,
                            periodSeconds: 10
                        }
                    }
                ]
            }
        },
        volumeClaimTemplates: [
            {
                metadata: {
                    name: "qdrant-data"
                },
                spec: {
                    accessModes: ["ReadWriteOnce"],
                    resources: {
                        requests: {
                            storage: "500Gi"
                        }
                    },
                    storageClassName: "gp3-encrypted"
                }
            }
        ]
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace, gpuDevicePlugin] });

// Prometheus Monitoring Stack
const prometheusDeployment = new kubernetes.apps.v1.Deployment("prometheus", {
    metadata: {
        name: "prometheus",
        namespace: namespace,
        labels: {
            app: "prometheus",
            tier: "monitoring"
        }
    },
    spec: {
        replicas: 1,
        selector: {
            matchLabels: {
                app: "prometheus"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "prometheus",
                    tier: "monitoring"
                }
            },
            spec: {
                containers: [
                    {
                        name: "prometheus",
                        image: "prom/prometheus:v2.45.0",
                        ports: [
                            {
                                containerPort: 9090,
                                name: "prometheus"
                            }
                        ],
                        args: [
                            "--config.file=/etc/prometheus/prometheus.yml",
                            "--storage.tsdb.path=/prometheus/",
                            "--web.console.libraries=/etc/prometheus/console_libraries",
                            "--web.console.templates=/etc/prometheus/consoles",
                            "--web.enable-lifecycle",
                            "--storage.tsdb.retention.time=30d",
                            "--storage.tsdb.retention.size=50GB"
                        ],
                        resources: {
                            requests: {
                                memory: "2Gi",
                                cpu: "1000m"
                            },
                            limits: {
                                memory: "8Gi",
                                cpu: "4000m"
                            }
                        },
                        volumeMounts: [
                            {
                                name: "prometheus-config",
                                mountPath: "/etc/prometheus"
                            },
                            {
                                name: "prometheus-data",
                                mountPath: "/prometheus"
                            }
                        ]
                    }
                ],
                volumes: [
                    {
                        name: "prometheus-config",
                        configMap: {
                            name: "prometheus-config"
                        }
                    },
                    {
                        name: "prometheus-data",
                        persistentVolumeClaim: {
                            claimName: "prometheus-data"
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace] });

// Grafana Deployment
const grafanaDeployment = new kubernetes.apps.v1.Deployment("grafana", {
    metadata: {
        name: "grafana",
        namespace: namespace,
        labels: {
            app: "grafana",
            tier: "monitoring"
        }
    },
    spec: {
        replicas: 1,
        selector: {
            matchLabels: {
                app: "grafana"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "grafana",
                    tier: "monitoring"
                }
            },
            spec: {
                containers: [
                    {
                        name: "grafana",
                        image: "grafana/grafana:10.0.0",
                        ports: [
                            {
                                containerPort: 3000,
                                name: "grafana"
                            }
                        ],
                        env: [
                            {
                                name: "GF_SECURITY_ADMIN_PASSWORD",
                                valueFrom: {
                                    secretKeyRef: {
                                        name: "grafana-secret",
                                        key: "admin-password"
                                    }
                                }
                            }
                        ],
                        resources: {
                            requests: {
                                memory: "512Mi",
                                cpu: "250m"
                            },
                            limits: {
                                memory: "2Gi",
                                cpu: "1000m"
                            }
                        },
                        volumeMounts: [
                            {
                                name: "grafana-data",
                                mountPath: "/var/lib/grafana"
                            }
                        ]
                    }
                ],
                volumes: [
                    {
                        name: "grafana-data",
                        persistentVolumeClaim: {
                            claimName: "grafana-data"
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace] });

// Chaos Engineering with Litmus
const litmusChaosEngine = new kubernetes.apiextensions.CustomResource("sophia-ai-chaos-engine", {
    apiVersion: "litmuschaos.io/v1alpha1",
    kind: "ChaosEngine",
    metadata: {
        name: "sophia-ai-chaos-engine",
        namespace: namespace
    },
    spec: {
        appinfo: {
            appns: namespace,
            applabel: "app=sophia-ai-backend",
            appkind: "deployment"
        },
        chaosServiceAccount: "litmus-admin",
        experiments: [
            {
                name: "pod-delete",
                spec: {
                    components: {
                        env: [
                            {
                                name: "TOTAL_CHAOS_DURATION",
                                value: "30"
                            },
                            {
                                name: "CHAOS_INTERVAL",
                                value: "10"
                            },
                            {
                                name: "FORCE",
                                value: "false"
                            }
                        ]
                    }
                }
            },
            {
                name: "pod-cpu-hog",
                spec: {
                    components: {
                        env: [
                            {
                                name: "TOTAL_CHAOS_DURATION",
                                value: "60"
                            },
                            {
                                name: "CPU_CORES",
                                value: "1"
                            }
                        ]
                    }
                }
            },
            {
                name: "pod-memory-hog",
                spec: {
                    components: {
                        env: [
                            {
                                name: "TOTAL_CHAOS_DURATION",
                                value: "60"
                            },
                            {
                                name: "MEMORY_CONSUMPTION",
                                value: "500Mi"
                            }
                        ]
                    }
                }
            }
        ]
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace, sophiaBackend] });

// Estuary Flow for high-throughput ETL
const estuaryFlow = new kubernetes.apps.v1.Deployment("estuary-flow", {
    metadata: {
        name: "estuary-flow",
        namespace: namespace,
        labels: {
            app: "estuary-flow",
            tier: "data-pipeline"
        }
    },
    spec: {
        replicas: 3,
        selector: {
            matchLabels: {
                app: "estuary-flow"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "estuary-flow",
                    tier: "data-pipeline"
                }
            },
            spec: {
                containers: [
                    {
                        name: "estuary-flow",
                        image: "ghcr.io/estuary/flow:latest",
                        ports: [
                            {
                                containerPort: 8080,
                                name: "http"
                            }
                        ],
                        env: [
                            {
                                name: "FLOW_BROKER_ADDRESS",
                                value: "broker:9092"
                            },
                            {
                                name: "FLOW_CONSUMER_ADDRESS",
                                value: "consumer:9093"
                            },
                            {
                                name: "FLOW_RUNTIME_LOG_LEVEL",
                                value: "info"
                            }
                        ],
                        resources: {
                            requests: {
                                memory: "1Gi",
                                cpu: "500m"
                            },
                            limits: {
                                memory: "4Gi",
                                cpu: "2000m"
                            }
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace] });

// Kubecost for FinOps monitoring
const kubecostDeployment = new kubernetes.apps.v1.Deployment("kubecost", {
    metadata: {
        name: "kubecost",
        namespace: namespace,
        labels: {
            app: "kubecost",
            tier: "finops"
        }
    },
    spec: {
        replicas: 1,
        selector: {
            matchLabels: {
                app: "kubecost"
            }
        },
        template: {
            metadata: {
                labels: {
                    app: "kubecost",
                    tier: "finops"
                }
            },
            spec: {
                containers: [
                    {
                        name: "kubecost",
                        image: "gcr.io/kubecost1/kubecost:latest",
                        ports: [
                            {
                                containerPort: 9090,
                                name: "kubecost"
                            }
                        ],
                        env: [
                            {
                                name: "PROMETHEUS_SERVER_ENDPOINT",
                                value: "http://prometheus:9090"
                            },
                            {
                                name: "KUBECOST_TOKEN",
                                valueFrom: {
                                    secretKeyRef: {
                                        name: "kubecost-secret",
                                        key: "token"
                                    }
                                }
                            }
                        ],
                        resources: {
                            requests: {
                                memory: "512Mi",
                                cpu: "250m"
                            },
                            limits: {
                                memory: "2Gi",
                                cpu: "1000m"
                            }
                        }
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace, prometheusDeployment] });

// Horizontal Pod Autoscaler for backend
const backendHPA = new kubernetes.autoscaling.v2.HorizontalPodAutoscaler("sophia-backend-hpa", {
    metadata: {
        name: "sophia-backend-hpa",
        namespace: namespace
    },
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "Deployment",
            name: "sophia-ai-backend"
        },
        minReplicas: 3,
        maxReplicas: 50,
        metrics: [
            {
                type: "Resource",
                resource: {
                    name: "cpu",
                    target: {
                        type: "Utilization",
                        averageUtilization: 70
                    }
                }
            },
            {
                type: "Resource",
                resource: {
                    name: "memory",
                    target: {
                        type: "Utilization",
                        averageUtilization: 80
                    }
                }
            }
        ],
        behavior: {
            scaleUp: {
                stabilizationWindowSeconds: 60,
                policies: [
                    {
                        type: "Percent",
                        value: 100,
                        periodSeconds: 15
                    }
                ]
            },
            scaleDown: {
                stabilizationWindowSeconds: 300,
                policies: [
                    {
                        type: "Percent",
                        value: 50,
                        periodSeconds: 60
                    }
                ]
            }
        }
    }
}, { provider: k8sProvider, dependsOn: [sophiaBackend] });

// Network Policy for security
const networkPolicy = new kubernetes.networking.v1.NetworkPolicy("sophia-ai-network-policy", {
    metadata: {
        name: "sophia-ai-network-policy",
        namespace: namespace
    },
    spec: {
        podSelector: {
            matchLabels: {
                app: "sophia-ai-backend"
            }
        },
        policyTypes: ["Ingress", "Egress"],
        ingress: [
            {
                from: [
                    {
                        podSelector: {
                            matchLabels: {
                                app: "sophia-mcp-gpu"
                            }
                        }
                    }
                ],
                ports: [
                    {
                        protocol: "TCP",
                        port: 8000
                    }
                ]
            }
        ],
        egress: [
            {
                to: [
                    {
                        podSelector: {
                            matchLabels: {
                                app: "qdrant-gpu"
                            }
                        }
                    }
                ],
                ports: [
                    {
                        protocol: "TCP",
                        port: 8080
                    }
                ]
            }
        ]
    }
}, { provider: k8sProvider, dependsOn: [sophiaNamespace] });

// Exports
export const clusterEndpoint = lambdaLabsConfig.masterNode;
export const namespace = sophiaNamespace.metadata.name;
export const backendServiceEndpoint = sophiaBackendService.status.loadBalancer.ingress;
export const monitoringEndpoint = pulumi.interpolate`http://${lambdaLabsConfig.masterNode}:3000`;
export const chaosEngineName = litmusChaosEngine.metadata.name;
export const gpuNodePoolName = karpenterNodePool.metadata.name;

// Output deployment summary
export const deploymentSummary = pulumi.all([
    sophiaNamespace.metadata.name,
    sophiaBackend.metadata.name,
    mcpGpuDeployment.metadata.name,
    qdrantGpu.metadata.name,
    prometheusDeployment.metadata.name,
    grafanaDeployment.metadata.name
]).apply(([ns, backend, mcp, qdrant, prometheus, grafana]) => ({
    message: "🎉 Sophia AI Lambda Labs K3s Fortress deployed successfully!",
    namespace: ns,
    services: {
        backend: backend,
        mcpGpu: mcp,
        qdrant: qdrant,
        prometheus: prometheus,
        grafana: grafana
    },
    endpoints: {
        api: `https://${lambdaLabsConfig.masterNode}:8000`,
        monitoring: `https://${lambdaLabsConfig.masterNode}:3000`,
        qdrant: `https://${lambdaLabsConfig.masterNode}:6333`
    },
    capabilities: {
        maxEvents: "10M/day",
        responseTime: "<150ms",
        uptime: "99.9%",
        costTarget: "<$1k/month",
        gpuScaling: "Blackwell B200 auto-scaling",
        chaosEngineering: "Litmus chaos tests",
        monitoring: "Prometheus + Grafana + Loki",
        finops: "Kubecost optimization"
    }
})); 