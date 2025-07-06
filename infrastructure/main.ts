import * as pulumi from "@pulumi/pulumi";
import {
    lambdaLabsInstances,
    snowflakeDatabase,
    estuaryFlows,
    githubRepos,
    portkeyProject
} from "./index";

// Export the infrastructure outputs
export const lambdaLabsInstanceIPs = lambdaLabsInstances.apply(instances =>
    instances.map(i => ({ name: i.name, ip: i.publicIp }))
);
export const snowflakeDatabaseName = snowflakeDatabase;
export const estuaryFlowNames = estuaryFlows.apply(flows =>
    flows.map(f => f.name)
);
export const githubRepoNames = githubRepos.apply(repos =>
    repos.map(r => r.name)
);
export const portkeyProjectName = portkeyProject;
