#!/usr/bin/env python3
"""
Fix common Docker build issues
Part of Phoenix 2.1 Docker remediation
"""

import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_pyproject_toml():
    """Fix pyproject.toml issues"""
    logger.info("🔧 Fixing pyproject.toml issues...")
    
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        logger.error("❌ pyproject.toml not found")
        return False
    
    # Read current content
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    # Check if readme is specified but doesn't exist in Docker context
    if 'readme = "README.md"' in content:
        readme_path = Path("README.md")
        if not readme_path.exists():
            logger.info("📝 Creating missing README.md")
            with open(readme_path, 'w') as f:
                f.write("""# Sophia AI Platform

Enterprise AI Orchestration Platform with Unified FastAPI backend.

## Quick Start

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Documentation

See `docs/` directory for comprehensive documentation.
""")
            logger.info("✅ Created README.md")
    
    return True

def fix_dockerignore():
    """Fix .dockerignore to include necessary files"""
    logger.info("🔧 Fixing .dockerignore...")
    
    dockerignore_path = Path(".dockerignore")
    if not dockerignore_path.exists():
        logger.warning("⚠️  .dockerignore not found")
        return False
    
    with open(dockerignore_path, 'r') as f:
        content = f.read()
    
    # Ensure README.md is not ignored
    if "!README.md" not in content:
        logger.info("📝 Adding README.md exception to .dockerignore")
        content = content.replace("*.md", "*.md\n!README.md")
        
        with open(dockerignore_path, 'w') as f:
            f.write(content)
        logger.info("✅ Updated .dockerignore")
    
    return True

def check_required_files():
    """Check for required files in build context"""
    logger.info("🔍 Checking required files...")
    
    required_files = [
        "pyproject.toml",
        "README.md",
        "backend/",
        "config/",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"❌ Missing required files: {missing_files}")
        return False
    
    logger.info("✅ All required files present")
    return True

def optimize_pyproject_dependencies():
    """Optimize dependencies in pyproject.toml"""
    logger.info("🔧 Optimizing dependencies...")
    
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    # Check for common problematic dependencies
    problematic_patterns = [
        "# MISSING",
        ">=1.7.4\",",  # Malformed version
        "\"\"",        # Empty strings
    ]
    
    issues_found = []
    for pattern in problematic_patterns:
        if pattern in content:
            issues_found.append(pattern)
    
    if issues_found:
        logger.warning(f"⚠️  Found potentially problematic patterns: {issues_found}")
        logger.info("💡 Consider running: python scripts/validate_docker_build.py")
    else:
        logger.info("✅ Dependencies look clean")
    
    return True

def create_minimal_backend_init():
    """Ensure backend/__init__.py exists for package detection"""
    logger.info("🔧 Ensuring backend package structure...")
    
    backend_init = Path("backend/__init__.py")
    if not backend_init.exists():
        logger.info("📝 Creating backend/__init__.py")
        backend_init.parent.mkdir(exist_ok=True)
        with open(backend_init, 'w') as f:
            f.write('"""Sophia AI Backend Package"""\n')
        logger.info("✅ Created backend/__init__.py")
    
    # Also ensure core module exists
    core_init = Path("backend/core/__init__.py")
    if not core_init.exists():
        logger.info("📝 Creating backend/core/__init__.py")
        core_init.parent.mkdir(exist_ok=True)
        with open(core_init, 'w') as f:
            f.write('"""Sophia AI Core Module"""\n')
        logger.info("✅ Created backend/core/__init__.py")
    
    return True

def main():
    """Main fix routine"""
    logger.info("🚀 Starting Docker build issue fixes...")
    
    fixes = [
        ("pyproject.toml", fix_pyproject_toml),
        (".dockerignore", fix_dockerignore),
        ("required files", check_required_files),
        ("dependencies", optimize_pyproject_dependencies),
        ("backend package", create_minimal_backend_init),
    ]
    
    results = {}
    for name, fix_func in fixes:
        logger.info(f"\n🔧 Running fix: {name}")
        try:
            results[name] = fix_func()
        except Exception as e:
            logger.error(f"❌ Fix failed for {name}: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 FIX SUMMARY")
    logger.info("="*50)
    
    for name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{name}: {status}")
    
    overall_success = all(results.values())
    logger.info(f"\nOverall Status: {'✅ ALL FIXES SUCCESSFUL' if overall_success else '❌ SOME FIXES FAILED'}")
    
    if overall_success:
        logger.info("\n🎉 Ready to test Docker build:")
        logger.info("   docker build --target production -t sophia-ai:test .")
    else:
        logger.info("\n🔧 Please address failed fixes before building")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 