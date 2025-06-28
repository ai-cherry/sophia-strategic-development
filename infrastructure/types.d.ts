/**
 * Explicit type declarations for Pulumi packages
 * These declarations help TypeScript resolve imports correctly
 * even when module resolution is challenging
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

declare module '@pulumi/aws' {
    export * from '@pulumi/aws';
    
    export namespace s3 {
        export class Bucket {
            public readonly id: Output<string>;
            public readonly arn: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
        
        export class BucketReplicationConfiguration {
            constructor(name: string, args: {
                bucket: Input<string>;
                role: Input<string>;
                rules: Input<any[]>;
            }, opts?: any);
        }
    }
    
    export namespace rds {
        export class Instance {
            public readonly id: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
        export class SubnetGroup {
            public readonly name: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
        export class ParameterGroup {
            public readonly name: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
    }
    
    export namespace dynamodb {
        export class Table {
            public readonly id: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
    }
    
    export namespace appautoscaling {
        export class Target {
            public readonly resourceId: Output<string>;
            public readonly scalableDimension: Output<string>;
            public readonly serviceNamespace: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
        export class Policy {
            constructor(name: string, args: any, opts?: any);
        }
    }
    
    export namespace efs {
        export class FileSystem {
            public readonly id: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
        export class MountTarget {
            constructor(name: string, args: any, opts?: any);
        }
    }
    
    export namespace elasticache {
        export class Cluster {
            constructor(name: string, args: any, opts?: any);
        }
        export class SubnetGroup {
            public readonly name: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
        export class ParameterGroup {
            public readonly name: Output<string>;
            constructor(name: string, args: any, opts?: any);
        }
    }
}

declare module '@pulumi/kubernetes' {
    export * from '@pulumi/kubernetes';
    
    export class Provider {
        constructor(name: string, args: any, opts?: any);
    }
    
    export namespace storage {
        export namespace v1 {
            export class StorageClass {
                constructor(name: string, args: any, opts?: any);
            }
        }
    }
}