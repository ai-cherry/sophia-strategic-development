#!/usr/bin/env python3
"""
Validate Docker build and dependencies
Part of Phoenix 2.1 Docker consolidation
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_toml_syntax():
    """Validate pyproject.toml syntax"""
    logger.info("🔍 Validating pyproject.toml syntax...")
    
    try:
        import tomlkit
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        
        # Parse TOML
        parsed = tomlkit.parse(content)
        logger.info("✅ pyproject.toml syntax is valid")
        
        # Check for common issues
        deps = parsed.get('project', {}).get('dependencies', [])
        logger.info(f"📦 Found {len(deps)} dependencies")
        
        # Check for invalid entries
        invalid_deps = []
        for dep in deps:
            if not isinstance(dep, str):
                invalid_deps.append(dep)
            elif dep.startswith('#') or 'MISSING' in dep:
                invalid_deps.append(dep)
        
        if invalid_deps:
            logger.warning(f"⚠️  Found {len(invalid_deps)} potentially invalid dependencies")
            for dep in invalid_deps[:5]:  # Show first 5
                logger.warning(f"   - {dep}")
        else:
            logger.info("✅ All dependencies appear valid")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ TOML validation failed: {e}")
        return False

def test_uv_resolve():
    """Test UV dependency resolution"""
    logger.info("🔍 Testing UV dependency resolution...")
    
    try:
        # Test UV sync
        result = subprocess.run(
            ['uv', 'pip', 'compile', 'pyproject.toml', '--dry-run'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("✅ UV dependency resolution successful")
            return True
        else:
            logger.error(f"❌ UV resolution failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ UV resolution timed out")
        return False
    except FileNotFoundError:
        logger.warning("⚠️  UV not installed, skipping resolution test")
        return True
    except Exception as e:
        logger.error(f"❌ UV test failed: {e}")
        return False

def test_docker_build():
    """Test Docker build"""
    logger.info("🔍 Testing Docker build...")
    
    try:
        # Start build process
        process = subprocess.Popen(
            ['docker', 'build', '--target', 'production', '-t', 'sophia-ai:validation', '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Monitor build progress
        build_logs = []
        if process.stdout:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    build_logs.append(line)
                    if 'ERROR' in line or 'failed' in line.lower():
                        logger.error(f"Build error: {line}")
        
        # Check result
        if process.returncode == 0:
            logger.info("✅ Docker build successful")
            return True, build_logs
        else:
            logger.error("❌ Docker build failed")
            return False, build_logs
            
    except Exception as e:
        logger.error(f"❌ Docker build test failed: {e}")
        return False, []

def test_container_startup():
    """Test container startup"""
    logger.info("🔍 Testing container startup...")
    
    try:
        # Start container
        result = subprocess.run(
            ['docker', 'run', '--rm', '-d', '--name', 'sophia-test', 
             '-p', '8001:8000', 'sophia-ai:validation'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Container start failed: {result.stderr}")
            return False
        
        container_id = result.stdout.strip()
        logger.info(f"📦 Container started: {container_id[:12]}")
        
        # Wait for startup
        time.sleep(10)
        
        # Test health endpoint
        health_result = subprocess.run(
            ['curl', '-f', 'http://localhost:8001/api/health'],
            capture_output=True,
            text=True
        )
        
        # Cleanup
        subprocess.run(['docker', 'stop', container_id], capture_output=True)
        
        if health_result.returncode == 0:
            logger.info("✅ Container startup and health check successful")
            return True
        else:
            logger.error("❌ Health check failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Container startup test failed: {e}")
        return False

def generate_build_report(results):
    """Generate build validation report"""
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "validation_results": results,
        "overall_status": "PASS" if all(results.values()) else "FAIL",
        "recommendations": []
    }
    
    # Add recommendations based on results
    if not results.get("toml_syntax", True):
        report["recommendations"].append("Fix pyproject.toml syntax errors")
    
    if not results.get("uv_resolve", True):
        report["recommendations"].append("Resolve dependency conflicts")
    
    if not results.get("docker_build", True):
        report["recommendations"].append("Fix Docker build issues")
    
    if not results.get("container_startup", True):
        report["recommendations"].append("Fix application startup issues")
    
    # Save report
    with open('docker_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📋 Validation report saved to docker_validation_report.json")
    return report

def main():
    """Main validation routine"""
    logger.info("🚀 Starting Docker build validation...")
    
    results = {}
    
    # Phase 1: TOML validation
    results["toml_syntax"] = validate_toml_syntax()
    
    # Phase 2: UV resolution
    results["uv_resolve"] = test_uv_resolve()
    
    # Phase 3: Docker build
    if results["toml_syntax"]:
        build_success, build_logs = test_docker_build()
        results["docker_build"] = build_success
        
        # Save build logs
        if build_logs:
            with open('docker_build_logs.txt', 'w') as f:
                f.write('\n'.join(build_logs))
    else:
        logger.warning("⚠️  Skipping Docker build due to TOML errors")
        results["docker_build"] = False
    
    # Phase 4: Container startup (only if build succeeded)
    if results["docker_build"]:
        results["container_startup"] = test_container_startup()
    else:
        logger.warning("⚠️  Skipping container test due to build failure")
        results["container_startup"] = False
    
    # Generate report
    report = generate_build_report(results)
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 VALIDATION SUMMARY")
    logger.info("="*50)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test.replace('_', ' ').title()}: {status}")
    
    logger.info(f"\nOverall Status: {report['overall_status']}")
    
    if report["recommendations"]:
        logger.info("\n🔧 Recommendations:")
        for rec in report["recommendations"]:
            logger.info(f"  - {rec}")
    
    # Exit with appropriate code
    sys.exit(0 if report["overall_status"] == "PASS" else 1)

if __name__ == "__main__":
    main() 