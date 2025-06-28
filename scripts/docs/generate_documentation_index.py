#!/usr/bin/env python3
"""
Automated Documentation Index Generator for Sophia AI

This script scans the docs directory and automatically generates the
SOPHIA_AI_DOCUMENTATION_MASTER_INDEX.md file with proper categorization,
priority ordering, and links.

Usage:
    python scripts/docs/generate_documentation_index.py
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class DocumentInfo:
    """Information about a documentation file"""
    path: str
    title: str
    category: str
    priority: int
    description: str
    file_size: int
    last_modified: datetime
    tags: List[str] = field(default_factory=list)

class DocumentationIndexGenerator:
    """Generates and maintains the master documentation index"""
    
    def __init__(self, docs_root: str = "docs", output_file: str = "SOPHIA_AI_DOCUMENTATION_MASTER_INDEX.md"):
        self.docs_root = Path(docs_root)
        self.output_file = Path(output_file)
        self.documents: List[DocumentInfo] = []
        
        # Category definitions with priorities
        self.categories = {
            "01-getting-started": {
                "name": "🚀 Getting Started",
                "priority": 1,
                "description": "Essential documents for new team members and quick setup"
            },
            "02-development": {
                "name": "💻 Development",
                "priority": 2,
                "description": "Development guides, coding standards, and workflows"
            },
            "03-architecture": {
                "name": "🏗️ Architecture",
                "priority": 3,
                "description": "System architecture, design patterns, and technical decisions"
            },
            "04-deployment": {
                "name": "🚀 Deployment",
                "priority": 4,
                "description": "Deployment guides, infrastructure, and production setup"
            },
            "05-integrations": {
                "name": "🔗 Integrations",
                "priority": 5,
                "description": "Third-party integrations and API documentation"
            },
            "06-mcp-servers": {
                "name": "🤖 MCP Servers",
                "priority": 6,
                "description": "Model Context Protocol servers and orchestration"
            },
            "07-performance": {
                "name": "⚡ Performance",
                "priority": 7,
                "description": "Performance optimization and monitoring"
            },
            "08-security": {
                "name": "🔒 Security",
                "priority": 8,
                "description": "Security guidelines, authentication, and best practices"
            },
            "implementation": {
                "name": "📋 Implementation Guides",
                "priority": 9,
                "description": "Step-by-step implementation and setup guides"
            },
            "reference": {
                "name": "📚 Reference",
                "priority": 10,
                "description": "API references, specifications, and technical documentation"
            },
            "root": {
                "name": "📄 Core Documentation",
                "priority": 0,
                "description": "Main documentation files in the root directory"
            }
        }
        
        # High-priority documents (always featured at the top)
        self.featured_documents = [
            "README.md",
            "SOPHIA_AI_CLEAN_ARCHITECTURE_GUIDE.md",
            "ARCHITECTURE_MASTER_GUIDE.md",
            "DEPLOYMENT_MASTER_GUIDE.md",
            "INTEGRATION_MASTER_GUIDE.md"
        ]

    def scan_documentation(self) -> None:
        """Scan the docs directory and collect document information"""
        print(f"📁 Scanning documentation in {self.docs_root}...")
        
        for root, dirs, files in os.walk(self.docs_root):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.md') and not file.startswith('.'):
                    file_path = Path(root) / file
                    doc_info = self._extract_document_info(file_path)
                    if doc_info:
                        self.documents.append(doc_info)
        
        print(f"✅ Found {len(self.documents)} documentation files")

    def _extract_document_info(self, file_path: Path) -> Optional[DocumentInfo]:
        """Extract information from a documentation file"""
        try:
            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Determine category from path
            relative_path = file_path.relative_to(self.docs_root)
            category = self._determine_category(relative_path)
            
            # Extract title and description from file content
            title, description, tags = self._parse_markdown_header(file_path)
            
            # Determine priority
            priority = self._calculate_priority(file_path.name, category, file_size)
            
            return DocumentInfo(
                path=str(relative_path),
                title=title,
                category=category,
                priority=priority,
                description=description,
                file_size=file_size,
                last_modified=last_modified,
                tags=tags
            )
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
            return None

    def _determine_category(self, relative_path: Path) -> str:
        """Determine the category of a document based on its path"""
        path_parts = relative_path.parts
        
        if len(path_parts) == 1:  # Root level
            return "root"
        
        first_dir = path_parts[0]
        
        # Check for numbered directories (01-getting-started, etc.)
        for category_key in self.categories:
            if first_dir == category_key or first_dir.startswith(category_key.split('-')[0]):
                return category_key
        
        # Special case mappings
        special_mappings = {
            "ai-coding": "02-development",
            "sample_queries": "99-reference",
            "deployment": "04-deployment",
            "integrations": "05-integrations",
            "implementation": "implementation",
            "archive": "99-reference"
        }
        
        return special_mappings.get(first_dir, "reference")

    def _parse_markdown_header(self, file_path: Path) -> Tuple[str, str, List[str]]:
        """Parse markdown file to extract title, description, and tags"""
        title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
        description = ""
        tags = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first h1 heading
            h1_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            
            # Extract description from content after title
            lines = content.split('\n')
            description_lines = []
            found_title = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('# ') and not found_title:
                    found_title = True
                    continue
                elif found_title and line and not line.startswith('#'):
                    if line.startswith('## '):
                        break
                    description_lines.append(line)
                    if len(description_lines) >= 2:  # Limit to first 2 lines
                        break
            
            description = ' '.join(description_lines)[:200] + "..." if description_lines else ""
            
            # Extract tags from content
            tags_match = re.search(r'(?:Tags?|Keywords?):\s*(.+)', content, re.IGNORECASE)
            if tags_match:
                tags = [tag.strip() for tag in tags_match.group(1).split(',')]
        
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")
        
        return title, description, tags

    def _calculate_priority(self, filename: str, category: str, file_size: int) -> int:
        """Calculate priority score for a document"""
        priority = 50  # Base priority
        
        # Featured documents get highest priority
        if filename in self.featured_documents:
            priority = 1
        
        # Adjust by category
        category_info = self.categories.get(category, {})
        category_priority = category_info.get("priority", 10)
        priority += category_priority * 10
        
        # Adjust by file size (larger files often more comprehensive)
        if file_size > 50000:  # > 50KB
            priority -= 5
        elif file_size > 10000:  # > 10KB
            priority -= 2
        
        # Special filename patterns
        if "master" in filename.lower() or "guide" in filename.lower():
            priority -= 10
        
        if "quick" in filename.lower() or "reference" in filename.lower():
            priority -= 5
        
        if "implementation" in filename.lower():
            priority -= 3
        
        return max(1, priority)  # Ensure priority is at least 1

    def generate_index(self) -> str:
        """Generate the master documentation index"""
        print("📝 Generating documentation index...")
        
        # Sort documents by category and priority
        self.documents.sort(key=lambda doc: (
            self.categories.get(doc.category, {}).get("priority", 999),
            doc.priority,
            doc.title.lower()
        ))
        
        # Generate the index content
        index_content = self._generate_header()
        index_content += self._generate_table_of_contents()
        index_content += self._generate_featured_section()
        index_content += self._generate_category_sections()
        index_content += self._generate_statistics()
        index_content += self._generate_footer()
        
        return index_content

    def _generate_header(self) -> str:
        """Generate the header section"""
        return f"""# Sophia AI Documentation Master Index

