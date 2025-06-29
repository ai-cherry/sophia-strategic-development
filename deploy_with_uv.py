#!/usr/bin/env python3
"""
🚀 UV-Compatible Deployment Script for Sophia AI
===============================================

This script handles deployment using UV for dependency management.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Main deployment function using UV."""
    print("🚀 Starting UV-based deployment...")
    
    # Install dependencies with UV
    subprocess.run([
        "uv", "pip", "install", "-r", "requirements.txt"
    ], check=True)
    
    # Run application with UV
    subprocess.run([
        "uv", "run", "python", "-m", "backend.app.fastapi_app"
    ], check=True)

if __name__ == "__main__":
    main()
