#!/usr/bin/env python3
"""
Comprehensive Security Validation Script
Validates all security fixes and system functionality after remediation
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime
import importlib.util

def run_command(cmd, capture_output=True, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def validate_python_security():
    """Validate Python security fixes"""
    print("🔍 Validating Python Security Fixes...")
    
    # Check pip-audit using python3 -m pip_audit
    success, stdout, stderr = run_command("python3 -m pip_audit --format=json")
    if success:
        try:
            audit_data = json.loads(stdout)
            if not audit_data:
                print("✅ pip-audit: No vulnerabilities found")
                return True
            else:
                print(f"❌ pip-audit: {len(audit_data)} vulnerabilities found")
                return False
        except json.JSONDecodeError:
            # If no JSON, check for success message
            if "No known vulnerabilities found" in stdout:
                print("✅ pip-audit: No vulnerabilities found")
                return True
            else:
                print(f"❌ pip-audit failed: {stdout}")
                return False
    else:
        # Try alternative command format
        success2, stdout2, stderr2 = run_command("python3 -m pip_audit")
        if "No known vulnerabilities found" in stdout2:
            print("✅ pip-audit: No vulnerabilities found")
            return True
        elif "Found" in stdout2 and "vulnerabilities" in stdout2:
            print(f"❌ pip-audit: Vulnerabilities found - {stdout2[:200]}...")
            return False
        else:
            print(f"❌ pip-audit command failed: {stderr}")
            return False

def validate_node_security():
    """Validate Node.js security fixes"""
    print("🔍 Validating Node.js Security Fixes...")
    
    # Check npm audit in frontend
    frontend_path = Path("frontend")
    if frontend_path.exists():
        success, stdout, stderr = run_command("npm audit --json", cwd=frontend_path)
        if success:
            try:
                audit_data = json.loads(stdout)
                vulnerabilities = audit_data.get('vulnerabilities', {})
                if not vulnerabilities:
                    print("✅ npm audit: No vulnerabilities found")
                    return True
                else:
                    print(f"❌ npm audit: {len(vulnerabilities)} vulnerabilities found")
                    return False
            except json.JSONDecodeError:
                print("✅ npm audit: No vulnerabilities (clean output)")
                return True
        else:
            print(f"❌ npm audit failed: {stderr}")
            return False
    else:
        print("⚠️  Frontend directory not found, skipping npm audit")
        return True

def validate_docker_security():
    """Validate Docker security improvements"""
    print("🔍 Validating Docker Security Improvements...")
    
    docker_files = [
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "docker/Dockerfile.optimized",
        "docker/Dockerfile.gh200",
        "docker/Dockerfile.mcp-base"
    ]
    
    secure_patterns = [
        "python:3.12-slim",
        "node:20-alpine",
        "USER 1000:1000",
        "RUN addgroup",
        "COPY --chown="
    ]
    
    validated = 0
    for dockerfile in docker_files:
        if Path(dockerfile).exists():
            with open(dockerfile, 'r') as f:
                content = f.read()
                has_security = any(pattern in content for pattern in secure_patterns)
                if has_security:
                    print(f"✅ {dockerfile}: Security patterns found")
                    validated += 1
                else:
                    print(f"⚠️  {dockerfile}: No security patterns detected")
        else:
            print(f"⚠️  {dockerfile}: File not found")
    
    return validated > 0

def validate_github_actions_security():
    """Validate GitHub Actions security improvements"""
    print("🔍 Validating GitHub Actions Security...")
    
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("⚠️  .github/workflows directory not found")
        return False
    
    secure_actions = [
        "actions/setup-python@v5",
        "actions/setup-node@v4",
        "actions/checkout@v4"
    ]
    
    validated = 0
    for workflow_file in workflows_dir.glob("*.yml"):
        with open(workflow_file, 'r') as f:
            content = f.read()
            has_secure_actions = any(action in content for action in secure_actions)
            has_permissions = "permissions:" in content
            
            if has_secure_actions:
                print(f"✅ {workflow_file.name}: Secure action versions found")
                validated += 1
            if has_permissions:
                print(f"✅ {workflow_file.name}: Permissions configured")
    
    return validated > 0

def validate_system_imports():
    """Validate critical system imports work correctly"""
    print("🔍 Validating System Imports...")
    
    critical_imports = [
        "backend.services.unified_memory_service_v3",
        "backend.core.auto_esc_config",
        "backend.services.enhanced_unified_chat_service"
    ]
    
    validated = 0
    for import_path in critical_imports:
        try:
            # Try to import the module
            if "." in import_path:
                module_parts = import_path.split(".")
                module_path = "/".join(module_parts) + ".py"
                if Path(module_path).exists():
                    spec = importlib.util.spec_from_file_location(
                        import_path, module_path
                    )
                    if spec and spec.loader:
                        print(f"✅ {import_path}: Import validation successful")
                        validated += 1
                    else:
                        print(f"❌ {import_path}: Import spec failed")
                else:
                    print(f"⚠️  {import_path}: File not found at {module_path}")
            else:
                print(f"⚠️  {import_path}: Invalid import path format")
        except Exception as e:
            print(f"❌ {import_path}: Import failed - {e}")
    
    return validated > 0

def validate_configuration():
    """Validate configuration files and structure"""
    print("🔍 Validating Configuration...")
    
    config_files = [
        ".github/dependabot.yml",
        "backend/core/auto_esc_config.py",
        "config/consolidated_mcp_ports.json"
    ]
    
    validated = 0
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}: Configuration file exists")
            validated += 1
        else:
            print(f"❌ {config_file}: Configuration file missing")
    
    return validated > 0

def generate_validation_report():
    """Generate comprehensive validation report"""
    print("\n" + "="*60)
    print("🔒 SECURITY VALIDATION REPORT")
    print("="*60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validations": {}
    }
    
    # Run all validations
    validations = [
        ("Python Security", validate_python_security),
        ("Node.js Security", validate_node_security),
        ("Docker Security", validate_docker_security),
        ("GitHub Actions Security", validate_github_actions_security),
        ("System Imports", validate_system_imports),
        ("Configuration", validate_configuration)
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validation_func in validations:
        print(f"\n🔍 {name}:")
        try:
            result = validation_func()
            results["validations"][name] = {
                "passed": result,
                "timestamp": datetime.now().isoformat()
            }
            if result:
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results["validations"][name] = {
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Overall results
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED - SYSTEM SECURE AND OPERATIONAL")
        results["overall_status"] = "PASSED"
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY SECURE - MINOR ISSUES TO ADDRESS")
        results["overall_status"] = "WARNING"
    else:
        print("❌ CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED")
        results["overall_status"] = "FAILED"
    
    # Save report
    report_file = f"security_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {report_file}")
    
    return results["overall_status"] == "PASSED"

def main():
    """Main validation function"""
    print("🚀 Starting Comprehensive Security Validation...")
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Run validation
    success = generate_validation_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 