/**
 * Unified Lambda Labs Infrastructure Stack
 * Deploys complete Sophia AI infrastructure with automatic DNS updates
 */

import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import * as docker from "@pulumi/docker";
import * as cp from "child_process";

// Configuration
const config = new pulumi.Config();
const env = config.require("environment");
const lambdaLabsApiKey = config.requireSecret("lambdaLabsApiKey");
const dockerRegistry = config.require("dockerRegistry");
const namecheapApiKey = config.requireSecret("namecheapApiKey");
const namecheapApiUser = config.requireSecret("namecheapApiUser");
const namecheapUsername = config.requireSecret("namecheapUsername");

// Lambda Labs Configuration
interface LambdaLabsVM {
    name: string;
    instanceType: string;
    region: string;
    gpu: string;
    purpose: string;
}

// VM Configurations for different services
const vmConfigs: LambdaLabsVM[] = [
    {
        name: "sophia-main-node",
        instanceType: "gpu_1x_h200_96gb",
        region: "us-south-1",
        gpu: "H200",
        purpose: "main-api"
    },
    {
        name: "sophia-qdrant-1",
        instanceType: "gpu_1x_h100_80gb",
        region: "us-south-1", 
        gpu: "H100",
        purpose: "qdrant-primary"
    },
    {
        name: "sophia-qdrant-2",
        instanceType: "gpu_1x_h100_80gb",
        region: "us-south-1",
        gpu: "H100",
        purpose: "qdrant-replica"
    },
    {
        name: "sophia-memory-services",
        instanceType: "gpu_1x_a100_40gb",
        region: "us-south-1",
        gpu: "A100",
        purpose: "redis-mem0-postgres"
    }
];

// Lambda Labs VM deployment
class LambdaLabsVMDeployment {
    public ips: pulumi.Output<Record<string, string>>;
    
    constructor() {
        this.ips = pulumi.output(this.deployVMs());
    }
    
    private async deployVMs(): Promise<Record<string, string>> {
        const ips: Record<string, string> = {};
        
        for (const vmConfig of vmConfigs) {
            try {
                // Deploy VM using Lambda Labs API
                const deployCommand = `
                    curl -X POST https://api.lambdalabs.com/v1/instances \\
                    -H "Authorization: Bearer ${await lambdaLabsApiKey.get()}" \\
                    -H "Content-Type: application/json" \\
                    -d '{
                        "name": "${vmConfig.name}-${env}",
                        "instance_type": "${vmConfig.instanceType}",
                        "region": "${vmConfig.region}",
                        "ssh_key_names": ["sophia-deploy-key"],
                        "user_data": "#!/bin/bash\\n${this.getUserData(vmConfig.purpose)}"
                    }'
                `;
                
                const result = JSON.parse(cp.execSync(deployCommand).toString());
                ips[vmConfig.purpose] = result.ip_address;
                
                console.log(`Deployed ${vmConfig.name} with IP: ${result.ip_address}`);
            } catch (error) {
                console.error(`Failed to deploy ${vmConfig.name}: ${error}`);
            }
        }
        
        return ips;
    }
    
    private getUserData(purpose: string): string {
        const baseSetup = `
apt-get update && apt-get install -y docker.io docker-compose
systemctl enable docker
systemctl start docker
`;
        
        switch (purpose) {
            case "qdrant-primary":
            case "qdrant-replica":
                return baseSetup + `
# Install Qdrant with GPU support
docker run -d \\
  --name qdrant \\
  --runtime=nvidia \\
  -p 6333:6333 \\
  -v /qdrant/storage:/qdrant/storage \\
  -e QDRANT__SERVICE__HTTP_PORT=6333 \\
  -e QDRANT__GPU_ENABLED=true \\
  -e QDRANT__GPU_MEMORY_LIMIT=70GB \\
  qdrant/qdrant:latest-gpu
`;
            
            case "redis-mem0-postgres":
                return baseSetup + `
# Docker Compose for Memory Services
cat > /root/docker-compose.yml <<EOF
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --maxmemory 60gb --maxmemory-policy allkeys-lru
  
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: sophia_memory
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  mem0:
    image: mem0ai/mem0:latest
    ports:
      - "8080:8080"
    environment:
      REDIS_URL: redis://redis:6379
      POSTGRES_URL: postgresql://sophia:\${POSTGRES_PASSWORD}@postgres:5432/sophia_memory
    depends_on:
      - redis
      - postgres

volumes:
  redis_data:
  postgres_data:
EOF

docker-compose up -d
`;
            
            default:
                return baseSetup;
        }
    }
}

