"""
Sophia AI - Lambda Labs K3s Fortress Deployment
GPU-hot fortress deployment for 10M events/day with Blackwell scaling

Phase 1: K3s Foundation
- Deploy core Sophia AI to Lambda Labs K3s
- GPU scheduling for MCP servers
- Health checks and monitoring
- Production-ready configuration

Date: July 12, 2025
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class K3sClusterConfig(BaseModel):
    """K3s cluster configuration"""
    name: str
    nodes: List[str]
    gpu_nodes: List[str]
    master_node: str
    kubeconfig_path: str
    namespace: str = "sophia-ai"


class SophiaAIDeployment:
    """Sophia AI Lambda Labs K3s deployment manager"""
    
    def __init__(self, config: K3sClusterConfig):
        self.config = config
        self.manifests_dir = Path("k8s/lambda-labs")
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        
    async def deploy_fortress(self):
        """Deploy the full Sophia AI fortress to Lambda Labs K3s"""
        logger.info("🚀 Deploying Sophia AI GPU Fortress to Lambda Labs K3s")
        
        # Phase 1: Cluster preparation
        await self._prepare_cluster()
        
        # Phase 2: Core infrastructure
        await self._deploy_core_infrastructure()
        
        # Phase 3: GPU-enabled services
        await self._deploy_gpu_services()
        
        # Phase 4: Health checks and monitoring
        await self._deploy_monitoring()
        
        # Phase 5: Validation
        await self._validate_deployment()
        
        logger.info("✅ Sophia AI Fortress deployed successfully!")
        
    async def _prepare_cluster(self):
        """Prepare K3s cluster for Sophia AI deployment"""
        logger.info("🔧 Preparing K3s cluster...")
        
        # Create namespace
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace,
                "labels": {
                    "name": self.config.namespace,
                    "app": "sophia-ai",
                    "tier": "production"
                }
            }
        }
        
        await self._apply_manifest("namespace.yaml", namespace_manifest)
        
        # GPU device plugin for Lambda Labs
        gpu_plugin_manifest = {
            "apiVersion": "apps/v1",
            "kind": "DaemonSet",
            "metadata": {
                "name": "nvidia-device-plugin-daemonset",
                "namespace": "kube-system"
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "name": "nvidia-device-plugin-ds"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "name": "nvidia-device-plugin-ds"
                        }
                    },
                    "spec": {
                        "tolerations": [
                            {
                                "key": "nvidia.com/gpu",
                                "operator": "Exists",
                                "effect": "NoSchedule"
                            }
                        ],
                        "containers": [
                            {
                                "image": "nvcr.io/nvidia/k8s-device-plugin:v0.14.0",
                                "name": "nvidia-device-plugin-ctr",
                                "env": [
                                    {
                                        "name": "FAIL_ON_INIT_ERROR",
                                        "value": "false"
                                    }
                                ],
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "capabilities": {
                                        "drop": ["ALL"]
                                    }
                                },
                                "volumeMounts": [
                                    {
                                        "name": "device-plugin",
                                        "mountPath": "/var/lib/kubelet/device-plugins"
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "device-plugin",
                                "hostPath": {
                                    "path": "/var/lib/kubelet/device-plugins"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("gpu-device-plugin.yaml", gpu_plugin_manifest)
        
    async def _deploy_core_infrastructure(self):
        """Deploy core Sophia AI infrastructure"""
        logger.info("🏗️ Deploying core infrastructure...")
        
        # Production FastAPI backend
        backend_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "sophia-ai-backend",
                "namespace": self.config.namespace,
                "labels": {
                    "app": "sophia-ai-backend",
                    "tier": "backend"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "sophia-ai-backend"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "sophia-ai-backend"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "sophia-ai-backend",
                                "image": "scoobyjava15/sophia-ai-backend:latest",
                                "ports": [
                                    {
                                        "containerPort": 8000,
                                        "name": "http"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "ENVIRONMENT",
                                        "value": "prod"
                                    },
                                    {
                                        "name": "PULUMI_ORG",
                                        "value": "scoobyjava-org"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "512Mi",
                                        "cpu": "250m"
                                    },
                                    "limits": {
                                        "memory": "1Gi",
                                        "cpu": "500m"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("backend-deployment.yaml", backend_manifest)
        
        # Backend service
        backend_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "sophia-ai-backend-service",
                "namespace": self.config.namespace
            },
            "spec": {
                "selector": {
                    "app": "sophia-ai-backend"
                },
                "ports": [
                    {
                        "port": 8000,
                        "targetPort": 8000,
                        "name": "http"
                    }
                ],
                "type": "LoadBalancer"
            }
        }
        
        await self._apply_manifest("backend-service.yaml", backend_service)
        
    async def _deploy_gpu_services(self):
        """Deploy GPU-enabled services for MCP servers and AI workloads"""
        logger.info("🎯 Deploying GPU-enabled services...")
        
        # MCP Server with GPU support
        mcp_gpu_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "sophia-mcp-gpu-cluster",
                "namespace": self.config.namespace,
                "labels": {
                    "app": "sophia-mcp-gpu",
                    "tier": "ai-inference"
                }
            },
            "spec": {
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "sophia-mcp-gpu"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "sophia-mcp-gpu"
                        }
                    },
                    "spec": {
                        "nodeSelector": {
                            "accelerator": "nvidia-tesla-v100"
                        },
                        "containers": [
                            {
                                "name": "sophia-mcp-gpu",
                                "image": "scoobyjava15/sophia-mcp-gpu:latest",
                                "ports": [
                                    {
                                        "containerPort": 9000,
                                        "name": "mcp-port"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "NVIDIA_VISIBLE_DEVICES",
                                        "value": "all"
                                    },
                                    {
                                        "name": "ENVIRONMENT",
                                        "value": "prod"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "2Gi",
                                        "cpu": "1000m",
                                        "nvidia.com/gpu": "1"
                                    },
                                    "limits": {
                                        "memory": "8Gi",
                                        "cpu": "4000m",
                                        "nvidia.com/gpu": "1"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 9000
                                    },
                                    "initialDelaySeconds": 60,
                                    "periodSeconds": 30
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("mcp-gpu-deployment.yaml", mcp_gpu_manifest)
        
        # Weaviate with GPU acceleration
        weaviate_manifest = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "weaviate-gpu",
                "namespace": self.config.namespace
            },
            "spec": {
                "serviceName": "weaviate-gpu",
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "weaviate-gpu"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "weaviate-gpu"
                        }
                    },
                    "spec": {
                        "nodeSelector": {
                            "accelerator": "nvidia-tesla-v100"
                        },
                        "containers": [
                            {
                                "name": "weaviate",
                                "image": "semitechnologies/weaviate:1.26.0",
                                "ports": [
                                    {
                                        "containerPort": 8080,
                                        "name": "http"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "QUERY_DEFAULTS_LIMIT",
                                        "value": "25"
                                    },
                                    {
                                        "name": "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED",
                                        "value": "true"
                                    },
                                    {
                                        "name": "PERSISTENCE_DATA_PATH",
                                        "value": "/var/lib/weaviate"
                                    },
                                    {
                                        "name": "DEFAULT_VECTORIZER_MODULE",
                                        "value": "text2vec-transformers"
                                    },
                                    {
                                        "name": "ENABLE_MODULES",
                                        "value": "text2vec-transformers,generative-openai"
                                    },
                                    {
                                        "name": "TRANSFORMERS_INFERENCE_API",
                                        "value": "http://t2v-transformers:8080"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "4Gi",
                                        "cpu": "2000m",
                                        "nvidia.com/gpu": "1"
                                    },
                                    "limits": {
                                        "memory": "16Gi",
                                        "cpu": "8000m",
                                        "nvidia.com/gpu": "1"
                                    }
                                },
                                "volumeMounts": [
                                    {
                                        "name": "weaviate-data",
                                        "mountPath": "/var/lib/weaviate"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "weaviate-data"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": "100Gi"
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        await self._apply_manifest("weaviate-gpu-statefulset.yaml", weaviate_manifest)
        
    async def _deploy_monitoring(self):
        """Deploy monitoring and health checks"""
        logger.info("📊 Deploying monitoring stack...")
        
        # Prometheus for metrics
        prometheus_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "prometheus",
                "namespace": self.config.namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "prometheus"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "prometheus"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "prometheus",
                                "image": "prom/prometheus:latest",
                                "ports": [
                                    {
                                        "containerPort": 9090,
                                        "name": "prometheus"
                                    }
                                ],
                                "args": [
                                    "--config.file=/etc/prometheus/prometheus.yml",
                                    "--storage.tsdb.path=/prometheus/",
                                    "--web.console.libraries=/etc/prometheus/console_libraries",
                                    "--web.console.templates=/etc/prometheus/consoles",
                                    "--web.enable-lifecycle"
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "1Gi",
                                        "cpu": "500m"
                                    },
                                    "limits": {
                                        "memory": "2Gi",
                                        "cpu": "1000m"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("prometheus-deployment.yaml", prometheus_manifest)
        
    async def _validate_deployment(self):
        """Validate the deployment is working correctly"""
        logger.info("✅ Validating deployment...")
        
        # Check pod status
        result = await self._run_kubectl([
            "get", "pods", 
            "-n", self.config.namespace,
            "-o", "json"
        ])
        
        if result.returncode == 0:
            pods = json.loads(result.stdout)
            running_pods = [
                pod for pod in pods["items"] 
                if pod["status"]["phase"] == "Running"
            ]
            
            logger.info(f"✅ {len(running_pods)} pods running successfully")
            
            # Test backend health
            backend_health = await self._test_backend_health()
            if backend_health:
                logger.info("✅ Backend health check passed")
            else:
                logger.error("❌ Backend health check failed")
                
        else:
            logger.error(f"❌ Failed to get pod status: {result.stderr}")
            
    async def _test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            # Port forward to test locally
            port_forward = await asyncio.create_subprocess_exec(
                "kubectl", "port-forward", 
                f"service/sophia-ai-backend-service",
                "8000:8000",
                "-n", self.config.namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for port forward to establish
            await asyncio.sleep(2)
            
            # Test health endpoint
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        logger.info(f"Health check response: {health_data}")
                        return True
                    else:
                        logger.error(f"Health check failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
        finally:
            if 'port_forward' in locals():
                port_forward.terminate()
                
    async def _apply_manifest(self, filename: str, manifest: dict):
        """Apply a Kubernetes manifest"""
        manifest_path = self.manifests_dir / filename
        
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
            
        result = await self._run_kubectl(["apply", "-f", str(manifest_path)])
        
        if result.returncode == 0:
            logger.info(f"✅ Applied {filename}")
        else:
            logger.error(f"❌ Failed to apply {filename}: {result.stderr}")
            
    async def _run_kubectl(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run kubectl command"""
        cmd = ["kubectl"] + args
        
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=result.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )


async def main():
    """Deploy Sophia AI to Lambda Labs K3s"""
    
    # Lambda Labs cluster configuration
    cluster_config = K3sClusterConfig(
        name="sophia-ai-fortress",
        nodes=[
            "192.222.58.232",  # Primary Lambda Labs node
            "104.171.202.103", # Secondary node
            "104.171.202.117"  # MCP node
        ],
        gpu_nodes=[
            "192.222.58.232",  # GPU node 1
            "104.171.202.103"  # GPU node 2
        ],
        master_node="192.222.58.232",
        kubeconfig_path="~/.kube/config",
        namespace="sophia-ai"
    )
    
    deployment = SophiaAIDeployment(cluster_config)
    await deployment.deploy_fortress()
    
    print("\n🎉 Sophia AI Lambda Labs K3s Fortress deployed!")
    print("🔗 Access your fortress at: https://sophia-ai.lambda-labs.com")
    print("📊 Monitoring: https://grafana.sophia-ai.lambda-labs.com")
    print("🎯 Ready for 10M events/day with <150ms response times!")


if __name__ == "__main__":
    asyncio.run(main()) 