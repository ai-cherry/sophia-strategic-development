/**
 * Sophia AI - Storage Infrastructure Components
 * 
 * This module provides storage infrastructure components for the Sophia AI platform,
 * including S3 buckets, EFS file systems, RDS instances, and DynamoDB tables.
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as k8s from "@pulumi/kubernetes";

/**
 * Storage component arguments
 */
export interface StorageArgs {
    /**
     * Environment name (e.g., dev, staging, prod)
     */
    environment: string;
    
    /**
     * VPC ID where storage resources will be created
     */
    vpcId: pulumi.Input<string>;
    
    /**
     * Subnet IDs where storage resources will be created
     */
    subnetIds: pulumi.Input<string>[];
    
    /**
     * Security group IDs for storage resources
     */
    securityGroupIds: pulumi.Input<string>[];
    
    /**
     * KMS key ARNs for encryption
     */
    kmsKeys?: {
        /**
         * KMS key ARN for data encryption
         */
        dataKey?: pulumi.Input<string>;
        
        /**
         * KMS key ARN for log encryption
         */
        logKey?: pulumi.Input<string>;
    };
    
    /**
     * S3 bucket configurations
     */
    s3Config?: {
        /**
         * Enable versioning for S3 buckets
         */
        enableVersioning?: boolean;
        
        /**
         * Enable replication for S3 buckets
         */
        enableReplication?: boolean;
        
        /**
         * Enable intelligent tiering for S3 buckets
         */
        enableIntelligentTiering?: boolean;
        
        /**
         * Transition days for S3 lifecycle policies
         */
        lifecycleDays?: {
            /**
             * Days until transition to STANDARD_IA
             */
            standardIa?: number;
            
            /**
             * Days until transition to GLACIER
             */
            glacier?: number;
            
            /**
             * Days until transition to DEEP_ARCHIVE
             */
            deepArchive?: number;
            
            /**
             * Days until expiration
             */
            expiration?: number;
        };
    };
    
    /**
     * RDS instance configurations
     */
    rdsConfig?: {
        /**
         * RDS instance class
         */
        instanceClass?: string;
        
        /**
         * RDS storage size in GB
         */
        allocatedStorage?: number;
        
        /**
         * RDS engine (e.g., postgres, mysql)
         */
        engine?: string;
        
        /**
         * RDS engine version
         */
        engineVersion?: string;
        
        /**
         * Enable Multi-AZ deployment
         */
        multiAz?: boolean;
    };
    
    /**
     * DynamoDB configurations
     */
    dynamoConfig?: {
        /**
         * Table configurations
         */
        tables?: {
            /**
             * Table name
             */
            name: string;
            
            /**
             * Hash key
             */
            hashKey: string;
            
            /**
             * Range key
             */
            rangeKey?: string;
            
            /**
             * Read capacity units
             */
            readCapacity?: number;
            
            /**
             * Write capacity units
             */
            writeCapacity?: number;
            
            /**
             * Enable point-in-time recovery
             */
            pointInTimeRecovery?: boolean;
            
            /**
             * Table attributes
             */
            attributes: {
                /**
                 * Attribute name
                 */
                name: string;
                
                /**
                 * Attribute type
                 */
                type: string;
            }[];
            
            /**
             * Global secondary indexes
             */
            globalSecondaryIndexes?: {
                /**
                 * Index name
                 */
                name: string;
                
                /**
                 * Hash key
                 */
                hashKey: string;
                
                /**
                 * Range key
                 */
                rangeKey?: string;
                
                /**
                 * Read capacity units
                 */
                readCapacity?: number;
                
                /**
                 * Write capacity units
                 */
                writeCapacity?: number;
                
                /**
                 * Projection type
                 */
                projectionType?: string;
            }[];
        }[];
        
        /**
         * Enable auto scaling
         */
        enableAutoScaling?: boolean;
    };
    
    /**
     * EFS configurations
     */
    efsConfig?: {
        /**
         * Performance mode (e.g., generalPurpose, maxIO)
         */
        performanceMode?: string;
        
        /**
         * Throughput mode (e.g., bursting, provisioned)
         */
        throughputMode?: string;
        
        /**
         * Provisioned throughput in MiB/s
         */
        provisionedThroughputInMibps?: number;
        
        /**
         * Enable encryption
         */
        encrypted?: boolean;
        
        /**
         * Enable lifecycle policy
         */
        enableLifecycle?: boolean;
    };
    
