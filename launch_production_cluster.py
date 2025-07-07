#!/usr/bin/env python3
"""
Sophia AI Production Cluster Provisioning
Creates a 3-node GH200 cluster for production deployment
"""

import json
import os
import subprocess
import time
from datetime import datetime

# Lambda Labs Configuration
LAMBDA_API_KEY = os.getenv(
    "LAMBDA_LABS_API_KEY",
    "secret_pulumi_87a092f03b5e4896a56542ed6e07d249.bHCTOCe4mkvm9jiT53DWZpnewReAoGic",
)
LAMBDA_API_URL = "https://cloud.lambdalabs.com/api/v1"

# Cluster Configuration
CLUSTER_CONFIG = {
    "nodes": [
        {
            "name": "lynn-sophia-gh200-worker-01",
            "role": "worker",
            "instance_type": "gpu_1x_gh200",
            "region": "us-east-3",
        },
        {
            "name": "lynn-sophia-gh200-worker-02",
            "role": "worker",
            "instance_type": "gpu_1x_gh200",
            "region": "us-east-3",
        },
    ],
    "ssh_key": "lynn-sophia-key",
    "master_ip": "192.222.51.151",
}


def launch_instances():
    """Launch Lambda Labs instances for the cluster"""
    print("🚀 Launching Lambda Labs GH200 Cluster...")

    launched_instances = []

    for node in CLUSTER_CONFIG["nodes"]:
        print(f"\n📦 Launching {node['name']}...")

        launch_data = {
            "region_name": node["region"],
            "instance_type_name": node["instance_type"],
            "ssh_key_names": [CLUSTER_CONFIG["ssh_key"]],
            "name": node["name"],
            "quantity": 1,
        }

        cmd = [
            "curl",
            "-u",
            f"{LAMBDA_API_KEY}:",
            "-X",
            "POST",
            "-H",
            "Content-Type: application/json",
            f"{LAMBDA_API_URL}/instance-operations/launch",
            "-d",
            json.dumps(launch_data),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if "data" in response and "instance_ids" in response["data"]:
                instance_id = response["data"]["instance_ids"][0]
                launched_instances.append(
                    {"id": instance_id, "name": node["name"], "role": node["role"]}
                )
                print(f"✅ Launched {node['name']}: {instance_id}")
            else:
                print(f"❌ Failed to launch {node['name']}: {response}")
        else:
            print(f"❌ API call failed: {result.stderr}")

    return launched_instances


def wait_for_instances(instances):
    """Wait for instances to become active and get IPs"""
    print("\n⏳ Waiting for instances to become active...")

    instance_details = []
    max_wait = 300  # 5 minutes
    start_time = time.time()

    while time.time() - start_time < max_wait:
        all_ready = True

        # Get instance status
        cmd = ["curl", "-u", f"{LAMBDA_API_KEY}:", f"{LAMBDA_API_URL}/instances"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            response = json.loads(result.stdout)

            for instance in instances:
                found = False
                for inst_data in response["data"]:
                    if inst_data["id"] == instance["id"]:
                        found = True
                        if inst_data["status"] == "active" and inst_data.get("ip"):
                            # Update instance details
                            instance_exists = False
                            for detail in instance_details:
                                if detail["id"] == instance["id"]:
                                    instance_exists = True
                                    break

                            if not instance_exists:
                                instance_details.append(
                                    {
                                        "id": instance["id"],
                                        "name": instance["name"],
                                        "role": instance["role"],
                                        "ip": inst_data["ip"],
                                        "private_ip": inst_data.get("private_ip"),
                                        "status": "active",
                                    }
                                )
                                print(
                                    f"✅ {instance['name']} is active: {inst_data['ip']}"
                                )
                        else:
                            all_ready = False
                        break

                if not found:
                    all_ready = False

        if all_ready and len(instance_details) == len(instances):
            break

        time.sleep(10)

    return instance_details


def generate_cluster_config(instances):
    """Generate cluster configuration file"""
    print("\n📝 Generating cluster configuration...")

    cluster_config = {
        "cluster_name": "sophia-ai-production",
        "created": datetime.now().isoformat(),
        "master": {
            "name": "lynn-sophia-gh200-master-01",
            "ip": CLUSTER_CONFIG["master_ip"],
            "role": "master",
        },
        "workers": instances,
        "total_nodes": len(instances) + 1,
        "ssh_key": CLUSTER_CONFIG["ssh_key"],
        "kubernetes": {"version": "v1.28.4", "cni": "flannel", "ingress": "nginx"},
    }

    with open("sophia_cluster_config.json", "w") as f:
        json.dump(cluster_config, f, indent=2)

    print("✅ Cluster configuration saved to sophia_cluster_config.json")

    return cluster_config


def main():
    print("🎯 Sophia AI Production Cluster Provisioning")
    print("=" * 50)

    # Launch instances
    instances = launch_instances()

    if not instances:
        print("❌ No instances launched. Exiting.")
        return

    # Wait for instances
    active_instances = wait_for_instances(instances)

    if len(active_instances) != len(instances):
        print(
            f"⚠️  Only {len(active_instances)}/{len(instances)} instances became active"
        )

    # Generate configuration
    cluster_config = generate_cluster_config(active_instances)

    # Print summary
    print("\n🎉 Cluster Provisioning Complete!")
    print("=" * 50)
    print(f"Master Node: {cluster_config['master']['ip']}")
    for worker in cluster_config["workers"]:
        print(f"Worker {worker['name']}: {worker['ip']}")

    print(f"\nTotal cluster size: {cluster_config['total_nodes']} nodes")
    print(f"Total GPU memory: {cluster_config['total_nodes'] * 96}GB")


if __name__ == "__main__":
    main()
