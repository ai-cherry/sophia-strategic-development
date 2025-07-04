#!/usr/bin/env python3
"""
Archive remaining non-core documentation files
"""

import os
import shutil
from datetime import datetime

# Core documents to keep
CORE_DOCS = {
    "API_DOCUMENTATION.md",
    "APPLICATION_STRUCTURE.md",
    "REMEDIATION_SUMMARY.md",  # Keep our new summary
    "IMMEDIATE_REMEDIATION_ACTIONS.md",  # Keep our action plan
}

# Documents that should be in subdirectories
SUBDIRECTORY_DOCS = {
    "00_SOPHIA_AI_SYSTEM_HANDBOOK.md": "system_handbook/",
}


def archive_remaining_docs():
    """Archive all non-core documents"""
    archive_dir = f"docs/archive/cleanup_{datetime.now().strftime('%Y%m%d')}_phase2"

    # Create archive directories
    os.makedirs(f"{archive_dir}/technical", exist_ok=True)
    os.makedirs(f"{archive_dir}/research", exist_ok=True)
    os.makedirs(f"{archive_dir}/strategy", exist_ok=True)
    os.makedirs(f"{archive_dir}/reference", exist_ok=True)
    os.makedirs(f"{archive_dir}/other", exist_ok=True)

    archived_count = 0
    kept_count = 0

    # Get all markdown files in docs root
    docs_dir = "docs"
    for file in os.listdir(docs_dir):
        if file.endswith(".md"):
            file_path = os.path.join(docs_dir, file)

            # Skip if it's a core document
            if file in CORE_DOCS:
                print(f"✅ KEEPING: {file} (core document)")
                kept_count += 1
                continue

            # Determine archive category
            if "STRATEGY" in file or "UNIVERSAL" in file:
                category = "strategy"
            elif "PROMPT" in file or "RESEARCH" in file:
                category = "research"
            elif any(
                tech in file
                for tech in ["DOCKER", "MCP", "LLM", "UNIFIED", "LANGCHAIN"]
            ):
                category = "technical"
            elif "REFERENCE" in file or "GUIDELINES" in file or "TEMPLATE" in file:
                category = "reference"
            else:
                category = "other"

            # Archive the file
            dst = os.path.join(archive_dir, category, file)
            try:
                shutil.move(file_path, dst)
                print(f"📦 Archived: {file} → {category}/")
                archived_count += 1
            except Exception as e:
                print(f"❌ Error archiving {file}: {e}")

    # Create index
    with open(f"{archive_dir}/INDEX.md", "w") as f:
        f.write("# Documentation Archive Index - Phase 2\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("## Summary\n")
        f.write(f"- Total files archived: {archived_count}\n")
        f.write(f"- Core files kept: {kept_count}\n")
        f.write(f"- Archive location: {archive_dir}\n\n")
        f.write("## Core Documents Retained\n")
        for doc in CORE_DOCS:
            f.write(f"- {doc}\n")

    print("\n📊 Summary:")
    print(f"   Archived: {archived_count} files")
    print(f"   Kept: {kept_count} core files")
    print(f"📝 Index created: {archive_dir}/INDEX.md")

    # Create missing core documents
    create_missing_core_docs()


def create_missing_core_docs():
    """Create any missing core documents"""
    print("\n📝 Creating missing core documents...")

    # Create DEPLOYMENT_CHECKLIST.md if missing
    if not os.path.exists("docs/DEPLOYMENT_CHECKLIST.md"):
        with open("docs/DEPLOYMENT_CHECKLIST.md", "w") as f:
            f.write(
                """# Sophia AI Deployment Checklist

## Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Snowflake connection verified
- [ ] MCP servers health check

## Deployment Steps
1. Build Docker image: `docker build -t sophia-ai .`
2. Run health checks: `python scripts/health_check.py`
3. Deploy: `docker-compose up -d`
4. Verify: `curl http://localhost:8000/health`

## Post-Deployment
- [ ] Monitor logs for errors
- [ ] Test chat endpoint
- [ ] Verify MCP connectivity
- [ ] Check performance metrics
"""
            )
        print("✅ Created DEPLOYMENT_CHECKLIST.md")

    # Create DEVELOPMENT_QUICKSTART.md if missing
    if not os.path.exists("docs/DEVELOPMENT_QUICKSTART.md"):
        with open("docs/DEVELOPMENT_QUICKSTART.md", "w") as f:
            f.write(
                """# Sophia AI Development Quickstart

## Prerequisites
- Python 3.12+
- UV package manager
- Docker Desktop
- Snowflake account

## Quick Setup (5 minutes)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ai-cherry/sophia-main.git
   cd sophia-main
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

3. **Configure environment:**
   ```bash
   export PULUMI_ORG=scoobyjava-org
   export ENVIRONMENT=prod
   ```

4. **Run the application:**
   ```bash
   cd backend/app
   python app.py
   ```

5. **Verify it's working:**
   ```bash
   curl http://localhost:8000/health
   ```

## Architecture Overview
See the [System Handbook](system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md) for detailed architecture.

## Common Tasks
- **Add an API endpoint:** See [API Documentation](API_DOCUMENTATION.md)
- **Deploy to production:** See [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- **Understand the structure:** See [Application Structure](APPLICATION_STRUCTURE.md)

## Need Help?
- Check the [Remediation Summary](REMEDIATION_SUMMARY.md) for current status
- Review [Immediate Actions](IMMEDIATE_REMEDIATION_ACTIONS.md) for ongoing work
"""
            )
        print("✅ Created DEVELOPMENT_QUICKSTART.md")


if __name__ == "__main__":
    archive_remaining_docs()
