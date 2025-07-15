import * as pulumi from "@pulumi/pulumi";

export interface GitHubRepository {
    name: string;
    private: boolean;
    branchProtection?: {
        branches: string[];
        requiredReviews?: number;
    };
}

export interface GitHubProviderArgs {
    token: pulumi.Input<string>;
    organization: string;
    repositories: GitHubRepository[];
    secrets?: {
        organization: boolean;
        syncWithPulumiESC: boolean;
    };
}

export class GitHubProvider extends pulumi.ComponentResource {
    public repositories: pulumi.Output<any[]>;

    constructor(name: string, args: GitHubProviderArgs, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:GitHub", name, {}, opts);

        // In a real implementation, this would use the GitHub provider
        // For now, we'll create a mock configuration
        this.repositories = pulumi.output(args.repositories.map(repo => ({
            name: repo.name,
            organization: args.organization,
            private: repo.private,
            branchProtection: repo.branchProtection,
            status: "configured"
        })));

        // Register outputs
        this.registerOutputs({
            repositories: this.repositories
        });
    }
}
