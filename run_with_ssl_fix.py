#!/usr/bin/env python3
"""
Sophia AI SSL Certificate Fix Wrapper

This script runs a Python script with the SSL_CERT_FILE environment variable
set to the path of the certifi cacert.pem file.

Usage:
    python run_with_ssl_fix.py <script> [args...]
"""

import os
import sys
import subprocess

# Set the SSL_CERT_FILE environment variable
os.environ["SSL_CERT_FILE"] = "/Users/lynnmusil/sophia-main-5/sophia_venv/lib/python3.11/site-packages/certifi/cacert.pem"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_with_ssl_fix.py <script> [args...]")
        sys.exit(1)
    
    # Get the script and arguments
    script = sys.argv[1]
    args = sys.argv[2:]
    
    # Run the script with the SSL certificate fix
    result = subprocess.run([sys.executable, script] + args)
    sys.exit(result.returncode)
