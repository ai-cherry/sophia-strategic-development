#!/usr/bin/env python3
"""
Infrastructure Validation Script
Validates that all infrastructure components are properly configured
"""

import sys
from pathlib import Path
from typing import List, Tuple


def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a required file exists"""
    if Path(filepath).exists():
        return True, f"✓ {filepath}"
    return False, f"✗ {filepath} - Missing"


def validate_pulumi_config() -> List[Tuple[bool, str]]:
    """Validate Pulumi configuration"""
    results = []

    # Check Pulumi.yaml
    exists, msg = check_file_exists("Pulumi.yaml")
    results.append((exists, msg))

    # Check for Python infrastructure
    if Path("infrastructure").exists():
        results.append((True, "✓ Infrastructure directory exists"))

        # Check for __main__.py
        main_exists, main_msg = check_file_exists("infrastructure/__main__.py")
        results.append((main_exists, main_msg))
    else:
        results.append((False, "✗ Infrastructure directory missing"))

    return results


def validate_esc_config() -> List[Tuple[bool, str]]:
    """Validate ESC configuration"""
    results = []
    esc_dir = Path("infrastructure/esc")

    if esc_dir.exists():
        results.append((True, "✓ ESC directory exists"))

        # Check for production environment
        prod_exists, prod_msg = check_file_exists(
            "infrastructure/esc/sophia-ai-production.yaml"
        )
        results.append((prod_exists, prod_msg))

        # Check for base environment
        base_exists, base_msg = check_file_exists(
            "infrastructure/esc/sophia-ai-platform-base.yaml"
        )
        results.append((base_exists, base_msg))
    else:
        results.append((False, "✗ ESC directory missing"))

    return results


def validate_github_actions() -> List[Tuple[bool, str]]:
    """Validate GitHub Actions workflows"""
    results = []
    workflows_dir = Path(".github/workflows")

    if workflows_dir.exists():
        results.append((True, "✓ Workflows directory exists"))

        # Check for key workflows
        for workflow in ["infrastructure-deploy.yml", "deploy-sophia-platform.yml"]:
            exists, msg = check_file_exists(f".github/workflows/{workflow}")
            results.append((exists, msg))
    else:
        results.append((False, "✗ Workflows directory missing"))

    return results


def validate_docker_config() -> List[Tuple[bool, str]]:
    """Validate Docker configuration"""
    results = []

    # Check main Dockerfile
    docker_exists, docker_msg = check_file_exists("Dockerfile")
    results.append((docker_exists, docker_msg))

    # Check docker-compose files
    for compose_file in ["docker-compose.yml", "docker-compose.prod.yml"]:
        exists, msg = check_file_exists(compose_file)
        results.append((exists, msg))

    return results


def validate_backend_config() -> List[Tuple[bool, str]]:
    """Validate backend configuration"""
    results = []

    # Check core configuration files
    for config_file in [
        "backend/core/auto_esc_config.py",
        "backend/core/enhanced_config.py",
        "backend/security/secret_management.py",
    ]:
        exists, msg = check_file_exists(config_file)
        results.append((exists, msg))

    return results


def main():
    """Main validation function"""
    print("=== Sophia AI Infrastructure Validation ===\n")

    all_results = []

    # Run all validations
    print("Pulumi Configuration:")
    pulumi_results = validate_pulumi_config()
    all_results.extend(pulumi_results)
    for _, msg in pulumi_results:
        print(f"  {msg}")

    print("\nESC Configuration:")
    esc_results = validate_esc_config()
    all_results.extend(esc_results)
    for _, msg in esc_results:
        print(f"  {msg}")

    print("\nGitHub Actions:")
    gh_results = validate_github_actions()
    all_results.extend(gh_results)
    for _, msg in gh_results:
        print(f"  {msg}")

    print("\nDocker Configuration:")
    docker_results = validate_docker_config()
    all_results.extend(docker_results)
    for _, msg in docker_results:
        print(f"  {msg}")

    print("\nBackend Configuration:")
    backend_results = validate_backend_config()
    all_results.extend(backend_results)
    for _, msg in backend_results:
        print(f"  {msg}")

    # Summary
    total = len(all_results)
    passed = sum(1 for success, _ in all_results if success)
    failed = total - passed

    print("\n=== Summary ===")
    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\n⚠️  Some infrastructure components are missing or misconfigured")
        sys.exit(1)
    else:
        print("\n✅ All infrastructure components are properly configured")
        sys.exit(0)


if __name__ == "__main__":
    main()
