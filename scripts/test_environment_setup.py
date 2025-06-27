#!/usr/bin/env python3
"""
Simple environment test script
"""

import os
import sys

print("=== Sophia AI Environment Test ===")
print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'Not set')}")
print(f"PULUMI_ORG: {os.environ.get('PULUMI_ORG', 'Not set')}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

# Test backend import
try:
    sys.path.insert(0, os.getcwd())
    import backend
    print("✅ Backend module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import backend: {e}")

print("\n=== Key Files Check ===")
files_to_check = [
    '.venv/bin/activate',
    'backend/__init__.py',
    'requirements.txt',
    '.cursorrules'
]

for file in files_to_check:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"{status} {file}: {'exists' if exists else 'missing'}")
