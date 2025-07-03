import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import { StorageComponents, StorageArgs } from "./index"; // Assuming index.ts exports these

// Main program entrypoint
async function main() {
    // Fetch configuration for the production environment
    // In a real scenario, these values would come from Pulumi config, another service, or be hardcoded for a specific environment.
    const config = new pulumi.Config();
    
    // Example VPC and Subnet details. Replace with your actual network configuration.
    // For this example, we'll look up the default VPC.
    const vpc = await aws.ec2.getVpc({ default: true });
    const subnets = await aws.ec2.getSubnetIds({ vpcId: vpc.id });

    const storageArgs: StorageArgs = {
        environment: "production",
        vpcId: vpc.id,
        subnetIds: subnets.ids,
        securityGroupIds: [], // Replace with actual security group IDs if needed
        s3Config: {
            enableVersioning: true,
        },
        rdsConfig: {
            instanceClass: "db.t3.micro",
            allocatedStorage: 20,
            engine: "postgres",
            engineVersion: "14.1",
            multiAz: false, // Set to true for production high availability
        },
        tags: {
            "Owner": "SophiaAI",
            "Project": "Phoenix",
        },
    };

    // Instantiate our storage infrastructure
    const storage = new StorageComponents("sophia-production-storage", storageArgs);

    // Export any important URLs, IDs, or endpoints
    return {
        modelArtifactsBucketName: storage.s3Buckets.modelArtifacts.bucket,
        trainingDataBucketName: storage.s3Buckets.trainingData.bucket,
        rdsEndpoint: storage.rdsInstances?.primary.endpoint,
    };
}

// Export the outputs of the main function
export const outputs = main(); 