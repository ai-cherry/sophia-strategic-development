import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const namespace = "sophia-ai-prod";

// Weaviate Deployment with GPU support and HA
export const weaviateDeployment = new k8s.apps.v1.Deployment("weaviate", {
    metadata: { 
        namespace,
        labels: {
            app: "weaviate",
            component: "vector-database",
            tier: "data"
        }
    },
    spec: {
        replicas: 3, // HA configuration
        selector: { matchLabels: { app: "weaviate" } },
        template: {
            metadata: { 
                labels: { 
                    app: "weaviate",
                    version: "1.25.4"
                } 
            },
            spec: {
                nodeSelector: { 
                    "beta.kubernetes.io/instance-type": "gpu",
                    "node.kubernetes.io/gpu-vendor": "nvidia"
                },
                tolerations: [
                    { 
                        key: "nvidia.com/gpu", 
                        operator: "Exists",
                        effect: "NoSchedule"
                    }
                ],
                affinity: {
                    podAntiAffinity: {
                        preferredDuringSchedulingIgnoredDuringExecution: [{
                            weight: 100,
                            podAffinityTerm: {
                                labelSelector: {
                                    matchExpressions: [{
                                        key: "app",
                                        operator: "In",
                                        values: ["weaviate"]
                                    }]
                                },
                                topologyKey: "kubernetes.io/hostname"
                            }
                        }]
                    }
                },
                containers: [{
                    name: "weaviate",
                    image: "semitechnologies/weaviate:1.25.4",
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
                        { name: "ENABLE_MODULES", value: "text2vec-transformers,text2vec-contextionary,ref2vec-centroid" },
                        { name: "TRANSFORMERS_INFERENCE_API", value: "http://lambda-inference-service.sophia-ai-prod:8080" },
                        { name: "DEFAULT_VECTORIZER_MODULE", value: "text2vec-transformers" },
                        { name: "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED", value: "false" },
                        { name: "AUTHENTICATION_OIDC_ENABLED", value: "true" },
                        { name: "AUTHENTICATION_OIDC_ISSUER", valueFrom: { secretKeyRef: { name: "weaviate-auth", key: "oidc-issuer" } } },
                        { name: "AUTHENTICATION_OIDC_CLIENT_ID", valueFrom: { secretKeyRef: { name: "weaviate-auth", key: "client-id" } } },
                        { name: "AUTHORIZATION_ADMINLIST_ENABLED", value: "true" },
                        { name: "AUTHORIZATION_ADMINLIST_USERS", valueFrom: { secretKeyRef: { name: "weaviate-auth", key: "admin-users" } } },
                        { name: "PERSISTENCE_DATA_PATH", value: "/var/lib/weaviate" },
                        { name: "CLUSTER_HOSTNAME", value: "weaviate-cluster" },
                        { name: "CLUSTER_GOSSIP_BIND_PORT", value: "7946" },
                        { name: "CLUSTER_DATA_BIND_PORT", value: "7947" },
                        { name: "PROMETHEUS_MONITORING_ENABLED", value: "true" },
                        { name: "PROMETHEUS_MONITORING_GROUP", value: "true" },
                        // Performance tuning
                        { name: "QUERY_DEFAULTS_LIMIT", value: "100" },
                        { name: "QUERY_MAXIMUM_RESULTS", value: "10000" },
                        { name: "TRACK_VECTOR_DIMENSIONS", value: "true" },
                        // GPU optimizations
                        { name: "CUDA_VISIBLE_DEVICES", value: "0" },
                        { name: "CUDA_CORE_COUNT", value: "16384" }  // B200 specs
                    ],
                    ports: [
                        { name: "http", containerPort: 8080 },
                        { name: "grpc", containerPort: 50051 },
                        { name: "metrics", containerPort: 2112 },
                        { name: "gossip", containerPort: 7946 },
                        { name: "data", containerPort: 7947 }
                    ],
                    volumeMounts: [{
                        name: "weaviate-data",
                        mountPath: "/var/lib/weaviate"
                    }],
                    livenessProbe: {
                        httpGet: {
                            path: "/v1/.well-known/live",
                            port: 8080
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 10,
                        timeoutSeconds: 3
                    },
                    readinessProbe: {
                        httpGet: {
                            path: "/v1/.well-known/ready",
                            port: 8080
                        },
                        initialDelaySeconds: 10,
                        periodSeconds: 5,
                        timeoutSeconds: 3
                    }
                }],
                volumes: [{
                    name: "weaviate-data",
                    persistentVolumeClaim: {
                        claimName: "weaviate-pvc"
                    }
                }]
            }
        }
    }
});

// Weaviate Service
export const weaviateService = new k8s.core.v1.Service("weaviate-service", {
    metadata: { 
        namespace,
        labels: {
            app: "weaviate",
            component: "vector-database"
        }
    },
    spec: {
        selector: { app: "weaviate" },
        type: "ClusterIP",
        ports: [
            { name: "http", port: 8080, targetPort: 8080 },
            { name: "grpc", port: 50051, targetPort: 50051 },
            { name: "metrics", port: 2112, targetPort: 2112 }
        ]
    }
});

// HPA for Weaviate
export const weaviateHPA = new k8s.autoscaling.v2.HorizontalPodAutoscaler("weaviate-hpa", {
    metadata: { namespace },
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "Deployment",
            name: weaviateDeployment.metadata.name
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
                        averageUtilization: 80
                    }
                }
            },
            {
                type: "Resource",
                resource: {
                    name: "memory",
                    target: {
                        type: "Utilization",
                        averageUtilization: 75
                    }
                }
            }
        ],
        behavior: {
            scaleUp: {
                stabilizationWindowSeconds: 60,
                policies: [{
                    type: "Percent",
                    value: 50,
                    periodSeconds: 60
                }]
            },
            scaleDown: {
                stabilizationWindowSeconds: 300,
                policies: [{
                    type: "Percent",
                    value: 10,
                    periodSeconds: 60
                }]
            }
        }
    }
});

// PVC for Weaviate
export const weaviatePVC = new k8s.core.v1.PersistentVolumeClaim("weaviate-pvc", {
    metadata: { namespace },
    spec: {
        accessModes: ["ReadWriteOnce"],
        storageClassName: "fast-ssd",
        resources: {
            requests: {
                storage: "100Gi"
            }
        }
    }
}); 