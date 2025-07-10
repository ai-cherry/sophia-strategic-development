#!/usr/bin/env python3
"""
Generate Kubernetes manifests for Sophia AI services.

This script creates the necessary K8s YAML files for deploying
all Sophia AI services to the K3s cluster on Lambda Labs.
"""

import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class K8sManifestGenerator:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.k8s_dir = self.root_dir / "kubernetes"
        self.base_dir = self.k8s_dir / "base"
        self.overlays_dir = self.k8s_dir / "overlays"

        # Service configurations
        self.services = {
            "sophia-api": {
                "image": "scoobyjava15/sophia-api:latest",
                "port": 8001,
                "replicas": 3,
                "env": {"ENVIRONMENT": "prod", "PULUMI_ORG": "scoobyjava-org"},
                "resources": {
                    "requests": {"cpu": "100m", "memory": "256Mi"},
                    "limits": {"cpu": "500m", "memory": "512Mi"},
                },
            },
            "mcp-servers": {
                "image": "scoobyjava15/mcp-servers:latest",
                "port": 9000,
                "replicas": 2,
                "env": {"ENVIRONMENT": "prod", "MCP_SERVER_TYPE": "unified"},
                "resources": {
                    "requests": {"cpu": "50m", "memory": "128Mi"},
                    "limits": {"cpu": "200m", "memory": "256Mi"},
                },
            },
            "redis": {
                "image": "redis:7-alpine",
                "port": 6379,
                "replicas": 1,
                "persistent": True,
                "resources": {
                    "requests": {"cpu": "50m", "memory": "64Mi"},
                    "limits": {"cpu": "100m", "memory": "128Mi"},
                },
            },
        }

    def create_directory_structure(self):
        """Create the K8s directory structure."""
        directories = [
            self.base_dir,
            self.base_dir / "deployments",
            self.base_dir / "services",
            self.base_dir / "configmaps",
            self.base_dir / "ingress",
            self.overlays_dir / "production",
            self.overlays_dir / "staging",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {directory.relative_to(self.root_dir)}")

    def generate_namespace(self):
        """Generate namespace manifest."""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "sophia-ai-prod",
                "labels": {"app": "sophia-ai", "environment": "production"},
            },
        }

        path = self.base_dir / "namespace.yaml"
        with open(path, "w") as f:
            yaml.dump(namespace, f, default_flow_style=False)
        logger.info(f"📝 Created: {path.relative_to(self.root_dir)}")

    def generate_deployment(self, name, config):
        """Generate deployment manifest for a service."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": "sophia-ai-prod",
                "labels": {
                    "app": name,
                    "component": "backend" if "api" in name else "infrastructure",
                },
            },
            "spec": {
                "replicas": config["replicas"],
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": config["image"],
                                "ports": [
                                    {"containerPort": config["port"], "name": "http"}
                                ],
                                "env": [
                                    {"name": k, "value": v}
                                    for k, v in config.get("env", {}).items()
                                ],
                                "resources": config.get("resources", {}),
                                "livenessProbe": {
                                    "httpGet": {"path": "/health", "port": "http"},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                }
                                if "api" in name or "mcp" in name
                                else None,
                                "readinessProbe": {
                                    "httpGet": {"path": "/health", "port": "http"},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                }
                                if "api" in name or "mcp" in name
                                else None,
                            }
                        ]
                    },
                },
            },
        }

        # Add persistent volume for Redis
        if config.get("persistent"):
            deployment["spec"]["template"]["spec"]["volumes"] = [
                {"name": "data", "persistentVolumeClaim": {"claimName": f"{name}-pvc"}}
            ]
            deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = [
                {"name": "data", "mountPath": "/data"}
            ]

        # Remove None values
        deployment = self._remove_none_values(deployment)

        path = self.base_dir / "deployments" / f"{name}-deployment.yaml"
        with open(path, "w") as f:
            yaml.dump(deployment, f, default_flow_style=False)
        logger.info(f"📝 Created: {path.relative_to(self.root_dir)}")

    def generate_service(self, name, config):
        """Generate service manifest."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": "sophia-ai-prod",
                "labels": {"app": name},
            },
            "spec": {
                "type": "ClusterIP",
                "selector": {"app": name},
                "ports": [
                    {
                        "port": config["port"],
                        "targetPort": config["port"],
                        "protocol": "TCP",
                        "name": "http",
                    }
                ],
            },
        }

        path = self.base_dir / "services" / f"{name}-service.yaml"
        with open(path, "w") as f:
            yaml.dump(service, f, default_flow_style=False)
        logger.info(f"📝 Created: {path.relative_to(self.root_dir)}")

    def generate_pvc(self, name):
        """Generate PersistentVolumeClaim for stateful services."""
        pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {"name": f"{name}-pvc", "namespace": "sophia-ai-prod"},
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {"requests": {"storage": "1Gi"}},
                "storageClassName": "local-path",
            },
        }

        path = self.base_dir / f"{name}-pvc.yaml"
        with open(path, "w") as f:
            yaml.dump(pvc, f, default_flow_style=False)
        logger.info(f"📝 Created: {path.relative_to(self.root_dir)}")

    def generate_ingress(self):
        """Generate ingress manifest."""
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "sophia-ai-ingress",
                "namespace": "sophia-ai-prod",
                "annotations": {
                    "kubernetes.io/ingress.class": "traefik",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                },
            },
            "spec": {
                "tls": [
                    {"hosts": ["api.sophia-ai.com"], "secretName": "sophia-ai-tls"}
                ],
                "rules": [
                    {
                        "host": "api.sophia-ai.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "sophia-api",
                                            "port": {"number": 8001},
                                        }
                                    },
                                }
                            ]
                        },
                    }
                ],
            },
        }

        path = self.base_dir / "ingress" / "ingress.yaml"
        with open(path, "w") as f:
            yaml.dump(ingress, f, default_flow_style=False)
        logger.info(f"📝 Created: {path.relative_to(self.root_dir)}")

    def generate_kustomization(self):
        """Generate kustomization.yaml for base resources."""
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "namespace": "sophia-ai-prod",
            "resources": ["namespace.yaml", "redis-pvc.yaml"],
        }

        # Add all deployments and services
        for subdir in ["deployments", "services", "ingress"]:
            dir_path = self.base_dir / subdir
            if dir_path.exists():
                for file in dir_path.glob("*.yaml"):
                    kustomization["resources"].append(f"{subdir}/{file.name}")

        path = self.base_dir / "kustomization.yaml"
        with open(path, "w") as f:
            yaml.dump(kustomization, f, default_flow_style=False)
        logger.info(f"📝 Created: {path.relative_to(self.root_dir)}")

    def generate_production_overlay(self):
        """Generate production overlay kustomization."""
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "namespace": "sophia-ai-prod",
            "resources": ["../../base"],
            "patchesStrategicMerge": ["replica-patch.yaml"],
            "images": [
                {"name": "scoobyjava15/sophia-api", "newTag": "latest"},
                {"name": "scoobyjava15/mcp-servers", "newTag": "latest"},
            ],
        }

        overlay_path = self.overlays_dir / "production" / "kustomization.yaml"
        with open(overlay_path, "w") as f:
            yaml.dump(kustomization, f, default_flow_style=False)
        logger.info(f"📝 Created: {overlay_path.relative_to(self.root_dir)}")

        # Create replica patch for production
        replica_patch = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "sophia-api", "namespace": "sophia-ai-prod"},
            "spec": {"replicas": 3},
        }

        patch_path = self.overlays_dir / "production" / "replica-patch.yaml"
        with open(patch_path, "w") as f:
            yaml.dump(replica_patch, f, default_flow_style=False)
        logger.info(f"📝 Created: {patch_path.relative_to(self.root_dir)}")

    def _remove_none_values(self, d):
        """Recursively remove None values from dictionary."""
        if not isinstance(d, dict):
            return d
        return {k: self._remove_none_values(v) for k, v in d.items() if v is not None}

    def generate_all(self):
        """Generate all K8s manifests."""
        logger.info("🚀 Starting K8s manifest generation...")

        # Create directory structure
        self.create_directory_structure()

        # Generate namespace
        self.generate_namespace()

        # Generate manifests for each service
        for name, config in self.services.items():
            self.generate_deployment(name, config)
            self.generate_service(name, config)

            # Generate PVC for stateful services
            if config.get("persistent"):
                self.generate_pvc(name)

        # Generate ingress
        self.generate_ingress()

        # Generate kustomization files
        self.generate_kustomization()
        self.generate_production_overlay()

        logger.info("\n✨ K8s manifest generation complete!")
        logger.info(f"📁 Manifests location: {self.k8s_dir}")

        # Print deployment instructions
        print("\n" + "=" * 60)
        print("K8S DEPLOYMENT INSTRUCTIONS")
        print("=" * 60)
        print("\nTo deploy to K3s cluster:")
        print("1. Test manifests:")
        print("   kubectl apply -k kubernetes/base --dry-run=client")
        print("\n2. Deploy to production:")
        print("   kubectl apply -k kubernetes/overlays/production")
        print("\n3. Check deployment status:")
        print("   kubectl get all -n sophia-ai-prod")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    generator = K8sManifestGenerator()
    generator.generate_all()
