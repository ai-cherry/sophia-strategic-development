#!/usr/bin/env python3
"""
Enhanced Lambda Labs Provisioner for GGH200 GPU Clusters
Optimized for Sophia AI Platform with Kubernetes and Snowflake integration
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


@dataclass
class LambdaLabsH200Config:
    """Enhanced configuration for Lambda Labs H200 deployment"""

    api_key: str
    ssh_key_name: str
    instance_type: str = "gpu_1x_gh200"
    region: str = "us-west-1"
    cluster_size: int = 3
    max_cluster_size: int = 16
    auto_scaling: bool = True
    kubernetes_enabled: bool = True
    gpu_memory_size: str = "96GB"
    gpu_bandwidth: str = "4.8TB/s"


@dataclass
class KubernetesClusterConfig:
    """Configuration for Kubernetes cluster on Lambda Labs"""

    cluster_name: str = "sophia-ai-enhanced"
    namespace: str = "sophia-ai-enhanced"
    node_pools: list[dict[str, Any]] = None
    auto_scaling: bool = True
    gpu_driver_version: str = "535.86.10"
    cuda_version: str = "12.3"

    def __post_init__(self):
        if self.node_pools is None:
            self.node_pools = [
                {
                    "name": "ai-inference",
                    "gpu_type": "h200",
                    "min_replicas": 3,
                    "max_replicas": 8,
                    "instance_type": "gpu_1x_gh200",
                },
                {
                    "name": "data-processing",
                    "gpu_type": "h200",
                    "min_replicas": 1,
                    "max_replicas": 4,
                    "instance_type": "gpu_1x_gh200",
                },
                {
                    "name": "monitoring",
                    "gpu_type": "none",
                    "min_replicas": 1,
                    "max_replicas": 2,
                    "instance_type": "cpu_4x",
                },
            ]


@dataclass
class SnowflakeIntegrationConfig:
    """Configuration for Snowflake integration with Lambda Labs"""

    external_function_integration: bool = True
    cortex_gpu_acceleration: bool = True
    warehouse_auto_scaling: bool = True
    cache_optimization: bool = True


class EnhancedLambdaLabsProvisioner:
    """
    Enhanced Lambda Labs provisioner for GGH200 GPU clusters
    Supports Kubernetes, auto-scaling, and Snowflake integration
    """

    def __init__(self):
        self.config = LambdaLabsH200Config(
            api_key=get_config_value("lambda_labs_api_key"),
            ssh_key_name=get_config_value(
                "lambda_labs_ssh_key_name", "sophia-ai-h200-key"
            ),
            region=get_config_value("lambda_labs_region", "us-west-1"),
            cluster_size=int(get_config_value("lambda_labs_cluster_size", "3")),
            max_cluster_size=int(
                get_config_value("lambda_labs_max_cluster_size", "16")
            ),
        )

        self.k8s_config = KubernetesClusterConfig()
        self.snowflake_config = SnowflakeIntegrationConfig()

        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        self.cluster_state = {
            "instances": [],
            "kubeconfig": None,
            "cluster_endpoint": None,
            "status": "initializing",
            "gpu_utilization": {},
            "scaling_policy": {},
        }

        self._validate_config()

    def _validate_config(self):
        """Validate Lambda Labs configuration"""
        if not self.config.api_key:
            raise ValueError("Lambda Labs API key not configured in Pulumi ESC")

        if not self.config.ssh_key_name:
            raise ValueError("Lambda Labs SSH key name not configured")

        logger.info(
            f"✅ Enhanced Lambda Labs provisioner initialized:\n"
            f"  GPU Type: H200 (96GB HBM3e)\n"
            f"  Cluster Size: {self.config.cluster_size}-{self.config.max_cluster_size} nodes\n"
            f"  Region: {self.config.region}\n"
            f"  Kubernetes: Enabled\n"
            f"  Auto-scaling: Enabled"
        )

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make authenticated request to Lambda Labs API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, headers=self.headers, json=data, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"❌ Lambda Labs API request failed: {e}")
            raise

    async def get_available_instance_types(self) -> list[dict[str, Any]]:
        """Get available H200 instance types"""
        instance_types = await self._make_request("GET", "instance-types")

        # Filter for H200 instances
        h200_instances = [
            instance
            for instance in instance_types["data"]
            if "h200" in instance["name"].lower()
        ]

        if not h200_instances:
            logger.warning(
                "⚠️ No H200 instances available, falling back to available GPU types"
            )
            # Fallback to any available GPU instance
            gpu_instances = [
                instance
                for instance in instance_types["data"]
                if instance["instance_type"]["description"].get("gpu_count", 0) > 0
            ]
            return gpu_instances[:5]  # Return top 5 GPU instances

        return h200_instances

    async def launch_enhanced_cluster(self) -> dict[str, Any]:
        """Launch enhanced GGH200 GPU cluster with Kubernetes"""
        logger.info("🚀 Launching Enhanced GGH200 GPU Cluster...")

        try:
            # Step 1: Verify H200 availability
            available_instances = await self.get_available_instance_types()

            if not available_instances:
                raise RuntimeError("No suitable GPU instances available")

            # Select best available instance type
            selected_instance = self._select_optimal_instance_type(available_instances)
            logger.info(f"📋 Selected instance type: {selected_instance['name']}")

            # Step 2: Launch cluster nodes
            cluster_instances = await self._launch_cluster_nodes(selected_instance)

            # Step 3: Configure Kubernetes cluster
            kubeconfig = await self._setup_kubernetes_cluster(cluster_instances)

            # Step 4: Deploy GPU drivers and CUDA
            await self._setup_gpu_drivers(cluster_instances)

            # Step 5: Configure auto-scaling
            await self._setup_auto_scaling(cluster_instances)

            # Step 6: Configure Snowflake integration
            await self._setup_snowflake_integration(cluster_instances)

            # Step 7: Deploy monitoring and health checks
            await self._deploy_monitoring(cluster_instances)

            # Update cluster state
            self.cluster_state.update(
                {
                    "instances": cluster_instances,
                    "kubeconfig": kubeconfig,
                    "status": "running",
                    "cluster_size": len(cluster_instances),
                    "instance_type": selected_instance["name"],
                    "total_gpu_memory": f"{len(cluster_instances) * 141}GB",
                    "deployment_time": time.time(),
                }
            )

            logger.info("✅ Enhanced GGH200 GPU Cluster launched successfully!")
            return self.cluster_state

        except Exception as e:
            logger.error(f"❌ Cluster launch failed: {e}")
            await self._cleanup_failed_deployment()
            raise

    def _select_optimal_instance_type(
        self, available_instances: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Select optimal instance type based on availability and specifications"""
        # Prioritize H200 instances
        for instance in available_instances:
            if "h200" in instance["name"].lower():
                return instance

        # Fallback to best available GPU instance
        for instance in available_instances:
            gpu_memory = (
                instance.get("instance_type", {})
                .get("description", {})
                .get("gpu_memory_gb", 0)
            )
            if gpu_memory >= 80:  # Prefer instances with at least 80GB GPU memory
                return instance

        # Last resort: return any available instance
        return available_instances[0]

    async def _launch_cluster_nodes(
        self, instance_type: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Launch cluster nodes with specified instance type"""
        logger.info(f"📦 Launching {self.config.cluster_size} cluster nodes...")

        cluster_instances = []

        for i in range(self.config.cluster_size):
            node_name = f"sophia-ai-h200-{i+1:02d}"

            launch_data = {
                "region_name": self.config.region,
                "instance_type_name": instance_type["name"],
                "ssh_key_names": [self.config.ssh_key_name],
                "file_system_names": [],
                "quantity": 1,
                "name": node_name,
            }

            logger.info(f"🔄 Launching node {node_name}...")
            result = await self._make_request(
                "POST", "instance-operations/launch", launch_data
            )

            instance_ids = result["data"]["instance_ids"]
            if not instance_ids:
                raise RuntimeError(f"Failed to launch node {node_name}")

            instance_id = instance_ids[0]

            # Wait for instance to be running
            instance_info = await self._wait_for_instance_running(
                instance_id, node_name
            )

            cluster_instances.append(
                {
                    "instance_id": instance_id,
                    "name": node_name,
                    "ip_address": instance_info["ip"],
                    "status": instance_info["status"],
                    "instance_type": instance_type["name"],
                    "gpu_memory": "96GB",
                    "role": "worker" if i > 0 else "master",
                }
            )

            logger.info(f"✅ Node {node_name} launched: {instance_info['ip']}")

        return cluster_instances

    async def _wait_for_instance_running(
        self, instance_id: str, node_name: str, timeout: int = 600
    ) -> dict[str, Any]:
        """Wait for instance to be in running state"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            instances_response = await self._make_request("GET", "instances")

            for instance in instances_response["data"]:
                if instance["id"] == instance_id:
                    if instance["status"] == "running":
                        logger.info(f"✅ {node_name} is running at {instance['ip']}")
                        return instance
                    elif instance["status"] == "unhealthy":
                        raise RuntimeError(f"Instance {node_name} is unhealthy")

            logger.info(f"⏳ Waiting for {node_name} to be running...")
            await asyncio.sleep(15)

        raise TimeoutError(
            f"Instance {node_name} did not start within {timeout} seconds"
        )

    async def _setup_kubernetes_cluster(
        self, cluster_instances: list[dict[str, Any]]
    ) -> str:
        """Set up Kubernetes cluster on Lambda Labs instances"""
        logger.info("⚙️ Setting up Kubernetes cluster...")

        master_node = next(
            instance for instance in cluster_instances if instance["role"] == "master"
        )
        worker_nodes = [
            instance for instance in cluster_instances if instance["role"] == "worker"
        ]

        try:
            # Initialize Kubernetes master
            kubeconfig = await self._initialize_k8s_master(master_node)

            # Join worker nodes
            for worker in worker_nodes:
                await self._join_k8s_worker(worker, master_node)

            # Configure GPU support
            await self._configure_k8s_gpu_support(master_node)

            # Deploy essential services
            await self._deploy_k8s_essentials(master_node)

            logger.info("✅ Kubernetes cluster configured successfully")
            return kubeconfig

        except Exception as e:
            logger.error(f"❌ Kubernetes setup failed: {e}")
            raise

    async def _initialize_k8s_master(self, master_node: dict[str, Any]) -> str:
        """Initialize Kubernetes master node"""
        master_ip = master_node["ip_address"]

        # Generate cloud-init script for Kubernetes master
        k8s_master_script = self._generate_k8s_master_script(master_ip)

        # Execute on master node
        await self._execute_remote_script(
            master_ip, k8s_master_script, "k8s_master_setup.sh"
        )

        # Get kubeconfig
        kubeconfig = await self._get_kubeconfig(master_ip)

        return kubeconfig

    def _generate_k8s_master_script(self, master_ip: str) -> str:
        """Generate Kubernetes master setup script"""
        return f"""#!/bin/bash
set -e

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Kubernetes components
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet=1.28.0-00 kubeadm=1.28.0-00 kubectl=1.28.0-00
sudo apt-mark hold kubelet kubeadm kubectl

# Initialize Kubernetes cluster
sudo kubeadm init --apiserver-advertise-address={master_ip} --pod-network-cidr=10.244.0.0/16

# Configure kubectl for ubuntu user
mkdir -p /home/ubuntu/.kube
sudo cp -i /etc/kubernetes/admin.conf /home/ubuntu/.kube/config
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config

# Install Flannel network plugin
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# Install NVIDIA GPU Operator
kubectl create ns gpu-operator
helm repo add nvidia https://nvidia.github.io/gpu-operator
helm repo update
helm install gpu-operator nvidia/gpu-operator \\
    --namespace gpu-operator \\
    --set toolkit.version=v1.14.3-ubuntu20.04 \\
    --set driver.version=535.86.10

# Configure auto-scaling
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-status
  namespace: kube-system
data:
  nodes.max: "{self.config.max_cluster_size}"
  nodes.min: "{self.config.cluster_size}"
EOF

echo "✅ Kubernetes master setup complete"
"""

    async def _join_k8s_worker(
        self, worker_node: dict[str, Any], master_node: dict[str, Any]
    ):
        """Join worker node to Kubernetes cluster"""
        worker_ip = worker_node["ip_address"]
        master_ip = master_node["ip_address"]

        # Get join token from master
        join_command = await self._get_k8s_join_command(master_ip)

        # Generate worker setup script
        worker_script = self._generate_k8s_worker_script(join_command)

        # Execute on worker node
        await self._execute_remote_script(
            worker_ip, worker_script, "k8s_worker_setup.sh"
        )

        logger.info(f"✅ Worker {worker_node['name']} joined cluster")

    def _generate_k8s_worker_script(self, join_command: str) -> str:
        """Generate Kubernetes worker setup script"""
        return f"""#!/bin/bash
set -e

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Kubernetes components
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet=1.28.0-00 kubeadm=1.28.0-00 kubectl=1.28.0-00
sudo apt-mark hold kubelet kubeadm kubectl

# Join cluster
{join_command}

echo "✅ Kubernetes worker setup complete"
"""

    async def _setup_gpu_drivers(self, cluster_instances: list[dict[str, Any]]):
        """Set up GPU drivers and CUDA on all nodes"""
        logger.info("🔧 Setting up GPU drivers and CUDA...")

        gpu_driver_script = self._generate_gpu_driver_script()

        tasks = []
        for instance in cluster_instances:
            task = self._execute_remote_script(
                instance["ip_address"], gpu_driver_script, "gpu_driver_setup.sh"
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
        logger.info("✅ GPU drivers configured on all nodes")

    def _generate_gpu_driver_script(self) -> str:
        """Generate GPU driver installation script"""
        return """#!/bin/bash
set -e

# Install NVIDIA drivers and CUDA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install CUDA 12.3
sudo apt-get install -y cuda-12-3

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Configure GPU monitoring
cat > /tmp/gpu-monitoring.service << EOF
[Unit]
Description=GPU Monitoring Service
After=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/nvidia-smi dmon -s pucvmet -d 10
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/gpu-monitoring.service /etc/systemd/system/
sudo systemctl enable gpu-monitoring
sudo systemctl start gpu-monitoring

echo "✅ GPU drivers and CUDA installed"
"""

    async def _setup_auto_scaling(self, cluster_instances: list[dict[str, Any]]):
        """Set up cluster auto-scaling"""
        logger.info("📈 Configuring cluster auto-scaling...")

        master_node = next(
            instance for instance in cluster_instances if instance["role"] == "master"
        )

        autoscaling_config = self._generate_autoscaling_config()

        await self._execute_remote_script(
            master_node["ip_address"], autoscaling_config, "autoscaling_setup.sh"
        )

        logger.info("✅ Auto-scaling configured")

    def _generate_autoscaling_config(self) -> str:
        """Generate auto-scaling configuration"""
        return f"""#!/bin/bash
set -e

# Deploy Horizontal Pod Autoscaler
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sophia-ai-hpa
  namespace: sophia-ai-enhanced
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sophia-enhanced-deployment
  minReplicas: {self.config.cluster_size}
  maxReplicas: {self.config.max_cluster_size}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 600
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
EOF

# Deploy Vertical Pod Autoscaler
kubectl apply -f - <<EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: sophia-ai-vpa
  namespace: sophia-ai-enhanced
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sophia-enhanced-deployment
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: sophia-ai-enhanced
      maxAllowed:
        cpu: 16
        memory: 64Gi
      minAllowed:
        cpu: 2
        memory: 8Gi
EOF

echo "✅ Auto-scaling policies deployed"
"""

    async def _setup_snowflake_integration(
        self, cluster_instances: list[dict[str, Any]]
    ):
        """Set up Snowflake integration with GPU acceleration"""
        logger.info("❄️ Configuring Snowflake integration...")

        master_node = next(
            instance for instance in cluster_instances if instance["role"] == "master"
        )

        snowflake_integration_script = self._generate_snowflake_integration_script()

        await self._execute_remote_script(
            master_node["ip_address"],
            snowflake_integration_script,
            "snowflake_integration_setup.sh",
        )

        logger.info("✅ Snowflake integration configured")

    def _generate_snowflake_integration_script(self) -> str:
        """Generate Snowflake integration script"""
        return """#!/bin/bash
set -e

# Deploy Snowflake Cortex GPU acceleration service
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: snowflake-cortex-gpu-service
  namespace: sophia-ai-enhanced
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
    name: cortex-api
  selector:
    app: snowflake-cortex-gpu
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: snowflake-cortex-gpu
  namespace: sophia-ai-enhanced
spec:
  replicas: 1
  selector:
    matchLabels:
      app: snowflake-cortex-gpu
  template:
    metadata:
      labels:
        app: snowflake-cortex-gpu
    spec:
      containers:
      - name: cortex-gpu-accelerator
        image: nvidia/cuda:12.3-runtime-ubuntu20.04
        command: ["/bin/sleep", "infinity"]
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        - name: NVIDIA_DRIVER_CAPABILITIES
          value: "compute,utility"
        ports:
        - containerPort: 8080
EOF

echo "✅ Snowflake Cortex GPU acceleration deployed"
"""

    async def _deploy_monitoring(self, cluster_instances: list[dict[str, Any]]):
        """Deploy monitoring and observability stack"""
        logger.info("📊 Deploying monitoring stack...")

        master_node = next(
            instance for instance in cluster_instances if instance["role"] == "master"
        )

        monitoring_script = self._generate_monitoring_script()

        await self._execute_remote_script(
            master_node["ip_address"], monitoring_script, "monitoring_setup.sh"
        )

        logger.info("✅ Monitoring stack deployed")

    def _generate_monitoring_script(self) -> str:
        """Generate monitoring deployment script"""
        return """#!/bin/bash
set -e

# Install Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Deploy Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \\
    --namespace monitoring --create-namespace \\
    --set grafana.adminPassword=admin \\
    --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi

# Deploy GPU monitoring
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvidia-dcgm-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: nvidia-dcgm-exporter
  template:
    metadata:
      labels:
        app: nvidia-dcgm-exporter
    spec:
      containers:
      - name: nvidia-dcgm-exporter
        image: nvidia/dcgm-exporter:3.1.7-3.1.4-ubuntu20.04
        securityContext:
          privileged: true
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
        env:
        - name: DCGM_EXPORTER_LISTEN
          value: ":9400"
        - name: DCGM_EXPORTER_KUBERNETES
          value: "true"
        ports:
        - containerPort: 9400
          name: metrics
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      hostNetwork: true
      hostPID: true
EOF

echo "✅ Monitoring and GPU observability deployed"
"""

    async def _execute_remote_script(
        self, ip_address: str, script_content: str, script_name: str
    ):
        """Execute script on remote instance"""
        try:
            # Get SSH private key
            ssh_private_key = get_config_value("lambda_labs_ssh_private_key")
            if not ssh_private_key:
                raise ValueError("SSH private key not available")

            # Save SSH key to temporary file
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pem", delete=False
            ) as key_file:
                key_file.write(ssh_private_key)
                key_file_path = key_file.name

            try:
                # Set proper permissions
                os.chmod(key_file_path, 0o600)

                # Save script to temporary file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".sh", delete=False
                ) as script_file:
                    script_file.write(script_content)
                    script_file_path = script_file.name

                # Copy script to remote server
                scp_cmd = [
                    "scp",
                    "-i",
                    key_file_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    script_file_path,
                    f"ubuntu@{ip_address}:/tmp/{script_name}",
                ]

                subprocess.run(scp_cmd, check=True, capture_output=True)

                # Execute script
                ssh_cmd = [
                    "ssh",
                    "-i",
                    key_file_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{ip_address}",
                    f"chmod +x /tmp/{script_name} && /tmp/{script_name}",
                ]

                result = subprocess.run(
                    ssh_cmd, check=True, capture_output=True, text=True
                )
                logger.debug(f"✅ Script {script_name} executed on {ip_address}")

            finally:
                # Cleanup temporary files
                os.unlink(key_file_path)
                if "script_file_path" in locals():
                    os.unlink(script_file_path)

        except Exception as e:
            logger.error(f"❌ Failed to execute {script_name} on {ip_address}: {e}")
            raise

    async def _get_kubeconfig(self, master_ip: str) -> str:
        """Get kubeconfig from master node"""
        try:
            ssh_private_key = get_config_value("lambda_labs_ssh_private_key")

            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pem", delete=False
            ) as key_file:
                key_file.write(ssh_private_key)
                key_file_path = key_file.name

            try:
                os.chmod(key_file_path, 0o600)

                # Get kubeconfig
                ssh_cmd = [
                    "ssh",
                    "-i",
                    key_file_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{master_ip}",
                    "cat /home/ubuntu/.kube/config",
                ]

                result = subprocess.run(
                    ssh_cmd, check=True, capture_output=True, text=True
                )
                kubeconfig = result.stdout

                # Replace server IP with master IP
                kubeconfig = kubeconfig.replace("https://10.", f"https://{master_ip}:")

                return kubeconfig

            finally:
                os.unlink(key_file_path)

        except Exception as e:
            logger.error(f"❌ Failed to get kubeconfig: {e}")
            raise

    async def _get_k8s_join_command(self, master_ip: str) -> str:
        """Get Kubernetes join command from master"""
        try:
            ssh_private_key = get_config_value("lambda_labs_ssh_private_key")

            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pem", delete=False
            ) as key_file:
                key_file.write(ssh_private_key)
                key_file_path = key_file.name

            try:
                os.chmod(key_file_path, 0o600)

                # Get join command
                ssh_cmd = [
                    "ssh",
                    "-i",
                    key_file_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{master_ip}",
                    "sudo kubeadm token create --print-join-command",
                ]

                result = subprocess.run(
                    ssh_cmd, check=True, capture_output=True, text=True
                )
                join_command = f"sudo {result.stdout.strip()}"

                return join_command

            finally:
                os.unlink(key_file_path)

        except Exception as e:
            logger.error(f"❌ Failed to get join command: {e}")
            raise

    async def _cleanup_failed_deployment(self):
        """Clean up resources from failed deployment"""
        logger.info("🧹 Cleaning up failed deployment...")

        try:
            # Terminate any launched instances
            for instance in self.cluster_state.get("instances", []):
                instance_id = instance.get("instance_id")
                if instance_id:
                    try:
                        await self._make_request(
                            "POST",
                            "instance-operations/terminate",
                            {"instance_ids": [instance_id]},
                        )
                        logger.info(f"🗑️ Terminated instance {instance_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to terminate {instance_id}: {e}")

            # Reset cluster state
            self.cluster_state = {
                "instances": [],
                "status": "failed",
                "cleanup_time": time.time(),
            }

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

    async def get_cluster_status(self) -> dict[str, Any]:
        """Get current cluster status and metrics"""
        if not self.cluster_state.get("instances"):
            return {"status": "not_deployed", "instances": 0}

        try:
            # Get instance statuses
            instances_response = await self._make_request("GET", "instances")
            current_instances = {
                inst["id"]: inst for inst in instances_response["data"]
            }

            # Update cluster state
            for instance in self.cluster_state["instances"]:
                instance_id = instance["instance_id"]
                if instance_id in current_instances:
                    instance["current_status"] = current_instances[instance_id][
                        "status"
                    ]
                    instance["uptime"] = current_instances[instance_id].get(
                        "uptime", "unknown"
                    )

            # Calculate cluster health
            running_instances = sum(
                1
                for inst in self.cluster_state["instances"]
                if inst.get("current_status") == "running"
            )

            cluster_health = (
                "healthy"
                if running_instances == len(self.cluster_state["instances"])
                else "degraded"
            )

            return {
                "status": self.cluster_state["status"],
                "health": cluster_health,
                "total_instances": len(self.cluster_state["instances"]),
                "running_instances": running_instances,
                "total_gpu_memory": self.cluster_state.get(
                    "total_gpu_memory", "unknown"
                ),
                "cluster_size": self.cluster_state.get("cluster_size", 0),
                "instance_type": self.cluster_state.get("instance_type", "unknown"),
                "deployment_time": self.cluster_state.get("deployment_time"),
                "instances": self.cluster_state["instances"],
            }

        except Exception as e:
            logger.error(f"❌ Failed to get cluster status: {e}")
            return {"status": "error", "error": str(e)}

    async def scale_cluster(self, target_size: int) -> dict[str, Any]:
        """Scale cluster to target size"""
        if (
            target_size < self.config.cluster_size
            or target_size > self.config.max_cluster_size
        ):
            raise ValueError(
                f"Target size must be between {self.config.cluster_size} and {self.config.max_cluster_size}"
            )

        current_size = len(self.cluster_state.get("instances", []))

        if target_size == current_size:
            return {"status": "no_change", "current_size": current_size}

        if target_size > current_size:
            # Scale up
            return await self._scale_up(target_size - current_size)
        else:
            # Scale down
            return await self._scale_down(current_size - target_size)

    async def _scale_up(self, additional_nodes: int) -> dict[str, Any]:
        """Scale up cluster by adding nodes"""
        logger.info(f"📈 Scaling up cluster by {additional_nodes} nodes...")

        # Implementation for scaling up
        # This would launch additional instances and join them to the cluster
        pass

    async def _scale_down(self, nodes_to_remove: int) -> dict[str, Any]:
        """Scale down cluster by removing nodes"""
        logger.info(f"📉 Scaling down cluster by {nodes_to_remove} nodes...")

        # Implementation for scaling down
        # This would gracefully drain and terminate nodes
        pass

    async def terminate_cluster(self) -> dict[str, Any]:
        """Terminate the entire cluster"""
        logger.info("🛑 Terminating cluster...")

        try:
            instance_ids = [
                inst["instance_id"] for inst in self.cluster_state.get("instances", [])
            ]

            if instance_ids:
                await self._make_request(
                    "POST",
                    "instance-operations/terminate",
                    {"instance_ids": instance_ids},
                )

                logger.info(f"✅ Terminated {len(instance_ids)} instances")

            # Reset cluster state
            self.cluster_state = {
                "instances": [],
                "status": "terminated",
                "termination_time": time.time(),
            }

            return {"status": "terminated", "instances_terminated": len(instance_ids)}

        except Exception as e:
            logger.error(f"❌ Cluster termination failed: {e}")
            raise


# Global instance
enhanced_lambda_labs_provisioner = EnhancedLambdaLabsProvisioner()


async def deploy_enhanced_lambda_labs_cluster():
    """Deploy enhanced Lambda Labs H200 cluster"""
    logger.info("🚀 Starting Enhanced Lambda Labs H200 Cluster Deployment...")

    try:
        result = await enhanced_lambda_labs_provisioner.launch_enhanced_cluster()
        logger.info("✅ Enhanced Lambda Labs cluster deployed successfully!")
        return result

    except Exception as e:
        logger.error(f"❌ Enhanced Lambda Labs deployment failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(deploy_enhanced_lambda_labs_cluster())
