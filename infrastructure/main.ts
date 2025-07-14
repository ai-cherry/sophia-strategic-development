import * as pulumi from "@pulumi/pulumi";
import {
    qdrantEndpoint,
    redisEndpoint,
    postgresqlEndpoint,
    lambdaInferenceEndpoint,
    stackInfo
} from "./pulumi/index";

// Export the new infrastructure outputs
export const qdrantUrl = qdrantEndpoint;
export const redisUrl = redisEndpoint;
export const postgresqlUrl = postgresqlEndpoint;
export const lambdaInferenceUrl = lambdaInferenceEndpoint;
export const deploymentInfo = stackInfo;

// Export all infrastructure endpoints
export const endpoints = {
  qdrant: qdrantEndpoint,
  // Add other endpoints as needed
};

// Log deployment info
pulumi.log.info("Sophia AI Infrastructure Deployed:");
pulumi.log.info(`- Qdrant: ${qdrantEndpoint}`);
pulumi.log.info(`- Pure Qdrant Architecture: ✅`);
