#!/bin/bash
# scripts/create_clean_architecture.sh

echo "Creating clean architecture directories..."

# Create main directories
mkdir -p api/{routes,models,dependencies,middleware}
mkdir -p core/{agents,services,use_cases,workflows,ports}
mkdir -p domain/{models,entities,events,value_objects}
mkdir -p infrastructure/{integrations,mcp_servers,etl,monitoring,security,services,database}
mkdir -p shared/{utils,prompts,constants,exceptions}

# Create __init__.py files
find api core domain infrastructure shared -type d -exec touch {}/__init__.py \;

# Create reports directory
mkdir -p reports

echo "Directory structure created successfully"
