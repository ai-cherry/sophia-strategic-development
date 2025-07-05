#!/usr/bin/env python3
"""
Sophia AI Infrastructure Readiness Validation
Validates all infrastructure components are ready for activation
"""
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def check_pulumi_esc():
    """Check Pulumi ESC connectivity and secrets"""

    try:
        # Run health gate to check ESC
        result = subprocess.run(
            ["python", "scripts/ci/deployment_health_gate.py"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )

        return result.returncode == 0
    except Exception:
        return False


def check_mcp_configuration():
    """Check MCP server configuration"""

    port_registry = PROJECT_ROOT / "config" / "unified_mcp_port_registry.json"
    mcp_servers_dir = PROJECT_ROOT / "mcp-servers"

    if not port_registry.exists():
        return False

    if not mcp_servers_dir.exists():
        return False

    # Check critical MCP servers exist
    critical_servers = ["ai_memory", "snowflake_admin", "ui_ux_agent"]
    missing_servers = []

    for server in critical_servers:
        server_dir = mcp_servers_dir / server
        if not server_dir.exists():
            missing_servers.append(server)

    return not missing_servers


def check_github_actions():
    """Check GitHub Actions workflows"""

    workflows_dir = PROJECT_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return False

    critical_workflows = ["sophia-master-deployment.yml", "deployment_health_gate.yml"]

    missing_workflows = []
    for workflow in critical_workflows:
        if not (workflows_dir / workflow).exists():
            missing_workflows.append(workflow)

    return not missing_workflows


def check_backend_dependencies():
    """Check backend dependencies"""

    backend_dir = PROJECT_ROOT / "backend"
    if not backend_dir.exists():
        return False

    # Check critical backend files
    critical_files = [
        "app/fastapi_app.py",
        "core/auto_esc_config.py",
        "services",
        "api",
    ]

    missing_files = []
    for file_path in critical_files:
        if not (backend_dir / file_path).exists():
            missing_files.append(file_path)

    return not missing_files


def check_frontend_dependencies():
    """Check frontend dependencies"""

    frontend_dir = PROJECT_ROOT / "frontend"
    if not frontend_dir.exists():
        return False

    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        return False

    # Check if node_modules exists or can be installed
    node_modules = frontend_dir / "node_modules"
    return node_modules.exists()


def check_activation_scripts():
    """Check activation scripts are present"""

    scripts_dir = PROJECT_ROOT / "scripts"
    critical_scripts = [
        "activate_sophia_production.py",
        "start_all_mcp_servers.py",
        "ci/deployment_health_gate.py",
    ]

    missing_scripts = []
    for script in critical_scripts:
        if not (scripts_dir / script).exists():
            missing_scripts.append(script)

    return not missing_scripts


def check_configuration_files():
    """Check configuration files"""

    config_dir = PROJECT_ROOT / "config"
    if not config_dir.exists():
        return False

    critical_configs = [
        "unified_mcp_port_registry.json",
        "cursor_enhanced_mcp_config.json",
    ]

    missing_configs = []
    for config in critical_configs:
        if not (config_dir / config).exists():
            missing_configs.append(config)

    return not missing_configs


def generate_readiness_report(checks):
    """Generate readiness report"""
    total_checks = len(checks)
    passed_checks = sum(1 for result in checks.values() if result)
    readiness_score = (passed_checks / total_checks) * 100

    report = {
        "readiness_score": readiness_score,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": total_checks - passed_checks,
        "checks": checks,
        "status": (
            "ready"
            if readiness_score >= 90
            else "partial"
            if readiness_score >= 70
            else "not_ready"
        ),
    }

    # Save report
    report_path = PROJECT_ROOT / "infrastructure_readiness_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    """Main validation function"""

    # Run all checks
    checks = {
        "pulumi_esc": check_pulumi_esc(),
        "mcp_configuration": check_mcp_configuration(),
        "github_actions": check_github_actions(),
        "backend_dependencies": check_backend_dependencies(),
        "frontend_dependencies": check_frontend_dependencies(),
        "activation_scripts": check_activation_scripts(),
        "configuration_files": check_configuration_files(),
    }

    # Generate report
    report = generate_readiness_report(checks)

    if report["failed_checks"] > 0:
        for _check_name, result in checks.items():
            if not result:
                pass

    if report["readiness_score"] >= 90:
        return 0
    elif report["readiness_score"] >= 70:
        return 1
    else:
        return 1


if __name__ == "__main__":
    exit(main())
