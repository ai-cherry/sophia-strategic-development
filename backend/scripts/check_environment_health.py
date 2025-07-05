#!/usr/bin/env python3
"""Sophia AI Environment Health Check"""

import json
import os
import subprocess


def check_environment_variables():
    """Check if environment variables are set correctly."""
    env_vars = {"ENVIRONMENT": "prod", "PULUMI_ORG": "scoobyjava-org"}

    issues = []
    for var, expected in env_vars.items():
        actual = os.getenv(var)
        if actual != expected:
            issues.append(f"{var}: expected {expected}, got {actual}")

    return len(issues) == 0, issues


def check_pulumi_auth():
    """Check Pulumi authentication."""
    try:
        result = subprocess.run(
            ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stderr if result.returncode != 0 else None
    except Exception as e:
        return False, str(e)


def check_stack_access():
    """Check access to production stack."""
    try:
        result = subprocess.run(
            [
                "pulumi",
                "env",
                "open",
                "scoobyjava-org/default/sophia-ai-production",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            config = json.loads(result.stdout)
            return True, f"Loaded {len(config)} secrets"
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def main():
    overall_health = True

    # Check 1: Environment Variables
    env_ok, env_issues = check_environment_variables()
    if not env_ok:
        overall_health = False
        for _issue in env_issues:
            pass

    # Check 2: Pulumi Authentication
    auth_ok, auth_error = check_pulumi_auth()
    if not auth_ok:
        overall_health = False

    # Check 3: Stack Access
    stack_ok, stack_info = check_stack_access()
    if stack_ok:
        pass
    else:
        overall_health = False

    # Overall Status

    if not overall_health:
        pass

    return 0 if overall_health else 1


if __name__ == "__main__":
    exit(main())
