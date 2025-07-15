import * as pulumi from "@pulumi/pulumi";
import axios from "axios";
import { decode } from "base-64";

export interface LambdaLabsInstanceConfig {
    name: string;
    instanceType: string;
    region: string;
    userData?: pulumi.Input<string>;
}

export class LambdaLabsProvider extends pulumi.ComponentResource {
    public instances: pulumi.Output<any[]>;

    constructor(name: string, args: {
        apiKey: pulumi.Input<string>;
        sshPublicKeyBase64: pulumi.Input<string>;
        instances: LambdaLabsInstanceConfig[];
    }, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:LambdaLabs", name, {}, opts);

        // Decode SSH public key
        const sshPublicKey = pulumi.output(args.sshPublicKeyBase64).apply(
            key => Buffer.from(key, 'base64').toString('utf-8')
        );

        // Create instances
        this.instances = pulumi.output(args.instances.map(instance => {
            // Inject SSH key into user data
            const userData = pulumi.interpolate`#!/bin/bash
echo "${sshPublicKey}" >> /home/ubuntu/.ssh/authorized_keys
${instance.userData || ""}
`;

            // Here we would call Lambda Labs API to create instance
            // For now, return a mock instance
            return {
                name: instance.name,
                type: instance.instanceType,
                region: instance.region,
                status: "provisioning",
                userData: userData,
            };
        }));
    }
}
