#!/usr/bin/env python3
"""
Sophia AI Environment Validation Script
Ensures the environment is properly configured for Cline and other AI tools
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(message: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{message.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def check_result(condition: bool, success_msg: str, failure_msg: str) -> bool:
    """Print check result and return status"""
    if condition:
        print(f"{GREEN}✅ {success_msg}{RESET}")
        return True
    else:
        print(f"{RED}❌ {failure_msg}{RESET}")
        return False

def validate_python_environment() -> bool:
    """Validate Python environment setup"""
    print_header("Python Environment Validation")
    
    checks = []
    
    # Check Python version
    python_version = sys.version_info
    checks.append(check_result(
        python_version >= (3, 8),
        f"Python version {python_version.major}.{python_version.minor} is supported",
        f"Python version {python_version.major}.{python_version.minor} is too old (need 3.8+)"
    ))
    
    # Check virtual environment
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    checks.append(check_result(
        venv_active or 'VIRTUAL_ENV' in os.environ,
        "Virtual environment is active",
        "Virtual environment is not active"
    ))
    
    # Check if in Sophia directory
    cwd = Path.cwd()
    sophia_dir = cwd.name == 'sophia-main' or 'sophia-main' in str(cwd)
    checks.append(check_result(
        sophia_dir,
        f"Working in Sophia directory: {cwd}",
        f"Not in Sophia directory: {cwd}"
    ))
    
    # Check PYTHONPATH
    pythonpath = os.environ.get('PYTHONPATH', '')
    has_sophia = 'sophia-main' in pythonpath or str(cwd) in pythonpath
    checks.append(check_result(
        has_sophia,
        "PYTHONPATH includes Sophia directory",
        "PYTHONPATH does not include Sophia directory"
    ))
    
    return all(checks)

def validate_environment_variables() -> bool:
    """Validate required environment variables"""
    print_header("Environment Variables Validation")
    
    required_vars = {
        'ENVIRONMENT': 'prod',
        'PULUMI_ORG': 'scoobyjava-org'
    }
    
    checks = []
    for var, expected in required_vars.items():
        value = os.environ.get(var)
        if expected:
            checks.append(check_result(
                value == expected,
                f"{var} = {value}",
                f"{var} is not set to {expected} (current: {value})"
            ))
        else:
            checks.append(check_result(
                value is not None,
                f"{var} is set",
                f"{var} is not set"
            ))
    
    # Check optional but important variables
    optional_vars = ['SOPHIA_HOME', 'VIRTUAL_ENV']
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"{GREEN}✅ {var} = {value}{RESET}")
    
    return all(checks)

def validate_vscode_settings() -> bool:
    """Validate VSCode settings"""
    print_header("VSCode Settings Validation")
    
    settings_path = Path('.vscode/settings.json')
    checks = []
    
    checks.append(check_result(
        settings_path.exists(),
        "VSCode settings file exists",
        "VSCode settings file not found"
    ))
    
    if settings_path.exists():
        try:
            with open(settings_path) as f:
                settings = json.load(f)
            
            # Check critical settings
            critical_settings = [
                'python.defaultInterpreterPath',
                'terminal.integrated.shellIntegration.enabled',
                'terminal.integrated.env.osx'
            ]
            
            for setting in critical_settings:
                value = settings
                for key in setting.split('.'):
                    value = value.get(key, {}) if isinstance(value, dict) else None
                
                checks.append(check_result(
                    value is not None,
                    f"{setting} is configured",
                    f"{setting} is not configured"
                ))
                
        except Exception as e:
            checks.append(check_result(
                False,
                "",
                f"Error reading VSCode settings: {e}"
            ))
    
    return all(checks)

def validate_shell_integration() -> bool:
    """Validate shell integration"""
    print_header("Shell Integration Validation")
    
    checks = []
    
    # Check shell type
    shell = os.environ.get('SHELL', '')
    checks.append(check_result(
        '/zsh' in shell or '/bash' in shell,
        f"Shell is supported: {shell}",
        f"Shell might not be supported: {shell}"
    ))
    
    # Check if in VSCode terminal
    term_program = os.environ.get('TERM_PROGRAM')
    if term_program:
        checks.append(check_result(
            term_program == 'vscode',
            "Running in VSCode terminal",
            f"Not running in VSCode terminal (TERM_PROGRAM={term_program})"
        ))
    else:
        print(f"{YELLOW}⚠️  Cannot determine terminal program (might be normal){RESET}")
    
    return all(checks)

def check_backend_imports() -> bool:
    """Check if backend modules can be imported"""
    print_header("Backend Module Import Test")
    
    checks = []
    test_imports = [
        'backend',
        'backend.core',
        'backend.agents',
        'backend.services'
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            checks.append(check_result(
                True,
                f"Can import {module}",
                ""
            ))
        except ImportError as e:
            checks.append(check_result(
                False,
                "",
                f"Cannot import {module}: {e}"
            ))
    
    return all(checks)

def run_quick_health_check() -> bool:
    """Run a quick health check if the script exists"""
    print_header("Quick Health Check")
    
    health_script = Path('backend/scripts/check_environment_health.py')
    
    if health_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(health_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"{GREEN}✅ Health check passed{RESET}")
                if result.stdout:
                    print(f"\n{result.stdout}")
                return True
            else:
                print(f"{RED}❌ Health check failed{RESET}")
                if result.stderr:
                    print(f"\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{YELLOW}⚠️  Health check timed out{RESET}")
            return False
        except Exception as e:
            print(f"{RED}❌ Error running health check: {e}{RESET}")
            return False
    else:
        print(f"{YELLOW}⚠️  Health check script not found{RESET}")
        return True  # Don't fail overall validation

def main():
    """Run all validations"""
    print(f"{BLUE}🔍 Sophia AI Environment Validation{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    validations = [
        ("Python Environment", validate_python_environment),
        ("Environment Variables", validate_environment_variables),
        ("VSCode Settings", validate_vscode_settings),
        ("Shell Integration", validate_shell_integration),
        ("Backend Imports", check_backend_imports),
        ("Health Check", run_quick_health_check)
    ]
    
    results = []
    for name, validator in validations:
        try:
            results.append((name, validator()))
        except Exception as e:
            print(f"{RED}❌ Error during {name}: {e}{RESET}")
            results.append((name, False))
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"{name}: {status}")
    
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    
    if all_passed:
        print(f"{GREEN}🚀 All validations passed! Environment is ready for Cline.{RESET}")
        print("\nQuick commands:")
        print("  - Start backend: python start_backend_services.py")
        print("  - Start MCP: python start_mcp_servers.py")
        print("  - Run tests: pytest")
        return 0
    else:
        print(f"{RED}❌ Some validations failed. Please check the issues above.{RESET}")
        print(f"\n{YELLOW}Troubleshooting tips:{RESET}")
        print("  1. Run: source verify_and_activate_env.sh")
        print("  2. Check MASTER_ENVIRONMENT_GUIDE.md for detailed fixes")
        print("  3. Restart VSCode after making changes")
        return 1

if __name__ == "__main__":
    sys.exit(main())
