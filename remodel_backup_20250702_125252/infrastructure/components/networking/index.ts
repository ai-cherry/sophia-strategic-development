/**
 * Sophia AI - Networking Infrastructure Components
 * 
 * This module provides reusable networking components for the Sophia AI platform,
 * including VPC, subnets, security groups, and network policies.
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as kubernetes from "@pulumi/kubernetes";

export interface NetworkingArgs {
    /**
     * Environment name (e.g., dev, staging, prod)
     */
    environment: string;
    
    /**
     * VPC CIDR block
     */
    vpcCidrBlock: string;
    
    /**
     * Configuration for public subnets
     */
    publicSubnets: {
        /**
         * CIDR blocks for public subnets
         */
        cidrBlocks: string[];
        
        /**
         * Availability zones for public subnets
         */
        availabilityZones?: string[];
    };
    
    /**
     * Configuration for private subnets
     */
    privateSubnets: {
        /**
         * CIDR blocks for private subnets
         */
        cidrBlocks: string[];
        
        /**
         * Availability zones for private subnets
         */
        availabilityZones?: string[];
    };
    
    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * NetworkingComponents creates and exports all networking resources required for the Sophia AI platform.
 */
export class NetworkingComponents extends pulumi.ComponentResource {
    /**
     * The Virtual Private Cloud (VPC)
     */
    public readonly vpc: aws.ec2.Vpc;
    
    /**
     * Public subnets for internet-facing resources
     */
    public readonly publicSubnets: aws.ec2.Subnet[];
    
    /**
     * Private subnets for internal resources
     */
    public readonly privateSubnets: aws.ec2.Subnet[];
    
    /**
     * Internet Gateway for public internet access
     */
    public readonly internetGateway: aws.ec2.InternetGateway;
    
    /**
     * NAT Gateways for private subnet internet access
     */
    public readonly natGateways: aws.ec2.NatGateway[];
    
    /**
     * Elastic IPs for NAT Gateways
     */
    public readonly elasticIps: aws.ec2.Eip[];
    
    /**
     * Route tables for public subnets
     */
    public readonly publicRouteTable: aws.ec2.RouteTable;
    
    /**
     * Route tables for private subnets
     */
    public readonly privateRouteTables: aws.ec2.RouteTable[];
    
    /**
     * Security group for AI-specific services
     */
    public readonly aiServicesSecurityGroup: aws.ec2.SecurityGroup;
    
    /**
     * Security group for database services
     */
    public readonly databaseSecurityGroup: aws.ec2.SecurityGroup;
    
    /**
     * Security group for web services
     */
    public readonly webServicesSecurityGroup: aws.ec2.SecurityGroup;
    
    /**
     * Network policy for Kubernetes
     */
    public readonly networkPolicy?: kubernetes.networking.v1.NetworkPolicy;
    
