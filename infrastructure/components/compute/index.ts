/**
 * Sophia AI - Compute Infrastructure Components
 * 
 * This module provides optimized compute resources for AI/ML workloads,
 * including EC2, EKS, and auto-scaling configurations.
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as eks from "@pulumi/eks";
import * as k8s from "@pulumi/kubernetes";

/**
 * Compute component arguments
 */
export interface ComputeArgs {
    /**
     * Environment name (e.g., dev, staging, prod)
     */
    environment: string;
    
    /**
     * VPC ID where compute resources will be created
     */
    vpcId: pulumi.Input<string>;
    
    /**
     * Subnet IDs where compute resources will be created
     */
    subnetIds: pulumi.Input<string>[];
    
    /**
     * Security group IDs for compute resources
     */
    securityGroupIds: pulumi.Input<string>[];
    
    /**
     * EKS cluster configuration options
     */
    eksConfig?: {
        /**
         * Kubernetes version
         */
        version: string;
        
        /**
         * Instance types for worker nodes
         */
        instanceTypes: string[];
        
        /**
         * Minimum number of nodes per nodegroup
         */
        minSize: number;
        
        /**
         * Maximum number of nodes per nodegroup
         */
        maxSize: number;
        
        /**
         * Desired number of nodes per nodegroup
         */
        desiredCapacity: number;
        
        /**
         * Map of node labels
         */
        labels?: { [key: string]: string };
        
        /**
         * Map of node taints
         */
        taints?: { [key: string]: string };
        
        /**
         * Enable GPU node group
         */
        enableGpu?: boolean;
        
        /**
         * GPU instance types
         */
        gpuInstanceTypes?: string[];
    };
    
    /**
     * Bastion host configuration
     */
    bastionConfig?: {
        /**
         * Enable bastion host
         */
        enabled: boolean;
        
        /**
         * Instance type for bastion host
         */
        instanceType: string;
        
        /**
         * SSH key name for bastion host
         */
        keyName: string;
    };
    
    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * Compute infrastructure components
 */
export class ComputeComponents extends pulumi.ComponentResource {
    /**
     * EKS cluster for Kubernetes workloads
     */
    public readonly eksCluster?: eks.Cluster;
    
    /**
     * Kubernetes provider
     */
    public readonly k8sProvider?: k8s.Provider;
    
    /**
     * Bastion host for secure access
     */
    public readonly bastionHost?: aws.ec2.Instance;
    
    /**
     * Node groups for EKS cluster
     */
    public readonly nodeGroups: eks.NodeGroup[];
    
    /**
     * GPU node group for ML workloads
     */
    public readonly gpuNodeGroup?: eks.NodeGroup;
    
    /**
     * Auto-scaling policies
     */
    public readonly scalingPolicies: aws.autoscaling.Policy[];
    
