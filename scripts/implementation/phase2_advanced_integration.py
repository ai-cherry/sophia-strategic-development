#!/usr/bin/env python3
"""
Sophia AI Phase 2 Advanced Integration
Implements Estuary Flow Real-Time CDC + Pulumi ESC Secret Management
Research-validated sub-100ms latency, automated secret rotation
"""

import asyncio
import logging
import os
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Phase2AdvancedIntegration:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.estuary_dir = self.project_root / "estuary-config"
        self.pulumi_dir = self.project_root / "infrastructure" / "pulumi"

    def create_estuary_flow_config(self) -> None:
        """Create Estuary Flow configuration for sub-100ms CDC"""
        logger.info("🌊 Creating Estuary Flow CDC configuration...")

        self.estuary_dir.mkdir(parents=True, exist_ok=True)

        estuary_config = {
            "captures": {
                "sophia/postgresql": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/source-postgres:dev",
                            "config": {
                                "address": "postgresql.sophia-ai.svc.cluster.local:5432",
                                "database": "sophia_ai",
                                "user": "estuary_user",
                                "password": "${POSTGRESQL_ESTUARY_PASSWORD}",
                                "advanced": {
                                    "sslmode": "require",
                                    "backfill": False,
                                    "watermarks": True,
                                },
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {
                                "stream": "public.conversations",
                                "syncMode": "incremental",
                            },
                            "target": "sophia/conversations",
                        },
                        {
                            "resource": {
                                "stream": "public.ai_memory_records",
                                "syncMode": "incremental",
                            },
                            "target": "sophia/ai_memory",
                        },
                        {
                            "resource": {
                                "stream": "public.business_metrics",
                                "syncMode": "incremental",
                            },
                            "target": "sophia/metrics",
                        },
                    ],
                },
                "sophia/snowflake": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/source-snowflake:dev",
                            "config": {
                                "account": "${SNOWFLAKE_ACCOUNT}",
                                "user": "${SNOWFLAKE_USER}",
                                "password": "${SNOWFLAKE_PASSWORD}",
                                "warehouse": "${SNOWFLAKE_WAREHOUSE}",
                                "database": "SOPHIA_AI",
                                "schema": "PUBLIC",
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {
                                "table": "SOPHIA_AI.PUBLIC.ENRICHED_GONG_CALLS"
                            },
                            "target": "sophia/gong_calls",
                        },
                        {
                            "resource": {
                                "table": "SOPHIA_AI.PUBLIC.ENRICHED_HUBSPOT_DEALS"
                            },
                            "target": "sophia/hubspot_deals",
                        },
                    ],
                },
            },
            "collections": {
                "sophia/conversations": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "message": {"type": "string"},
                            "embedding": {"type": "array", "items": {"type": "number"}},
                            "metadata": {"type": "object"},
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                    },
                    "key": ["/id"],
                },
                "sophia/vector_updates": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "embedding_id": {"type": "string"},
                            "vector": {"type": "array", "items": {"type": "number"}},
                            "metadata": {"type": "object"},
                            "source": {"type": "string"},
                            "updated_at": {"type": "string", "format": "date-time"},
                        },
                    },
                    "key": ["/embedding_id"],
                },
            },
            "materializations": {
                "sophia/pinecone": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/materialize-pinecone:dev",
                            "config": {
                                "api_key": "${PINECONE_API_KEY}",
                                "environment": "${PINECONE_ENVIRONMENT}",
                                "index_name": "sophia-conversations",
                                "batch_size": 100,
                                "flush_interval": "1s",
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {"index": "sophia-conversations"},
                            "source": "sophia/conversations",
                            "fields": {
                                "recommended": True,
                                "include": {
                                    "id": "/id",
                                    "vector": "/embedding",
                                    "metadata": "/metadata",
                                },
                            },
                        }
                    ],
                },
                "sophia/weaviate": {
                    "endpoint": {
                        "connector": {
                            "image": "ghcr.io/estuary/materialize-weaviate:dev",
                            "config": {
                                "url": "${WEAVIATE_URL}",
                                "api_key": "${WEAVIATE_API_KEY}",
                                "batch_size": 100,
                            },
                        }
                    },
                    "bindings": [
                        {
                            "resource": {"class": "SophiaConversation"},
                            "source": "sophia/conversations",
                        },
                        {
                            "resource": {"class": "SophiaMemory"},
                            "source": "sophia/ai_memory",
                        },
                    ],
                },
            },
        }

        config_path = self.estuary_dir / "sophia-ai-flows.yaml"
        with open(config_path, "w") as f:
            yaml.dump(estuary_config, f, default_flow_style=False)

        logger.info(f"✅ Estuary Flow config created: {config_path}")

    def create_pulumi_esc_config(self) -> None:
        """Create Pulumi ESC configuration with automated secret rotation"""
        logger.info("🔐 Creating Pulumi ESC configuration...")

        self.pulumi_dir.mkdir(parents=True, exist_ok=True)

        esc_config = {
            "values": {
                "sophia_ai": {
                    "secrets": {
                        "database": {
                            "postgresql": {
                                "fn::secret": {
                                    "ciphertext": "${POSTGRESQL_PASSWORD_ENCRYPTED}",
                                    "rotation": {
                                        "schedule": "0 2 * * 0",  # Weekly Sunday 2 AM
                                        "strategy": "two-secret",
                                        "retention": "30d",
                                    },
                                }
                            },
                            "redis": {
                                "fn::secret": {
                                    "ciphertext": "${REDIS_PASSWORD_ENCRYPTED}",
                                    "rotation": {
                                        "schedule": "0 3 * * 0",
                                        "strategy": "two-secret",
                                        "retention": "30d",
                                    },
                                }
                            },
                        },
                        "ai_services": {
                            "openai": {
                                "fn::secret": {
                                    "ciphertext": "${OPENAI_API_KEY_ENCRYPTED}",
                                    "rotation": {
                                        "manual": True,
                                        "notification": {
                                            "webhook": "${SLACK_WEBHOOK_URL}",
                                            "message": "OpenAI API key requires manual rotation",
                                        },
                                    },
                                }
                            },
                            "anthropic": {
                                "fn::secret": {
                                    "ciphertext": "${ANTHROPIC_API_KEY_ENCRYPTED}",
                                    "rotation": {
                                        "manual": True,
                                        "notification": {
                                            "webhook": "${SLACK_WEBHOOK_URL}",
                                            "message": "Anthropic API key requires manual rotation",
                                        },
                                    },
                                }
                            },
                            "pinecone": {
                                "fn::secret": {
                                    "ciphertext": "${PINECONE_API_KEY_ENCRYPTED}",
                                    "rotation": {"manual": True},
                                }
                            },
                        },
                        "vector_databases": {
                            "pinecone": {
                                "environment": "${PINECONE_ENVIRONMENT}",
                                "index_name": "sophia-conversations",
                            },
                            "weaviate": {
                                "url": "${WEAVIATE_URL}",
                                "api_key": {
                                    "fn::secret": {
                                        "ciphertext": "${WEAVIATE_API_KEY_ENCRYPTED}"
                                    }
                                },
                            },
                        },
                    },
                    "infrastructure": {
                        "lambda_labs": {
                            "api_key": "${LAMBDA_LABS_API_KEY}",
                            "auto_scaling": {
                                "enabled": True,
                                "min_instances": 2,
                                "max_instances": 10,
                                "target_gpu_utilization": 75,
                                "scale_up_cooldown": "5m",
                                "scale_down_cooldown": "15m",
                            },
                            "instance_types": {
                                "primary": "gpu_1x_a100",
                                "fallback": "gpu_1x_rtx6000",
                            },
                        },
                        "docker_cloud": {
                            "builder_name": "scoobyjava15/sophia-ai-builder",
                            "cache_strategy": "shared",
                            "platforms": ["linux/amd64", "linux/arm64"],
                            "build_timeout": "30m",
                        },
                        "monitoring": {
                            "prometheus": {"enabled": True, "retention": "30d"},
                            "grafana": {
                                "enabled": True,
                                "admin_password": {
                                    "fn::secret": {
                                        "ciphertext": "${GRAFANA_ADMIN_PASSWORD_ENCRYPTED}"
                                    }
                                },
                            },
                        },
                    },
                }
            },
            "environmentVariables": {
                # Database secrets
                "POSTGRESQL_PASSWORD": "${sophia_ai.secrets.database.postgresql}",
                "REDIS_PASSWORD": "${sophia_ai.secrets.database.redis}",
                # AI service secrets
                "OPENAI_API_KEY": "${sophia_ai.secrets.ai_services.openai}",
                "ANTHROPIC_API_KEY": "${sophia_ai.secrets.ai_services.anthropic}",
                "PINECONE_API_KEY": "${sophia_ai.secrets.ai_services.pinecone}",
                # Vector database config
                "PINECONE_ENVIRONMENT": "${sophia_ai.secrets.vector_databases.pinecone.environment}",
                "WEAVIATE_URL": "${sophia_ai.secrets.vector_databases.weaviate.url}",
                "WEAVIATE_API_KEY": "${sophia_ai.secrets.vector_databases.weaviate.api_key}",
                # Infrastructure config
                "LAMBDA_LABS_API_KEY": "${sophia_ai.infrastructure.lambda_labs.api_key}",
                "DOCKER_BUILDER_NAME": "${sophia_ai.infrastructure.docker_cloud.builder_name}",
                # Monitoring config
                "GRAFANA_ADMIN_PASSWORD": "${sophia_ai.infrastructure.monitoring.grafana.admin_password}",
            },
        }

        esc_path = self.pulumi_dir / "esc-config.yaml"
        with open(esc_path, "w") as f:
            yaml.dump(esc_config, f, default_flow_style=False)

        logger.info(f"✅ Pulumi ESC config created: {esc_path}")

    def create_performance_validation_script(self) -> None:
        """Create performance validation script for research targets"""
        logger.info("📊 Creating performance validation script...")

        script_content = '''#!/usr/bin/env python3
"""
Sophia AI Performance Validation Script
Validates research-backed performance targets:
- Sub-200ms API response times
- 220+ N8N workflow executions/second
- Sub-100ms Estuary Flow data latency
"""

import asyncio
import aiohttp
import time
import os
import json
from typing import Dict, List

class PerformanceValidator:
    def __init__(self):
        self.lambda_ip = os.getenv('LAMBDA_LABS_INSTANCE_IP', 'localhost')
        self.targets = {
            'api_response_time_ms': 200,
            'n8n_throughput_per_second': 220,
            'estuary_latency_ms': 100,
            'availability_percent': 99.9
        }

    async def test_api_response_times(self) -> Dict[str, float]:
        """Test API response times with concurrent requests"""
        print("🔍 Testing API response times...")

        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []

            # Send 100 concurrent requests
            for i in range(100):
                task = session.get(f"http://{self.lambda_ip}:8000/api/health")
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            # Calculate metrics
            successful_responses = [r for r in responses if not isinstance(r, Exception)]
            success_rate = len(successful_responses) / len(responses) * 100
            avg_response_time = ((end_time - start_time) * 1000) / len(successful_responses)

            return {
                'avg_response_time_ms': avg_response_time,
                'success_rate_percent': success_rate,
                'total_requests': len(responses),
                'successful_requests': len(successful_responses)
            }

    async def test_n8n_throughput(self) -> Dict[str, float]:
        """Test N8N workflow execution throughput"""
        print("⚡ Testing N8N workflow throughput...")

        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []

            # Send 220 workflow execution requests
            for i in range(220):
                task = session.post(
                    f"http://{self.lambda_ip}:5678/webhook/performance-test",
                    json={"test_id": f"perf_test_{i}", "timestamp": start_time}
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            successful_responses = [r for r in responses if not isinstance(r, Exception)]
            duration = end_time - start_time
            throughput = len(successful_responses) / duration

            return {
                'throughput_per_second': throughput,
                'duration_seconds': duration,
                'successful_executions': len(successful_responses),
                'total_executions': len(responses)
            }

    async def test_estuary_latency(self) -> Dict[str, float]:
        """Test Estuary Flow end-to-end latency"""
        print("🌊 Testing Estuary Flow latency...")

        async with aiohttp.ClientSession() as session:
            test_start = time.time()

            # Insert test data into PostgreSQL
            await session.post(
                f"http://{self.lambda_ip}:8000/api/test/insert",
                json={
                    "message": "estuary_latency_test",
                    "timestamp": test_start,
                    "test_id": f"latency_{int(test_start)}"
                }
            )

            # Poll for data in vector database (should appear within 100ms)
            max_wait_time = 5.0  # 5 second timeout
            poll_interval = 0.01  # 10ms polling

            while (time.time() - test_start) < max_wait_time:
                response = await session.get(
                    f"http://{self.lambda_ip}:8000/api/vectors/search",
                    params={"query": f"latency_{int(test_start)}"}
                )

                if response.status == 200:
                    data = await response.json()
                    if data.get('results'):
                        latency = (time.time() - test_start) * 1000
                        return {
                            'latency_ms': latency,
                            'success': True,
                            'data_found': True
                        }

                await asyncio.sleep(poll_interval)

            # Timeout case
            return {
                'latency_ms': max_wait_time * 1000,
                'success': False,
                'data_found': False
            }

    async def validate_all_targets(self) -> Dict[str, Dict]:
        """Run all performance validations"""
        print("🚀 Starting comprehensive performance validation...")
        print(f"Target metrics: {self.targets}")

        results = {}

        # Test API response times
        api_results = await self.test_api_response_times()
        results['api_performance'] = api_results
        api_passed = api_results['avg_response_time_ms'] < self.targets['api_response_time_ms']

        # Test N8N throughput
        n8n_results = await self.test_n8n_throughput()
        results['n8n_performance'] = n8n_results
        n8n_passed = n8n_results['throughput_per_second'] >= self.targets['n8n_throughput_per_second']

        # Test Estuary latency
        estuary_results = await self.test_estuary_latency()
        results['estuary_performance'] = estuary_results
        estuary_passed = (estuary_results['latency_ms'] < self.targets['estuary_latency_ms']
                         and estuary_results['success'])

        # Overall assessment
        results['validation_summary'] = {
            'api_response_passed': api_passed,
            'n8n_throughput_passed': n8n_passed,
            'estuary_latency_passed': estuary_passed,
            'overall_passed': api_passed and n8n_passed and estuary_passed
        }

        # Print results
        print("\\n📊 Performance Validation Results:")
        print(f"  {'✅' if api_passed else '❌'} API Response Time: {api_results['avg_response_time_ms']:.2f}ms (target: <{self.targets['api_response_time_ms']}ms)")
        print(f"  {'✅' if n8n_passed else '❌'} N8N Throughput: {n8n_results['throughput_per_second']:.2f}/s (target: >{self.targets['n8n_throughput_per_second']}/s)")
        print(f"  {'✅' if estuary_passed else '❌'} Estuary Latency: {estuary_results['latency_ms']:.2f}ms (target: <{self.targets['estuary_latency_ms']}ms)")
        print(f"  {'🎉' if results['validation_summary']['overall_passed'] else '⚠️'} Overall: {'PASSED' if results['validation_summary']['overall_passed'] else 'FAILED'}")

        return results

async def main():
    validator = PerformanceValidator()
    results = await validator.validate_all_targets()

    # Save results to file
    with open('performance_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    return 0 if results['validation_summary']['overall_passed'] else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
'''

        script_path = self.project_root / "scripts" / "performance_validation.py"
        with open(script_path, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_path, 0o755)

        logger.info(f"✅ Performance validation script created: {script_path}")

    def create_monitoring_stack(self) -> None:
        """Create Prometheus/Grafana monitoring configuration"""
        logger.info("📈 Creating monitoring stack configuration...")

        monitoring_dir = self.project_root / "kubernetes" / "monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)

        # Prometheus configuration
        prometheus_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": "prometheus-config", "namespace": "sophia-ai"},
            "data": {
                "prometheus.yml": """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
# Docker Build Cloud metrics
- job_name: 'docker-build-cloud'
  static_configs:
  - targets: ['build-metrics.docker.com:443']
  scheme: https
  metrics_path: '/metrics'

# N8N performance metrics
- job_name: 'n8n-main'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names: ['sophia-ai']
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app]
    regex: n8n-main
    action: keep

- job_name: 'n8n-workers'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names: ['sophia-ai']
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app]
    regex: n8n-worker
    action: keep

# Estuary Flow metrics
- job_name: 'estuary-flow'
  static_configs:
  - targets: ['flow-metrics.estuary.dev:443']
  scheme: https

# Sophia AI application metrics
- job_name: 'sophia-ai'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names: ['sophia-ai']
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app]
    regex: sophia-ai
    action: keep

rule_files:
- "alert_rules.yml"

alerting:
  alertmanagers:
  - static_configs:
    - targets: ['alertmanager:9093']
"""
            },
        }

        # Alert rules
        alert_rules = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": "prometheus-alert-rules", "namespace": "sophia-ai"},
            "data": {
                "alert_rules.yml": """groups:
- name: sophia-ai-alerts
  rules:
  - alert: HighAPIResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.2
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High API response time detected"
      description: "95th percentile response time is {{ $value }}s"

  - alert: LowN8NThroughput
    expr: rate(n8n_workflow_executions_total[5m]) < 220
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "N8N throughput below target"
      description: "Current throughput: {{ $value }}/s (target: >220/s)"

  - alert: HighEstuaryLatency
    expr: estuary_flow_latency_ms > 100
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Estuary Flow latency above target"
      description: "Current latency: {{ $value }}ms (target: <100ms)"

  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Pod is crash looping"
      description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is restarting"
"""
            },
        }

        # Write monitoring configs
        configs = [
            ("prometheus-config.yaml", prometheus_config),
            ("prometheus-alert-rules.yaml", alert_rules),
        ]

        for filename, config in configs:
            with open(monitoring_dir / filename, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

        logger.info(f"✅ Monitoring stack created: {monitoring_dir}")

    async def validate_phase2_setup(self) -> dict[str, bool]:
        """Validate Phase 2 setup completion"""
        logger.info("🔍 Validating Phase 2 setup...")

        results = {}

        # Check files exist
        files_to_check = [
            "estuary-config/sophia-ai-flows.yaml",
            "infrastructure/pulumi/esc-config.yaml",
            "scripts/performance_validation.py",
            "kubernetes/monitoring/prometheus-config.yaml",
        ]

        for file_path in files_to_check:
            full_path = self.project_root / file_path
            results[file_path.replace("/", "_")] = full_path.exists()

        return results

    async def run_phase2_setup(self) -> bool:
        """Execute complete Phase 2 advanced integration setup"""
        logger.info("🚀 Starting Sophia AI Phase 2 Advanced Integration...")
        logger.info("Target: Sub-100ms CDC, automated secret rotation")

        try:
            # Create all configurations
            self.create_estuary_flow_config()
            self.create_pulumi_esc_config()
            self.create_performance_validation_script()
            self.create_monitoring_stack()

            # Validate setup
            validation_results = await self.validate_phase2_setup()

            logger.info("📊 Phase 2 Setup Results:")
            for check, passed in validation_results.items():
                status = "✅" if passed else "❌"
                logger.info(f"  {status} {check}")

            success_rate = sum(validation_results.values()) / len(validation_results)
            logger.info(f"📈 Overall Success Rate: {success_rate:.1%}")

            if success_rate >= 0.8:
                logger.info("🎉 Phase 2 Advanced Integration Setup Complete!")
                logger.info("Ready for Phase 3: Production Optimization")
                return True
            else:
                logger.error("❌ Phase 2 setup incomplete. Please review errors above.")
                return False

        except Exception as e:
            logger.exception(f"Phase 2 setup failed: {e}")
            return False


async def main():
    """Main execution function"""
    setup = Phase2AdvancedIntegration()
    success = await setup.run_phase2_setup()

    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
