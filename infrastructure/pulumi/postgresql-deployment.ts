import * as k8s from "@pulumi/kubernetes";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const namespace = "sophia-ai-prod";

// PostgreSQL Deployment with pgvector
export const postgresqlDeployment = new k8s.apps.v1.Deployment("postgresql", {
    metadata: { 
        namespace,
        labels: {
            app: "postgresql",
            component: "database",
            tier: "data"
        }
    },
    spec: {
        replicas: 2, // Primary + Replica
        selector: { matchLabels: { app: "postgresql" } },
        template: {
            metadata: { 
                labels: { 
                    app: "postgresql",
                    version: "16-pgvector"
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
                                    values: ["postgresql"]
                                }]
                            },
                            topologyKey: "kubernetes.io/hostname"
                        }]
                    }
                },
                initContainers: [{
                    name: "init-pgvector",
                    image: "pgvector/pgvector:pg16",
                    command: ["/bin/sh", "-c"],
                    args: [`
set -e
echo "Initializing PostgreSQL with pgvector..."

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
done

# Create database and extensions
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres <<EOF
-- Create sophia_vectors database if not exists
SELECT 'CREATE DATABASE sophia_vectors'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sophia_vectors');
\\gexec

-- Connect to sophia_vectors
\\c sophia_vectors

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For hybrid search
CREATE EXTENSION IF NOT EXISTS btree_gin; -- For compound indexes

-- Create optimized schema
CREATE SCHEMA IF NOT EXISTS knowledge;

-- Create knowledge base table with optimized structure
CREATE TABLE IF NOT EXISTS knowledge.knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    metadata JSONB DEFAULT '{}',
    source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add GIN index for JSONB metadata searches
    CONSTRAINT valid_metadata CHECK (jsonb_typeof(metadata) = 'object')
);

-- Create optimized indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding 
ON knowledge.knowledge_base 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create index for metadata searches
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata 
ON knowledge.knowledge_base 
USING gin (metadata);

-- Create compound index for hybrid searches
CREATE INDEX IF NOT EXISTS idx_knowledge_content_trgm 
ON knowledge.knowledge_base 
USING gin (content gin_trgm_ops);

-- Create index for timestamp queries
CREATE INDEX IF NOT EXISTS idx_knowledge_created 
ON knowledge.knowledge_base (created_at DESC);

-- Set up performance parameters
ALTER SYSTEM SET shared_preload_libraries = 'vector';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET random_page_cost = 1.1; -- SSD optimization

-- Reload configuration
SELECT pg_reload_conf();

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA knowledge TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA knowledge TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA knowledge TO postgres;

EOF

echo "PostgreSQL with pgvector initialized successfully!"
`],
                    env: [{
                        name: "POSTGRES_PASSWORD",
                        valueFrom: {
                            secretKeyRef: {
                                name: "postgresql-auth",
                                key: "password"
                            }
                        }
                    }],
                    volumeMounts: [{
                        name: "postgres-data",
                        mountPath: "/var/lib/postgresql/data"
                    }]
                }],
                containers: [{
                    name: "postgresql",
                    image: "pgvector/pgvector:pg16",
                    resources: {
                        requests: {
                            cpu: "2",
                            memory: "8Gi"
                        },
                        limits: {
                            cpu: "4",
                            memory: "16Gi"
                        }
                    },
                    env: [
                        {
                            name: "POSTGRES_DB",
                            value: "sophia_vectors"
                        },
                        {
                            name: "POSTGRES_USER",
                            value: "postgres"
                        },
                        {
                            name: "POSTGRES_PASSWORD",
                            valueFrom: {
                                secretKeyRef: {
                                    name: "postgresql-auth",
                                    key: "password"
                                }
                            }
                        },
                        {
                            name: "PGDATA",
                            value: "/var/lib/postgresql/data/pgdata"
                        },
                        // Performance tuning
                        {
                            name: "POSTGRES_INIT_ARGS",
                            value: "--encoding=UTF8 --locale=en_US.UTF-8"
                        }
                    ],
                    ports: [
                        { name: "postgresql", containerPort: 5432 }
                    ],
                    volumeMounts: [
                        {
                            name: "postgres-data",
                            mountPath: "/var/lib/postgresql/data"
                        },
                        {
                            name: "postgres-config",
                            mountPath: "/etc/postgresql/postgresql.conf",
                            subPath: "postgresql.conf"
                        }
                    ],
                    livenessProbe: {
                        exec: {
                            command: ["pg_isready", "-U", "postgres"]
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 10
                    },
                    readinessProbe: {
                        exec: {
                            command: ["pg_isready", "-U", "postgres"]
                        },
                        initialDelaySeconds: 5,
                        periodSeconds: 5
                    }
                }],
                volumes: [
                    {
                        name: "postgres-data",
                        persistentVolumeClaim: {
                            claimName: "postgresql-pvc"
                        }
                    },
                    {
                        name: "postgres-config",
                        configMap: {
                            name: "postgresql-config"
                        }
                    }
                ]
            }
        }
    }
});