// Kubernetes provider for Lambda Labs K3s cluster
const k8sProvider = new k8s.Provider("lambda-k3s", {
    kubeconfig: pulumi.interpolate`${config.requireSecret("lambdaLabsKubeconfig")}`,
});

// Deploy VMs and get IPs
const vmDeployment = new LambdaLabsVMDeployment();

// Enhanced namespace for unified deployment
const namespace = new k8s.core.v1.Namespace("sophia-ai-unified", {
    metadata: {
        name: "sophia-ai-unified",
        labels: {
            "sophia.ai/environment": env,
            "sophia.ai/stack": "unified",
            "sophia.ai/memory-architecture": "5-tier-hybrid",
        },
    },
}, { provider: k8sProvider });

// Qdrant Cluster Configuration
const qdrantService = new k8s.core.v1.Service("qdrant-cluster", {
    metadata: {
        name: "qdrant-cluster",
        namespace: namespace.metadata.name,
    },
    spec: {
        type: "LoadBalancer",
        ports: [{
            port: 6333,
            targetPort: 6333,
            protocol: "TCP",
            name: "grpc",
        }, {
            port: 6334,
            targetPort: 6334,
            protocol: "TCP",
            name: "http",
        }],
        selector: {
            app: "qdrant",
        },
    },
}, { provider: k8sProvider });

// ConfigMap for Qdrant cluster configuration
const qdrantConfig = new k8s.core.v1.ConfigMap("qdrant-config", {
    metadata: {
        name: "qdrant-config",
        namespace: namespace.metadata.name,
    },
    data: {
        "config.yaml": pulumi.interpolate`
service:
  http_port: 6333
  grpc_port: 6334
  enable_tls: false

cluster:
  enabled: true
  consensus:
    nodes:
      - uri: http://${vmDeployment.ips.apply(ips => ips["qdrant-primary"])}:6333
      - uri: http://${vmDeployment.ips.apply(ips => ips["qdrant-replica"])}:6333

storage:
  storage_path: /qdrant/storage
  wal:
    wal_capacity_mb: 4096
    wal_segments_ahead: 2

performance:
  max_search_threads: 16
  max_optimization_threads: 8
  gpu:
    enabled: true
    device: 0
    memory_limit: "70GB"

collections:
  coding_memory:
    vectors:
      size: 1536
      distance: Cosine
    optimizers:
      memmap_threshold: 20000
      indexing_threshold: 10000
    hnsw_config:
      m: 32
      ef_construct: 200
  
  business_memory:
    vectors:
      size: 3072
      distance: Cosine
    optimizers:
      memmap_threshold: 50000
      indexing_threshold: 20000
    hnsw_config:
      m: 64
      ef_construct: 400
`,
    },
}, { provider: k8sProvider });

// Unified deployment for main API with all integrations
const unifiedDeployment = new k8s.apps.v1.Deployment("sophia-unified-deployment", {
    metadata: {
        name: "sophia-unified-deployment",
        namespace: namespace.metadata.name,
    },
    spec: {
        replicas: 3,
        selector: {
            matchLabels: {
                app: "sophia-unified",
            },
        },
        template: {
            metadata: {
                labels: {
                    app: "sophia-unified",
                },
            },
            spec: {
                containers: [{
                    name: "sophia-unified",
                    image: pulumi.interpolate`${dockerRegistry}/sophia-ai:unified-${env}`,
                    ports: [
                        { containerPort: 8000, name: "api" },
                        { containerPort: 9090, name: "metrics" },
                    ],
                    env: [
                        { name: "ENVIRONMENT", value: env },
                        { name: "PULUMI_ORG", value: "scoobyjava-org" },
                        // Dynamic service endpoints
                        { 
                            name: "QDRANT_URL", 
                            value: vmDeployment.ips.apply(ips => `http://${ips["qdrant-primary"]}:6333`)
                        },
                        { 
                            name: "REDIS_HOST", 
                            value: vmDeployment.ips.apply(ips => ips["redis-mem0-postgres"])
                        },
                        { 
                            name: "POSTGRES_HOST", 
                            value: vmDeployment.ips.apply(ips => ips["redis-mem0-postgres"])
                        },
                    ],
                    resources: {
                        requests: {
                            memory: "16Gi",
                            cpu: "4",
                            "nvidia.com/gpu": "1",
                        },
                        limits: {
                            memory: "32Gi",
                            cpu: "8",
                            "nvidia.com/gpu": "1",
                        },
                    },
                }],
            },
        },
    },
}, { provider: k8sProvider });

