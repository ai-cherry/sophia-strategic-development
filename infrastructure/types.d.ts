/**
 * Explicit type declarations for Lambda Labs Kubernetes Infrastructure
 * These declarations help TypeScript resolve imports correctly
 * for our Lambda Labs + Kubernetes + Docker + Pulumi stack
 */

declare module '@pulumi/pulumi' {
    export * from '@pulumi/pulumi';

    export interface Input<T> {
        // Marker interface for Input types
    }

    export type Output<T> = {
        // Simplified Output type for reference
        apply<U>(func: (t: T) => Input<U>): Output<U>;
        apply<U>(func: (t: T) => U): Output<U>;
    };

    export function interpolate(literals: TemplateStringsArray, ...placeholders: any[]): Output<string>;

    export function output<T>(val: Input<T>): Output<T>;

    // Base resource class for all Pulumi resources
    export class Resource {
        constructor(type: string, name: string, custom: boolean, props?: any, opts?: ResourceOptions);
    }

    export class ComponentResource extends Resource {
        constructor(type: string, name: string, props?: any, opts?: ComponentResourceOptions);
        registerOutputs(outputs: { [key: string]: any }): void;
    }

    export interface ResourceOptions {
        parent?: Resource;
        provider?: any;
        dependsOn?: any[];
        protect?: boolean;
    }

    export interface ComponentResourceOptions extends ResourceOptions {
        // Additional component resource options
    }
}

declare module '@pulumi/kubernetes' {
    export * from '@pulumi/kubernetes';

    export class Provider {
        constructor(name: string, args: any, opts?: any);
    }

    export namespace apps {
        export namespace v1 {
            export class Deployment {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                public readonly status: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class StatefulSet {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class DaemonSet {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }

