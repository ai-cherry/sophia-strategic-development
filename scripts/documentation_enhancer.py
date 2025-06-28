#!/usr/bin/env python3
"""
Documentation Enhancer Script
Enhances remaining documentation for AI coders and maintainers
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentationEnhancer:
    """Enhance documentation for AI-friendly consumption"""

    def __init__(self):
        self.docs_path = Path("docs")
        self.enhanced_files = []
        self.metadata_template = {
            "title": "",
            "description": "",
            "tags": [],
            "last_updated": "",
            "dependencies": [],
            "related_docs": [],
        }

    def extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1) if match else "Untitled"

    def extract_description(self, content: str) -> str:
        """Extract description from first paragraph after title"""
        lines = content.split("\n")
        in_description = False
        description_lines = []

        for line in lines:
            if line.startswith("# ") and not in_description:
                in_description = True
                continue
            elif in_description and line.strip() and not line.startswith("#"):
                description_lines.append(line.strip())
            elif in_description and (
                line.startswith("#") or len(description_lines) > 2
            ):
                break

        return " ".join(description_lines[:2])

    def extract_tags(self, content: str, filepath: Path) -> list[str]:
        """Extract relevant tags from content and filepath"""
        tags = []

        # Tag based on directory
        if "getting-started" in str(filepath):
            tags.append("onboarding")
        elif "architecture" in str(filepath):
            tags.append("architecture")
        elif "integrations" in str(filepath):
            tags.append("integration")
        elif "deployment" in str(filepath):
            tags.append("deployment")
        elif "api" in str(filepath):
            tags.append("api")

        # Tag based on content keywords
        keywords = {
            "docker": ["docker", "container"],
            "kubernetes": ["k8s", "kubernetes", "kubectl"],
            "mcp": ["mcp", "model context protocol"],
            "agent": ["agent", "base_agent"],
            "gong": ["gong", "gong.io"],
            "linear": ["linear"],
            "security": ["security", "authentication", "secret"],
            "database": ["database", "postgres", "redis"],
            "monitoring": ["monitoring", "observability", "metrics"],
        }

        content_lower = content.lower()
        for tag, patterns in keywords.items():
            if any(pattern in content_lower for pattern in patterns):
                tags.append(tag)

        return list(set(tags))

    def add_metadata_header(self, content: str, metadata: dict) -> str:
        """Add metadata header to markdown file"""
        metadata_yaml = f"""---
title: {metadata["title"]}
description: {metadata["description"]}
tags: {", ".join(metadata["tags"])}
last_updated: {metadata["last_updated"]}
dependencies: {", ".join(metadata["dependencies"]) if metadata["dependencies"] else "none"}
related_docs: {", ".join(metadata["related_docs"]) if metadata["related_docs"] else "none"}
---

