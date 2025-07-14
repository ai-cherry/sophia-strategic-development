import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const namespace = "sophia-ai-prod";

// Redis StatefulSet with Sentinel for HA
export const redisStatefulSet = new k8s.apps.v1.StatefulSet("redis", {
    metadata: { 
        namespace,
        labels: {
            app: "redis",
            component: "cache",
            tier: "data"
        }
    },
    spec: {
        serviceName: "redis-headless",
        replicas: 3,
        selector: { matchLabels: { app: "redis" } },
        template: {
            metadata: { 
                labels: { 
                    app: "redis",
                    version: "7.2"
                } 
            },
            spec: {
                affinity: {
                    podAntiAffinity: {
                        requiredDuringSchedulingIgnoredDuringExecution: [{
                            labelSelector: {
                                matchExpressions: [{
                                    key: "app",
                                    operator: "In",
                                    values: ["redis"]
                                }]
                            },
                            topologyKey: "kubernetes.io/hostname"
                        }]
                    }
                },
                containers: [{
                    name: "redis",
                    image: "redis:7.2-alpine",
                    command: [
                        "redis-server",
                        "/etc/redis/redis.conf"
                    ],
                    resources: {
                        requests: {
                            cpu: "500m",
                            memory: "2Gi"
                        },
                        limits: {
                            cpu: "2",
                            memory: "8Gi"
                        }
                    },
                    env: [
                        {
                            name: "REDIS_PASSWORD",
                            valueFrom: {
                                secretKeyRef: {
                                    name: "redis-auth",
                                    key: "password"
                                }
                            }
                        }
                    ],
                    ports: [
                        { name: "redis", containerPort: 6379 }
                    ],
                    volumeMounts: [
                        {
                            name: "redis-data",
                            mountPath: "/data"
                        },
                        {
                            name: "redis-config",
                            mountPath: "/etc/redis"
                        }
                    ],
                    livenessProbe: {
                        exec: {
                            command: ["redis-cli", "ping"]
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 10
                    },
                    readinessProbe: {
                        exec: {
                            command: ["redis-cli", "ping"]
                        },
                        initialDelaySeconds: 5,
                        periodSeconds: 5
                    }
                }],
                volumes: [{
                    name: "redis-config",
                    configMap: {
                        name: "redis-config"
                    }
                }]
            }
        },
        volumeClaimTemplates: [{
            metadata: {
                name: "redis-data"
            },
            spec: {
                accessModes: ["ReadWriteOnce"],
                storageClassName: "fast-ssd",
                resources: {
                    requests: {
                        storage: "10Gi"
                    }
                }
            }
        }]
    }
});

// Redis Sentinel for HA
export const redisSentinel = new k8s.apps.v1.Deployment("redis-sentinel", {
    metadata: { namespace },
    spec: {
        replicas: 3,
        selector: { matchLabels: { app: "redis-sentinel" } },
        template: {
            metadata: {
                labels: {
                    app: "redis-sentinel"
                }
            },
            spec: {
                affinity: {
                    podAntiAffinity: {
                        requiredDuringSchedulingIgnoredDuringExecution: [{
                            labelSelector: {
                                matchExpressions: [{
                                    key: "app",
                                    operator: "In",
                                    values: ["redis-sentinel"]
                                }]
                            },
                            topologyKey: "kubernetes.io/hostname"
                        }]
                    }
                },
                containers: [{
                    name: "sentinel",
                    image: "redis:7.2-alpine",
                    command: [
                        "redis-sentinel",
                        "/etc/redis-sentinel/sentinel.conf"
                    ],
                    resources: {
                        requests: {
                            cpu: "100m",
                            memory: "256Mi"
                        },
                        limits: {
                            cpu: "500m",
                            memory: "512Mi"
                        }
                    },
                    env: [
                        {
                            name: "REDIS_PASSWORD",
                            valueFrom: {
                                secretKeyRef: {
                                    name: "redis-auth",
                                    key: "password"
                                }
                            }
                        }
                    ],
                    ports: [
                        { name: "sentinel", containerPort: 26379 }
                    ],
                    volumeMounts: [{
                        name: "sentinel-config",
                        mountPath: "/etc/redis-sentinel"
                    }]
                }],
                volumes: [{
                    name: "sentinel-config",
                    configMap: {
                        name: "redis-sentinel-config"
                    }
                }]
            }
        }
    }
});

// Redis Services
export const redisHeadlessService = new k8s.core.v1.Service("redis-headless", {
    metadata: { namespace },
    spec: {
        clusterIP: "None",
        selector: { app: "redis" },
        ports: [
            { name: "redis", port: 6379 }
        ]
    }
});

export const redisService = new k8s.core.v1.Service("redis-service", {
    metadata: { 
        namespace,
        labels: {
            app: "redis",
            component: "cache"
        }
    },
    spec: {
        selector: { app: "redis" },
        type: "ClusterIP",
        ports: [
            { name: "redis", port: 6379, targetPort: 6379 }
        ]
    }
});

// Redis ConfigMap
export const redisConfigMap = new k8s.core.v1.ConfigMap("redis-config", {
    metadata: { namespace },
    data: {
        "redis.conf": `
# Redis configuration for Sophia AI

# Persistence
dir /data
dbfilename dump.rdb
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Memory management
maxmemory 6gb
maxmemory-policy allkeys-lru

# Security
requirepass $(REDIS_PASSWORD)
protected-mode yes

# Performance tuning
tcp-backlog 511
timeout 0
tcp-keepalive 300

# Snapshotting
save 900 1
save 300 10
save 60 10000

# Replication
replica-read-only yes

# Logging
loglevel notice
logfile ""

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Advanced config
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000

# Threading
io-threads 4
io-threads-do-reads yes

# Modules
loadmodule /usr/lib/redis/modules/redisbloom.so
`
    }
});

// Redis Sentinel ConfigMap
export const redisSentinelConfigMap = new k8s.core.v1.ConfigMap("redis-sentinel-config", {
    metadata: { namespace },
    data: {
        "sentinel.conf": `
# Redis Sentinel configuration

port 26379
dir /tmp

sentinel monitor mymaster redis-0.redis-headless.sophia-ai-prod.svc.cluster.local 6379 2
sentinel auth-pass mymaster $(REDIS_PASSWORD)
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000

sentinel announce-ip $(POD_IP)
sentinel announce-port 26379
`
    }
});

// Redis HPA
export const redisHPA = new k8s.autoscaling.v2.HorizontalPodAutoscaler("redis-hpa", {
    metadata: { namespace },
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "StatefulSet",
            name: redisStatefulSet.metadata.name
        },
        minReplicas: 3,
        maxReplicas: 6,
        metrics: [{
            type: "Resource",
            resource: {
                name: "memory",
                target: {
                    type: "Utilization",
                    averageUtilization: 70
                }
            }
        }]
    }
}); 