    constructor(name: string, args: NetworkingArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:networking:NetworkingComponents", name, {}, opts);
        
        // Assign default tags
        const tags = {
            Environment: args.environment,
            Project: "sophia-ai-platform",
            ManagedBy: "pulumi",
            Component: "networking",
            CreatedAt: new Date().toISOString(),
            ...args.tags,
        };
        
        // Create VPC
        this.vpc = new aws.ec2.Vpc(`${name}-vpc`, {
            cidrBlock: args.vpcCidrBlock,
            enableDnsHostnames: true,
            enableDnsSupport: true,
            tags: {
                ...tags,
                Name: `${name}-vpc-${args.environment}`,
            },
        }, { parent: this });
        
        // Create Internet Gateway
        this.internetGateway = new aws.ec2.InternetGateway(`${name}-igw`, {
            vpcId: this.vpc.id,
            tags: {
                ...tags,
                Name: `${name}-igw-${args.environment}`,
            },
        }, { parent: this });
        
        // Create Public Route Table
        this.publicRouteTable = new aws.ec2.RouteTable(`${name}-public-rt`, {
            vpcId: this.vpc.id,
            routes: [{
                cidrBlock: "0.0.0.0/0",
                gatewayId: this.internetGateway.id,
            }],
            tags: {
                ...tags,
                Name: `${name}-public-rt-${args.environment}`,
            },
        }, { parent: this });
        
        // Get availability zones if not provided
        const getAvailabilityZones = aws.getAvailabilityZones();
        
        // Create Public Subnets
        this.publicSubnets = [];
        args.publicSubnets.cidrBlocks.forEach((cidrBlock, i) => {
            const az = args.publicSubnets.availabilityZones 
                ? args.publicSubnets.availabilityZones[i] 
                : getAvailabilityZones.then(azs => azs.names[i % azs.names.length]);
            
            const subnet = new aws.ec2.Subnet(`${name}-public-subnet-${i + 1}`, {
                vpcId: this.vpc.id,
                cidrBlock: cidrBlock,
                availabilityZone: az,
                mapPublicIpOnLaunch: true,
                tags: {
                    ...tags,
                    Name: `${name}-public-subnet-${i + 1}-${args.environment}`,
                    "kubernetes.io/role/elb": "1",
                },
            }, { parent: this });
            
            // Associate with Public Route Table
            new aws.ec2.RouteTableAssociation(`${name}-public-rta-${i + 1}`, {
                subnetId: subnet.id,
                routeTableId: this.publicRouteTable.id,
            }, { parent: this });
            
            this.publicSubnets.push(subnet);
        });
        
        // Create Elastic IPs and NAT Gateways for private subnet internet access
        this.elasticIps = [];
        this.natGateways = [];
        
        // Create one NAT Gateway per AZ for high availability
        this.publicSubnets.forEach((subnet, i) => {
            const eip = new aws.ec2.Eip(`${name}-eip-${i + 1}`, {
                vpc: true,
                tags: {
                    ...tags,
                    Name: `${name}-eip-${i + 1}-${args.environment}`,
                },
            }, { parent: this });
            
            const natGateway = new aws.ec2.NatGateway(`${name}-nat-${i + 1}`, {
                allocationId: eip.id,
                subnetId: subnet.id,
                tags: {
                    ...tags,
                    Name: `${name}-nat-${i + 1}-${args.environment}`,
                },
            }, { parent: this });
            
            this.elasticIps.push(eip);
            this.natGateways.push(natGateway);
        });
        
        // Create Private Subnets and Route Tables
        this.privateSubnets = [];
        this.privateRouteTables = [];
        
        args.privateSubnets.cidrBlocks.forEach((cidrBlock, i) => {
            const az = args.privateSubnets.availabilityZones 
                ? args.privateSubnets.availabilityZones[i] 
                : getAvailabilityZones.then(azs => azs.names[i % azs.names.length]);
            
            // Create private subnet
            const subnet = new aws.ec2.Subnet(`${name}-private-subnet-${i + 1}`, {
                vpcId: this.vpc.id,
                cidrBlock: cidrBlock,
                availabilityZone: az,
                tags: {
                    ...tags,
                    Name: `${name}-private-subnet-${i + 1}-${args.environment}`,
                    "kubernetes.io/role/internal-elb": "1",
                },
            }, { parent: this });
            
            // Create route table with route to NAT Gateway
            const natGatewayIndex = i % this.natGateways.length;
            const routeTable = new aws.ec2.RouteTable(`${name}-private-rt-${i + 1}`, {
                vpcId: this.vpc.id,
                routes: [{
                    cidrBlock: "0.0.0.0/0",
                    natGatewayId: this.natGateways[natGatewayIndex].id,
                }],
                tags: {
                    ...tags,
                    Name: `${name}-private-rt-${i + 1}-${args.environment}`,
                },
            }, { parent: this });
            
            // Associate with Private Route Table
            new aws.ec2.RouteTableAssociation(`${name}-private-rta-${i + 1}`, {
                subnetId: subnet.id,
                routeTableId: routeTable.id,
            }, { parent: this });
            
            this.privateSubnets.push(subnet);
            this.privateRouteTables.push(routeTable);
        });
        
        // Create Security Groups
        
        // AI Services Security Group - optimized for ML workloads
        this.aiServicesSecurityGroup = new aws.ec2.SecurityGroup(`${name}-ai-services-sg`, {
            vpcId: this.vpc.id,
            description: "Security group for AI/ML services with optimized data transfer",
            ingress: [
                // Allow internal traffic for AI service mesh
                {
                    protocol: "tcp",
                    fromPort: 8000,
                    toPort: 9000,
                    self: true,
                    description: "AI service mesh internal communication",
                },
                // Allow traffic from web services
                {
                    protocol: "tcp",
                    fromPort: 8000,
                    toPort: 9000,
                    // Will be updated with web services SG ID
                    description: "Web services to AI services",
                },
            ],
            egress: [
                // Allow all outbound traffic
                {
                    protocol: "-1",
                    fromPort: 0,
                    toPort: 0,
                    cidrBlocks: ["0.0.0.0/0"],
                    description: "All outbound traffic",
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-ai-services-sg-${args.environment}`,
                ResourceType: "AI/ML",
            },
        }, { parent: this });
        
        // Database Security Group
        this.databaseSecurityGroup = new aws.ec2.SecurityGroup(`${name}-database-sg`, {
            vpcId: this.vpc.id,
            description: "Security group for database services",
            ingress: [
                // PostgreSQL
                {
                    protocol: "tcp",
                    fromPort: 5432,
                    toPort: 5432,
                    securityGroups: [this.aiServicesSecurityGroup.id],
                    description: "PostgreSQL from AI services",
                },
                // Redis
                {
                    protocol: "tcp",
                    fromPort: 6379,
                    toPort: 6379,
                    securityGroups: [this.aiServicesSecurityGroup.id],
                    description: "Redis from AI services",
                },
            ],
            egress: [
                // Allow all outbound traffic
                {
                    protocol: "-1",
                    fromPort: 0,
                    toPort: 0,
                    cidrBlocks: ["0.0.0.0/0"],
                    description: "All outbound traffic",
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-database-sg-${args.environment}`,
                ResourceType: "Database",
            },
        }, { parent: this });
        
        // Web Services Security Group
        this.webServicesSecurityGroup = new aws.ec2.SecurityGroup(`${name}-web-services-sg`, {
            vpcId: this.vpc.id,
            description: "Security group for web services",
            ingress: [
                // HTTP
                {
                    protocol: "tcp",
                    fromPort: 80,
                    toPort: 80,
                    cidrBlocks: ["0.0.0.0/0"],
                    description: "HTTP from anywhere",
                },
                // HTTPS
                {
                    protocol: "tcp",
                    fromPort: 443,
                    toPort: 443,
                    cidrBlocks: ["0.0.0.0/0"],
                    description: "HTTPS from anywhere",
                },
                // API Gateway
                {
                    protocol: "tcp",
                    fromPort: 8000,
                    toPort: 8000,
                    cidrBlocks: ["0.0.0.0/0"],
                    description: "API Gateway from anywhere",
                },
            ],
            egress: [
                // Allow all outbound traffic
                {
                    protocol: "-1",
                    fromPort: 0,
                    toPort: 0,
                    cidrBlocks: ["0.0.0.0/0"],
                    description: "All outbound traffic",
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-web-services-sg-${args.environment}`,
                ResourceType: "WebServices",
            },
        }, { parent: this });
        
        // Update AI Services Security Group to allow traffic from Web Services
        new aws.ec2.SecurityGroupRule(`${name}-web-to-ai-rule`, {
            type: "ingress",
            fromPort: 8000,
            toPort: 9000,
            protocol: "tcp",
            securityGroupId: this.aiServicesSecurityGroup.id,
            sourceSecurityGroupId: this.webServicesSecurityGroup.id,
            description: "Web services to AI services",
        }, { parent: this });
        
        // Register all resources
        this.registerOutputs({
            vpc: this.vpc,
            publicSubnets: this.publicSubnets,
            privateSubnets: this.privateSubnets,
            internetGateway: this.internetGateway,
            natGateways: this.natGateways,
            elasticIps: this.elasticIps,
            publicRouteTable: this.publicRouteTable,
            privateRouteTables: this.privateRouteTables,
            aiServicesSecurityGroup: this.aiServicesSecurityGroup,
            databaseSecurityGroup: this.databaseSecurityGroup,
            webServicesSecurityGroup: this.webServicesSecurityGroup,
        });
    }
}

/**
 * Create a Kubernetes NetworkPolicy for secure pod communication
 */
export function createNetworkPolicy(
    name: string,
    namespace: string,
    k8sProvider: kubernetes.Provider,
): kubernetes.networking.v1.NetworkPolicy {
    return new kubernetes.networking.v1.NetworkPolicy(`${name}-network-policy`, {
        metadata: {
            name: `${name}-network-policy`,
            namespace: namespace,
        },
        spec: {
            podSelector: {
                matchLabels: {
                    app: name,
                },
            },
            policyTypes: [
                "Ingress",
                "Egress",
            ],
            ingress: [
                // Allow ingress from within the same namespace
                {
                    from: [
                        {
                            namespaceSelector: {
                                matchLabels: {
                                    name: namespace,
                                },
                            },
                        },
                    ],
                },
            ],
            egress: [
                // Allow egress to specific services
                {
                    to: [
                        {
                            namespaceSelector: {
                                matchLabels: {
                                    name: namespace,
                                },
                            },
                        },
                    ],
                },
                // Allow DNS resolution
                {
                    to: [
                        {
                            namespaceSelector: {
                                matchLabels: {
                                    name: "kube-system",
                                },
                            },
                        },
                    ],
                    ports: [
                        {
                            protocol: "UDP",
                            port: 53,
                        },
                    ],
                },
            ],
        },
    }, { provider: k8sProvider });
}

/**
 * NetworkPolicyArgs defines the arguments for creating network policies
 */
export interface NetworkPolicyArgs {
    /**
     * Application name
     */
    appName: string;
    
    /**
     * Kubernetes namespace
     */
    namespace: string;
    
    /**
     * Allowed ingress namespaces
     */
    allowedIngressNamespaces?: string[];
    
    /**
     * Allowed egress namespaces
     */
    allowedEgressNamespaces?: string[];
    
    /**
     * Allowed ingress ports
     */
    allowedIngressPorts?: number[];
    
    /**
     * Allowed egress ports
     */
    allowedEgressPorts?: number[];
}

/**
 * Create a customized Kubernetes NetworkPolicy
 */
export function createCustomNetworkPolicy(
    name: string,
    args: NetworkPolicyArgs,
    k8sProvider: kubernetes.Provider,
): kubernetes.networking.v1.NetworkPolicy {
    const ingressNamespaces = args.allowedIngressNamespaces || [args.namespace];
    const egressNamespaces = args.allowedEgressNamespaces || [args.namespace, "kube-system"];
    
    const ingressRules = ingressNamespaces.map(ns => ({
        from: [
            {
                namespaceSelector: {
                    matchLabels: {
                        name: ns,
                    },
                },
            },
        ],
        ports: args.allowedIngressPorts?.map(port => ({
            protocol: "TCP",
            port: port,
        })),
    }));
    
    const egressRules = egressNamespaces.map(ns => ({
        to: [
            {
                namespaceSelector: {
                    matchLabels: {
                        name: ns,
                    },
                },
            },
        ],
        ports: args.allowedEgressPorts?.map(port => ({
            protocol: "TCP",
            port: port,
        })),
    }));
    
    // Always add DNS egress rule
    egressRules.push({
        to: [
            {
                namespaceSelector: {
                    matchLabels: {
                        name: "kube-system",
                    },
                },
            },
        ],
        ports: [
            {
                protocol: "UDP",
                port: 53,
            },
        ],
    });
    
    return new kubernetes.networking.v1.NetworkPolicy(`${name}-network-policy`, {
        metadata: {
            name: `${name}-network-policy`,
            namespace: args.namespace,
        },
        spec: {
            podSelector: {
                matchLabels: {
                    app: args.appName,
                },
            },
            policyTypes: [
                "Ingress",
                "Egress",
            ],
            ingress: ingressRules,
            egress: egressRules,
        },
    }, { provider: k8sProvider });
}