"""
        # Remove existing metadata if present
        if content.startswith("---"):
            content = re.sub(r"^---.*?---\n\n", "", content, flags=re.DOTALL)

        return metadata_yaml + content

    def add_table_of_contents(self, content: str) -> str:
        """Add table of contents after metadata"""
        headers = re.findall(r"^(#{2,})\s+(.+)$", content, re.MULTILINE)

        if len(headers) < 3:
            return content

        toc = "\n## Table of Contents\n\n"
        for level, title in headers:
            indent = "  " * (len(level) - 2)
            anchor = title.lower().replace(" ", "-").replace("/", "-")
            toc += f"{indent}- [{title}](#{anchor})\n"

        # Insert TOC after first heading
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# ") and i + 1 < len(lines):
                lines.insert(i + 2, toc)
                break

        return "\n".join(lines)

    def enhance_code_blocks(self, content: str) -> str:
        """Enhance code blocks with language hints and examples"""
        # Add language hints to code blocks without them
        content = re.sub(r"```\n", "```python\n", content)

        # Add example indicators
        def add_example_label(match):
            code = match.group(1)
            lang = match.group(0).split("\n")[0].replace("```", "").strip()
            if "example" not in match.group(0).lower():
                return f"```{lang}\n# Example usage:\n{code}\n```"
            return match.group(0)

        content = re.sub(
            r"```(\w+)\n(.*?)\n```", add_example_label, content, flags=re.DOTALL
        )

        return content

    def add_quick_reference(self, content: str) -> str:
        """Add quick reference section for AI coders"""
        # Extract key functions/classes
        functions = re.findall(r"def\s+(\w+)\s*\(", content)
        classes = re.findall(r"class\s+(\w+)\s*[:\(]", content)

        if not functions and not classes:
            return content

        quick_ref = "\n## Quick Reference\n\n"

        if classes:
            quick_ref += "### Classes\n"
            for cls in set(classes):
                quick_ref += f"- `{cls}`\n"
            quick_ref += "\n"

        if functions:
            quick_ref += "### Functions\n"
            for func in set(functions):
                quick_ref += f"- `{func}()`\n"
            quick_ref += "\n"

        # Insert after TOC or after title
        lines = content.split("\n")
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("## Table of Contents"):
                # Find end of TOC
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("##") and "Contents" not in lines[j]:
                        lines.insert(j, quick_ref)
                        inserted = True
                        break
                break

        if not inserted:
            # Insert after first heading
            for i, line in enumerate(lines):
                if line.startswith("# ") and i + 1 < len(lines):
                    lines.insert(i + 2, quick_ref)
                    break

        return "\n".join(lines)

    def enhance_file(self, filepath: Path) -> bool:
        """Enhance a single documentation file"""
        try:
            content = filepath.read_text()
            original_content = content

            # Extract metadata
            metadata = self.metadata_template.copy()
            metadata["title"] = self.extract_title(content)
            metadata["description"] = self.extract_description(content)
            metadata["tags"] = self.extract_tags(content, filepath)
            metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            # Apply enhancements
            content = self.add_metadata_header(content, metadata)
            content = self.add_table_of_contents(content)
            content = self.enhance_code_blocks(content)
            content = self.add_quick_reference(content)

            # Write enhanced content
            if content != original_content:
                filepath.write_text(content)
                self.enhanced_files.append(str(filepath))
                print(f"✓ Enhanced: {filepath}")
                return True
            else:
                print(f"  No changes needed: {filepath}")
                return False

        except Exception as e:
            print(f"✗ Failed to enhance {filepath}: {e}")
            return False

    def create_index_file(self):
        """Create an index file for all documentation"""
        index_content = """# Sophia AI Documentation Index

Welcome to the Sophia AI documentation. This index provides quick access to all documentation organized by category.

## Quick Links

- [Getting Started Guide](getting-started/quickstart.md)
- [Architecture Overview](architecture/overview.md)
- [API Reference](api/reference.md)
- [Deployment Guide](deployment/production-guide.md)

## Documentation Structure

"""

        # Scan docs directory
        categories = {}
        for doc_file in self.docs_path.rglob("*.md"):
            if doc_file.name == "README.md":
                continue

            category = doc_file.parent.name
            if category == "docs":
                category = "general"

            if category not in categories:
                categories[category] = []

            # Read title from file
            try:
                title = self.extract_title(doc_file.read_text())
                relative_path = doc_file.relative_to(self.docs_path)
                categories[category].append((title, str(relative_path)))
            except Exception as e:
                logger.debug(f"Could not process file {doc_file}: {e}")
                pass

        # Build index content
        for category, docs in sorted(categories.items()):
            index_content += f"\n### {category.replace('-', ' ').title()}\n\n"
            for title, path in sorted(docs):
                index_content += f"- [{title}]({path})\n"

        # Add metadata section
        index_content += """
## For AI Coders

All documentation includes:
- Structured metadata (tags, dependencies)
- Table of contents for easy navigation
- Code examples with clear language indicators
- Quick reference sections for classes/functions

Use the tags in each document to find related content quickly.
"""

        # Write index file
        index_path = self.docs_path / "README.md"
        index_path.write_text(index_content)
        print(f"✓ Created documentation index: {index_path}")

    def generate_enhancement_report(self):
        """Generate a report of all enhancements"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "enhanced_files": self.enhanced_files,
            "total_enhanced": len(self.enhanced_files),
        }

        report_path = "documentation_enhancement_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Enhancement report saved to {report_path}")

    def run(self):
        """Execute the enhancement process"""
        print("=== Sophia AI Documentation Enhancement ===\n")

        # Enhance all markdown files in docs directory
        print("Enhancing documentation files...")
        for doc_file in self.docs_path.rglob("*.md"):
            if doc_file.name != "README.md":
                self.enhance_file(doc_file)

        # Create index file
        print("\nCreating documentation index...")
        self.create_index_file()

        # Generate report
        self.generate_enhancement_report()

        # Summary
        print("\n=== Summary ===")
        print(f"Files enhanced: {len(self.enhanced_files)}")
        print("\nDocumentation is now optimized for AI coders!")


def main():
    """Main function"""
    enhancer = DocumentationEnhancer()
    enhancer.run()


if __name__ == "__main__":
    main()