    /**
     * ElastiCache configurations
     */
    elastiCacheConfig?: {
        /**
         * Engine (e.g., redis, memcached)
         */
        engine?: string;
        
        /**
         * Node type
         */
        nodeType?: string;
        
        /**
         * Number of nodes
         */
        numNodes?: number;
        
        /**
         * Parameter group name
         */
        parameterGroupName?: string;
    };
    
    /**
     * Kubernetes provider for StorageClass resources
     */
    k8sProvider?: k8s.Provider;
    
    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * Storage infrastructure components
 */
export class StorageComponents extends pulumi.ComponentResource {
    /**
     * S3 buckets
     */
    public readonly s3Buckets: {
        /**
         * Model artifacts bucket
         */
        modelArtifacts: aws.s3.Bucket;
        
        /**
         * Training data bucket
         */
        trainingData: aws.s3.Bucket;
        
        /**
         * Logs bucket
         */
        logs: aws.s3.Bucket;
        
        /**
         * Data lake bucket
         */
        dataLake: aws.s3.Bucket;
    };
    
    /**
     * RDS instances
     */
    public readonly rdsInstances?: {
        /**
         * Primary RDS instance
         */
        primary: aws.rds.Instance;
        
        /**
         * Read replica RDS instance
         */
        readReplica?: aws.rds.Instance;
    };
    
    /**
     * DynamoDB tables
     */
    public readonly dynamoTables?: aws.dynamodb.Table[];
    
    /**
     * DynamoDB auto scaling settings
     */
    public readonly dynamoAutoScaling?: {
        /**
         * Read capacity auto scaling
         */
        readCapacity: aws.appautoscaling.Target[];
        
        /**
         * Write capacity auto scaling
         */
        writeCapacity: aws.appautoscaling.Target[];
        
        /**
         * Read capacity scaling policy
         */
        readScalingPolicy: aws.appautoscaling.Policy[];
        
        /**
         * Write capacity scaling policy
         */
        writeScalingPolicy: aws.appautoscaling.Policy[];
    };
    
    /**
     * EFS file systems
     */
    public readonly efsFileSystems?: {
        /**
         * Model file system
         */
        modelFs: aws.efs.FileSystem;
        
        /**
         * Mount targets
         */
        mountTargets: aws.efs.MountTarget[];
    };
    
    /**
     * ElastiCache clusters
     */
    public readonly elastiCacheClusters?: {
        /**
         * Model cache cluster
         */
        modelCache: aws.elasticache.Cluster;
        
        /**
         * Subnet group
         */
        subnetGroup: aws.elasticache.SubnetGroup;
    };
    
    /**
     * Kubernetes storage classes
     */
    public readonly k8sStorageClasses?: {
        /**
         * EFS storage class
         */
        efs: k8s.storage.v1.StorageClass;
        
        /**
         * GP3 storage class
         */
        gp3: k8s.storage.v1.StorageClass;
    };
    