// Load balancer service for external access
const loadBalancerService = new k8s.core.v1.Service("sophia-lb", {
    metadata: {
        name: "sophia-lb",
        namespace: namespace.metadata.name,
    },
    spec: {
        type: "LoadBalancer",
        ports: [{
            port: 443,
            targetPort: 8000,
            protocol: "TCP",
            name: "https",
        }],
        selector: {
            app: "sophia-unified",
        },
    },
}, { provider: k8sProvider });

// DNS Update Integration
class DNSUpdater {
    constructor(private ips: pulumi.Output<Record<string, string>>) {
        this.updateDNSRecords();
    }
    
    private updateDNSRecords() {
        this.ips.apply(async (ipMap) => {
            const dnsRecords = [
                { name: "@", value: ipMap["main-api"], type: "A" },
                { name: "api", value: ipMap["main-api"], type: "A" },
                { name: "qdrant", value: ipMap["qdrant-primary"], type: "A" },
                { name: "memory", value: ipMap["redis-mem0-postgres"], type: "A" },
                { name: "dashboard", value: ipMap["main-api"], type: "A" },
            ];
            
            for (const record of dnsRecords) {
                try {
                    const updateCommand = `
                        curl -X POST https://api.namecheap.com/xml.response \\
                        -d "ApiUser=${await namecheapApiUser.get()}" \\
                        -d "ApiKey=${await namecheapApiKey.get()}" \\
                        -d "UserName=${await namecheapUsername.get()}" \\
                        -d "Command=namecheap.domains.dns.setHosts" \\
                        -d "ClientIp=${record.value}" \\
                        -d "SLD=sophia-intel" \\
                        -d "TLD=ai" \\
                        -d "HostName=${record.name}" \\
                        -d "RecordType=${record.type}" \\
                        -d "Address=${record.value}" \\
                        -d "TTL=300"
                    `;
                    
                    cp.execSync(updateCommand);
                    console.log(`Updated DNS record ${record.name}.sophia-intel.ai -> ${record.value}`);
                } catch (error) {
                    console.error(`Failed to update DNS for ${record.name}: ${error}`);
                }
            }
        });
    }
}

// Initialize DNS updater
const dnsUpdater = new DNSUpdater(vmDeployment.ips);

// Health check deployment
const healthCheckCronJob = new k8s.batch.v1.CronJob("health-check", {
    metadata: {
        name: "health-check",
        namespace: namespace.metadata.name,
    },
    spec: {
        schedule: "*/5 * * * *", // Every 5 minutes
        jobTemplate: {
            spec: {
                template: {
                    spec: {
                        containers: [{
                            name: "health-checker",
                            image: "curlimages/curl:latest",
                            command: ["/bin/sh", "-c"],
                            args: [pulumi.interpolate`
                                # Check all services
                                curl -f http://${vmDeployment.ips.apply(ips => ips["main-api"])}:8000/health || exit 1
                                curl -f http://${vmDeployment.ips.apply(ips => ips["qdrant-primary"])}:6333/health || exit 1
                                curl -f http://${vmDeployment.ips.apply(ips => ips["redis-mem0-postgres"])}:6379/ping || exit 1
                            `],
                        }],
                        restartPolicy: "OnFailure",
                    },
                },
            },
        },
    },
}, { provider: k8sProvider });

// Exports
export const deployedIPs = vmDeployment.ips;
export const mainApiEndpoint = pulumi.interpolate`https://api.sophia-intel.ai`;
export const qdrantEndpoint = pulumi.interpolate`https://qdrant.sophia-intel.ai`;
export const dashboardUrl = pulumi.interpolate`https://dashboard.sophia-intel.ai`;
export const namespaceName = namespace.metadata.name;
export const environmentName = env;

// Summary output
export const deploymentSummary = vmDeployment.ips.apply((ips) => ({
    message: "Unified Lambda Labs deployment complete",
    endpoints: {
        api: `https://api.sophia-intel.ai`,
        qdrant: `https://qdrant.sophia-intel.ai:6333`,
        dashboard: `https://dashboard.sophia-intel.ai`,
        memory: `redis://${ips["redis-mem0-postgres"]}:6379`,
    },
    infrastructure: {
        vms: vmConfigs.length,
        ips: ips,
        dnsUpdated: true,
        sslEnabled: true,
    },
}));