**Last Updated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  
**Total Documents**: {len(self.documents)}  
**Auto-Generated**: This index is automatically generated by `scripts/docs/generate_documentation_index.py`

## Overview

This is the comprehensive master index for all Sophia AI documentation. Documents are organized by category and prioritized by importance and relevance.

"""

    def _generate_table_of_contents(self) -> str:
        """Generate table of contents"""
        toc = "## Table of Contents\n\n"
        
        # Get categories that have documents
        categories_with_docs = set(doc.category for doc in self.documents)
        
        for category_key, category_info in sorted(self.categories.items(), key=lambda x: x[1]["priority"]):
            if category_key in categories_with_docs:
                toc += f"- [{category_info['name']}](#{self._anchor_link(category_info['name'])})\n"
        
        toc += "- [📊 Documentation Statistics](#documentation-statistics)\n\n"
        return toc

    def _generate_featured_section(self) -> str:
        """Generate featured documents section"""
        featured = "## ⭐ Featured Documentation\n\n"
        featured += "Essential documents for getting started and understanding the system architecture.\n\n"
        
        featured_docs = [doc for doc in self.documents if doc.path.split('/')[-1] in self.featured_documents]
        featured_docs.sort(key=lambda x: self.featured_documents.index(x.path.split('/')[-1]) if x.path.split('/')[-1] in self.featured_documents else 999)
        
        for doc in featured_docs[:5]:  # Limit to top 5
            featured += f"### 📌 [{doc.title}]({doc.path})\n"
            featured += f"{doc.description}\n\n"
        
        return featured

    def _generate_category_sections(self) -> str:
        """Generate sections for each category"""
        content = ""
        
        # Group documents by category
        docs_by_category = {}
        for doc in self.documents:
            if doc.category not in docs_by_category:
                docs_by_category[doc.category] = []
            docs_by_category[doc.category].append(doc)
        
        # Generate section for each category
        for category_key, category_info in sorted(self.categories.items(), key=lambda x: x[1]["priority"]):
            if category_key in docs_by_category:
                content += f"## {category_info['name']}\n\n"
                content += f"{category_info['description']}\n\n"
                
                # Sort documents within category by priority
                category_docs = sorted(docs_by_category[category_key], key=lambda x: (x.priority, x.title.lower()))
                
                for doc in category_docs:
                    content += f"### [{doc.title}]({doc.path})\n"
                    if doc.description:
                        content += f"{doc.description}\n"
                    
                    # Add metadata
                    metadata = []
                    if doc.file_size > 10000:
                        metadata.append(f"📄 {doc.file_size // 1000}KB")
                    if doc.tags:
                        metadata.append(f"🏷️ {', '.join(doc.tags[:3])}")
                    
                    if metadata:
                        content += f"*{' | '.join(metadata)}*\n"
                    
                    content += "\n"
                
                content += "---\n\n"
        
        return content

    def _generate_statistics(self) -> str:
        """Generate documentation statistics"""
        stats = "## 📊 Documentation Statistics\n\n"
        
        # Documents by category
        category_counts = {}
        total_size = 0
        
        for doc in self.documents:
            category_counts[doc.category] = category_counts.get(doc.category, 0) + 1
            total_size += doc.file_size
        
        stats += "### Documents by Category\n\n"
        for category_key, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            category_name = self.categories.get(category_key, {}).get("name", category_key)
            stats += f"- {category_name}: {count} documents\n"
        
        stats += f"\n### Total Documentation Size\n\n"
        stats += f"**{total_size // 1000} KB** across {len(self.documents)} files\n\n"
        
        # Recent updates
        recent_docs = sorted(self.documents, key=lambda x: x.last_modified, reverse=True)[:5]
        stats += "### Recently Updated\n\n"
        for doc in recent_docs:
            date_str = doc.last_modified.strftime('%Y-%m-%d')
            stats += f"- [{doc.title}]({doc.path}) - {date_str}\n"
        
        stats += "\n"
        return stats

    def _generate_footer(self) -> str:
        """Generate footer section"""
        return f"""## 🔄 Maintenance

