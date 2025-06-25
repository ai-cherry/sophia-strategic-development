#!/usr/bin/env python3
"""
Agent Migration Planner
Implements the phased migration strategy from expert recommendations
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from enum import Enum


class ServiceType(Enum):
    """Service deployment types"""

    MICROSERVICE = "microservice"
    PLUGIN = "plugin"
    LAMBDA = "lambda"
    CRONJOB = "cronjob"


class MigrationPhase(Enum):
    """Migration phases"""

    FOUNDATION = 1
    CORE_SERVICES = 2
    SCALE_OPTIMIZE = 3


# Service catalog with expert-recommended classifications
SERVICE_CATALOG = {
    # Always-On Services (Microservices)
    "gong-data-processor": {
        "type": ServiceType.MICROSERVICE,
        "phase": MigrationPhase.FOUNDATION,
        "priority": 1,
        "dependencies": ["kafka", "postgres"],
        "resources": {"cpu": "1000m", "memory": "2Gi"},
        "rationale": "High volume, always-on data processing",
    },
    "competitive-intelligence-monitor": {
        "type": ServiceType.MICROSERVICE,
        "phase": MigrationPhase.CORE_SERVICES,
        "priority": 2,
        "dependencies": ["kafka", "redis"],
        "resources": {"cpu": "500m", "memory": "1Gi"},
        "rationale": "Real-time monitoring requires constant availability",
    },
    "compliance-scanner": {
        "type": ServiceType.MICROSERVICE,
        "phase": MigrationPhase.FOUNDATION,
        "priority": 1,
        "dependencies": ["postgres"],
        "resources": {"cpu": "500m", "memory": "1Gi"},
        "rationale": "Critical compliance monitoring",
    },
    # On-Demand Services (Plugins/Lambda)
    "claude-code-generator": {
        "type": ServiceType.PLUGIN,
        "phase": MigrationPhase.CORE_SERVICES,
        "priority": 3,
        "dependencies": ["api-gateway"],
        "resources": {"memory": "512MB", "timeout": "60s"},
        "rationale": "On-demand, stateless code generation",
    },
    "slack-notifier": {
        "type": ServiceType.LAMBDA,
        "phase": MigrationPhase.CORE_SERVICES,
        "priority": 3,
        "dependencies": ["eventbridge"],
        "resources": {"memory": "256MB", "timeout": "30s"},
        "rationale": "Event-driven, lightweight notifications",
    },
    # Periodic Services (CronJobs)
    "linear-sync": {
        "type": ServiceType.CRONJOB,
        "phase": MigrationPhase.CORE_SERVICES,
        "priority": 2,
        "dependencies": ["postgres"],
        "resources": {"cpu": "200m", "memory": "512Mi"},
        "schedule": "*/15 * * * *",
        "rationale": "Periodic sync, medium volume",
    },
    "nmhc-prospect-enricher": {
        "type": ServiceType.CRONJOB,
        "phase": MigrationPhase.CORE_SERVICES,
        "priority": 2,
        "dependencies": ["postgres", "redis"],
        "resources": {"cpu": "500m", "memory": "1Gi"},
        "schedule": "0 2 * * *",
        "rationale": "Daily batch enrichment process",
    },
}


class MigrationPlanner:
    """Plan and track agent migration"""

    def __init__(self):
        self.start_date = datetime.now()
        self.services = SERVICE_CATALOG

    def get_phase_timeline(self) -> Dict[MigrationPhase, Tuple[datetime, datetime]]:
        """Get timeline for each migration phase"""
        return {
            MigrationPhase.FOUNDATION: (
                self.start_date,
                self.start_date + timedelta(days=30),
            ),
            MigrationPhase.CORE_SERVICES: (
                self.start_date + timedelta(days=31),
                self.start_date + timedelta(days=90),
            ),
            MigrationPhase.SCALE_OPTIMIZE: (
                self.start_date + timedelta(days=91),
                self.start_date + timedelta(days=180),
            ),
        }

    def get_phase_services(self, phase: MigrationPhase) -> List[Dict]:
        """Get services for a specific phase"""
        services = []
        for name, config in self.services.items():
            if config["phase"] == phase:
                services.append({"name": name, **config})
        return sorted(services, key=lambda x: x["priority"])

    def generate_migration_plan(self) -> Dict:
        """Generate complete migration plan"""
        timeline = self.get_phase_timeline()
        plan = {
            "generated_at": datetime.now().isoformat(),
            "total_services": len(self.services),
            "phases": {},
        }

        for phase in MigrationPhase:
            services = self.get_phase_services(phase)
            start, end = timeline[phase]

            plan["phases"][phase.name] = {
                "phase_number": phase.value,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "duration_days": (end - start).days,
                "services": services,
                "infrastructure_requirements": self._get_phase_requirements(phase),
            }

        return plan

    def _get_phase_requirements(self, phase: MigrationPhase) -> Dict:
        """Get infrastructure requirements for each phase"""
        requirements = {
            MigrationPhase.FOUNDATION: {
                "kubernetes": "Core cluster with monitoring",
                "observability": "Prometheus, Grafana, Loki",
                "ci_cd": "GitHub Actions pipelines",
                "message_bus": "Kafka cluster (3 nodes)",
                "database": "PostgreSQL with replication",
            },
            MigrationPhase.CORE_SERVICES: {
                "event_bus": "AWS EventBridge",
                "serverless": "Lambda runtime environment",
                "api_gateway": "Kong or AWS API Gateway",
                "secrets": "AWS Secrets Manager",
                "monitoring": "Enhanced dashboards",
            },
            MigrationPhase.SCALE_OPTIMIZE: {
                "service_mesh": "Linkerd (if needed)",
                "cost_optimization": "Spot instances, reserved capacity",
                "self_service": "Developer portal",
                "plugin_registry": "Internal registry with CI/CD",
                "advanced_monitoring": "ML-based anomaly detection",
            },
        }
        return requirements.get(phase, {})

    def validate_dependencies(self) -> List[str]:
        """Validate service dependencies are met"""
        issues = []
        deployed = set()

        for phase in MigrationPhase:
            services = self.get_phase_services(phase)
            for service in services:
                for dep in service.get("dependencies", []):
                    if dep not in deployed and dep not in [
                        "kafka",
                        "postgres",
                        "redis",
                        "eventbridge",
                        "api-gateway",
                    ]:
                        issues.append(
                            f"{service['name']} depends on {dep} which is not yet deployed"
                        )
                deployed.add(service["name"])

        return issues

    def generate_deployment_manifest(self, service_name: str) -> Dict:
        """Generate deployment manifest for a service"""
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not found")

        service = self.services[service_name]

        if service["type"] == ServiceType.MICROSERVICE:
            return self._generate_k8s_deployment(service_name, service)
        elif service["type"] == ServiceType.LAMBDA:
            return self._generate_lambda_config(service_name, service)
        elif service["type"] == ServiceType.CRONJOB:
            return self._generate_cronjob_config(service_name, service)
        elif service["type"] == ServiceType.PLUGIN:
            return self._generate_plugin_config(service_name, service)

    def _generate_k8s_deployment(self, name: str, config: Dict) -> Dict:
        """Generate Kubernetes deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": name, "labels": {"app": name, "type": "microservice"}},
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": f"sophia-ai/{name}:latest",
                                "resources": {
                                    "requests": config["resources"],
                                    "limits": config["resources"],
                                },
                                "livenessProbe": {
                                    "httpGet": {"path": "/health", "port": 8080},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                            }
                        ]
                    },
                },
            },
        }

    def _generate_lambda_config(self, name: str, config: Dict) -> Dict:
        """Generate Lambda function configuration"""
        return {
            "FunctionName": name,
            "Runtime": "python3.11",
            "Handler": f"{name}.handler",
            "MemorySize": int(config["resources"]["memory"].rstrip("MB")),
            "Timeout": int(config["resources"]["timeout"].rstrip("s")),
            "Environment": {"Variables": {"SERVICE_NAME": name}},
        }

    def _generate_cronjob_config(self, name: str, config: Dict) -> Dict:
        """Generate Kubernetes CronJob configuration"""
        return {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {"name": name},
            "spec": {
                "schedule": config.get("schedule", "0 * * * *"),
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": name,
                                        "image": f"sophia-ai/{name}:latest",
                                        "resources": {"requests": config["resources"]},
                                    }
                                ],
                                "restartPolicy": "OnFailure",
                            }
                        }
                    }
                },
            },
        }

    def _generate_plugin_config(self, name: str, config: Dict) -> Dict:
        """Generate plugin configuration"""
        return {
            "plugin_name": name,
            "version": "1.0.0",
            "type": "skill",
            "resources": config["resources"],
            "permissions": ["read", "write"],
            "sandbox": True,
        }


def main():
    """Generate and display migration plan"""
    planner = MigrationPlanner()

    # Generate migration plan
    print("=== Sophia AI Agent Migration Plan ===\n")
    plan = planner.generate_migration_plan()

    # Display plan
    for phase_name, phase_data in plan["phases"].items():
        print(f"\n{phase_name} (Phase {phase_data['phase_number']})")
        print(
            f"Duration: {phase_data['start_date'][:10]} to {phase_data['end_date'][:10]}"
        )
        print(f"Services to migrate: {len(phase_data['services'])}")

        for service in phase_data["services"]:
            print(
                f"  - {service['name']} ({service['type'].value}) [Priority: {service['priority']}]"
            )
            print(f"    Rationale: {service['rationale']}")

        print("\nInfrastructure Requirements:")
        for req, desc in phase_data["infrastructure_requirements"].items():
            print(f"  - {req}: {desc}")

    # Validate dependencies
    print("\n=== Dependency Validation ===")
    issues = planner.validate_dependencies()
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All dependencies validated successfully")

    # Save plan to file
    with open("migration_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    print("\n✓ Migration plan saved to migration_plan.json")


if __name__ == "__main__":
    main()
