declare module 'child_process' {
    export function execSync(command: string): Buffer;
}

declare module '@pulumi/pulumi' {
    export class Config {
        constructor(name?: string);
        require(key: string): string;
        requireSecret(key: string): pulumi.Output<string>;
        get(key: string): string | undefined;
        getSecret(key: string): pulumi.Output<string | undefined>;
    }
    
    export function output<T>(val: T | Promise<T>): Output<T>;
    export function interpolate(literals: TemplateStringsArray, ...placeholders: any[]): Output<string>;
    
    export interface Output<T> {
        apply<U>(func: (t: T) => U | Promise<U>): Output<U>;
        get(): Promise<T>;
    }
}

declare module '@pulumi/kubernetes' {
    // Add K8s type declarations as needed
}

declare module '@pulumi/docker' {
    // Add Docker type declarations as needed
}
