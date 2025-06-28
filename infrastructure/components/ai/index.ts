/**
 * Sophia AI - AI/ML Infrastructure Components
 * 
 * This module provides specialized infrastructure components for AI/ML workloads,
 * including optimized compute resources, GPU support, auto-scaling, and model storage.
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as kubernetes from "@pulumi/kubernetes";
import * as eks from "@pulumi/eks";

/**
 * AI infrastructure component arguments
 */
export interface AIInfrastructureArgs {
    /**
     * Environment name (e.g., dev, staging, prod)
     */
    environment: string;
    
    /**
     * VPC ID where resources will be created
     */
    vpcId: pulumi.Input<string>;
    
    /**
     * Subnet IDs where resources will be created
     */
    subnetIds: pulumi.Input<string>[];
    
    /**
     * Security group IDs for ML workloads
     */
    securityGroupIds: pulumi.Input<string>[];
    
    /**
     * EKS cluster for Kubernetes deployments
     */
    eksCluster?: eks.Cluster;
    
    /**
     * Kubernetes provider for deployments
     */
    k8sProvider?: kubernetes.Provider;
    
    /**
     * Namespace for Kubernetes resources
     */
    namespace?: string;
    
    /**
     * Enable GPU support
     */
    enableGpu?: boolean;
    
    /**
     * GPU instance type (if enableGpu is true)
     * Default: g4dn.xlarge
     */
    gpuInstanceType?: string;
    
    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * AI-specific infrastructure components
 */
export class AIInfrastructure extends pulumi.ComponentResource {
    /**
     * Auto-scaling group for CPU-based ML workloads
     */
    public readonly cpuAutoScalingGroup?: aws.autoscaling.Group;
    
    /**
     * Auto-scaling group for GPU-based ML workloads
     */
    public readonly gpuAutoScalingGroup?: aws.autoscaling.Group;
    
    /**
     * Model artifact bucket for storing ML models
     */
    public readonly modelArtifactBucket: aws.s3.Bucket;
    
    /**
     * EFS file system for shared model storage
     */
    public readonly modelFileSystem: aws.efs.FileSystem;
    
    /**
     * EFS mount targets in each subnet
     */
    public readonly modelFileMountTargets: aws.efs.MountTarget[];
    
    /**
     * Elastic Cache Redis cluster for model caching
     */
    public readonly modelCache: aws.elasticache.Cluster;
    
    /**
     * Kubernetes storage class for model artifacts
     */
    public readonly modelStorageClass?: kubernetes.storage.v1.StorageClass;
    
    /**
     * Kubernetes persistent volume for model storage
     */
    public readonly modelPersistentVolume?: kubernetes.core.v1.PersistentVolume;
    
    /**
     * Kubernetes resource quota for ML namespaces
     */
    public readonly mlResourceQuota?: kubernetes.core.v1.ResourceQuota;
    
    /**
     * Kubernetes pod disruption budget for ML services
     */
    public readonly mlPodDisruptionBudget?: kubernetes.policy.v1.PodDisruptionBudget;
    
    /**
     * Kubernetes horizontal pod autoscaler for ML services
     */
    public readonly mlHorizontalPodAutoscaler?: kubernetes.autoscaling.v2.HorizontalPodAutoscaler;
    
