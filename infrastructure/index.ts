import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as kubernetes from "@pulumi/kubernetes";
import * as docker from "@pulumi/docker";
import * as github from "@pulumi/github";
import * as vercel from "@pulumiverse/vercel";

// Get current stack and configuration
const config = new pulumi.Config();
const stack = pulumi.getStack();
const isProduction = stack === "sophia-ai-platform-prod";
const isStaging = stack === "sophia-ai-platform-staging";
const isDevelopment = stack === "sophia-ai-platform-dev";

// Common tags for all resources
const commonTags = {
    Environment: stack,
    Project: "sophia-ai-platform",
    ManagedBy: "pulumi",
    CreatedAt: new Date().toISOString(),
};

/**
 * === VERCEL FRONTEND DEPLOYMENT ===
 * Production-ready Vercel deployment with custom domains
 */

// Vercel Team configuration
const vercelTeamConfig = {
    teamId: config.requireSecret("vercel_team_id"),
};

// Production Vercel Project
const frontendProject = new vercel.Project("sophia-frontend", {
    name: isProduction ? "sophia-ai-frontend-prod" : 
          isStaging ? "sophia-ai-frontend-staging" : 
          "sophia-ai-frontend-dev",
    framework: "vite",
    buildCommand: "npm run build",
    outputDirectory: "dist",
    installCommand: "npm ci",
    devCommand: "npm run dev",
    teamId: vercelTeamConfig.teamId,
    gitRepository: {
        type: "github",
        repo: "ai-cherry/sophia-main",
        productionBranch: isProduction ? "main" : 
                         isStaging ? "develop" : 
                         "dev",
    },
    environmentVariables: [
        {
            key: "REACT_APP_ENVIRONMENT",
            value: stack,
            targets: ["production", "preview", "development"],
        },
        {
            key: "REACT_APP_API_URL",
            value: isProduction ? "https://api.sophia.payready.com" :
                   isStaging ? "https://api.staging.sophia.payready.com" :
                   "https://api.dev.sophia.payready.com",
            targets: ["production", "preview", "development"],
        },
        {
            key: "REACT_APP_WS_URL", 
            value: isProduction ? "wss://api.sophia.payready.com/ws" :
                   isStaging ? "wss://api.staging.sophia.payready.com/ws" :
                   "wss://api.dev.sophia.payready.com/ws",
            targets: ["production", "preview", "development"],
        },
    ],
}, {
    protect: isProduction, // Protect production resources
});

// Custom domain for production
let frontendDomain: vercel.ProjectDomain | undefined;
if (isProduction) {
    frontendDomain = new vercel.ProjectDomain("sophia-frontend-domain", {
        projectId: frontendProject.id,
        domain: "app.sophia-intel.ai",
    });
} else if (isStaging) {
    frontendDomain = new vercel.ProjectDomain("sophia-frontend-staging-domain", {
        projectId: frontendProject.id, 
        domain: "staging.app.sophia-intel.ai",
    });
}

/**
 * === DOCKER REGISTRY SETUP ===
 * Container registry for MCP servers and backend services
 */

// Docker images for the platform
const dockerRegistry = "registry.digitalocean.com/sophia-ai";

const images = {
    backend: new docker.Image("sophia-backend", {
        imageName: `${dockerRegistry}/sophia-backend:${stack}`,
        build: {
            context: "../",
            dockerfile: "../Dockerfile",
            args: {
                ENVIRONMENT: stack,
                BUILD_DATE: new Date().toISOString(),
            },
        },
        registry: {
            server: dockerRegistry,
            username: config.requireSecret("docker_username"),
            password: config.requireSecret("docker_token"),
        },
    }),

    mcpGateway: new docker.Image("mcp-gateway", {
        imageName: `${dockerRegistry}/mcp-gateway:${stack}`,
        build: {
            context: "../mcp-gateway",
            dockerfile: "../mcp-gateway/Dockerfile",
        },
        registry: {
            server: dockerRegistry,
            username: config.requireSecret("docker_username"),
            password: config.requireSecret("docker_token"),
        },
    }),
};

/**
 * === KUBERNETES CLUSTER SETUP ===
 * EKS cluster for MCP gateway and backend services
 */

// VPC for EKS cluster
const vpc = new aws.ec2.Vpc("sophia-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: {
        ...commonTags,
        Name: `sophia-vpc-${stack}`,
    },
});

// Subnets for EKS
const publicSubnets = [1, 2].map(i => new aws.ec2.Subnet(`sophia-public-subnet-${i}`, {
    vpcId: vpc.id,
    cidrBlock: `10.0.${i}.0/24`,
    availabilityZone: aws.getAvailabilityZones().then(azs => azs.names[i - 1]),
    mapPublicIpOnLaunch: true,
    tags: {
        ...commonTags,
        Name: `sophia-public-subnet-${i}-${stack}`,
        "kubernetes.io/role/elb": "1",
    },
}));

