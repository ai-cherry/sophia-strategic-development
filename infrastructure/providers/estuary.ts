import * as pulumi from "@pulumi/pulumi";

export interface EstuaryFlow {
    name: string;
    source: string;
    destination: string;
    schedule: string;
}

export interface EstuaryProviderArgs {
    accessToken: pulumi.Input<string>;
    tenant: pulumi.Input<string>;
    flows: EstuaryFlow[];
}

export class EstuaryProvider extends pulumi.ComponentResource {
    public flows: pulumi.Output<any[]>;

    constructor(name: string, args: EstuaryProviderArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:Estuary", name, {}, opts);

        // In a real implementation, this would use the Estuary API
        // For now, we'll create a mock configuration
        this.flows = pulumi.output(args.flows.map(flow => ({
            name: flow.name,
            source: flow.source,
            destination: flow.destination,
            schedule: flow.schedule,
            tenant: args.tenant,
            status: "configured"
        })));

        // Register outputs
        this.registerOutputs({
            flows: this.flows
        });
    }
}