    constructor(name: string, args: ComputeArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:compute:ComputeComponents", name, {}, opts);
        
        // Initialize arrays
        this.nodeGroups = [];
        this.scalingPolicies = [];
        
        // Assign default tags
        const tags = {
            Environment: args.environment,
            Project: "sophia-ai-platform",
            ManagedBy: "pulumi",
            Component: "compute",
            CreatedAt: new Date().toISOString(),
            ...args.tags,
        };
        
        // Create EKS cluster if configured
        if (args.eksConfig) {
            const clusterTags = {
                ...tags,
                KubernetesCluster: `${name}-eks-${args.environment}`,
            };
            
            // Create EKS cluster with advanced configuration
            this.eksCluster = new eks.Cluster(`${name}-eks`, {
                vpcId: args.vpcId,
                subnetIds: args.subnetIds,
                instanceType: args.eksConfig.instanceTypes[0],
                desiredCapacity: 2, // Control plane nodes
                minSize: 2,
                maxSize: 4,
                storageClasses: "gp3",
                deployDashboard: false, // Use Kubernetes Dashboard or other monitoring tools instead
                version: args.eksConfig.version,
                roleMappings: [
                    {
                        groups: ["system:masters"],
                        roleArn: "arn:aws:iam::ACCOUNT_ID:role/SophiaAIAdminRole",
                        username: "admin",
                    },
                ],
                clusterTags: clusterTags,
                nodeAssociatePublicIpAddress: false, // Nodes in private subnets
                nodeRootVolumeSize: 100, // Larger root volume for ML workloads
                createOidcProvider: true, // Enable OIDC for service account IAM roles
                endpointPrivateAccess: true, // Enable private endpoint
                endpointPublicAccess: true, // Also enable public endpoint for initial setup
                publicAccessCidrs: ["YOUR_CIDR_HERE/32"], // Restrict public access to specific CIDR
                enabledClusterLogTypes: [
                    "api",
                    "audit",
                    "authenticator",
                    "controllerManager",
                    "scheduler",
                ],
                skipDefaultNodeGroup: true, // We'll create our own optimized node groups
                tags: clusterTags,
                // Set cluster encryption config for security
                encryptionConfigKeyArn: undefined, // Set to KMS key ARN for encryption
            }, { parent: this });
            
            // Create Kubernetes provider
            this.k8sProvider = new k8s.Provider(`${name}-k8s-provider`, {
                kubeconfig: this.eksCluster.kubeconfig,
            }, { parent: this });
            
            // Create optimized node groups for different workloads
            
            // Create node group for general workloads
            const generalNodeGroup = new eks.NodeGroup(`${name}-general-ng`, {
                cluster: this.eksCluster,
                instanceType: args.eksConfig.instanceTypes[0],
                desiredCapacity: args.eksConfig.desiredCapacity,
                minSize: args.eksConfig.minSize,
                maxSize: args.eksConfig.maxSize,
                labels: {
                    "role": "general",
                    "workload-type": "mixed",
                    ...args.eksConfig.labels,
                },
                taints: args.eksConfig.taints,
                amiType: "AL2_x86_64",
                diskSize: 100,
                nodeRootVolumeType: "gp3",
                nodeRootVolumeIops: 3000,
                nodeRootVolumeThroughput: 125,
                tags: {
                    ...tags,
                    Name: `${name}-general-ng-${args.environment}`,
                    NodeGroupType: "General",
                },
            }, { parent: this });
            
            this.nodeGroups.push(generalNodeGroup);
            
            // Create node group for CPU-intensive workloads (optimized for inference)
            const cpuNodeGroup = new eks.NodeGroup(`${name}-cpu-optimized-ng`, {
                cluster: this.eksCluster,
                instanceType: "c6i.2xlarge", // Compute-optimized for inference
                desiredCapacity: args.eksConfig.desiredCapacity - 1, // Start with fewer nodes
                minSize: 1,
                maxSize: args.eksConfig.maxSize * 2, // Allow scaling up further for CPU workloads
                labels: {
                    "role": "cpu-optimized",
                    "workload-type": "inference",
                    "accelerator": "cpu",
                    ...args.eksConfig.labels,
                },
                taints: {
                    "dedicated": "cpu-inference:NoSchedule", // Ensure only CPU workloads land here
                    ...args.eksConfig.taints,
                },
                amiType: "AL2_x86_64",
                diskSize: 100,
                nodeRootVolumeType: "gp3",
                nodeRootVolumeIops: 3000,
                nodeRootVolumeThroughput: 125,
                tags: {
                    ...tags,
                    Name: `${name}-cpu-optimized-ng-${args.environment}`,
                    NodeGroupType: "CPUOptimized",
                },
            }, { parent: this });
            
            this.nodeGroups.push(cpuNodeGroup);
            
            // Create node group for memory-intensive workloads (optimized for ML model loading)
            const memoryNodeGroup = new eks.NodeGroup(`${name}-memory-optimized-ng`, {
                cluster: this.eksCluster,
                instanceType: "r6i.2xlarge", // Memory-optimized for model loading
                desiredCapacity: 1, // Start with minimal nodes
                minSize: 1,
                maxSize: args.eksConfig.maxSize,
                labels: {
                    "role": "memory-optimized",
                    "workload-type": "model-serving",
                    ...args.eksConfig.labels,
                },
                taints: {
                    "dedicated": "memory-intensive:NoSchedule", // Ensure only memory-intensive workloads land here
                    ...args.eksConfig.taints,
                },
                amiType: "AL2_x86_64",
                diskSize: 100,
                nodeRootVolumeType: "gp3",
                nodeRootVolumeIops: 3000,
                nodeRootVolumeThroughput: 125,
                tags: {
                    ...tags,
                    Name: `${name}-memory-optimized-ng-${args.environment}`,
                    NodeGroupType: "MemoryOptimized",
                },
            }, { parent: this });
            
            this.nodeGroups.push(memoryNodeGroup);
            
            // Create GPU node group if enabled
            if (args.eksConfig.enableGpu && args.eksConfig.gpuInstanceTypes && args.eksConfig.gpuInstanceTypes.length > 0) {
                this.gpuNodeGroup = new eks.NodeGroup(`${name}-gpu-ng`, {
                    cluster: this.eksCluster,
                    instanceType: args.eksConfig.gpuInstanceTypes[0], // e.g., "g4dn.xlarge"
                    desiredCapacity: 1, // Start with minimal GPU nodes
                    minSize: 0, // Allow scaling to zero when not needed
                    maxSize: 5, // Limit GPU nodes for cost control
                    labels: {
                        "role": "gpu-accelerated",
                        "workload-type": "gpu-inference",
                        "accelerator": "nvidia-gpu",
                        ...args.eksConfig.labels,
                    },
                    taints: {
                        "nvidia.com/gpu": "present:NoSchedule", // Ensure only GPU workloads land here
                        ...args.eksConfig.taints,
                    },
                    amiType: "AL2_x86_64_GPU", // GPU-enabled AMI
                    diskSize: 100,
                    nodeRootVolumeType: "gp3",
                    nodeRootVolumeIops: 3000,
                    nodeRootVolumeThroughput: 125,
                    tags: {
                        ...tags,
                        Name: `${name}-gpu-ng-${args.environment}`,
                        NodeGroupType: "GPUAccelerated",
                    },
                }, { parent: this });
                
                this.nodeGroups.push(this.gpuNodeGroup);
                
                // Create GPU utilization scaling policy
                const gpuScalingPolicy = new aws.autoscaling.Policy(`${name}-gpu-scaling-policy`, {
                    autoscalingGroupName: this.gpuNodeGroup.nodeGroupName,
                    policyType: "TargetTrackingScaling",
                    targetTrackingConfiguration: {
                        customizedMetricSpecification: {
                            metricName: "gpu_utilization",
                            namespace: "AWS/EC2",
                            statistic: "Average",
                            dimensions: [
                                {
                                    name: "AutoScalingGroupName",
                                    value: this.gpuNodeGroup.nodeGroupName,
                                },
                            ],
                        },
                        targetValue: 75.0, // Target 75% GPU utilization
                    },
                }, { parent: this });
                
                this.scalingPolicies.push(gpuScalingPolicy);
            }
            
            // Create Cluster Autoscaler policy for dynamic scaling
            if (this.eksCluster) {
                const clusterAutoscalerPolicy = new aws.iam.Policy(`${name}-cluster-autoscaler-policy`, {
                    description: "Policy for Kubernetes Cluster Autoscaler",
                    policy: JSON.stringify({
                        Version: "2012-10-17",
                        Statement: [
                            {
                                Effect: "Allow",
                                Action: [
                                    "autoscaling:DescribeAutoScalingGroups",
                                    "autoscaling:DescribeAutoScalingInstances",
                                    "autoscaling:DescribeLaunchConfigurations",
                                    "autoscaling:DescribeTags",
                                    "autoscaling:SetDesiredCapacity",
                                    "autoscaling:TerminateInstanceInAutoScalingGroup",
                                    "ec2:DescribeLaunchTemplateVersions",
                                ],
                                Resource: "*",
                            },
                        ],
                    }),
                    tags: {
                        ...tags,
                        Name: `${name}-cluster-autoscaler-policy-${args.environment}`,
                    },
                }, { parent: this });
                
                // Deploy Cluster Autoscaler if we have a k8s provider
                if (this.k8sProvider) {
                    const clusterAutoscalerServiceAccount = new k8s.core.v1.ServiceAccount(`${name}-cluster-autoscaler-sa`, {
                        metadata: {
                            name: "cluster-autoscaler",
                            namespace: "kube-system",
                            annotations: {
                                "eks.amazonaws.com/role-arn": clusterAutoscalerPolicy.arn,
                            },
                        },
                    }, { provider: this.k8sProvider, parent: this });
                    
                    // Note: In a real implementation, you would deploy the actual Cluster Autoscaler deployment here
                }
            }
        }
        
        // Create bastion host if configured
        if (args.bastionConfig && args.bastionConfig.enabled) {
            // Get public subnet for bastion (assuming first subnet is public)
            const bastionSubnetId = args.subnetIds[0];
            
            // Create security group for bastion
            const bastionSg = new aws.ec2.SecurityGroup(`${name}-bastion-sg`, {
                vpcId: args.vpcId,
                description: "Security group for bastion host",
                ingress: [
                    {
                        protocol: "tcp",
                        fromPort: 22,
                        toPort: 22,
                        cidrBlocks: ["YOUR_CIDR_HERE/32"], // Restrict SSH access to specific IPs
                        description: "SSH access",
                    },
                ],
                egress: [
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
                    Name: `${name}-bastion-sg-${args.environment}`,
                },
            }, { parent: this });
            
            // Create bastion host
            this.bastionHost = new aws.ec2.Instance(`${name}-bastion`, {
                ami: aws.ec2.getAmi({
                    mostRecent: true,
                    owners: ["amazon"],
                    filters: [{
                        name: "name",
                        values: ["amzn2-ami-hvm-*-x86_64-gp2"],
                    }],
                }).then(ami => ami.id),
                instanceType: args.bastionConfig.instanceType,
                subnetId: bastionSubnetId,
                vpcSecurityGroupIds: [bastionSg.id],
                keyName: args.bastionConfig.keyName,
                rootBlockDevice: {
                    volumeSize: 20,
                    volumeType: "gp3",
                    deleteOnTermination: true,
                    encrypted: true,
                },
                monitoring: true,
                tags: {
                    ...tags,
                    Name: `${name}-bastion-${args.environment}`,
                },
                userData: pulumi.interpolate`#!/bin/bash
# Update system
yum update -y

# Install useful tools
yum install -y jq awscli kubectl git

# Configure SSM for secure session management
yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Set up kubectl for EKS
aws eks update-kubeconfig --name ${name}-eks-${args.environment} --region $(curl -s http://169.254.169.254/latest/meta-data/placement/region)

# Hardening
# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/g' /etc/ssh/sshd_config
# Disable password auth
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config
systemctl restart sshd
`,
            }, { parent: this });
        }
        
        // Register outputs
        this.registerOutputs({
            eksCluster: this.eksCluster,
            k8sProvider: this.k8sProvider,
            nodeGroups: this.nodeGroups,
            gpuNodeGroup: this.gpuNodeGroup,
            bastionHost: this.bastionHost,
            scalingPolicies: this.scalingPolicies,
        });
    }
}

/**
 * Configuration for spot instance node pools
 */
export interface SpotNodePoolArgs {
    /**
     * EKS cluster
     */
    cluster: eks.Cluster;
    