const privateSubnets = [1, 2].map(i => new aws.ec2.Subnet(`sophia-private-subnet-${i}`, {
    vpcId: vpc.id,
    cidrBlock: `10.0.${i + 10}.0/24`,
    availabilityZone: aws.getAvailabilityZones().then(azs => azs.names[i - 1]),
    tags: {
        ...commonTags,
        Name: `sophia-private-subnet-${i}-${stack}`,
        "kubernetes.io/role/internal-elb": "1",
    },
}));

// Internet Gateway
const igw = new aws.ec2.InternetGateway("sophia-igw", {
    vpcId: vpc.id,
    tags: {
        ...commonTags,
        Name: `sophia-igw-${stack}`,
    },
});

// Route table for public subnets
const publicRouteTable = new aws.ec2.RouteTable("sophia-public-rt", {
    vpcId: vpc.id,
    routes: [{
        cidrBlock: "0.0.0.0/0",
        gatewayId: igw.id,
    }],
    tags: {
        ...commonTags,
        Name: `sophia-public-rt-${stack}`,
    },
});

// Associate public subnets with route table
publicSubnets.forEach((subnet, i) => {
    new aws.ec2.RouteTableAssociation(`sophia-public-rta-${i + 1}`, {
        subnetId: subnet.id,
        routeTableId: publicRouteTable.id,
    });
});

// EKS Cluster IAM Role
const eksRole = new aws.iam.Role("sophia-eks-role", {
    assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
            Action: "sts:AssumeRole",
            Effect: "Allow",
            Principal: {
                Service: "eks.amazonaws.com",
            },
        }],
    }),
    tags: commonTags,
});

new aws.iam.RolePolicyAttachment("sophia-eks-service-policy", {
    role: eksRole.name,
    policyArn: "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
});

// EKS Cluster
const eksCluster = new aws.eks.Cluster("sophia-eks", {
    name: `sophia-cluster-${stack}`,
    roleArn: eksRole.arn,
    vpcConfig: {
        subnetIds: [...publicSubnets.map(s => s.id), ...privateSubnets.map(s => s.id)],
    },
    version: "1.28",
    tags: {
        ...commonTags,
        Name: `sophia-cluster-${stack}`,
    },
}, {
    dependsOn: [publicRouteTable], 
});

// Node Group IAM Role
const nodeGroupRole = new aws.iam.Role("sophia-nodegroup-role", {
    assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
            Action: "sts:AssumeRole",
            Effect: "Allow",
            Principal: {
                Service: "ec2.amazonaws.com",
            },
        }],
    }),
    tags: commonTags,
});

const nodeGroupPolicies = [
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
];

nodeGroupPolicies.forEach((policy, i) => {
    new aws.iam.RolePolicyAttachment(`sophia-nodegroup-policy-${i}`, {
        role: nodeGroupRole.name,
        policyArn: policy,
    });
});

// EKS Node Group
const nodeGroup = new aws.eks.NodeGroup("sophia-nodegroup", {
    clusterName: eksCluster.name,
    nodeGroupName: `sophia-nodes-${stack}`,
    nodeRoleArn: nodeGroupRole.arn,
    subnetIds: privateSubnets.map(s => s.id),
    
    scalingConfig: {
        desiredSize: isProduction ? 3 : 2,
        maxSize: isProduction ? 6 : 3,
        minSize: 1,
    },
    
    instanceTypes: [isProduction ? "t3.large" : "t3.medium"],
    
    remoteAccess: {
        ec2SshKey: config.get("ssh_key_name") || "sophia-key",
    },
    
    tags: {
        ...commonTags,
        Name: `sophia-nodes-${stack}`,
    },
});

/**
 * === KUBERNETES DEPLOYMENTS ===
 * Deploy MCP Gateway and monitoring to EKS
 */

// Kubernetes provider for EKS
const k8sProvider = new kubernetes.Provider("sophia-k8s", {
    kubeconfig: eksCluster.kubeconfigJson,
});

// Namespace for Sophia AI
const namespace = new kubernetes.core.v1.Namespace("sophia-namespace", {
    metadata: {
        name: "sophia-ai",
        labels: {
            environment: stack,
        },
    },
}, { provider: k8sProvider });

