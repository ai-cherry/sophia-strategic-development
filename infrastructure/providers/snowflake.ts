import * as pulumi from "@pulumi/pulumi";

export interface SnowflakeDatabase {
    name: string;
    schemas: string[];
    warehouses: string[];
}

export interface SnowflakeProviderArgs {
    account: pulumi.Input<string>;
    username: pulumi.Input<string>;
    password: pulumi.Input<string>;
    role: pulumi.Input<string>;
    databases: SnowflakeDatabase[];
}

export class SnowflakeProvider extends pulumi.ComponentResource {
    public database: pulumi.Output<any>;

    constructor(name: string, args: SnowflakeProviderArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:Snowflake", name, {}, opts);

        // In a real implementation, this would use the Snowflake provider
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
