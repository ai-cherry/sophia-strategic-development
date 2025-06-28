#!/bin/bash

# Install Git hooks for the Sophia AI project

echo "Installing Git hooks..."

# Create the .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy the pre-commit hook
cp .githooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

echo "Git hooks installed successfully."
echo "The pre-commit hook will check for architecture inconsistencies before each commit."