    export namespace core {
        export namespace v1 {
            export class Service {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class ConfigMap {
                public readonly metadata: Output<any>;
                public readonly data: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class Secret {
                public readonly metadata: Output<any>;
                public readonly data: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class Namespace {
                public readonly metadata: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class PersistentVolume {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class PersistentVolumeClaim {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class Pod {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }

    export namespace networking {
        export namespace v1 {
            export class NetworkPolicy {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class Ingress {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }

    export namespace rbac {
        export namespace v1 {
            export class Role {
                public readonly metadata: Output<any>;
                public readonly rules: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class RoleBinding {
                public readonly metadata: Output<any>;
                public readonly subjects: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class ClusterRole {
                public readonly metadata: Output<any>;
                public readonly rules: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class ClusterRoleBinding {
                public readonly metadata: Output<any>;
                public readonly subjects: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }

    export namespace storage {
        export namespace v1 {
            export class StorageClass {
                public readonly metadata: Output<any>;
                public readonly provisioner: Output<string>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }

    export namespace autoscaling {
        export namespace v2 {
            export class HorizontalPodAutoscaler {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }

    export namespace batch {
        export namespace v1 {
            export class Job {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }

            export class CronJob {
                public readonly metadata: Output<any>;
                public readonly spec: Output<any>;
                constructor(name: string, args: any, opts?: any);
            }
        }
    }
}

declare module '@pulumi/docker' {
    export * from '@pulumi/docker';

    export class Image {
        public readonly imageName: Output<string>;
        public readonly repoDigest: Output<string>;
        constructor(name: string, args: any, opts?: any);
    }

    export class Registry {
        public readonly id: Output<string>;
        public readonly server: Output<string>;
        constructor(name: string, args: any, opts?: any);
    }

    export class Container {
        public readonly id: Output<string>;
        public readonly name: Output<string>;
        constructor(name: string, args: any, opts?: any);
    }

    export class Network {
        public readonly id: Output<string>;
        public readonly name: Output<string>;
        constructor(name: string, args: any, opts?: any);
    }

    export class Volume {
        public readonly id: Output<string>;
        public readonly name: Output<string>;
        constructor(name: string, args: any, opts?: any);
    }
}

declare module '@pulumi/lambda-labs' {
    // Lambda Labs specific types for future integration
    export interface LambdaLabsInstanceArgs {
        instanceType: string;
        region: string;
        sshKeyName?: string;
        userData?: string;
        tags?: { [key: string]: string };
    }

    export class Instance {
        public readonly id: Output<string>;
        public readonly publicIp: Output<string>;
        public readonly privateIp: Output<string>;
        constructor(name: string, args: LambdaLabsInstanceArgs, opts?: any);
    }

    export interface LambdaLabsKubernetesArgs {
        instanceType: string;
        nodeCount: number;
        kubernetesVersion?: string;
        gpuType: string;
        region: string;
    }

    export class KubernetesCluster {
        public readonly id: Output<string>;
        public readonly kubeconfig: Output<string>;
        public readonly endpoint: Output<string>;
        constructor(name: string, args: LambdaLabsKubernetesArgs, opts?: any);
    }
}

// Sophia AI specific component types
declare module 'sophia-ai/components' {
    export interface LambdaLabsGPUWorkloadArgs {
        environment: string;
        gpuType: 'rtx-4090' | 'a10' | 'a100';
        replicas: number;
        modelName: string;
        containerImage: string;
        resources: {
            requests: {
                cpu: string;
                memory: string;
                'nvidia.com/gpu': string;
            };
            limits: {
                cpu: string;
                memory: string;
                'nvidia.com/gpu': string;
            };
        };
    }

    export interface ELIMINATEDCortexArgs {
        account: string;
        user: string;
        password: string;
        warehouse: string;
        database: string;
        schema: string;
        role?: string;
    }

    export interface PortkeyGatewayArgs {
        apiKey: string;
        virtualKey: string;
        baseUrl: string;
        cacheStrategy?: 'semantic' | 'exact' | 'disabled';
        retryPolicy?: {
            maxRetries: number;
            backoffMultiplier: number;
            maxBackoffTime: number;
        };
    }

    export interface EstuaryFlowArgs {
        accessToken: string;
        flowName: string;
        sourceConnector: string;
        destinationConnector: string;
        transformations?: any[];
    }

    export interface SecretManagerArgs {
        environment: string;
        pulumiOrg: string;
        escEnvironment: string;
        githubOrgSecrets: boolean;
        rotationPeriod: string;
    }
}

// AI/ML specific types
declare module 'sophia-ai/ml' {
    export interface ModelDeploymentArgs {
        modelName: string;
        modelVersion: string;
        containerImage: string;
        gpuEnabled: boolean;
        replicas: number;
        resources: {
            cpu: string;
            memory: string;
            gpu?: string;
        };
        environment: string;
    }

    export interface VectorDatabaseArgs {
        provider: 'pinecone' | 'weaviate' | 'qdrant';
        dimension: number;
        metric: 'cosine' | 'euclidean' | 'dotproduct';
        environment: string;
        apiKey: string;
    }

    export interface InferenceEndpointArgs {
        modelName: string;
        endpoint: string;
        authentication: 'api-key' | 'oauth' | 'none';
        rateLimit?: {
            requestsPerMinute: number;
            burstSize: number;
        };
        caching?: {
            enabled: boolean;
            ttl: number;
        };
    }
}

// Security and monitoring types
declare module 'sophia-ai/security' {
    export interface SecurityPolicyArgs {
        namespace: string;
        podSecurityStandard: 'privileged' | 'baseline' | 'restricted';
        networkPolicies: boolean;
        rbacEnabled: boolean;
        secretScanning: boolean;
        vulnerabilityScanning: boolean;
    }

    export interface MonitoringStackArgs {
        prometheus: {
            enabled: boolean;
            retention: string;
            storageClass: string;
        };
        grafana: {
            enabled: boolean;
            dashboards: string[];
        };
        alerting: {
            rules: Array<{
                name: string;
                condition: string;
                duration: string;
                severity: 'warning' | 'critical';
            }>;
        };
    }
}

// Data pipeline types
declare module 'sophia-ai/data' {
    export interface DataPipelineArgs {
        name: string;
        source: {
            type: 'ELIMINATED' | 'postgres' | 'api' | 'file';
            connection: any;
        };
        destination: {
            type: 'ELIMINATED' | 'pinecone' | 'weaviate' | 'file';
            connection: any;
        };
        transformations: Array<{
            type: 'sql' | 'python' | 'dbt';
            config: any;
        }>;
        schedule?: string;
    }

    export interface EmbeddingPipelineArgs {
        modelName: string;
        inputSource: string;
        outputDestination: string;
        batchSize: number;
        dimension: number;
        environment: string;
    }
}