// PostgreSQL Service
export const postgresqlService = new k8s.core.v1.Service("postgresql-service", {
    metadata: { 
        namespace,
        labels: {
            app: "postgresql",
            component: "database"
        }
    },
    spec: {
        selector: { app: "postgresql" },
        type: "ClusterIP",
        ports: [
            { name: "postgresql", port: 5432, targetPort: 5432 }
        ]
    }
});

// PostgreSQL PVC
export const postgresqlPVC = new k8s.core.v1.PersistentVolumeClaim("postgresql-pvc", {
    metadata: { namespace },
    spec: {
        accessModes: ["ReadWriteOnce"],
        storageClassName: "fast-ssd",
        resources: {
            requests: {
                storage: "200Gi"
            }
        }
    }
});

// PostgreSQL ConfigMap for advanced configuration
export const postgresqlConfigMap = new k8s.core.v1.ConfigMap("postgresql-config", {
    metadata: { namespace },
    data: {
        "postgresql.conf": `
# PostgreSQL configuration optimized for pgvector workloads

# Connection settings
listen_addresses = '*'
port = 5432
max_connections = 200
superuser_reserved_connections = 3

# Memory settings
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 2GB
work_mem = 256MB
wal_buffers = 16MB

# Checkpoint settings
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB

# Planner settings
random_page_cost = 1.1  # SSD optimization
effective_io_concurrency = 200  # SSD optimization
default_statistics_target = 100

# Parallel query settings
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

# pgvector specific
shared_preload_libraries = 'vector'

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_duration = off
log_lock_waits = on
log_statement = 'mod'
log_temp_files = 0

# Autovacuum tuning
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.05

# Replication settings (for future HA)
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/archive/%f && cp %p /var/lib/postgresql/archive/%f'
max_wal_senders = 3
wal_keep_size = 1GB
hot_standby = on
`
    }
});

// PostgreSQL monitoring service
export const postgresqlExporter = new k8s.apps.v1.Deployment("postgres-exporter", {
    metadata: { namespace },
    spec: {
        replicas: 1,
        selector: { matchLabels: { app: "postgres-exporter" } },
        template: {
            metadata: {
                labels: {
                    app: "postgres-exporter"
                }
            },
            spec: {
                containers: [{
                    name: "postgres-exporter",
                    image: "prometheuscommunity/postgres-exporter:v0.15.0",
                    resources: {
                        requests: {
                            cpu: "100m",
                            memory: "128Mi"
                        },
                        limits: {
                            cpu: "500m",
                            memory: "256Mi"
                        }
                    },
                    env: [{
                        name: "DATA_SOURCE_NAME",
                        value: "postgresql://postgres:$(POSTGRES_PASSWORD)@postgresql-service:5432/sophia_vectors?sslmode=disable"
                    }, {
                        name: "POSTGRES_PASSWORD",
                        valueFrom: {
                            secretKeyRef: {
                                name: "postgresql-auth",
                                key: "password"
                            }
                        }
                    }],
                    ports: [
                        { name: "metrics", containerPort: 9187 }
                    ]
                }]
            }
        }
    }
}); 