    constructor(name: string, args: AIInfrastructureArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:ai:AIInfrastructure", name, {}, opts);
        
        // Assign default tags
        const tags = {
            Environment: args.environment,
            Project: "sophia-ai-platform",
            ManagedBy: "pulumi",
            Component: "ai-infrastructure",
            CreatedAt: new Date().toISOString(),
            ...args.tags,
        };
        
        // Create model artifact bucket
        this.modelArtifactBucket = new aws.s3.Bucket(`${name}-model-artifacts`, {
            acl: "private",
            versioning: {
                enabled: true,
            },
            serverSideEncryptionConfiguration: {
                rule: {
                    applyServerSideEncryptionByDefault: {
                        sseAlgorithm: "AES256",
                    },
                },
            },
            lifecycleRules: [
                {
                    id: "archive-old-versions",
                    prefix: "models/",
                    status: "Enabled",
                    noncurrentVersionTransitions: [
                        {
                            days: 30,
                            storageClass: "STANDARD_IA",
                        },
                        {
                            days: 90,
                            storageClass: "GLACIER",
                        },
                    ],
                    noncurrentVersionExpiration: {
                        days: 365,
                    },
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-model-artifacts-${args.environment}`,
                ResourceType: "ModelStorage",
            },
        }, { parent: this });
        
        // Create model file system (EFS)
        this.modelFileSystem = new aws.efs.FileSystem(`${name}-model-fs`, {
            encrypted: true,
            performanceMode: "generalPurpose",
            throughputMode: "bursting",
            lifecyclePolicies: [
                {
                    transitionToIa: "AFTER_30_DAYS",
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-model-fs-${args.environment}`,
                ResourceType: "ModelFileSystem",
            },
        }, { parent: this });
        
        // Create EFS mount targets in each subnet
        this.modelFileMountTargets = [];
        args.subnetIds.forEach((subnetId, i) => {
            const mountTarget = new aws.efs.MountTarget(`${name}-mount-target-${i + 1}`, {
                fileSystemId: this.modelFileSystem.id,
                subnetId: subnetId,
                securityGroups: args.securityGroupIds,
            }, { parent: this });
            
            this.modelFileMountTargets.push(mountTarget);
        });
        
        // Create ElastiCache Redis cluster for model caching
        const subnetGroup = new aws.elasticache.SubnetGroup(`${name}-cache-subnet-group`, {
            subnetIds: args.subnetIds,
            tags: {
                ...tags,
                Name: `${name}-cache-subnet-group-${args.environment}`,
            },
        }, { parent: this });
        
        this.modelCache = new aws.elasticache.Cluster(`${name}-model-cache`, {
            engine: "redis",
            engineVersion: "6.2",
            nodeType: "cache.r6g.large", // Memory-optimized for ML caching
            numCacheNodes: 1,
            parameterGroupName: "default.redis6.x",
            port: 6379,
            subnetGroupName: subnetGroup.name,
            securityGroupIds: args.securityGroupIds,
            applyImmediately: true,
            snapshotRetentionLimit: 7,
            snapshotWindow: "05:00-09:00",
            maintenanceWindow: "sun:23:00-mon:01:00",
            tags: {
                ...tags,
                Name: `${name}-model-cache-${args.environment}`,
                ResourceType: "ModelCache",
            },
        }, { parent: this });
        
        // Create EC2 Launch Templates and Auto Scaling Groups for ML workloads
        if (args.enableGpu) {
            // Create GPU-enabled launch template
            const gpuLaunchTemplate = new aws.ec2.LaunchTemplate(`${name}-gpu-launch-template`, {
                imageId: aws.ec2.getAmi({
                    mostRecent: true,
                    owners: ["amazon"],
                    filters: [{
                        name: "name",
                        values: ["amzn2-ami-ecs-gpu-hvm-2.0.*-x86_64-ebs"],
                    }],
                }).then(ami => ami.id),
                instanceType: args.gpuInstanceType || "g4dn.xlarge",
                vpcSecurityGroupIds: args.securityGroupIds,
                userData: pulumi.interpolate`#!/bin/bash
# Install GPU drivers and optimization tools
sudo yum update -y
sudo amazon-linux-extras install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Setup for ML workloads
sudo mkdir -p /opt/ml/model
sudo mount -t nfs4 ${this.modelFileSystem.dnsName}:/ /opt/ml/model

# Configure GPU for ML optimization
sudo nvidia-smi -pm 1
sudo nvidia-smi --auto-boost-default=0
sudo nvidia-smi -ac 5001,1590

# Configure resource limits
echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
`,
                blockDeviceMappings: [
                    {
                        deviceName: "/dev/xvda",
                        ebs: {
                            volumeSize: 100, // GB
                            volumeType: "gp3",
                            iops: 3000,
                            throughput: 125,
                            deleteOnTermination: true,
                        },
                    },
                ],
                metadataOptions: {
                    httpEndpoint: "enabled",
                    httpTokens: "required", // IMDSv2 for security
                },
                tagSpecifications: [
                    {
                        resourceType: "instance",
                        tags: {
                            ...tags,
                            Name: `${name}-gpu-instance-${args.environment}`,
                            ResourceType: "GPUCompute",
                        },
                    },
                ],
            }, { parent: this });
            
            // Create GPU Auto Scaling Group
            this.gpuAutoScalingGroup = new aws.autoscaling.Group(`${name}-gpu-asg`, {
                vpcZoneIdentifiers: args.subnetIds,
                launchTemplate: {
                    id: gpuLaunchTemplate.id,
                    version: "$Latest",
                },
                minSize: 1,
                maxSize: 5,
                desiredCapacity: 1,
                healthCheckType: "EC2",
                healthCheckGracePeriod: 300,
                defaultCooldown: 300,
                forceDelete: false,
                terminationPolicies: ["OldestLaunchTemplate", "OldestInstance"],
                tags: [
                    {
                        key: "Name",
                        value: `${name}-gpu-instance-${args.environment}`,
                        propagateAtLaunch: true,
                    },
                    {
                        key: "Environment",
                        value: args.environment,
                        propagateAtLaunch: true,
                    },
                    {
                        key: "Project",
                        value: "sophia-ai-platform",
                        propagateAtLaunch: true,
                    },
                    {
                        key: "ResourceType",
                        value: "GPUCompute",
                        propagateAtLaunch: true,
                    },
                ],
            }, { parent: this });
            
            // Create ML-specific auto-scaling policies based on GPU utilization
            const gpuUtilizationPolicy = new aws.autoscaling.Policy(`${name}-gpu-utilization-policy`, {
                autoscalingGroupName: this.gpuAutoScalingGroup.name,
                policyType: "TargetTrackingScaling",
                targetTrackingConfiguration: {
                    predefinedMetricSpecification: {
                        predefinedMetricType: "ASGAverageCPUUtilization",
                    },
                    targetValue: 70.0,
                },
            }, { parent: this });
        }
        
        // Create Kubernetes resources if provider is available
        if (args.k8sProvider && args.namespace) {
            // Create storage class for model volumes
            this.modelStorageClass = new kubernetes.storage.v1.StorageClass(`${name}-model-storage-class`, {
                metadata: {
                    name: `${name}-model-storage`,
                },
                provisioner: "efs.csi.aws.com",
                parameters: {
                    fileSystemId: this.modelFileSystem.id,
                    provisioningMode: "efs-ap",
                    directoryPerms: "700",
                },
                reclaimPolicy: "Retain",
                volumeBindingMode: "Immediate",
                allowVolumeExpansion: true,
            }, { provider: args.k8sProvider, parent: this });
            
            // Create resource quota for ML namespace
            this.mlResourceQuota = new kubernetes.core.v1.ResourceQuota(`${name}-ml-resource-quota`, {
                metadata: {
                    name: `${name}-ml-resource-quota`,
                    namespace: args.namespace,
                },
                spec: {
                    hard: {
                        "limits.cpu": args.enableGpu ? "32" : "16",
                        "limits.memory": args.enableGpu ? "128Gi" : "64Gi",
                        "pods": "50",
                        "services": "20",
                        "persistentvolumeclaims": "10",
                        "requests.storage": "1Ti",
                    },
                },
            }, { provider: args.k8sProvider, parent: this });
            
            // Create pod disruption budget for ML services
            this.mlPodDisruptionBudget = new kubernetes.policy.v1.PodDisruptionBudget(`${name}-ml-pdb`, {
                metadata: {
                    name: `${name}-ml-pdb`,
                    namespace: args.namespace,
                },
                spec: {
                    minAvailable: 1,
                    selector: {
                        matchLabels: {
                            component: "ml-service",
                        },
                    },
                },
            }, { provider: args.k8sProvider, parent: this });
            
            // Create horizontal pod autoscaler optimized for ML workloads
            this.mlHorizontalPodAutoscaler = new kubernetes.autoscaling.v2.HorizontalPodAutoscaler(`${name}-ml-hpa`, {
                metadata: {
                    name: `${name}-ml-hpa`,
                    namespace: args.namespace,
                },
                spec: {
                    scaleTargetRef: {
                        apiVersion: "apps/v1",
                        kind: "Deployment",
                        name: `${name}-ml-service`,
                    },
                    minReplicas: 2,
                    maxReplicas: 10,
                    metrics: [
                        {
                            type: "Resource",
                            resource: {
                                name: "cpu",
                                target: {
                                    type: "Utilization",
                                    averageUtilization: 75,
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
                        // Custom metrics can be added here for ML-specific scaling
                    ],
                    behavior: {
                        scaleDown: {
                            stabilizationWindowSeconds: 300,
                            policies: [
                                {
                                    type: "Pods",
                                    value: 1,
                                    periodSeconds: 60,
                                },
                            ],
                        },
                        scaleUp: {
                            stabilizationWindowSeconds: 0,
                            policies: [
                                {
                                    type: "Pods",
                                    value: 2,
                                    periodSeconds: 60,
                                },
                                {
                                    type: "Percent",
                                    value: 100,
                                    periodSeconds: 30,
                                },
                            ],
                        },
                    },
                },
            }, { provider: args.k8sProvider, parent: this });
        }
        
        // Register outputs
        this.registerOutputs({
            modelArtifactBucket: this.modelArtifactBucket,
            modelFileSystem: this.modelFileSystem,
            modelFileMountTargets: this.modelFileMountTargets,
            modelCache: this.modelCache,
            gpuAutoScalingGroup: this.gpuAutoScalingGroup,
            cpuAutoScalingGroup: this.cpuAutoScalingGroup,
            modelStorageClass: this.modelStorageClass,
            mlResourceQuota: this.mlResourceQuota,
            mlPodDisruptionBudget: this.mlPodDisruptionBudget,
            mlHorizontalPodAutoscaler: this.mlHorizontalPodAutoscaler,
        });
    }
}

/**
 * Configuration for a specialized ML/AI deployment
 */
export interface MLDeploymentArgs {
    /**
     * Kubernetes namespace
     */
    namespace: string;
    
    /**
     * Model storage class name
     */
    storageClassName: string;
    
    /**
     * Model cache Redis URI
     */
    modelCacheUri: string;
    
    /**
     * Number of replicas
     */
    replicas?: number;
    
    /**
     * Container resource requests
     */
    resourceRequests?: {
        cpu: string;
        memory: string;
        gpu?: string;
    };
    
    /**
     * Container resource limits
     */
    resourceLimits?: {
        cpu: string;
        memory: string;
        gpu?: string;
    };
    
    /**
     * Model volume size
     */
    modelVolumeSize?: string;
    
    /**
     * Environment variables
     */
    env?: { [key: string]: pulumi.Input<string> };
    
    /**
     * Enable custom model cache initialization
     */
    enableModelCacheInit?: boolean;
    
    /**
     * Auto-scaling configuration
     */
    autoScaling?: {
        minReplicas: number;
        maxReplicas: number;
        targetCpuUtilization: number;
        targetMemoryUtilization: number;
    };
}

/**
 * Create a specialized ML/AI deployment with optimized configurations
 */
export function createMLDeployment(
    name: string,
    args: MLDeploymentArgs,
    image: string,
    k8sProvider: kubernetes.Provider,
): {
    deployment: kubernetes.apps.v1.Deployment;
    service: kubernetes.core.v1.Service;
    pvc: kubernetes.core.v1.PersistentVolumeClaim;
    hpa?: kubernetes.autoscaling.v2.HorizontalPodAutoscaler;
} {
    // Create PVC for model storage
    const pvc = new kubernetes.core.v1.PersistentVolumeClaim(`${name}-model-pvc`, {
        metadata: {
            name: `${name}-model-data`,
            namespace: args.namespace,
        },
        spec: {
            accessModes: ["ReadWriteMany"],
            storageClassName: args.storageClassName,
            resources: {
                requests: {
                    storage: args.modelVolumeSize || "10Gi",
                },
            },
        },
    }, { provider: k8sProvider });
    
    // Prepare container with ML-optimized settings
    const containers: kubernetes.types.input.core.v1.Container[] = [
        {
            name: name,
            image: image,
            ports: [
                {
                    containerPort: 8000,
                    name: "http",
                },
                {
                    containerPort: 9000,
                    name: "metrics",
                },
            ],
            env: [
                {
                    name: "MODEL_CACHE_URI",
                    value: args.modelCacheUri,
                },
                {
                    name: "MODEL_PATH",
                    value: "/models",
                },
                {
                    name: "TRANSFORMERS_CACHE",
                    value: "/models/.cache",
                },
                {
                    name: "TORCH_HOME",
                    value: "/models/.torch",
                },
                {
                    name: "OMP_NUM_THREADS",
                    value: "1",
                },
                {
                    name: "MKL_NUM_THREADS",
                    value: "1",
                },
                {
                    name: "TOKENIZERS_PARALLELISM",
                    value: "false",
                },
                // Add any custom environment variables
                ...Object.entries(args.env || {}).map(([key, value]) => ({
                    name: key,
                    value: value,
                })),
            ],
            resources: {
                requests: {
                    cpu: args.resourceRequests?.cpu || "1",
                    memory: args.resourceRequests?.memory || "2Gi",
                    ...(args.resourceRequests?.gpu ? { "nvidia.com/gpu": args.resourceRequests.gpu } : {}),
                },
                limits: {
                    cpu: args.resourceLimits?.cpu || "2",
                    memory: args.resourceLimits?.memory || "4Gi",
                    ...(args.resourceLimits?.gpu ? { "nvidia.com/gpu": args.resourceLimits.gpu } : {}),
                },
            },
            volumeMounts: [
                {
                    name: "model-data",
                    mountPath: "/models",
                },
            ],
            livenessProbe: {
                httpGet: {
                    path: "/health",
                    port: "http",
                },
                initialDelaySeconds: 60, // Longer for ML models to load
                periodSeconds: 30,
                timeoutSeconds: 10,
                failureThreshold: 3,
            },
            readinessProbe: {
                httpGet: {
                    path: "/ready",
                    port: "http",
                },
                initialDelaySeconds: 120, // Longer for ML models to load
                periodSeconds: 30,
                timeoutSeconds: 10,
                failureThreshold: 3,
            },
            startupProbe: {
                httpGet: {
                    path: "/health",
                    port: "http",
                },
                initialDelaySeconds: 60,
                periodSeconds: 10,
                timeoutSeconds: 10,
                failureThreshold: 30, // Allow up to 5 minutes for startup
            },
            lifecycle: {
                preStop: {
                    exec: {
                        command: ["/bin/sh", "-c", "sleep 10"],
                    },
                },
            },
            securityContext: {
                allowPrivilegeEscalation: false,
                runAsNonRoot: true,
                runAsUser: 1000,
                capabilities: {
                    drop: ["ALL"],
                },
            },
        },
    ];
    
    // Add init container for model cache population if enabled
    if (args.enableModelCacheInit) {
        containers.push({
            name: `${name}-model-init`,
            image: image,
            command: ["/bin/sh", "-c"],
            args: [
                "python -m model_download --cache-dir=/models/.cache",
            ],
            env: [
                {
                    name: "MODEL_PATH",
                    value: "/models",
                },
                {
                    name: "TRANSFORMERS_CACHE",
                    value: "/models/.cache",
                },
                {
                    name: "TORCH_HOME",
                    value: "/models/.torch",
                },
            ],
            volumeMounts: [
                {
                    name: "model-data",
                    mountPath: "/models",
                },
            ],
            resources: {
                requests: {
                    cpu: "500m",
                    memory: "1Gi",
                },
                limits: {
                    cpu: "1",
                    memory: "2Gi",
                },
            },
        });
    }
    
    // Create deployment
    const deployment = new kubernetes.apps.v1.Deployment(`${name}-deployment`, {
        metadata: {
            name: name,
            namespace: args.namespace,
            labels: {
                app: name,
                component: "ml-service",
            },
            annotations: {
                "prometheus.io/scrape": "true",
                "prometheus.io/port": "9000",
                "prometheus.io/path": "/metrics",
            },
        },
        spec: {
            replicas: args.replicas || 2,
            selector: {
                matchLabels: {
                    app: name,
                },
            },
            strategy: {
                type: "RollingUpdate",
                rollingUpdate: {
                    maxUnavailable: 0,
                    maxSurge: 1,
                },
            },
            template: {
                metadata: {
                    labels: {
                        app: name,
                        component: "ml-service",
                    },
                    annotations: {
                        "prometheus.io/scrape": "true",
                        "prometheus.io/port": "9000",
                        "prometheus.io/path": "/metrics",
                    },
                },
                spec: {
                    containers: containers,
                    volumes: [
                        {
                            name: "model-data",
                            persistentVolumeClaim: {
                                claimName: pvc.metadata.name,
                            },
                        },
                    ],
                    // Node affinity for ML workloads
                    affinity: {
                        nodeAffinity: {
                            requiredDuringSchedulingIgnoredDuringExecution: {
                                nodeSelectorTerms: [
                                    {
                                        matchExpressions: [
                                            {
                                                key: "kubernetes.io/arch",
                                                operator: "In",
                                                values: ["amd64"],
                                            },
                                            // If GPU is requested, add GPU node selector
                                            ...(args.resourceRequests?.gpu || args.resourceLimits?.gpu ? [
                                                {
                                                    key: "accelerator",
                                                    operator: "In",
                                                    values: ["nvidia-gpu"],
                                                },
                                            ] : []),
                                        ],
                                    },
                                ],
                            },
                        },
                        // Pod anti-affinity to spread across nodes
                        podAntiAffinity: {
                            preferredDuringSchedulingIgnoredDuringExecution: [
                                {
                                    weight: 100,
                                    podAffinityTerm: {
                                        labelSelector: {
                                            matchExpressions: [
                                                {
                                                    key: "app",
                                                    operator: "In",
                                                    values: [name],
                                                },
                                            ],
                                        },
                                        topologyKey: "kubernetes.io/hostname",
                                    },
                                },
                            ],
                        },
                    },
                    // Priority class for ML workloads
                    priorityClassName: "high-priority",
                    // Topology spread constraints
                    topologySpreadConstraints: [
                        {
                            maxSkew: 1,
                            topologyKey: "kubernetes.io/hostname",
                            whenUnsatisfiable: "ScheduleAnyway",
                            labelSelector: {
                                matchLabels: {
                                    app: name,
                                },
                            },
                        },
                        {
                            maxSkew: 1,
                            topologyKey: "topology.kubernetes.io/zone",
                            whenUnsatisfiable: "ScheduleAnyway",
                            labelSelector: {
                                matchLabels: {
                                    app: name,
                                },
                            },
                        },
                    ],
                },
            },
        },
    }, { provider: k8sProvider });
    
    // Create service
    const service = new kubernetes.core.v1.Service(`${name}-service`, {
        metadata: {
            name: name,
            namespace: args.namespace,
            labels: {
                app: name,
                component: "ml-service",
            },
        },
        spec: {
            ports: [
                {
                    port: 80,
                    targetPort: 8000,
                    protocol: "TCP",
                    name: "http",
                },
                {
                    port: 9000,
                    targetPort: 9000,
                    protocol: "TCP",
                    name: "metrics",
                },
            ],
            selector: {
                app: name,
            },
            type: "ClusterIP",
            sessionAffinity: "ClientIP",
        },
    }, { provider: k8sProvider });
    
    // Create HPA if auto-scaling is enabled
    let hpa: kubernetes.autoscaling.v2.HorizontalPodAutoscaler | undefined;
    if (args.autoScaling) {
        hpa = new kubernetes.autoscaling.v2.HorizontalPodAutoscaler(`${name}-hpa`, {
            metadata: {
                name: `${name}-hpa`,
                namespace: args.namespace,
            },
            spec: {
                scaleTargetRef: {
                    apiVersion: "apps/v1",
                    kind: "Deployment",
                    name: deployment.metadata.name,
                },
                minReplicas: args.autoScaling.minReplicas,
                maxReplicas: args.autoScaling.maxReplicas,
                metrics: [
                    {
                        type: "Resource",
                        resource: {
                            name: "cpu",
                            target: {
                                type: "Utilization",
                                averageUtilization: args.autoScaling.targetCpuUtilization,
                            },
                        },
                    },
                    {
                        type: "Resource",
                        resource: {
                            name: "memory",
                            target: {
                                type: "Utilization",
                                averageUtilization: args.autoScaling.targetMemoryUtilization,
                            },
                        },
                    },
                ],
                behavior: {
                    scaleDown: {
                        stabilizationWindowSeconds: 300,
                        policies: [
                            {
                                type: "Pods",
                                value: 1,
                                periodSeconds: 60,
                            },
                        ],
                    },
                    scaleUp: {
                        stabilizationWindowSeconds: 0,
                        policies: [
                            {
                                type: "Pods",
                                value: 2,
                                periodSeconds: 60,
                            },
                            {
                                type: "Percent",
                                value: 100,
                                periodSeconds: 30,
                            },
                        ],
                    },
                },
            },
        }, { provider: k8sProvider });
    }
    
    return {
        deployment,
        service,
        pvc,
        hpa,
    };
}