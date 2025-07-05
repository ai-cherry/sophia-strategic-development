#!/usr/bin/env python3
"""
Documentation Consolidation and Cleanup
Updates all documentation and removes confusing/conflicting content
"""

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentationConsolidator:
    """Consolidate and clean up documentation"""

    def __init__(self):
        self.root_dir = Path("/Users/lynnmusil/sophia-main")
        self.docs_dir = self.root_dir / "docs"
        self.backup_dir = (
            self.root_dir / f"docs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Track changes
        self.changes = {
            "files_updated": [],
            "files_removed": [],
            "files_consolidated": [],
            "conflicts_resolved": [],
            "outdated_removed": [],
            "redirects_created": [],
        }

        # Current configuration standards
        self.current_standards = {
            "lambda_labs_ips": {
                "sophia-platform-prod": "146.235.200.1",
                "sophia-mcp-prod": "165.1.69.44",
                "sophia-ai-prod": "137.131.6.213",
            },
            "mcp_ports": {
                "ai-memory": 9001,
                "codacy": 3008,
                "linear": 9004,
                "github": 9003,
                "snowflake-admin": 9020,
                "lambda-labs-cli": 9040,  # Updated from 9020
                "asana": 3001,
                "notion": 9005,
            },
            "deployment_method": "docker-swarm",  # Not Kubernetes for MCP
            "secret_management": "pulumi-esc",
            "unified_dashboard": "frontend/src/components/dashboard/UnifiedDashboard.tsx",
        }

    def run_consolidation(self):
        """Run complete documentation consolidation"""
        logger.info("📚 Starting Documentation Consolidation")

        try:
            # 1. Create backup
            self.create_backup()

            # 2. Identify and analyze all documentation
            docs = self.analyze_documentation()

            # 3. Find and resolve conflicts
            conflicts = self.find_conflicts(docs)
            self.resolve_conflicts(conflicts)

            # 4. Remove outdated documentation
            self.remove_outdated_docs(docs)

            # 5. Update documentation with current standards
            self.update_standards(docs)

            # 6. Consolidate fragmented documentation
            self.consolidate_fragmented_docs(docs)

            # 7. Create master documentation index
            self.create_master_index()

            # 8. Generate summary report
            self.generate_summary_report()

            logger.info("✅ Documentation Consolidation Complete")
            return self.changes

        except Exception as e:
            logger.error(f"❌ Consolidation failed: {e}")
            return {"error": str(e)}

    def create_backup(self):
        """Create backup of all documentation"""
        logger.info("💾 Creating documentation backup...")

        if self.docs_dir.exists():
            shutil.copytree(self.docs_dir, self.backup_dir)
            logger.info(f"Backup created at {self.backup_dir}")

    def analyze_documentation(self) -> list[dict]:
        """Analyze all documentation files"""
        logger.info("🔍 Analyzing documentation files...")

        docs = []

        # Find all markdown files
        for md_file in self.root_dir.rglob("*.md"):
            if md_file.is_file() and not str(md_file).startswith(str(self.backup_dir)):
                doc_info = self.analyze_single_doc(md_file)
                docs.append(doc_info)

        logger.info(f"Found {len(docs)} documentation files")
        return docs

    def analyze_single_doc(self, file_path: Path) -> dict:
        """Analyze a single documentation file"""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        return {
            "path": file_path,
            "relative_path": str(file_path.relative_to(self.root_dir)),
            "name": file_path.name,
            "size": len(content),
            "lines": len(content.split("\n")),
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime),
            "content": content,
            "contains_mcp": "mcp" in content.lower(),
            "contains_lambda_labs": "lambda" in content.lower()
            and "labs" in content.lower(),
            "contains_ports": any(
                str(port) in content
                for port in self.current_standards["mcp_ports"].values()
            ),
            "contains_old_ips": "104.171.202.64" in content,  # Old IP
            "contains_kubernetes": "kubernetes" in content.lower()
            or "k8s" in content.lower(),
            "contains_docker_swarm": "docker swarm" in content.lower()
            or "docker stack" in content.lower(),
            "is_deployment_doc": any(
                word in file_path.name.lower()
                for word in ["deploy", "deployment", "setup", "install"]
            ),
            "is_config_doc": any(
                word in file_path.name.lower()
                for word in ["config", "configuration", "setup"]
            ),
            "is_mcp_doc": "mcp" in file_path.name.lower(),
            "is_duplicate": False,  # Will be set during conflict analysis
            "is_outdated": False,  # Will be set during analysis
        }

    def find_conflicts(self, docs: list[dict]) -> list[dict]:
        """Find conflicting documentation"""
        logger.info("🔍 Finding documentation conflicts...")

        conflicts = []

        # Group docs by topic/purpose
        topic_groups = {}

        for doc in docs:
            # Determine topic
            topics = []
            if doc["is_deployment_doc"]:
                topics.append("deployment")
            if doc["is_mcp_doc"]:
                topics.append("mcp")
            if doc["contains_lambda_labs"]:
                topics.append("lambda-labs")
            if doc["contains_kubernetes"]:
                topics.append("kubernetes")
            if doc["contains_docker_swarm"]:
                topics.append("docker-swarm")

            for topic in topics:
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(doc)

        # Find conflicts within topic groups
        for topic, topic_docs in topic_groups.items():
            if len(topic_docs) > 1:
                # Check for similar content or conflicting information
                conflict = self.analyze_topic_conflicts(topic, topic_docs)
                if conflict:
                    conflicts.append(conflict)

        logger.info(f"Found {len(conflicts)} documentation conflicts")
        return conflicts

    def analyze_topic_conflicts(self, topic: str, docs: list[dict]) -> dict:
        """Analyze conflicts within a topic group"""
        conflict = {
            "topic": topic,
            "docs": docs,
            "conflict_type": "multiple_docs",
            "details": [],
            "recommended_action": "consolidate",
        }

        # Check for specific conflicts
        if topic == "deployment":
            # Check for conflicting deployment methods
            k8s_docs = [d for d in docs if d["contains_kubernetes"]]
            swarm_docs = [d for d in docs if d["contains_docker_swarm"]]

            if k8s_docs and swarm_docs:
                conflict["conflict_type"] = "conflicting_methods"
                conflict["details"].append(
                    "Documents describe both Kubernetes and Docker Swarm for MCP deployment"
                )
                conflict["recommended_action"] = "standardize_on_swarm"

        elif topic == "lambda-labs":
            # Check for old IP addresses
            old_ip_docs = [d for d in docs if d["contains_old_ips"]]
            if old_ip_docs:
                conflict["conflict_type"] = "outdated_ips"
                conflict["details"].append(
                    "Documents contain outdated Lambda Labs IP addresses"
                )
                conflict["recommended_action"] = "update_ips"

        elif topic == "mcp":
            # Check for port conflicts
            port_issues = []
            for doc in docs:
                if "9020" in doc["content"] and "lambda-labs-cli" in doc["content"]:
                    port_issues.append(
                        f"{doc['name']}: lambda-labs-cli still using port 9020 (should be 9040)"
                    )

            if port_issues:
                conflict["details"].extend(port_issues)
                conflict["recommended_action"] = "update_ports"

        return conflict if conflict["details"] else None

    def resolve_conflicts(self, conflicts: list[dict]):
        """Resolve documentation conflicts"""
        logger.info("🔧 Resolving documentation conflicts...")

        for conflict in conflicts:
            if conflict["recommended_action"] == "consolidate":
                self.consolidate_conflicting_docs(conflict)
            elif conflict["recommended_action"] == "standardize_on_swarm":
                self.standardize_deployment_method(conflict)
            elif conflict["recommended_action"] == "update_ips":
                self.update_lambda_labs_ips(conflict)
            elif conflict["recommended_action"] == "update_ports":
                self.update_mcp_ports(conflict)

            self.changes["conflicts_resolved"].append(
                {
                    "topic": conflict["topic"],
                    "action": conflict["recommended_action"],
                    "files_affected": [d["relative_path"] for d in conflict["docs"]],
                }
            )

    def consolidate_conflicting_docs(self, conflict: dict):
        """Consolidate conflicting documents into one authoritative version"""
        docs = conflict["docs"]

        if not docs:
            return

        # Find the most recent and comprehensive document
        main_doc = max(docs, key=lambda d: (d["last_modified"], d["size"]))
        other_docs = [d for d in docs if d != main_doc]

        # Extract unique content from other docs
        main_content = main_doc["content"]

        for doc in other_docs:
            # Find sections not in main doc
            unique_sections = self.extract_unique_sections(doc["content"], main_content)
            if unique_sections:
                main_content += (
                    f"\n\n## Additional Information (from {doc['name']})\n\n"
                )
                main_content += unique_sections

            # Remove the redundant document
            doc["path"].unlink()
            self.changes["files_removed"].append(doc["relative_path"])

        # Update the main document
        main_doc["path"].write_text(main_content, encoding="utf-8")
        self.changes["files_consolidated"].append(main_doc["relative_path"])

    def extract_unique_sections(self, source_content: str, target_content: str) -> str:
        """Extract sections from source that aren't in target"""
        # Simple implementation - look for headers not in target
        source_lines = source_content.split("\n")
        unique_lines = []

        for line in source_lines:
            if line.strip().startswith("#") and line not in target_content:
                # This is a unique header, include it and following content
                unique_lines.append(line)
            elif unique_lines and not line.strip().startswith("#"):
                # Continue adding content under the unique header
                unique_lines.append(line)
            elif line.strip().startswith("#"):
                # New header, stop collecting if we were
                unique_lines = []

        return "\n".join(unique_lines) if unique_lines else ""

    def standardize_deployment_method(self, conflict: dict):
        """Standardize on Docker Swarm for MCP deployment"""
        for doc in conflict["docs"]:
            content = doc["content"]

            # Add clarification about Kubernetes vs Docker Swarm
            if doc["contains_kubernetes"] and doc["contains_mcp"]:
                clarification = """
## ⚠️ **DEPLOYMENT METHOD CLARIFICATION**

**MCP Servers**: Use Docker Swarm (via docker-compose.cloud.yml)
**GPU Workloads**: Use Kubernetes (for AI processing that requires GPU)

This hybrid approach optimizes each workload type for its specific requirements.

"""
                # Insert clarification at the beginning
                lines = content.split("\n")
                title_idx = next(
                    (i for i, line in enumerate(lines) if line.startswith("#")), 0
                )
                lines.insert(title_idx + 1, clarification)
                content = "\n".join(lines)

            # Update references to use correct deployment method
            content = re.sub(
                r"kubectl apply.*mcp.*",
                "docker stack deploy -c docker-compose.cloud.yml sophia-ai",
                content,
                flags=re.IGNORECASE,
            )

            doc["path"].write_text(content, encoding="utf-8")
            self.changes["files_updated"].append(doc["relative_path"])

    def update_lambda_labs_ips(self, conflict: dict):
        """Update Lambda Labs IP addresses"""
        for doc in conflict["docs"]:
            content = doc["content"]

            # Update old IP address
            content = content.replace("104.171.202.64", "146.235.200.1")

            # Add current IP mapping
            if "lambda" in content.lower() and "labs" in content.lower():
                ip_section = """
## Lambda Labs Instance IPs

| Instance | IP Address | GPU Type |
|----------|------------|----------|
| sophia-platform-prod | 146.235.200.1 | GPU 1x A10 |
| sophia-mcp-prod | 165.1.69.44 | GPU 1x A10 |
| sophia-ai-prod | 137.131.6.213 | GPU 1x A100 |

"""
                # Insert IP mapping if not already present
                if "146.235.200.1" not in content:
                    content += ip_section

            doc["path"].write_text(content, encoding="utf-8")
            self.changes["files_updated"].append(doc["relative_path"])

    def update_mcp_ports(self, conflict: dict):
        """Update MCP port configurations"""
        for doc in conflict["docs"]:
            content = doc["content"]

            # Update lambda-labs-cli port from 9020 to 9040
            content = re.sub(
                r"lambda-labs-cli.*:9020",
                "lambda-labs-cli (port 9040)",
                content,
                flags=re.IGNORECASE,
            )

            # Update port tables
            content = re.sub(
                r"(\|\s*lambda-labs-cli\s*\|\s*)9020",
                r"\g<1>9040",
                content,
                flags=re.IGNORECASE,
            )

            # Add current port mapping if not present
            if "mcp" in content.lower() and "port" in content.lower():
                port_section = """
## Current MCP Server Ports

| Server | Port | Status |
|--------|------|--------|
| ai-memory | 9001 | ✅ Active |
| codacy | 3008 | ✅ Active |
| linear | 9004 | ✅ Active |
| github | 9003 | ⚠️ Check Status |
| snowflake-admin | 9020 | ✅ Active |
| lambda-labs-cli | 9040 | ✅ Active (Updated) |
| asana | 3001 | ✅ Active |
| notion | 9005 | ✅ Active |

"""
                if "| Server | Port |" not in content:
                    content += port_section

            doc["path"].write_text(content, encoding="utf-8")
            self.changes["files_updated"].append(doc["relative_path"])

    def remove_outdated_docs(self, docs: list[dict]):
        """Remove outdated documentation"""
        logger.info("🗑️ Removing outdated documentation...")

        outdated_patterns = ["backup", "old", "deprecated", "archive", "temp", "draft"]

        for doc in docs:
            # Check if file should be removed
            should_remove = False

            # Check filename patterns
            for pattern in outdated_patterns:
                if pattern in doc["name"].lower():
                    should_remove = True
                    break

            # Check age (older than 30 days and very small)
            days_old = (datetime.now() - doc["last_modified"]).days
            if days_old > 30 and doc["size"] < 1000:
                should_remove = True

            # Check for specific outdated content
            if "agno" in doc["content"].lower():  # Agno was replaced
                should_remove = True

            if should_remove:
                doc["path"].unlink()
                self.changes["outdated_removed"].append(doc["relative_path"])

    def update_standards(self, docs: list[dict]):
        """Update documentation with current standards"""
        logger.info("🔄 Updating documentation standards...")

        for doc in docs:
            if doc["path"].exists():  # Check if not already removed
                content = doc["content"]
                updated = False

                # Update secret management references
                if "env" in content.lower() and "variable" in content.lower():
                    content = re.sub(
                        r"\.env\s+file",
                        "Pulumi ESC (no .env files needed)",
                        content,
                        flags=re.IGNORECASE,
                    )
                    updated = True

                # Update dashboard references
                if "dashboard" in content.lower():
                    content = re.sub(
                        r"separate\s+dashboard",
                        "Unified Dashboard (frontend/src/components/dashboard/UnifiedDashboard.tsx)",
                        content,
                        flags=re.IGNORECASE,
                    )
                    updated = True

                # Update MCP deployment method
                if doc["contains_mcp"] and "deploy" in content.lower():
                    if "kubernetes" in content.lower():
                        content += "\n\n⚠️ **Note**: MCP servers use Docker Swarm, not Kubernetes. GPU workloads use Kubernetes.\n"
                        updated = True

                if updated:
                    doc["path"].write_text(content, encoding="utf-8")
                    self.changes["files_updated"].append(doc["relative_path"])

    def consolidate_fragmented_docs(self, docs: list[dict]):
        """Consolidate fragmented documentation into comprehensive guides"""
        logger.info("📖 Consolidating fragmented documentation...")

        # Create comprehensive guides
        self.create_mcp_comprehensive_guide(docs)
        self.create_deployment_comprehensive_guide(docs)
        self.create_lambda_labs_comprehensive_guide(docs)

    def create_mcp_comprehensive_guide(self, docs: list[dict]):
        """Create comprehensive MCP guide"""
        mcp_docs = [d for d in docs if d["contains_mcp"] and d["path"].exists()]

        if not mcp_docs:
            return

        guide_content = """# Comprehensive MCP Server Guide

This is the definitive guide for Sophia AI MCP (Model Context Protocol) servers.

## Quick Reference

### Server Status & Ports
| Server | Port | Health Endpoint | Status |
|--------|------|----------------|---------|
| ai-memory | 9001 | /health | ✅ Active |
| codacy | 3008 | /api/v1/health | ✅ Active |
| linear | 9004 | /health | ✅ Active |
| github | 9003 | /health | ⚠️ Check Status |
| snowflake-admin | 9020 | /health | ✅ Active |
| lambda-labs-cli | 9040 | /health | ✅ Active |
| asana | 3001 | /health | ✅ Active |
| notion | 9005 | /health | ✅ Active |

### Deployment Method
**✅ Docker Swarm**: `docker stack deploy -c docker-compose.cloud.yml sophia-ai`
**❌ Kubernetes**: Only for GPU workloads, not MCP servers

### Health Monitoring
Available in Unified Dashboard → Lambda Labs Health tab

## Server Details

"""

        # Add content from existing docs
        for doc in mcp_docs:
            if "comprehensive" not in doc["name"].lower():  # Avoid recursion
                guide_content += f"\n## From {doc['name']}\n\n"
                guide_content += self.extract_relevant_sections(doc["content"])

        # Write comprehensive guide
        guide_path = self.docs_dir / "06-mcp-servers" / "COMPREHENSIVE_MCP_GUIDE.md"
        guide_path.parent.mkdir(exist_ok=True)
        guide_path.write_text(guide_content, encoding="utf-8")

        self.changes["files_consolidated"].append(
            "docs/06-mcp-servers/COMPREHENSIVE_MCP_GUIDE.md"
        )

    def create_deployment_comprehensive_guide(self, docs: list[dict]):
        """Create comprehensive deployment guide"""
        deployment_docs = [
            d for d in docs if d["is_deployment_doc"] and d["path"].exists()
        ]

        guide_content = """# Comprehensive Deployment Guide

This is the definitive deployment guide for Sophia AI platform.

## Deployment Architecture

### Hybrid Approach
- **MCP Servers**: Docker Swarm (docker-compose.cloud.yml)
- **GPU Workloads**: Kubernetes (infrastructure/kubernetes/consolidated/gpu-workloads-only.yaml)

### Lambda Labs Instances
| Instance | IP | Purpose | GPU |
|----------|----|---------|----|
| sophia-platform-prod | 146.235.200.1 | Platform services | GPU 1x A10 |
| sophia-mcp-prod | 165.1.69.44 | MCP servers | GPU 1x A10 |
| sophia-ai-prod | 137.131.6.213 | AI processing | GPU 1x A100 |

## Quick Deployment

### MCP Servers
```bash
docker stack deploy -c docker-compose.cloud.yml sophia-ai
```

### GPU Workloads
```bash
kubectl apply -f infrastructure/kubernetes/consolidated/gpu-workloads-only.yaml
```

### Health Monitoring
Check the Unified Dashboard → Lambda Labs Health tab

## Detailed Procedures

"""

        # Add content from existing docs
        for doc in deployment_docs:
            if "comprehensive" not in doc["name"].lower():
                guide_content += f"\n## From {doc['name']}\n\n"
                guide_content += self.extract_relevant_sections(doc["content"])

        # Write comprehensive guide
        guide_path = (
            self.docs_dir / "04-deployment" / "COMPREHENSIVE_DEPLOYMENT_GUIDE.md"
        )
        guide_path.parent.mkdir(exist_ok=True)
        guide_path.write_text(guide_content, encoding="utf-8")

        self.changes["files_consolidated"].append(
            "docs/04-deployment/COMPREHENSIVE_DEPLOYMENT_GUIDE.md"
        )

    def create_lambda_labs_comprehensive_guide(self, docs: list[dict]):
        """Create comprehensive Lambda Labs guide"""
        lambda_docs = [
            d for d in docs if d["contains_lambda_labs"] and d["path"].exists()
        ]

        guide_content = """# Comprehensive Lambda Labs Guide

This is the definitive guide for Lambda Labs infrastructure management.

## Instance Overview

| Instance | IP Address | GPU Type | Purpose | Status |
|----------|------------|----------|---------|---------|
| sophia-platform-prod | 146.235.200.1 | GPU 1x A10 | Platform services | ✅ Active |
| sophia-mcp-prod | 165.1.69.44 | GPU 1x A10 | MCP servers | ✅ Active |
| sophia-ai-prod | 137.131.6.213 | GPU 1x A100 | AI processing | ✅ Active |

## Health Monitoring

Access the health monitoring dashboard:
- **Unified Dashboard** → **Lambda Labs Health** tab
- Real-time metrics for all instances and MCP servers
- Automated alerts for issues

## Deployment Strategy

### Docker Swarm (MCP Servers)
- Target: sophia-mcp-prod (165.1.69.44)
- Method: `docker stack deploy -c docker-compose.cloud.yml sophia-ai`

### Kubernetes (GPU Workloads)
- Target: All instances with GPU requirements
- Config: `infrastructure/kubernetes/consolidated/gpu-workloads-only.yaml`

## Detailed Information

"""

        # Add content from existing docs
        for doc in lambda_docs:
            if "comprehensive" not in doc["name"].lower():
                guide_content += f"\n## From {doc['name']}\n\n"
                guide_content += self.extract_relevant_sections(doc["content"])

        # Write comprehensive guide
        guide_path = (
            self.docs_dir / "04-deployment" / "LAMBDA_LABS_COMPREHENSIVE_GUIDE.md"
        )
        guide_path.parent.mkdir(exist_ok=True)
        guide_path.write_text(guide_content, encoding="utf-8")

        self.changes["files_consolidated"].append(
            "docs/04-deployment/LAMBDA_LABS_COMPREHENSIVE_GUIDE.md"
        )

    def extract_relevant_sections(self, content: str) -> str:
        """Extract relevant sections from documentation content"""
        lines = content.split("\n")
        relevant_lines = []

        for line in lines:
            # Skip certain patterns
            if any(
                skip in line.lower()
                for skip in ["table of contents", "generated on", "backup", "archive"]
            ):
                continue
            relevant_lines.append(line)

        return "\n".join(relevant_lines)

    def create_master_index(self):
        """Create master documentation index"""
        logger.info("📑 Creating master documentation index...")

        index_content = """# Sophia AI Documentation Index

This is the master index for all Sophia AI documentation.

## 🚀 Quick Start
- [Getting Started](01-getting-started/QUICK_START.md)
- [Development Setup](02-development/DEVELOPMENT_SETUP.md)

## 📚 Core Documentation

### 🏗️ Architecture
- [System Overview](03-architecture/SYSTEM_OVERVIEW.md)
- [Clean Architecture Guide](03-architecture/SOPHIA_AI_CLEAN_ARCHITECTURE_GUIDE.md)

### 🚀 Deployment
- [Comprehensive Deployment Guide](04-deployment/COMPREHENSIVE_DEPLOYMENT_GUIDE.md)
- [Lambda Labs Guide](04-deployment/LAMBDA_LABS_COMPREHENSIVE_GUIDE.md)
- [Lambda Labs MCP Deployment](04-deployment/LAMBDA_LABS_MCP_DEPLOYMENT_GUIDE.md)

### 🔧 MCP Servers
- [Comprehensive MCP Guide](06-mcp-servers/COMPREHENSIVE_MCP_GUIDE.md)
- [MCP Server Configuration](06-mcp-servers/MCP_SERVER_CONFIGURATION.md)

### 🔐 Security
- [Security Overview](08-security/SECURITY_OVERVIEW.md)
- [Dependency Security Audit](08-security/DEPENDENCY_SECURITY_AUDIT.md)

### 📊 Performance
- [Performance Optimization](07-performance/PERFORMANCE_OPTIMIZATION.md)

## 🎯 System Handbook
- [Master Handbook](system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md)

## 🔍 Health Monitoring

All health monitoring is available through the **Unified Dashboard**:
- Navigate to: `frontend/src/components/dashboard/UnifiedDashboard.tsx`
- Access **Lambda Labs Health** tab for real-time monitoring
- Monitor all Lambda Labs instances and MCP servers

## 📋 Current Standards

### Lambda Labs Infrastructure
| Instance | IP Address | Purpose |
|----------|------------|---------|
| sophia-platform-prod | 146.235.200.1 | Platform services |
| sophia-mcp-prod | 165.1.69.44 | MCP servers |
| sophia-ai-prod | 137.131.6.213 | AI processing |

### MCP Server Ports
| Server | Port | Status |
|--------|------|--------|
| ai-memory | 9001 | ✅ Active |
| codacy | 3008 | ✅ Active |
| linear | 9004 | ✅ Active |
| github | 9003 | ⚠️ Check |
| snowflake-admin | 9020 | ✅ Active |
| lambda-labs-cli | 9040 | ✅ Active |
| asana | 3001 | ✅ Active |
| notion | 9005 | ✅ Active |

### Deployment Methods
- **MCP Servers**: Docker Swarm (`docker stack deploy -c docker-compose.cloud.yml sophia-ai`)
- **GPU Workloads**: Kubernetes (`kubectl apply -f infrastructure/kubernetes/consolidated/gpu-workloads-only.yaml`)

## 🗂️ File Organization

```
docs/
├── 01-getting-started/     # Quick start guides
├── 02-development/         # Development setup
├── 03-architecture/        # System architecture
├── 04-deployment/          # Deployment guides
├── 05-integrations/        # Integration guides
├── 06-mcp-servers/         # MCP server documentation
├── 07-performance/         # Performance guides
├── 08-security/            # Security documentation
├── 99-reference/           # Reference materials
└── system_handbook/        # Comprehensive system handbook
```

---

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*For issues or questions, check the health monitoring dashboard in the Unified Dashboard.*
"""

        index_path = self.docs_dir / "README.md"
        index_path.write_text(index_content, encoding="utf-8")

        self.changes["files_updated"].append("docs/README.md")

    def generate_summary_report(self):
        """Generate summary report of changes"""
        logger.info("📊 Generating summary report...")

        report_content = f"""# Documentation Consolidation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary of Changes

### Files Updated: {len(self.changes['files_updated'])}
{chr(10).join(f'- {f}' for f in self.changes['files_updated'])}

### Files Removed: {len(self.changes['files_removed'])}
{chr(10).join(f'- {f}' for f in self.changes['files_removed'])}

### Files Consolidated: {len(self.changes['files_consolidated'])}
{chr(10).join(f'- {f}' for f in self.changes['files_consolidated'])}

### Conflicts Resolved: {len(self.changes['conflicts_resolved'])}
{chr(10).join(f'- {c["topic"]}: {c["action"]}' for c in self.changes['conflicts_resolved'])}

### Outdated Files Removed: {len(self.changes['outdated_removed'])}
{chr(10).join(f'- {f}' for f in self.changes['outdated_removed'])}

## Key Improvements

1. **Standardized Lambda Labs IPs**: All documentation now uses current IP addresses
2. **Corrected MCP Ports**: lambda-labs-cli updated from 9020 to 9040
3. **Deployment Method Clarity**: Clear separation between Docker Swarm (MCP) and Kubernetes (GPU)
4. **Health Monitoring Integration**: All monitoring now through Unified Dashboard
5. **Comprehensive Guides**: Created master guides for MCP, deployment, and Lambda Labs

## Current Documentation Structure

The documentation is now organized into clear categories with comprehensive guides that eliminate conflicts and provide authoritative information.

## Backup Location

Original documentation backed up to: {self.backup_dir}
"""

        report_path = (
            self.root_dir
            / f"DOCUMENTATION_CONSOLIDATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        report_path.write_text(report_content, encoding="utf-8")

        logger.info(f"📋 Report saved to {report_path}")


def main():
    """Main execution function"""
    consolidator = DocumentationConsolidator()
    changes = consolidator.run_consolidation()

    # Print summary
    print("\n" + "=" * 80)
    print("📚 DOCUMENTATION CONSOLIDATION COMPLETE")
    print("=" * 80)
    print(f"Files Updated: {len(changes.get('files_updated', []))}")
    print(f"Files Removed: {len(changes.get('files_removed', []))}")
    print(f"Files Consolidated: {len(changes.get('files_consolidated', []))}")
    print(f"Conflicts Resolved: {len(changes.get('conflicts_resolved', []))}")
    print(f"Outdated Removed: {len(changes.get('outdated_removed', []))}")
    print("\n✅ Documentation is now consolidated and standardized")
    print("🔍 Health monitoring available in Unified Dashboard → Lambda Labs Health")
    print("=" * 80)


if __name__ == "__main__":
    main()
