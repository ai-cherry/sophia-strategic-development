#!/usr/bin/env bash
# Simple setup script for Sophia AI
# Installs required Python packages

set -e

if [ ! -f requirements.txt ]; then
  echo "requirements.txt not found. Please ensure it exists before running this script." >&2
  exit 1
fi

pip install -r requirements.txt

echo "Dependencies installed."