// MCP Gateway Deployment
const mcpGatewayDeployment = new kubernetes.apps.v1.Deployment("mcp-gateway-deployment", {
    metadata: {
        name: "mcp-gateway",
        namespace: namespace.metadata.name,
        labels: {
            app: "mcp-gateway",
            environment: stack,
        },
    },
    spec: {
        replicas: isProduction ? 3 : 2,
        selector: {
            matchLabels: {
                app: "mcp-gateway",
            },
        },
        template: {
            metadata: {
                labels: {
                    app: "mcp-gateway",
                },
            },
            spec: {
                containers: [{
                    name: "mcp-gateway",
                    image: images.mcpGateway.imageName,
                    ports: [{
                        containerPort: 8080,
                        name: "http",
                    }],
                    env: [
                        {
                            name: "ENVIRONMENT",
                            value: stack,
                        },
                        {
                            name: "LOG_LEVEL",
                            value: isProduction ? "INFO" : "DEBUG",
                        },
                    ],
                    resources: {
                        requests: {
                            cpu: "100m",
                            memory: "128Mi",
                        },
                        limits: {
                            cpu: "500m",
                            memory: "512Mi",
                        },
                    },
                    livenessProbe: {
                        httpGet: {
                            path: "/health",
                            port: 8080,
                        },
                        initialDelaySeconds: 30,
                        periodSeconds: 10,
                    },
                    readinessProbe: {
                        httpGet: {
                            path: "/ready",
                            port: 8080,
                        },
                        initialDelaySeconds: 5,
                        periodSeconds: 5,
                    },
                }],
            },
        },
    },
}, { provider: k8sProvider });

// MCP Gateway Service
const mcpGatewayService = new kubernetes.core.v1.Service("mcp-gateway-service", {
    metadata: {
        name: "mcp-gateway",
        namespace: namespace.metadata.name,
        labels: {
            app: "mcp-gateway",
        },
    },
    spec: {
        type: "LoadBalancer",
        ports: [{
            port: 80,
            targetPort: 8080,
            protocol: "TCP",
        }],
        selector: {
            app: "mcp-gateway",
        },
    },
}, { provider: k8sProvider });

/**
 * === MONITORING SETUP ===
 * Prometheus and Grafana for observability
 */

// Prometheus Deployment
const prometheusDeployment = new kubernetes.apps.v1.Deployment("prometheus-deployment", {
    metadata: {
        name: "prometheus",
        namespace: namespace.metadata.name,
    },
    spec: {
        replicas: 1,
        selector: {
            matchLabels: {
                app: "prometheus",
            },
        },
        template: {
            metadata: {
                labels: {
                    app: "prometheus",
                },
            },
            spec: {
                containers: [{
                    name: "prometheus",
                    image: "prom/prometheus:v2.45.0",
                    ports: [{
                        containerPort: 9090,
                    }],
                    resources: {
                        requests: {
                            cpu: "100m",
                            memory: "256Mi",
                        },
                        limits: {
                            cpu: "1000m",
                            memory: "1Gi",
                        },
                    },
                }],
            },
        },
    },
}, { provider: k8sProvider, profiles: [!isDevelopment ? undefined : 'monitoring'] });

/**
 * === GITHUB INTEGRATION ===
 * Repository webhooks and deployment status
 */

const githubWebhook = new github.RepositoryWebhook("sophia-deployment-webhook", {
    repository: "sophia-main",
    configuration: {
        url: pulumi.interpolate`${mcpGatewayService.status.loadBalancer.ingress[0].hostname}/webhook/github`,
        contentType: "json",
        insecureSsl: false,
        secret: config.requireSecret("github_webhook_secret"),
    },
    events: ["push", "pull_request", "deployment"],
});

/**
 * === OUTPUTS ===
 * Export important URLs and configurations
 */

export const frontendUrl = isProduction ? "https://app.sophia-intel.ai" :
                           isStaging ? "https://staging.app.sophia-intel.ai" :
                           frontendProject.id.apply(id => `https://${id}.vercel.app`);

export const mcpGatewayUrl = mcpGatewayService.status.loadBalancer.ingress[0].hostname.apply(
    hostname => `http://${hostname}`
);

export const kubernetesCluster = {
    name: eksCluster.name,
    endpoint: eksCluster.endpoint,
    version: eksCluster.version,
};

export const dockerImages = {
    backend: images.backend.imageName,
    mcpGateway: images.mcpGateway.imageName,
};

export const infrastructure = {
    vpc: vpc.id,
    cluster: eksCluster.name,
    nodeGroup: nodeGroup.nodeGroupName,
    namespace: namespace.metadata.name,
};

// Stack-specific outputs
export const customDomain = isProduction ? frontendDomain?.domain : undefined;
export const sslCertificate = isProduction ? "Auto-provisioned by Vercel" : undefined;

export const deploymentInfo = {
    environment: stack,
    deployedAt: new Date().toISOString(),
    version: "2.0.0",
    components: {
        frontend: "Vercel",
        backend: "EKS + Docker",
        mcpGateway: "Kubernetes",
        monitoring: isProduction ? "Prometheus + Grafana" : "Basic logging",
    },
}; 