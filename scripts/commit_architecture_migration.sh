#!/bin/bash

# Commit and push architecture migration changes to GitHub

echo "Committing architecture migration changes to GitHub..."

# Add all the new files
git add .githooks/pre-commit
git add scripts/install_git_hooks.sh
git add scripts/check_architecture_consistency.py
git add scripts/migrate_vector_store_access.py
git add scripts/build_admin_dashboard.py
git add scripts/run_architecture_migration.py
git add .github/workflows/architecture-consistency.yml
git add examples/gong_mcp_client.py
git add examples/deploy_production_mcp.py
git add examples/memory_manager_client.py
git add deploy_production_mcp.py
git add architecture_migration_summary.md
git add scripts/commit_architecture_migration.sh

# Add any modified files
git add -u

# Commit the changes
git commit -m "Implement architecture migration to MCP federation model

- Add architecture consistency checker
- Add vector store access migration tool
- Add admin dashboard builder
- Add architecture migration automation
- Add CI/CD integration with GitHub Actions
- Add git hooks for pre-commit checks
- Add example implementations for migration patterns
- Add comprehensive documentation"

# Push to main branch
git push origin main

echo "Architecture migration changes committed and pushed to GitHub."
echo "Migration complete!"
