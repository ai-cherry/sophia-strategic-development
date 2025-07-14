import * as pulumi from "@pulumi/pulumi";

export interface modern_stackDatabase {
    name: string;
    schemas: string[];
    warehouses: string[];
}

export interface modern_stackProviderArgs {
    account: pulumi.Input<string>;
    username: pulumi.Input<string>;
    password: pulumi.Input<string>;
    role: pulumi.Input<string>;
    databases: modern_stackDatabase[];
}

export class modern_stackProvider extends pulumi.ComponentResource {
    public database: pulumi.Output<any>;

    constructor(name: string, args: modern_stackProviderArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:modern_stack", name, {}, opts);

        // In a real implementation, this would use the modern_stack provider
        // For now, we'll create a mock configuration
        this.database = pulumi.output({
            account: args.account,
            databases: args.databases.map(db => ({
                name: db.name,
                schemas: db.schemas,
                warehouses: db.warehouses,
                status: "configured"
            }))
        });

        // Register outputs
        this.registerOutputs({
            database: this.database
        });
    }
}
