/**
 * Sophia AI - Security Infrastructure Components
 *
 * This module provides security infrastructure components for the Sophia AI platform,
 * including IAM roles, security groups, KMS keys, and encryption policies.
 */

import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as k8s from "@pulumi/kubernetes";

/**
 * Security component arguments
 */
export interface SecurityArgs {
    /**
     * Environment name (e.g., dev, staging, prod)
     */
    environment: string;

    /**
     * VPC ID where security resources will be created
     */
    vpcId: pulumi.Input<string>;

    /**
     * Kubernetes provider for RBAC and policy resources
     */
    k8sProvider?: k8s.Provider;

    /**
     * Enable advanced security features
     */
    enableAdvancedSecurity?: boolean;

    /**
     * AWS account ID for resource ARNs
     */
    accountId?: string;

    /**
     * AWS region for resource ARNs
     */
    region?: string;

    /**
     * Tags to apply to all resources
     */
    tags?: { [key: string]: string };
}

/**
 * Security infrastructure components
 */
export class SecurityComponents extends pulumi.ComponentResource {
    /**
     * KMS key for data encryption
     */
    public readonly dataEncryptionKey: aws.kms.Key;

    /**
     * KMS key for log encryption
     */
    public readonly logEncryptionKey: aws.kms.Key;

    /**
     * KMS key for secret encryption
     */
    public readonly secretEncryptionKey: aws.kms.Key;

    /**
     * Service roles for various components
     */
    public readonly serviceRoles: {
        mlWorkloads: aws.iam.Role;
        dataProcessing: aws.iam.Role;
        monitoring: aws.iam.Role;
    };

    /**
     * IAM policies for various components
     */
    public readonly policies: {
        mlWorkloads: aws.iam.Policy;
        dataProcessing: aws.iam.Policy;
        monitoring: aws.iam.Policy;
        secretsAccess: aws.iam.Policy;
        s3Access: aws.iam.Policy;
        kmsAccess: aws.iam.Policy;
    };

    /**
     * VPC Endpoint for secure AWS service access
     */
    public readonly vpcEndpoints: {
        s3: aws.ec2.VpcEndpoint;
        dynamodb: aws.ec2.VpcEndpoint;
        secretsManager?: aws.ec2.VpcEndpoint;
        kms?: aws.ec2.VpcEndpoint;
        ecr?: aws.ec2.VpcEndpoint;
        ecrApi?: aws.ec2.VpcEndpoint;
    };

    /**
     * IAM OIDC provider for Kubernetes service accounts
     */
    public readonly oidcProvider?: aws.iam.OpenIdConnectProvider;

    /**
     * K8s security policies and service accounts
     */
    public readonly k8sSecurityResources?: {
        psp: k8s.policy.v1beta1.PodSecurityPolicy;
        networkPolicies: k8s.networking.v1.NetworkPolicy[];
        serviceAccounts: k8s.core.v1.ServiceAccount[];
    };

    constructor(name: string, args: SecurityArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:security:SecurityComponents", name, {}, opts);

        // Assign default tags
        const tags = {
            Environment: args.environment,
            Project: "sophia-ai-platform",
            ManagedBy: "pulumi",
            Component: "security",
            CreatedAt: new Date().toISOString(),
            ...args.tags,
        };

        // Create KMS keys for encryption
        this.dataEncryptionKey = new aws.kms.Key(`${name}-data-encryption-key`, {
            description: "KMS key for encrypting Sophia AI data",
            enableKeyRotation: true,
            deletionWindowInDays: 30,
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: {
                            AWS: `arn:aws:iam::${args.accountId || "*"}:root`,
                        },
                        Action: "kms:*",
                        Resource: "*",
                    },
                    {
                        Effect: "Allow",
                        Principal: {
                            Service: "s3.amazonaws.com",
                        },
                        Action: [
                            "kms:GenerateDataKey*",
                            "kms:Decrypt",
                        ],
                        Resource: "*",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-data-encryption-key-${args.environment}`,
                Type: "DataEncryption",
            },
        }, { parent: this });

        this.logEncryptionKey = new aws.kms.Key(`${name}-log-encryption-key`, {
            description: "KMS key for encrypting Sophia AI logs",
            enableKeyRotation: true,
            deletionWindowInDays: 30,
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: {
                            AWS: `arn:aws:iam::${args.accountId || "*"}:root`,
                        },
                        Action: "kms:*",
                        Resource: "*",
                    },
                    {
                        Effect: "Allow",
                        Principal: {
                            Service: "logs.amazonaws.com",
                        },
                        Action: [
                            "kms:GenerateDataKey*",
                            "kms:Decrypt",
                        ],
                        Resource: "*",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-log-encryption-key-${args.environment}`,
                Type: "LogEncryption",
            },
        }, { parent: this });

