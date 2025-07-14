import * as pulumi from "@pulumi/pulumi";
import {
    weaviateEndpoint,
    redisEndpoint,
    postgresqlEndpoint,
    lambdaInferenceEndpoint,
    stackInfo
} from "./pulumi/index";

// Export the new infrastructure outputs
export const weaviateUrl = weaviateEndpoint;
export const redisUrl = redisEndpoint;
export const postgresqlUrl = postgresqlEndpoint;
export const lambdaInferenceUrl = lambdaInferenceEndpoint;
export const deploymentInfo = stackInfo;

// Log deployment info
pulumi.log.info("Sophia AI Memory Architecture deployed:");
pulumi.log.info(`- Weaviate: ${weaviateEndpoint}`);
pulumi.log.info(`- Redis: ${redisEndpoint}`);
pulumi.log.info(`- PostgreSQL: ${postgresqlEndpoint}`);
pulumi.log.info(`- Lambda Inference: ${lambdaInferenceEndpoint}`);