This documentation index is automatically maintained by the Sophia AI team. 

### Updating the Index

To regenerate this index after adding or modifying documentation:

```bash
cd ~/sophia-main
python scripts/docs/generate_documentation_index.py
```

### Contributing to Documentation

1. Place new documents in the appropriate category directory (`docs/XX-category/`)
2. Follow the markdown formatting standards
3. Include a clear title and description
4. Run the index generator to update this file
5. Commit both your new documentation and the updated index

---

**Generated by**: Sophia AI Documentation System  
**Script**: `scripts/docs/generate_documentation_index.py`  
**Version**: 1.0  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _anchor_link(self, text: str) -> str:
        """Convert text to GitHub markdown anchor link format"""
        return text.lower().replace(' ', '-').replace('🚀', '').replace('💻', '').replace('🏗️', '').replace('🔗', '').replace('🤖', '').replace('⚡', '').replace('🔒', '').replace('📋', '').replace('📚', '').replace('📄', '').strip('-')

    def write_index(self, content: str) -> None:
        """Write the generated index to file"""
        print(f"💾 Writing index to {self.output_file}...")
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Documentation index generated successfully!")
        print(f"📊 {len(self.documents)} documents indexed")

def main():
    """Main function to generate the documentation index"""
    print("🚀 Sophia AI Documentation Index Generator")
    print("=" * 50)
    
    generator = DocumentationIndexGenerator()
    
    try:
        # Scan documentation
        generator.scan_documentation()
        
        # Generate index
        index_content = generator.generate_index()
        
        # Write to file
        generator.write_index(index_content)
        
        print("\n🎉 Documentation index generation completed!")
        
    except Exception as e:
        print(f"❌ Error generating documentation index: {e}")
        raise

if __name__ == "__main__":
    main() 