        this.secretEncryptionKey = new aws.kms.Key(`${name}-secret-encryption-key`, {
            description: "KMS key for encrypting Sophia AI secrets",
            enableKeyRotation: true,
            deletionWindowInDays: 30,
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: {
                            AWS: `arn:aws:iam::${args.accountId || "*"}:root`,
                        },
                        Action: "kms:*",
                        Resource: "*",
                    },
                    {
                        Effect: "Allow",
                        Principal: {
                            Service: "secretsmanager.amazonaws.com",
                        },
                        Action: [
                            "kms:GenerateDataKey*",
                            "kms:Decrypt",
                        ],
                        Resource: "*",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-secret-encryption-key-${args.environment}`,
                Type: "SecretEncryption",
            },
        }, { parent: this });

        // Create IAM policies with least privilege

        // ML workloads policy
        const mlWorkloadsPolicy = new aws.iam.Policy(`${name}-ml-workloads-policy`, {
            description: "IAM policy for ML workloads with least privilege",
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Action: [
                            "s3:GetObject",
                            "s3:ListBucket",
                        ],
                        Resource: [
                            `arn:aws:s3:::${name}-model-artifacts-${args.environment}`,
                            `arn:aws:s3:::${name}-model-artifacts-${args.environment}/*`,
                        ],
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "kms:Decrypt",
                            "kms:GenerateDataKey*",
                        ],
                        Resource: this.dataEncryptionKey.arn,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        Resource: `arn:aws:logs:${args.region || "*"}:${args.accountId || "*"}:log-group:/aws/sophia-ai/${args.environment}/*`,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "secretsmanager:GetSecretValue",
                        ],
                        Resource: `arn:aws:secretsmanager:${args.region || "*"}:${args.accountId || "*"}:secret:sophia-ai/${args.environment}/ml-*`,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "elasticache:DescribeCacheClusters",
                        ],
                        Resource: "*",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-ml-workloads-policy-${args.environment}`,
                Type: "IAMPolicy",
            },
        }, { parent: this });

        // Data processing policy
        const dataProcessingPolicy = new aws.iam.Policy(`${name}-data-processing-policy`, {
            description: "IAM policy for data processing with least privilege",
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Action: [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket",
                        ],
                        Resource: [
                            `arn:aws:s3:::${name}-data-processing-${args.environment}`,
                            `arn:aws:s3:::${name}-data-processing-${args.environment}/*`,
                        ],
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "kms:Decrypt",
                            "kms:GenerateDataKey*",
                        ],
                        Resource: this.dataEncryptionKey.arn,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        Resource: `arn:aws:logs:${args.region || "*"}:${args.accountId || "*"}:log-group:/aws/sophia-ai/${args.environment}/*`,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "secretsmanager:GetSecretValue",
                        ],
                        Resource: `arn:aws:secretsmanager:${args.region || "*"}:${args.accountId || "*"}:secret:sophia-ai/${args.environment}/data-*`,
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-data-processing-policy-${args.environment}`,
                Type: "IAMPolicy",
            },
        }, { parent: this });

        // Monitoring policy
        const monitoringPolicy = new aws.iam.Policy(`${name}-monitoring-policy`, {
            description: "IAM policy for monitoring with least privilege",
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Action: [
                            "cloudwatch:PutMetricData",
                            "cloudwatch:GetMetricData",
                            "cloudwatch:GetMetricStatistics",
                            "cloudwatch:ListMetrics",
                        ],
                        Resource: "*",
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "logs:DescribeLogStreams",
                            "logs:DescribeLogGroups",
                            "logs:FilterLogEvents",
                        ],
                        Resource: `arn:aws:logs:${args.region || "*"}:${args.accountId || "*"}:log-group:/aws/sophia-ai/${args.environment}/*`,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "kms:Decrypt",
                        ],
                        Resource: this.logEncryptionKey.arn,
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-monitoring-policy-${args.environment}`,
                Type: "IAMPolicy",
            },
        }, { parent: this });

        // Secrets access policy
        const secretsAccessPolicy = new aws.iam.Policy(`${name}-secrets-access-policy`, {
            description: "IAM policy for secrets access with least privilege",
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Action: [
                            "secretsmanager:GetSecretValue",
                            "secretsmanager:DescribeSecret",
                        ],
                        Resource: `arn:aws:secretsmanager:${args.region || "*"}:${args.accountId || "*"}:secret:sophia-ai/${args.environment}/*`,
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "kms:Decrypt",
                        ],
                        Resource: this.secretEncryptionKey.arn,
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-secrets-access-policy-${args.environment}`,
                Type: "IAMPolicy",
            },
        }, { parent: this });

        // S3 access policy
        const s3AccessPolicy = new aws.iam.Policy(`${name}-s3-access-policy`, {
            description: "IAM policy for S3 access with least privilege",
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Action: [
                            "s3:GetObject",
                            "s3:ListBucket",
                        ],
                        Resource: [
                            `arn:aws:s3:::${name}-*-${args.environment}`,
                            `arn:aws:s3:::${name}-*-${args.environment}/*`,
                        ],
                    },
                    {
                        Effect: "Allow",
                        Action: [
                            "kms:Decrypt",
                        ],
                        Resource: this.dataEncryptionKey.arn,
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-s3-access-policy-${args.environment}`,
                Type: "IAMPolicy",
            },
        }, { parent: this });

        // KMS access policy
        const kmsAccessPolicy = new aws.iam.Policy(`${name}-kms-access-policy`, {
            description: "IAM policy for KMS access with least privilege",
            policy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Action: [
                            "kms:Decrypt",
                            "kms:GenerateDataKey*",
                        ],
                        Resource: [
                            this.dataEncryptionKey.arn,
                            this.secretEncryptionKey.arn,
                        ],
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-kms-access-policy-${args.environment}`,
                Type: "IAMPolicy",
            },
        }, { parent: this });

        // Create IAM roles with least privilege

        // ML workloads role
        const mlWorkloadsRole = new aws.iam.Role(`${name}-ml-workloads-role`, {
            description: "IAM role for ML workloads with least privilege",
            assumeRolePolicy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: {
                            Service: "ec2.amazonaws.com",
                        },
                        Action: "sts:AssumeRole",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-ml-workloads-role-${args.environment}`,
                Type: "IAMRole",
            },
        }, { parent: this });

        // Attach policy to ML workloads role
        new aws.iam.RolePolicyAttachment(`${name}-ml-workloads-policy-attachment`, {
            role: mlWorkloadsRole,
            policyArn: mlWorkloadsPolicy.arn,
        }, { parent: this });

        // Data processing role
        const dataProcessingRole = new aws.iam.Role(`${name}-data-processing-role`, {
            description: "IAM role for data processing with least privilege",
            assumeRolePolicy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: {
                            Service: "ec2.amazonaws.com",
                        },
                        Action: "sts:AssumeRole",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-data-processing-role-${args.environment}`,
                Type: "IAMRole",
            },
        }, { parent: this });

        // Attach policy to data processing role
        new aws.iam.RolePolicyAttachment(`${name}-data-processing-policy-attachment`, {
            role: dataProcessingRole,
            policyArn: dataProcessingPolicy.arn,
        }, { parent: this });

        // Monitoring role
        const monitoringRole = new aws.iam.Role(`${name}-monitoring-role`, {
            description: "IAM role for monitoring with least privilege",
            assumeRolePolicy: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: {
                            Service: "ec2.amazonaws.com",
                        },
                        Action: "sts:AssumeRole",
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-monitoring-role-${args.environment}`,
                Type: "IAMRole",
            },
        }, { parent: this });

        // Attach policy to monitoring role
        new aws.iam.RolePolicyAttachment(`${name}-monitoring-policy-attachment`, {
            role: monitoringRole,
            policyArn: monitoringPolicy.arn,
        }, { parent: this });

        // Assign roles
        this.serviceRoles = {
            mlWorkloads: mlWorkloadsRole,
            dataProcessing: dataProcessingRole,
            monitoring: monitoringRole,
        };

        // Assign policies
        this.policies = {
            mlWorkloads: mlWorkloadsPolicy,
            dataProcessing: dataProcessingPolicy,
            monitoring: monitoringPolicy,
            secretsAccess: secretsAccessPolicy,
            s3Access: s3AccessPolicy,
            kmsAccess: kmsAccessPolicy,
        };

        // Create VPC endpoints for secure AWS service access

        // S3 VPC endpoint
        const s3VpcEndpoint = new aws.ec2.VpcEndpoint(`${name}-s3-vpc-endpoint`, {
            vpcId: args.vpcId,
            serviceName: `com.amazonaws.${args.region || "us-east-1"}.s3`,
            vpcEndpointType: "Gateway",
            routeTableIds: [], // Needs to be populated with route table IDs
            policyDocument: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: "*",
                        Action: [
                            "s3:GetObject",
                            "s3:ListBucket",
                        ],
                        Resource: [
                            `arn:aws:s3:::${name}-*-${args.environment}`,
                            `arn:aws:s3:::${name}-*-${args.environment}/*`,
                        ],
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-s3-vpc-endpoint-${args.environment}`,
                Type: "VPCEndpoint",
            },
        }, { parent: this });

        // DynamoDB VPC endpoint
        const dynamodbVpcEndpoint = new aws.ec2.VpcEndpoint(`${name}-dynamodb-vpc-endpoint`, {
            vpcId: args.vpcId,
            serviceName: `com.amazonaws.${args.region || "us-east-1"}.dynamodb`,
            vpcEndpointType: "Gateway",
            routeTableIds: [], // Needs to be populated with route table IDs
            policyDocument: JSON.stringify({
                Version: "2012-10-17",
                Statement: [
                    {
                        Effect: "Allow",
                        Principal: "*",
                        Action: [
                            "dynamodb:GetItem",
                            "dynamodb:Query",
                            "dynamodb:Scan",
                        ],
                        Resource: `arn:aws:dynamodb:${args.region || "*"}:${args.accountId || "*"}:table/sophia-ai-*-${args.environment}`,
                    },
                ],
            }),
            tags: {
                ...tags,
                Name: `${name}-dynamodb-vpc-endpoint-${args.environment}`,
                Type: "VPCEndpoint",
            },
        }, { parent: this });

        // Advanced security features
        let secretsManagerVpcEndpoint: aws.ec2.VpcEndpoint | undefined;
        let kmsVpcEndpoint: aws.ec2.VpcEndpoint | undefined;
        let ecrVpcEndpoint: aws.ec2.VpcEndpoint | undefined;
        let ecrApiVpcEndpoint: aws.ec2.VpcEndpoint | undefined;

        if (args.enableAdvancedSecurity) {
            // Secrets Manager VPC endpoint
            secretsManagerVpcEndpoint = new aws.ec2.VpcEndpoint(`${name}-secretsmanager-vpc-endpoint`, {
                vpcId: args.vpcId,
                serviceName: `com.amazonaws.${args.region || "us-east-1"}.secretsmanager`,
                vpcEndpointType: "Interface",
                subnetIds: [], // Needs to be populated with subnet IDs
                securityGroupIds: [], // Needs to be populated with security group IDs
                privateDnsEnabled: true,
                tags: {
                    ...tags,
                    Name: `${name}-secretsmanager-vpc-endpoint-${args.environment}`,
                    Type: "VPCEndpoint",
                },
            }, { parent: this });

            // KMS VPC endpoint
            kmsVpcEndpoint = new aws.ec2.VpcEndpoint(`${name}-kms-vpc-endpoint`, {
                vpcId: args.vpcId,
                serviceName: `com.amazonaws.${args.region || "us-east-1"}.kms`,
                vpcEndpointType: "Interface",
                subnetIds: [], // Needs to be populated with subnet IDs
                securityGroupIds: [], // Needs to be populated with security group IDs
                privateDnsEnabled: true,
                tags: {
                    ...tags,
                    Name: `${name}-kms-vpc-endpoint-${args.environment}`,
                    Type: "VPCEndpoint",
                },
            }, { parent: this });

            // ECR VPC endpoint
            ecrVpcEndpoint = new aws.ec2.VpcEndpoint(`${name}-ecr-vpc-endpoint`, {
                vpcId: args.vpcId,
                serviceName: `com.amazonaws.${args.region || "us-east-1"}.ecr.dkr`,
                vpcEndpointType: "Interface",
                subnetIds: [], // Needs to be populated with subnet IDs
                securityGroupIds: [], // Needs to be populated with security group IDs
                privateDnsEnabled: true,
                tags: {
                    ...tags,
                    Name: `${name}-ecr-vpc-endpoint-${args.environment}`,
                    Type: "VPCEndpoint",
                },
            }, { parent: this });

            // ECR API VPC endpoint
            ecrApiVpcEndpoint = new aws.ec2.VpcEndpoint(`${name}-ecr-api-vpc-endpoint`, {
                vpcId: args.vpcId,
                serviceName: `com.amazonaws.${args.region || "us-east-1"}.ecr.api`,
                vpcEndpointType: "Interface",
                subnetIds: [], // Needs to be populated with subnet IDs
                securityGroupIds: [], // Needs to be populated with security group IDs
                privateDnsEnabled: true,
                tags: {
                    ...tags,
                    Name: `${name}-ecr-api-vpc-endpoint-${args.environment}`,
                    Type: "VPCEndpoint",
                },
            }, { parent: this });
        }

        // Assign VPC endpoints
        this.vpcEndpoints = {
            s3: s3VpcEndpoint,
            dynamodb: dynamodbVpcEndpoint,
            secretsManager: secretsManagerVpcEndpoint,
            kms: kmsVpcEndpoint,
            ecr: ecrVpcEndpoint,
            ecrApi: ecrApiVpcEndpoint,
        };

        // Kubernetes security resources
        if (args.k8sProvider) {
            // Create network policies
            const denyAllIngressPolicy = new k8s.networking.v1.NetworkPolicy(`${name}-deny-all-ingress`, {
                metadata: {
                    name: "deny-all-ingress",
                    namespace: "default",
                },
                spec: {
                    podSelector: {},
                    policyTypes: ["Ingress"],
                },
            }, { provider: args.k8sProvider, parent: this });

            const allowInternalIngressPolicy = new k8s.networking.v1.NetworkPolicy(`${name}-allow-internal-ingress`, {
                metadata: {
                    name: "allow-internal-ingress",
                    namespace: "default",
                },
                spec: {
                    podSelector: {},
                    ingress: [
                        {
                            from: [
                                {
                                    podSelector: {},
                                },
                            ],
                        },
                    ],
                    policyTypes: ["Ingress"],
                },
            }, { provider: args.k8sProvider, parent: this });

            // Create Pod Security Policy
            const podSecurityPolicy = new k8s.policy.v1beta1.PodSecurityPolicy(`${name}-restricted-psp`, {
                metadata: {
                    name: "restricted-psp",
                },
                spec: {
                    privileged: false,
                    allowPrivilegeEscalation: false,
                    requiredDropCapabilities: ["ALL"],
                    volumes: [
                        "configMap",
                        "emptyDir",
                        "projected",
                        "secret",
                        "downwardAPI",
                        "persistentVolumeClaim",
                    ],
                    hostNetwork: false,
                    hostIpc: false,
                    hostPid: false,
                    runAsUser: {
                        rule: "MustRunAsNonRoot",
                    },
                    seLinux: {
                        rule: "RunAsAny",
                    },
                    supplementalGroups: {
                        rule: "MustRunAs",
                        ranges: [
                            {
                                min: 1,
                                max: 65535,
                            },
                        ],
                    },
                    fsGroup: {
                        rule: "MustRunAs",
                        ranges: [
                            {
                                min: 1,
                                max: 65535,
                            },
                        ],
                    },
                    readOnlyRootFilesystem: true,
                },
            }, { provider: args.k8sProvider, parent: this });

            // Create service accounts for ML workloads
            const mlServiceAccount = new k8s.core.v1.ServiceAccount(`${name}-ml-service-account`, {
                metadata: {
                    name: "ml-service-account",
                    namespace: "default",
                    annotations: {
                        "eks.amazonaws.com/role-arn": mlWorkloadsRole.arn,
                    },
                },
            }, { provider: args.k8sProvider, parent: this });

            // Create service account for data processing
            const dataServiceAccount = new k8s.core.v1.ServiceAccount(`${name}-data-service-account`, {
                metadata: {
                    name: "data-service-account",
                    namespace: "default",
                    annotations: {
                        "eks.amazonaws.com/role-arn": dataProcessingRole.arn,
                    },
                },
            }, { provider: args.k8sProvider, parent: this });

            // Create service account for monitoring
            const monitoringServiceAccount = new k8s.core.v1.ServiceAccount(`${name}-monitoring-service-account`, {
                metadata: {
                    name: "monitoring-service-account",
                    namespace: "default",
                    annotations: {
                        "eks.amazonaws.com/role-arn": monitoringRole.arn,
                    },
                },
            }, { provider: args.k8sProvider, parent: this });

            // Assign Kubernetes security resources
            this.k8sSecurityResources = {
                psp: podSecurityPolicy,
                networkPolicies: [
                    denyAllIngressPolicy,
                    allowInternalIngressPolicy,
                ],
                serviceAccounts: [
                    mlServiceAccount,
                    dataServiceAccount,
                    monitoringServiceAccount,
                ],
            };
        }

        // Register outputs
        this.registerOutputs({
            dataEncryptionKey: this.dataEncryptionKey,
            logEncryptionKey: this.logEncryptionKey,
            secretEncryptionKey: this.secretEncryptionKey,
            serviceRoles: this.serviceRoles,
            policies: this.policies,
            vpcEndpoints: this.vpcEndpoints,
            oidcProvider: this.oidcProvider,
            k8sSecurityResources: this.k8sSecurityResources,
        });
    }
}

/**
 * Create a KMS key for encrypting sensitive data
 */
export function createEncryptionKey(
    name: string,
    description: string,
    accountId: string,
    serviceNames: string[],
    keyAlias?: string,
    tags?: { [key: string]: string },
    parent?: pulumi.Resource,
): aws.kms.Key {
    // Create service statements
    const serviceStatements = serviceNames.map(serviceName => ({
        Effect: "Allow",
        Principal: {
            Service: `${serviceName}.amazonaws.com`,
        },
        Action: [
            "kms:GenerateDataKey*",
            "kms:Decrypt",
        ],
        Resource: "*",
    }));

    // Create KMS key
    const key = new aws.kms.Key(`${name}-key`, {
        description,
        enableKeyRotation: true,
        deletionWindowInDays: 30,
        policy: JSON.stringify({
            Version: "2012-10-17",
            Statement: [
                {
                    Effect: "Allow",
                    Principal: {
                        AWS: `arn:aws:iam::${accountId}:root`,
                    },
                    Action: "kms:*",
                    Resource: "*",
                },
                ...serviceStatements,
            ],
        }),
        tags,
    }, { parent });

    // Create alias if provided
    if (keyAlias) {
        new aws.kms.Alias(`${name}-alias`, {
            name: `alias/${keyAlias}`,
            targetKeyId: key.id,
        }, { parent });
    }

    return key;
}

/**
 * Create a least-privilege IAM policy for a specific service
 */
export function createLeastPrivilegePolicy(
    name: string,
    description: string,
    statements: any[],
    tags?: { [key: string]: string },
    parent?: pulumi.Resource,
): aws.iam.Policy {
    return new aws.iam.Policy(`${name}-policy`, {
        description,
        policy: JSON.stringify({
            Version: "2012-10-17",
            Statement: statements,
        }),
        tags,
    }, { parent });
}

/**
 * Create a service account with associated IAM role
 */
export function createServiceAccount(
    name: string,
    namespace: string,
    roleArn: pulumi.Input<string>,
    k8sProvider: k8s.Provider,
    annotations?: { [key: string]: string },
    parent?: pulumi.Resource,
): k8s.core.v1.ServiceAccount {
    return new k8s.core.v1.ServiceAccount(`${name}-sa`, {
        metadata: {
            name,
            namespace,
            annotations: {
                "eks.amazonaws.com/role-arn": roleArn,
                ...annotations,
            },
        },
    }, { provider: k8sProvider, parent });
}