    constructor(name: string, args: StorageArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:storage:StorageComponents", name, {}, opts);
        
        // Assign default tags
        const tags = {
            Environment: args.environment,
            Project: "sophia-ai-platform",
            ManagedBy: "pulumi",
            Component: "storage",
            CreatedAt: new Date().toISOString(),
            ...args.tags,
        };
        
        // Set default S3 lifecycle days
        const lifecycleDays = {
            standardIa: args.s3Config?.lifecycleDays?.standardIa || 30,
            glacier: args.s3Config?.lifecycleDays?.glacier || 90,
            deepArchive: args.s3Config?.lifecycleDays?.deepArchive || 180,
            expiration: args.s3Config?.lifecycleDays?.expiration || 365,
        };
        
        // Create S3 buckets
        
        // Model artifacts bucket - optimized for ML model storage
        const modelArtifactsBucket = new aws.s3.Bucket(`${name}-model-artifacts`, {
            acl: "private",
            versioning: {
                enabled: args.s3Config?.enableVersioning !== false, // Default to true
            },
            serverSideEncryptionConfiguration: {
                rule: {
                    applyServerSideEncryptionByDefault: {
                        sseAlgorithm: args.kmsKeys?.dataKey ? "aws:kms" : "AES256",
                        kmsMasterKeyId: args.kmsKeys?.dataKey,
                    },
                },
            },
            lifecycleRules: [
                {
                    id: "model-artifacts-lifecycle",
                    enabled: true,
                    prefix: "models/",
                    transitions: [
                        {
                            days: lifecycleDays.standardIa,
                            storageClass: "STANDARD_IA",
                        },
                        {
                            days: lifecycleDays.glacier,
                            storageClass: "GLACIER",
                        },
                    ],
                    noncurrentVersionTransitions: [
                        {
                            days: 7,
                            storageClass: "STANDARD_IA",
                        },
                        {
                            days: 30,
                            storageClass: "GLACIER",
                        },
                    ],
                    noncurrentVersionExpiration: {
                        days: lifecycleDays.expiration,
                    },
                },
            ],
            corsRules: [
                {
                    allowedHeaders: ["*"],
                    allowedMethods: ["GET", "PUT", "POST", "DELETE", "HEAD"],
                    allowedOrigins: ["*"],
                    exposeHeaders: ["ETag", "x-amz-server-side-encryption"],
                    maxAgeSeconds: 3000,
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-model-artifacts-${args.environment}`,
                ResourceType: "S3Bucket",
                DataClassification: "Confidential",
                StorageType: "ModelArtifacts",
            },
        }, { parent: this });
        
        // Training data bucket - optimized for large dataset storage
        const trainingDataBucket = new aws.s3.Bucket(`${name}-training-data`, {
            acl: "private",
            versioning: {
                enabled: args.s3Config?.enableVersioning !== false,
            },
            serverSideEncryptionConfiguration: {
                rule: {
                    applyServerSideEncryptionByDefault: {
                        sseAlgorithm: args.kmsKeys?.dataKey ? "aws:kms" : "AES256",
                        kmsMasterKeyId: args.kmsKeys?.dataKey,
                    },
                },
            },
            tags: {
                ...tags,
                Name: `${name}-training-data-${args.environment}`,
                ResourceType: "S3Bucket",
                DataClassification: "Confidential",
                StorageType: "TrainingData",
            },
        }, { parent: this });
        
        // Logs bucket - optimized for log storage
        const logsBucket = new aws.s3.Bucket(`${name}-logs`, {
            acl: "private",
            versioning: {
                enabled: false, // Logs don't need versioning
            },
            serverSideEncryptionConfiguration: {
                rule: {
                    applyServerSideEncryptionByDefault: {
                        sseAlgorithm: args.kmsKeys?.logKey ? "aws:kms" : "AES256",
                        kmsMasterKeyId: args.kmsKeys?.logKey,
                    },
                },
            },
            lifecycleRules: [
                {
                    id: "logs-lifecycle",
                    enabled: true,
                    transitions: [
                        {
                            days: 30,
                            storageClass: "STANDARD_IA",
                        },
                        {
                            days: 90,
                            storageClass: "GLACIER",
                        },
                    ],
                    expiration: {
                        days: 365, // 1 year retention for logs
                    },
                },
            ],
            tags: {
                ...tags,
                Name: `${name}-logs-${args.environment}`,
                ResourceType: "S3Bucket",
                DataClassification: "Internal",
                StorageType: "Logs",
            },
        }, { parent: this });
        
        // Data lake bucket - optimized for analytics and large-scale data storage
        const dataLakeBucket = new aws.s3.Bucket(`${name}-data-lake`, {
            acl: "private",
            versioning: {
                enabled: args.s3Config?.enableVersioning !== false, // Default to true
            },
            serverSideEncryptionConfiguration: {
                rule: {
                    applyServerSideEncryptionByDefault: {
                        sseAlgorithm: args.kmsKeys?.dataKey ? "aws:kms" : "AES256",
                        kmsMasterKeyId: args.kmsKeys?.dataKey,
                    },
                },
            },
            lifecycleRules: [
                {
                    id: "data-lake-lifecycle",
                    enabled: true,
                    transitions: [
                        {
                            days: lifecycleDays.standardIa,
                            storageClass: "STANDARD_IA",
                        },
                        {
                            days: lifecycleDays.glacier,
                            storageClass: "GLACIER",
                        },
                    ],
                    noncurrentVersionTransitions: [
                        {
                            days: 7,
                            storageClass: "STANDARD_IA",
                        },
                        {
                            days: 30,
                            storageClass: "GLACIER",
                        },
                    ],
                    noncurrentVersionExpiration: {
                        days: lifecycleDays.expiration,
                    },
                },
            ],
            // Intelligent tiering for data lake
            ...(args.s3Config?.enableIntelligentTiering ? {
                intelligentTieringConfigurations: [
                    {
                        name: "data-lake-tiering",
                        status: "Enabled",
                        tierings: [
                            {
                                accessTier: "ARCHIVE_ACCESS",
                                days: 90,
                            },
                            {
                                accessTier: "DEEP_ARCHIVE_ACCESS",
                                days: 180,
                            },
                        ],
                    },
                ],
            } : {}),
            tags: {
                ...tags,
                Name: `${name}-data-lake-${args.environment}`,
                ResourceType: "S3Bucket",
                DataClassification: "Confidential",
                StorageType: "DataLake",
            },
        }, { parent: this });
        
        // Assign S3 buckets
        this.s3Buckets = {
            modelArtifacts: modelArtifactsBucket,
            trainingData: trainingDataBucket,
            logs: logsBucket,
            dataLake: dataLakeBucket,
        };
        
        // Create RDS instance if configured
        if (args.rdsConfig) {
            // Create RDS subnet group
            const rdsSubnetGroup = new aws.rds.SubnetGroup(`${name}-rds-subnet-group`, {
                subnetIds: args.subnetIds,
                tags: {
                    ...tags,
                    Name: `${name}-rds-subnet-group-${args.environment}`,
                },
            }, { parent: this });
            
            // Create RDS parameter group
            const rdsParameterGroup = new aws.rds.ParameterGroup(`${name}-rds-parameter-group`, {
                family: args.rdsConfig.engine === "postgres" ? "postgres14" : "mysql8.0",
                description: `Parameter group for ${args.environment} Sophia AI RDS instance`,
                parameters: args.rdsConfig.engine === "postgres" ? [
                    // Postgres optimizations for ML workloads
                    {
                        name: "shared_buffers",
                        value: "2GB",
                    },
                    {
                        name: "work_mem",
                        value: "100MB",
                    },
                    {
                        name: "maintenance_work_mem",
                        value: "256MB",
                    },
                    {
                        name: "effective_cache_size",
                        value: "6GB",
                    },
                    {
                        name: "max_connections",
                        value: "200",
                    },
                ] : [
                    // MySQL optimizations for ML workloads
                    {
                        name: "innodb_buffer_pool_size",
                        value: "2GB",
                    },
                    {
                        name: "innodb_log_file_size",
                        value: "256MB",
                    },
                    {
                        name: "max_connections",
                        value: "200",
                    },
                ],
                tags: {
                    ...tags,
                    Name: `${name}-rds-parameter-group-${args.environment}`,
                },
            }, { parent: this });
            
            // Create RDS instance
            const rdsInstance = new aws.rds.Instance(`${name}-rds`, {
                engine: args.rdsConfig.engine || "postgres",
                instanceClass: args.rdsConfig.instanceClass || "db.t3.medium",
                allocatedStorage: args.rdsConfig.allocatedStorage || 20,
                engineVersion: args.rdsConfig.engineVersion || (args.rdsConfig.engine === "postgres" ? "14.5" : "8.0"),
                dbName: `sophia_${args.environment}`,
                username: "sophia_admin", // In production, use Secrets Manager
                password: pulumi.output("REPLACE_ME_WITH_SECRET"), // In production, use Secrets Manager
                skipFinalSnapshot: args.environment !== "prod", // Only create final snapshot in prod
                finalSnapshotIdentifier: args.environment === "prod" ? `${name}-final-snapshot-${new Date().getTime()}` : undefined,
                backupRetentionPeriod: args.environment === "prod" ? 7 : 1,
                backupWindow: "03:00-04:00",
                maintenanceWindow: "sun:04:00-sun:05:00",
                multiAz: args.rdsConfig.multiAz || args.environment === "prod",
                publiclyAccessible: false,
                vpcSecurityGroupIds: args.securityGroupIds,
                dbSubnetGroupName: rdsSubnetGroup.name,
                parameterGroupName: rdsParameterGroup.name,
                storageType: "gp3",
                storageEncrypted: true,
                kmsKeyId: args.kmsKeys?.dataKey,
                performanceInsightsEnabled: true,
                performanceInsightsRetentionPeriod: 7,
                monitoringInterval: 30,
                enabledCloudwatchLogsExports: ["postgresql", "upgrade"],
                autoMinorVersionUpgrade: true,
                deletionProtection: args.environment === "prod",
                tags: {
                    ...tags,
                    Name: `${name}-rds-${args.environment}`,
                    ResourceType: "RDSInstance",
                },
            }, { parent: this });
            
            // Create RDS read replica for production environment
            let rdsReadReplica: aws.rds.Instance | undefined;
            if (args.environment === "prod") {
                rdsReadReplica = new aws.rds.Instance(`${name}-rds-replica`, {
                    instanceClass: args.rdsConfig.instanceClass || "db.t3.medium",
                    replicateSourceDb: rdsInstance.id,
                    publiclyAccessible: false,
                    vpcSecurityGroupIds: args.securityGroupIds,
                    parameterGroupName: rdsParameterGroup.name,
                    storageType: "gp3",
                    performanceInsightsEnabled: true,
                    performanceInsightsRetentionPeriod: 7,
                    monitoringInterval: 30,
                    enabledCloudwatchLogsExports: ["postgresql", "upgrade"],
                    autoMinorVersionUpgrade: true,
                    tags: {
                        ...tags,
                        Name: `${name}-rds-replica-${args.environment}`,
                        ResourceType: "RDSReadReplica",
                    },
                }, { parent: this });
            }
            
            // Assign RDS instances
            this.rdsInstances = {
                primary: rdsInstance,
                readReplica: rdsReadReplica,
            };
        }
        
        // Create DynamoDB tables if configured
        if (args.dynamoConfig?.tables && args.dynamoConfig.tables.length > 0) {
            this.dynamoTables = [];
            
            // Arrays for auto scaling resources
            const readCapacityTargets: aws.appautoscaling.Target[] = [];
            const writeCapacityTargets: aws.appautoscaling.Target[] = [];
            const readScalingPolicies: aws.appautoscaling.Policy[] = [];
            const writeScalingPolicies: aws.appautoscaling.Policy[] = [];
            
            // Create tables
            args.dynamoConfig.tables.forEach((tableConfig, i) => {
                const tableName = `${name}-${tableConfig.name}-${args.environment}`;
                
                // Create table
                const table = new aws.dynamodb.Table(`${name}-dynamo-table-${i + 1}`, {
                    name: tableName,
                    billingMode: "PROVISIONED",
                    readCapacity: tableConfig.readCapacity || 5,
                    writeCapacity: tableConfig.writeCapacity || 5,
                    hashKey: tableConfig.hashKey,
                    rangeKey: tableConfig.rangeKey,
                    attributes: tableConfig.attributes,
                    globalSecondaryIndexes: tableConfig.globalSecondaryIndexes,
                    pointInTimeRecovery: {
                        enabled: tableConfig.pointInTimeRecovery || args.environment === "prod",
                    },
                    serverSideEncryption: args.kmsKeys?.dataKey ? {
                        enabled: true,
                        kmsKeyArn: args.kmsKeys.dataKey,
                    } : undefined,
                    tags: {
                        ...tags,
                        Name: tableName,
                        ResourceType: "DynamoDBTable",
                    },
                }, { parent: this });
                
                this.dynamoTables?.push(table);
                
                // Set up auto scaling if enabled
                if (args.dynamoConfig?.enableAutoScaling) {
                    // Read capacity auto scaling
                    const readCapacityTarget = new aws.appautoscaling.Target(`${name}-dynamo-read-target-${i + 1}`, {
                        maxCapacity: 100,
                        minCapacity: tableConfig.readCapacity || 5,
                        resourceId: pulumi.interpolate`table/${tableName}`,
                        scalableDimension: "dynamodb:table:ReadCapacityUnits",
                        serviceNamespace: "dynamodb",
                    }, { parent: this });
                    
                    readCapacityTargets.push(readCapacityTarget);
                    
                    // Read capacity scaling policy
                    const readScalingPolicy = new aws.appautoscaling.Policy(`${name}-dynamo-read-policy-${i + 1}`, {
                        policyType: "TargetTrackingScaling",
                        resourceId: readCapacityTarget.resourceId,
                        scalableDimension: readCapacityTarget.scalableDimension,
                        serviceNamespace: readCapacityTarget.serviceNamespace,
                        targetTrackingScalingPolicyConfiguration: {
                            predefinedMetricSpecification: {
                                predefinedMetricType: "DynamoDBReadCapacityUtilization",
                            },
                            targetValue: 70,
                            scaleInCooldown: 60,
                            scaleOutCooldown: 60,
                        },
                    }, { parent: this });
                    
                    readScalingPolicies.push(readScalingPolicy);
                    
                    // Write capacity auto scaling
                    const writeCapacityTarget = new aws.appautoscaling.Target(`${name}-dynamo-write-target-${i + 1}`, {
                        maxCapacity: 100,
                        minCapacity: tableConfig.writeCapacity || 5,
                        resourceId: pulumi.interpolate`table/${tableName}`,
                        scalableDimension: "dynamodb:table:WriteCapacityUnits",
                        serviceNamespace: "dynamodb",
                    }, { parent: this });
                    
                    writeCapacityTargets.push(writeCapacityTarget);
                    
                    // Write capacity scaling policy
                    const writeScalingPolicy = new aws.appautoscaling.Policy(`${name}-dynamo-write-policy-${i + 1}`, {
                        policyType: "TargetTrackingScaling",
                        resourceId: writeCapacityTarget.resourceId,
                        scalableDimension: writeCapacityTarget.scalableDimension,
                        serviceNamespace: writeCapacityTarget.serviceNamespace,
                        targetTrackingScalingPolicyConfiguration: {
                            predefinedMetricSpecification: {
                                predefinedMetricType: "DynamoDBWriteCapacityUtilization",
                            },
                            targetValue: 70,
                            scaleInCooldown: 60,
                            scaleOutCooldown: 60,
                        },
                    }, { parent: this });
                    
                    writeScalingPolicies.push(writeScalingPolicy);
                }
            });
            
            // Assign DynamoDB auto scaling resources
            if (args.dynamoConfig?.enableAutoScaling) {
                this.dynamoAutoScaling = {
                    readCapacity: readCapacityTargets,
                    writeCapacity: writeCapacityTargets,
                    readScalingPolicy: readScalingPolicies,
                    writeScalingPolicy: writeScalingPolicies,
                };
            }
        }
        
        // Create EFS file systems if configured
        if (args.efsConfig) {
            // Create EFS file system optimized for ML workloads
            const modelFs = new aws.efs.FileSystem(`${name}-model-fs`, {
                encrypted: args.efsConfig.encrypted !== false, // Default to true
                kmsKeyId: args.kmsKeys?.dataKey,
                performanceMode: args.efsConfig.performanceMode || "generalPurpose",
                throughputMode: args.efsConfig.throughputMode || "bursting",
                provisionedThroughputInMibps: args.efsConfig.throughputMode === "provisioned" ? 
                    args.efsConfig.provisionedThroughputInMibps || 128 : undefined,
                lifecyclePolicies: args.efsConfig.enableLifecycle ? [
                    {
                        transitionToIa: "AFTER_30_DAYS",
                    },
                ] : undefined,
                tags: {
                    ...tags,
                    Name: `${name}-model-fs-${args.environment}`,
                    ResourceType: "EFSFileSystem",
                    StorageType: "ModelFileSystem",
                },
            }, { parent: this });
            
            // Create mount targets in each subnet
            const mountTargets: aws.efs.MountTarget[] = [];
            
            args.subnetIds.forEach((subnetId, i) => {
                const mountTarget = new aws.efs.MountTarget(`${name}-mount-target-${i + 1}`, {
                    fileSystemId: modelFs.id,
                    subnetId: subnetId,
                    securityGroups: args.securityGroupIds,
                }, { parent: this });
                
                mountTargets.push(mountTarget);
            });
            
            // Assign EFS file systems
            this.efsFileSystems = {
                modelFs: modelFs,
                mountTargets: mountTargets,
            };
            
            // Create EFS storage class for Kubernetes if K8s provider is available
            if (args.k8sProvider) {
                const efsStorageClass = new k8s.storage.v1.StorageClass(`${name}-efs-sc`, {
                    metadata: {
                        name: `${name}-efs-sc-${args.environment}`,
                        annotations: {
                            "storageclass.kubernetes.io/is-default-class": "false",
                        },
                    },
                    provisioner: "efs.csi.aws.com",
                    parameters: {
                        fileSystemId: modelFs.id,
                        provisioningMode: "efs-ap",
                        directoryPerms: "700",
                    },
                    reclaimPolicy: "Retain",
                    volumeBindingMode: "Immediate",
                    allowVolumeExpansion: true,
                }, { provider: args.k8sProvider, parent: this });
                
                const gp3StorageClass = new k8s.storage.v1.StorageClass(`${name}-gp3-sc`, {
                    metadata: {
                        name: `${name}-gp3-sc-${args.environment}`,
                        annotations: {
                            "storageclass.kubernetes.io/is-default-class": "true",
                        },
                    },
                    provisioner: "ebs.csi.aws.com",
                    parameters: {
                        type: "gp3",
                        iops: "3000",
                        throughput: "125",
                        encrypted: "true",
                        kmsKeyId: args.kmsKeys?.dataKey,
                    },
                    reclaimPolicy: "Delete",
                    volumeBindingMode: "WaitForFirstConsumer",
                    allowVolumeExpansion: true,
                }, { provider: args.k8sProvider, parent: this });
                
                // Assign Kubernetes storage classes
                this.k8sStorageClasses = {
                    efs: efsStorageClass,
                    gp3: gp3StorageClass,
                };
            }
        }
        
        // Create ElastiCache cluster if configured
        if (args.elastiCacheConfig) {
            // Create subnet group
            const subnetGroup = new aws.elasticache.SubnetGroup(`${name}-cache-subnet-group`, {
                subnetIds: args.subnetIds,
                tags: {
                    ...tags,
                    Name: `${name}-cache-subnet-group-${args.environment}`,
                },
            }, { parent: this });
            
            // Create parameter group
            const parameterGroup = new aws.elasticache.ParameterGroup(`${name}-cache-parameter-group`, {
                family: args.elastiCacheConfig.engine === "redis" ? "redis6.x" : "memcached1.6",
                description: `Parameter group for ${args.environment} Sophia AI ElastiCache cluster`,
                parameters: args.elastiCacheConfig.engine === "redis" ? [
                    // Redis optimizations for ML workloads
                    {
                        name: "maxmemory-policy",
                        value: "volatile-lru",
                    },
                    {
                        name: "activedefrag",
                        value: "yes",
                    },
                ] : [
                    // Memcached optimizations
                    {
                        name: "max_item_size",
                        value: "10485760", // 10MB for larger model artifacts
                    },
                ],
                tags: {
                    ...tags,
                    Name: `${name}-cache-parameter-group-${args.environment}`,
                },
            }, { parent: this });
            
            // Create ElastiCache cluster
            const modelCache = new aws.elasticache.Cluster(`${name}-model-cache`, {
                engine: args.elastiCacheConfig.engine || "redis",
                nodeType: args.elastiCacheConfig.nodeType || "cache.t3.medium",
                numCacheNodes: args.elastiCacheConfig.numNodes || 1,
                parameterGroupName: args.elastiCacheConfig.parameterGroupName || parameterGroup.name,
                subnetGroupName: subnetGroup.name,
                securityGroupIds: args.securityGroupIds,
                engineVersion: args.elastiCacheConfig.engine === "redis" ? "6.2" : "1.6.6",
                port: args.elastiCacheConfig.engine === "redis" ? 6379 : 11211,
                snapshotRetentionLimit: args.environment === "prod" ? 7 : 1,
                snapshotWindow: "03:00-04:00",
                maintenanceWindow: "sun:04:00-sun:05:00",
                applyImmediately: true,
                tags: {
                    ...tags,
                    Name: `${name}-model-cache-${args.environment}`,
                    ResourceType: "ElastiCacheCluster",
                    CacheType: "ModelCache",
                },
            }, { parent: this });
            
            // Assign ElastiCache clusters
            this.elastiCacheClusters = {
                modelCache: modelCache,
                subnetGroup: subnetGroup,
            };
        }
        
        this.registerOutputs({
            s3Buckets: this.s3Buckets,
            rdsInstances: this.rdsInstances,
            dynamoTables: this.dynamoTables,
            dynamoAutoScaling: this.dynamoAutoScaling,
            efsFileSystems: this.efsFileSystems,
            elastiCacheClusters: this.elastiCacheClusters,
            k8sStorageClasses: this.k8sStorageClasses,
        });
    }
}