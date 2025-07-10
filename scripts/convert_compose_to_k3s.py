#!/usr/bin/env python3
"""
Convert Docker Compose MCP Server Configurations to K3s Manifests
Specifically designed for Sophia AI MCP server migration
Date: July 10, 2025
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


class ComposeToK3sConverter:
    """Convert Docker Compose configurations to K3s manifests"""

    def __init__(self, compose_file: str, output_dir: str = "k3s-manifests"):
        self.compose_file = compose_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # MCP server specific configurations
        self.mcp_config = {
            "ai-memory": {"port": 9000, "gpu": True, "tier": "PRIMARY"},
            "snowflake-unified": {"port": 9001, "gpu": False, "tier": "PRIMARY"},
            "github": {"port": 9003, "gpu": False, "tier": "PRIMARY"},
            "slack": {"port": 9004, "gpu": False, "tier": "PRIMARY"},
            "gong": {"port": 9005, "gpu": False, "tier": "PRIMARY"},
            "codacy": {"port": 9008, "gpu": False, "tier": "SECONDARY"},
            "hubspot": {"port": 9009, "gpu": False, "tier": "SECONDARY"},
            "linear": {"port": 9002, "gpu": False, "tier": "SECONDARY"},
            "notion": {"port": 9007, "gpu": False, "tier": "SECONDARY"},
            "asana": {"port": 9006, "gpu": False, "tier": "SECONDARY"},
        }

    def load_compose(self) -> dict[str, Any]:
        """Load Docker Compose file"""
        with open(self.compose_file) as f:
            return yaml.safe_load(f)

    def convert_service_to_deployment(
        self, name: str, service: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert a Docker Compose service to K3s Deployment"""

        # Extract service details
        image = service.get("image", f"scoobyjava15/mcp-{name}:latest")
        ports = service.get("ports", [])
        environment = service.get("environment", [])
        deploy = service.get("deploy", {})

        # Get MCP specific config
        mcp_info = self.mcp_config.get(name, {})
        port = mcp_info.get("port", 9000)
        needs_gpu = mcp_info.get("gpu", False)
        tier = mcp_info.get("tier", "SECONDARY")

        # Create deployment manifest
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"mcp-{name}",
                "namespace": "sophia-mcp",
                "labels": {
                    "app": f"mcp-{name}",
                    "tier": "mcp",
                    "service-tier": tier.lower(),
                    "version": "v1.0.0",
                },
            },
            "spec": {
                "replicas": deploy.get("replicas", 2 if tier == "PRIMARY" else 1),
                "selector": {"matchLabels": {"app": f"mcp-{name}"}},
                "template": {
                    "metadata": {
                        "labels": {
                            "app": f"mcp-{name}",
                            "tier": "mcp",
                            "service-tier": tier.lower(),
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "ports": [{"containerPort": port, "name": "mcp"}],
                                "env": self._convert_environment(environment),
                                "envFrom": [
                                    {"secretRef": {"name": f"mcp-{name}-secrets"}}
                                ],
                                "resources": self._get_resources(deploy, needs_gpu),
                                "livenessProbe": {
                                    "httpGet": {"path": "/health", "port": "mcp"},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": "/ready", "port": "mcp"},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ]
                    },
                },
            },
        }

        # Add GPU specific configurations
        if needs_gpu:
            deployment["spec"]["template"]["spec"]["nodeSelector"] = {
                "nvidia.com/gpu": "true"
            }
            deployment["spec"]["template"]["spec"]["runtimeClassName"] = "nvidia"

        return deployment

    def create_service(self, name: str, port: int) -> dict[str, Any]:
        """Create K3s Service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"mcp-{name}",
                "namespace": "sophia-mcp",
                "labels": {"app": f"mcp-{name}"},
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [
                    {
                        "port": port,
                        "targetPort": "mcp",
                        "protocol": "TCP",
                        "name": "mcp",
                    }
                ],
                "selector": {"app": f"mcp-{name}"},
            },
        }

    def create_configmap(self, name: str) -> dict[str, Any]:
        """Create ConfigMap for service configuration"""
        mcp_info = self.mcp_config.get(name, {})

        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": f"mcp-{name}-config", "namespace": "sophia-mcp"},
            "data": {
                "server-config.json": json.dumps(
                    {
                        "name": name,
                        "version": "1.0.0",
                        "port": mcp_info.get("port", 9000),
                        "tier": mcp_info.get("tier", "SECONDARY"),
                        "description": f"MCP {name} server",
                    },
                    indent=2,
                )
            },
        }

    def create_hpa(self, name: str, tier: str) -> dict[str, Any]:
        """Create Horizontal Pod Autoscaler"""
        min_replicas = 2 if tier == "PRIMARY" else 1
        max_replicas = 10 if tier == "PRIMARY" else 5

        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {"name": f"mcp-{name}-hpa", "namespace": "sophia-mcp"},
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"mcp-{name}",
                },
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {"type": "Utilization", "averageUtilization": 70},
                        },
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {"type": "Utilization", "averageUtilization": 80},
                        },
                    },
                ],
            },
        }

    def _convert_environment(self, env_list: list[Any]) -> list[dict[str, str]]:
        """Convert environment variables from compose to K8s format"""
        env_vars = []

        # Default environment variables for all MCP servers
        env_vars.extend(
            [
                {"name": "ENVIRONMENT", "value": "prod"},
                {"name": "PULUMI_ORG", "value": "scoobyjava-org"},
                {"name": "K3S_DEPLOYMENT", "value": "true"},
            ]
        )

        # Convert compose environment variables
        for env in env_list:
            if isinstance(env, str) and "=" in env:
                key, value = env.split("=", 1)
                # Skip secrets that should come from SecretRef
                if any(
                    secret in key.lower()
                    for secret in ["password", "token", "key", "secret"]
                ):
                    continue
                env_vars.append({"name": key, "value": value})
            elif isinstance(env, dict):
                for key, value in env.items():
                    if not any(
                        secret in key.lower()
                        for secret in ["password", "token", "key", "secret"]
                    ):
                        env_vars.append({"name": key, "value": str(value)})

        return env_vars

    def _get_resources(self, deploy: dict[str, Any], needs_gpu: bool) -> dict[str, Any]:
        """Get resource requirements"""
        resources = deploy.get("resources", {})
        limits = resources.get("limits", {})

        # Default resources based on GPU needs
        if needs_gpu:
            return {
                "requests": {"memory": "4Gi", "cpu": "2", "nvidia.com/gpu": "1"},
                "limits": {"memory": "8Gi", "cpu": "4", "nvidia.com/gpu": "1"},
            }
        else:
            return {
                "requests": {
                    "memory": limits.get("memory", "1Gi"),
                    "cpu": limits.get("cpus", "500m"),
                },
                "limits": {
                    "memory": limits.get("memory", "2Gi"),
                    "cpu": limits.get("cpus", "1"),
                },
            }

    def convert(self):
        """Convert Docker Compose to K3s manifests"""
        compose_data = self.load_compose()
        services = compose_data.get("services", {})

        print(f"Converting {len(services)} services to K3s manifests...")

        for service_name, service_config in services.items():
            # Clean service name (remove -v2 suffixes for consistency)
            clean_name = service_name.replace("-v2", "").replace("_", "-")

            # Skip non-MCP services
            if not any(mcp in clean_name for mcp in self.mcp_config.keys()):
                print(f"Skipping non-MCP service: {service_name}")
                continue

            print(f"\nConverting {service_name} -> mcp-{clean_name}")

            # Get MCP configuration
            mcp_info = self.mcp_config.get(clean_name, {})
            port = mcp_info.get("port", 9000)
            tier = mcp_info.get("tier", "SECONDARY")

            # Create manifests
            manifests = []

            # Deployment
            deployment = self.convert_service_to_deployment(clean_name, service_config)
            manifests.append(deployment)

            # Service
            service = self.create_service(clean_name, port)
            manifests.append(service)

            # ConfigMap
            configmap = self.create_configmap(clean_name)
            manifests.append(configmap)

            # HPA
            hpa = self.create_hpa(clean_name, tier)
            manifests.append(hpa)

            # Write to file
            output_file = self.output_dir / f"mcp-{clean_name}.yaml"
            with open(output_file, "w") as f:
                yaml.dump_all(manifests, f, default_flow_style=False)

            print(f"✓ Created {output_file}")

        # Create kustomization.yaml
        self._create_kustomization()

        print(f"\n✅ Conversion complete! Manifests saved to {self.output_dir}/")

    def _create_kustomization(self):
        """Create kustomization.yaml for easy deployment"""
        resources = sorted([f.name for f in self.output_dir.glob("mcp-*.yaml")])

        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "namespace": "sophia-mcp",
            "resources": resources,
            "commonLabels": {
                "app.kubernetes.io/part-of": "sophia-ai",
                "app.kubernetes.io/managed-by": "k3s",
            },
        }

        with open(self.output_dir / "kustomization.yaml", "w") as f:
            yaml.dump(kustomization, f, default_flow_style=False)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Docker Compose MCP configurations to K3s manifests"
    )
    parser.add_argument("compose_file", help="Path to Docker Compose file")
    parser.add_argument(
        "-o",
        "--output",
        default="k3s-manifests",
        help="Output directory for K3s manifests (default: k3s-manifests)",
    )

    args = parser.parse_args()

    # Check if compose file exists
    if not Path(args.compose_file).exists():
        print(f"Error: Compose file '{args.compose_file}' not found")
        sys.exit(1)

    # Convert
    converter = ComposeToK3sConverter(args.compose_file, args.output)
    converter.convert()


if __name__ == "__main__":
    main()
