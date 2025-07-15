import * as pulumi from "@pulumi/pulumi";

export interface PortkeyProject {
    name: string;
    virtualKeys: boolean;
    costAlerts?: {
        daily: number;
        monthly: number;
    };
}

export interface PortkeyProviderArgs {
    apiKey: pulumi.Input<string>;
    projects: PortkeyProject[];
}

export class PortkeyProvider extends pulumi.ComponentResource {
    public project: pulumi.Output<any>;

    constructor(name: string, args: PortkeyProviderArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:Portkey", name, {}, opts);

        // In a real implementation, this would use the Portkey API
        // For now, we'll create a mock configuration
        this.project = pulumi.output({
            projects: args.projects.map(project => ({
                name: project.name,
                virtualKeys: project.virtualKeys,
                costAlerts: project.costAlerts,
                status: "configured"
            }))
        });

        // Register outputs
        this.registerOutputs({
            project: this.project
        });
    }
}
