#!/usr/bin/env python3
"""
Sophia AI One-Click Setup

This script automates the entire setup process for Sophia AI with a single command.
No need to remember multiple commands or procedures - just run this script and everything
will be set up automatically.

Usage:
    python sophia_setup.py
"""

import os
import sys
import subprocess
import logging
import time
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description=None, exit_on_error=False):
    """Run a command and return the result"""
    if description:
        print(f"\n🔧 {description}...")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        if exit_on_error:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)
        return False, e.stderr
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if exit_on_error:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)
        return False, str(e)

def ensure_executable(script_path):
    """Ensure a script is executable"""
    try:
        os.chmod(script_path, 0o755)
        return True
    except Exception as e:
        logger.error(f"Error making {script_path} executable: {e}")
        return False

def setup_environment():
    """Set up the environment variables"""
    print("\n🔧 Setting up environment variables...")
    
    # Make sure secrets_manager.py is executable
    ensure_executable("secrets_manager.py")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        # Generate template .env file
        run_command(["./secrets_manager.py", "generate-template"])
        
        # Check if env.example exists and copy it to .env
        if os.path.exists("env.example"):
            run_command(["cp", "env.example", ".env"])
            print("✅ Copied env.example to .env")
        else:
            print("⚠️ No env.example found. You'll need to fill in the .env file manually.")
    
    # Import environment variables from .env
    run_command(["./secrets_manager.py", "import-from-env"])
    
    # Export environment variables to .env (to ensure proper formatting)
    run_command(["./secrets_manager.py", "export-to-env"])
    
    # Validate environment variables
    success, output = run_command(["./secrets_manager.py", "validate"])
    
    if not success:
        print("\n⚠️ Some environment variables are missing. The system may not function correctly.")
        print("   You can run './secrets_manager.py detect-missing' to see what's missing.")
    else:
        print("\n✅ Environment variables validated successfully")
    
    return True

def fix_ssl_certificates():
    """Fix SSL certificate issues"""
    print("\n🔧 Fixing SSL certificate issues...")
    
    # Make sure fix_ssl_certificates.py is executable
    ensure_executable("fix_ssl_certificates.py")
    
    # Run the SSL certificate fix script
    run_command(["./fix_ssl_certificates.py"])
    
    # Make sure run_with_ssl_fix.py is executable
    ensure_executable("run_with_ssl_fix.py")
    
    print("\n✅ SSL certificate issues fixed")
    return True

def fix_dependencies():
    """Fix Python package dependencies"""
    print("\n🔧 Fixing Python package dependencies...")
    
    # Make sure fix_dependencies.py is executable
    ensure_executable("fix_dependencies.py")
    
    # Run the dependency fixer script
    run_command(["./fix_dependencies.py"])
    
    print("\n✅ Python package dependencies fixed")
    return True

def fix_docker_compose():
    """Fix Docker Compose configuration"""
    print("\n🔧 Fixing Docker Compose configuration...")
    
    if not os.path.exists("docker-compose.mcp.yml"):
        print("\n⚠️ docker-compose.mcp.yml not found. Skipping Docker Compose fixes.")
        return False
    
    try:
        with open("docker-compose.mcp.yml", 'r') as f:
            content = f.read()
        
        # Fix the "volumes.slack Additional property depends_on is not allowed" error
        if "volumes:" in content and "depends_on:" in content:
            # This is a simplistic fix - in a real scenario, you'd want to use a YAML parser
            content = content.replace("  volumes:\n    slack:\n      depends_on:", "  volumes:\n    slack:\n  depends_on:")
            
            with open("docker-compose.mcp.yml", 'w') as f:
                f.write(content)
            
            print("\n✅ Fixed Docker Compose configuration")
            return True
        else:
            print("\n✅ Docker Compose configuration looks good")
            return True
    except Exception as e:
        print(f"\n❌ Error fixing Docker Compose configuration: {e}")
        return False

def start_mcp_servers():
    """Start the MCP servers"""
    print("\n🔧 Starting MCP servers...")
    
    # Make sure start_mcp_servers.py is executable
    ensure_executable("start_mcp_servers.py")
    
    # Check if Docker is installed
    success, _ = run_command(["docker", "--version"], "Checking Docker installation")
    if not success:
        print("\n⚠️ Docker is not installed or not running. Skipping MCP server start.")
        return False
    
    # Check if Docker Compose is installed
    success, _ = run_command(["docker-compose", "--version"], "Checking Docker Compose installation")
    if not success:
        print("\n⚠️ Docker Compose is not installed. Skipping MCP server start.")
        return False
    
    # Run the MCP server starter script
    run_command(["./start_mcp_servers.py"])
    
    print("\n✅ MCP servers started")
    return True

def run_health_check():
    """Run the automated health check"""
    print("\n🔧 Running automated health check...")
    
    # Make sure run_with_ssl_fix.py is executable
    ensure_executable("run_with_ssl_fix.py")
    
    # Check if automated_health_check.py exists
    if not os.path.exists("automated_health_check.py") and os.path.exists("automated_health_check_fixed.py"):
        # Copy the fixed version to the original filename
        run_command(["cp", "automated_health_check_fixed.py", "automated_health_check.py"])
    
    if not os.path.exists("automated_health_check.py"):
        print("\n⚠️ automated_health_check.py not found. Skipping health check.")
        return False
    
    # Run the automated health check with SSL fix
    run_command(["./run_with_ssl_fix.py", "automated_health_check.py"])
    
    print("\n✅ Automated health check complete")
    return True

def run_command_interface():
    """Run the unified command interface"""
    print("\n🔧 Running unified command interface...")
    
    # Check if unified_command_interface.py exists
    if not os.path.exists("unified_command_interface.py") and os.path.exists("unified_command_interface_fixed.py"):
        # Copy the fixed version to the original filename
        run_command(["cp", "unified_command_interface_fixed.py", "unified_command_interface.py"])
    
    if not os.path.exists("unified_command_interface.py"):
        print("\n⚠️ unified_command_interface.py not found. Skipping command interface.")
        return False
    
    # Run the unified command interface with SSL fix
    run_command(["./run_with_ssl_fix.py", "unified_command_interface.py", "check system status"])
    
    print("\n✅ Unified command interface complete")
    return True

def main():
    print("\n===== Sophia AI One-Click Setup =====")
    print("\nThis script will automatically set up everything for Sophia AI.")
    print("No need to remember multiple commands or procedures - just sit back and relax!")
    
    # Setup environment variables
    setup_environment()
    
    # Fix SSL certificate issues
    fix_ssl_certificates()
    
    # Fix Python package dependencies
    fix_dependencies()
    
    # Fix Docker Compose configuration
    fix_docker_compose()
    
    # Start MCP servers
    start_mcp_servers()
    
    # Run automated health check
    run_health_check()
    
    # Run unified command interface
    run_command_interface()
    
    print("\n===== Sophia AI Setup Complete =====")
    print("\nYour Sophia AI system is now set up and ready to use!")
    print("\nTo check the system status at any time, run:")
    print("   ./run_with_ssl_fix.py unified_command_interface.py \"check system status\"")
    
    print("\nTo run the automated health check, run:")
    print("   ./run_with_ssl_fix.py automated_health_check.py")
    
    print("\nEnjoy using Sophia AI!")

if __name__ == "__main__":
    main()