    /**
     * Node pool name
     */
    name: string;
    
    /**
     * List of instance types to use for spot instances
     */
    instanceTypes: string[];
    
    /**
     * Minimum size of node pool
     */
    minSize: number;
    
    /**
     * Maximum size of node pool
     */
    maxSize: number;
    
    /**
     * Desired capacity of node pool
     */
    desiredCapacity: number;
    
    /**
     * Node labels
     */
    labels?: { [key: string]: string };
    
    /**
     * Node taints
     */
    taints?: { [key: string]: string };
    
    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * Create a cost-optimized spot instance node pool
 */
export function createSpotNodePool(
    args: SpotNodePoolArgs,
    parent?: pulumi.Resource,
): eks.NodeGroup {
    const labels = {
        "lifecycle": "spot",
        "workload-type": "batch",
        ...args.labels,
    };
    
    // Create mixed instance policy node group
    return new eks.NodeGroup(`${args.name}-spot-ng`, {
        cluster: args.cluster,
        instanceTypes: args.instanceTypes,
        desiredCapacity: args.desiredCapacity,
        minSize: args.minSize,
        maxSize: args.maxSize,
        labels: labels,
        taints: args.taints,
        capacityType: "SPOT", // Use spot instances for cost optimization
        diskSize: 50,
        nodeRootVolumeType: "gp3",
        nodeRootVolumeIops: 3000,
        nodeRootVolumeThroughput: 125,
        tags: {
            Name: `${args.name}-spot-ng`,
            NodeGroupType: "Spot",
            ...args.tags,
        },
    }, { parent });
}

/**
 * Create optimized auto-scaling policies for ML workloads
 * @param nodeGroupName Auto Scaling Group name
 * @param metricType Type of metric to scale on
 * @param targetValue Target utilization value
 * @param cooldown Cooldown period in seconds
 */
export function createOptimizedScalingPolicy(
    name: string,
    nodeGroupName: pulumi.Input<string>,
    metricType: "CPU" | "Memory" | "GPU" | "Custom",
    targetValue: number,
    cooldown: number = 300,
    parent?: pulumi.Resource,
): aws.autoscaling.Policy {
    let predefinedMetricType: string | undefined;
    let customizedMetricSpecification: any | undefined;
    
    // Configure metric type
    switch (metricType) {
        case "CPU":
            predefinedMetricType = "ASGAverageCPUUtilization";
            break;
        case "Memory":
            // Using custom metric for memory
            customizedMetricSpecification = {
                metricName: "memory_utilization",
                namespace: "AWS/EC2",
                statistic: "Average",
                dimensions: [
                    {
                        name: "AutoScalingGroupName",
                        value: nodeGroupName,
                    },
                ],
            };
            break;
        case "GPU":
            // Using custom metric for GPU
            customizedMetricSpecification = {
                metricName: "gpu_utilization",
                namespace: "AWS/EC2",
                statistic: "Average",
                dimensions: [
                    {
                        name: "AutoScalingGroupName",
                        value: nodeGroupName,
                    },
                ],
            };
            break;
        case "Custom":
            // Using custom metric
            customizedMetricSpecification = {
                metricName: "custom_scaling_metric",
                namespace: "Sophia/AI",
                statistic: "Average",
                dimensions: [
                    {
                        name: "AutoScalingGroupName",
                        value: nodeGroupName,
                    },
                ],
            };
            break;
    }
    
    // Create the policy
    return new aws.autoscaling.Policy(`${name}-${metricType.toLowerCase()}-scaling-policy`, {
        autoscalingGroupName: nodeGroupName,
        policyType: "TargetTrackingScaling",
        estimatedInstanceWarmup: 300,
        targetTrackingConfiguration: {
            predefinedMetricSpecification: predefinedMetricType ? { predefinedMetricType } : undefined,
            customizedMetricSpecification,
            targetValue,
            disableScaleIn: false,
        },
    }, { parent });
}