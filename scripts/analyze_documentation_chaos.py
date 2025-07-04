#!/usr/bin/env python3
"""
Analyze documentation chaos and categorize all docs
"""

import os
import re
from collections import defaultdict
from datetime import datetime


def categorize_doc(filename):
    """Categorize document based on filename patterns"""
    filename_lower = filename.lower()

    # Core documents
    if filename == "00_SOPHIA_AI_SYSTEM_HANDBOOK.md":
        return "CORE", "System Handbook - Single source of truth"
    if filename == "API_DOCUMENTATION.md":
        return "CORE", "API specifications"
    if filename == "DEPLOYMENT_CHECKLIST.md":
        return "CORE", "Deployment procedures"
    if filename == "APPLICATION_STRUCTURE.md":
        return "CORE", "Current app structure"

    # Plans (likely obsolete)
    if "_PLAN" in filename or "PLAN_" in filename:
        return "PLAN", "Planning document - likely superseded"

    # Status reports
    if "_STATUS" in filename or "STATUS_" in filename:
        return "STATUS", "Status report - historical"

    # Completion reports
    if "_COMPLETE" in filename or "COMPLETION" in filename:
        return "COMPLETE", "Completion report - historical"

    # Implementation docs
    if "_IMPLEMENTATION" in filename:
        return "IMPLEMENTATION", "Implementation details - check if current"

    # Phase-specific docs
    if re.search(r"PHASE_\d", filename):
        return "PHASE", "Phase-specific document - likely historical"

    # Week-specific docs
    if re.search(r"WEEK_\d", filename):
        return "WEEK", "Week-specific action plan - likely obsolete"

    # Strategy docs
    if "_STRATEGY" in filename:
        return "STRATEGY", "Strategy document - check relevance"

    # Technical docs
    if any(
        tech in filename_lower
        for tech in ["docker", "langchain", "mcp", "llm", "unified"]
    ):
        return "TECHNICAL", "Technical documentation - may be current"

    # Research/prompts
    if "_PROMPT" in filename or "_RESEARCH" in filename:
        return "RESEARCH", "Research or prompt document"

    # Other
    return "OTHER", "Uncategorized document"


def analyze_docs():
    """Analyze all documentation files"""
    docs_dir = "docs"
    categories = defaultdict(list)

    print("📚 Analyzing Documentation Structure...\n")

    # Walk through docs directory
    total_docs = 0
    for root, dirs, files in os.walk(docs_dir):
        # Skip archive directories
        if "archive" in root:
            continue

        for file in files:
            if file.endswith(".md") or file.endswith(".json"):
                total_docs += 1
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                category, description = categorize_doc(file)

                # Get file size
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path) / 1024  # KB
                except (FileNotFoundError, OSError):
                    size = 0  # File doesn't exist or can't be accessed

                categories[category].append(
                    {"path": rel_path, "size": size, "description": description}
                )

    # Print analysis
    print(f"📊 Total Documents: {total_docs}\n")

    # Print by category
    for category, docs in sorted(categories.items()):
        print(f"\n{'='*60}")
        print(f"📁 {category} ({len(docs)} documents)")
        print(f"{'='*60}")

        # Sort by size descending
        docs.sort(key=lambda x: x["size"], reverse=True)

        for doc in docs:
            print(f"  📄 {doc['path']:<50} {doc['size']:>6.1f} KB")
            print(f"     {doc['description']}")

    # Recommendations
    print(f"\n\n{'='*60}")
    print("🎯 RECOMMENDATIONS")
    print(f"{'='*60}\n")

    print("1. KEEP (Core Documents):")
    for doc in categories.get("CORE", []):
        print(f"   ✅ {doc['path']}")

    print("\n2. ARCHIVE (Historical Documents):")
    archive_categories = [
        "PLAN",
        "STATUS",
        "COMPLETE",
        "PHASE",
        "WEEK",
        "IMPLEMENTATION",
    ]
    archive_count = sum(len(categories.get(cat, [])) for cat in archive_categories)
    print(f"   📦 {archive_count} documents should be moved to archive/")

    print("\n3. REVIEW (Need Manual Review):")
    review_categories = ["TECHNICAL", "STRATEGY", "RESEARCH", "OTHER"]
    review_count = sum(len(categories.get(cat, [])) for cat in review_categories)
    print(f"   🔍 {review_count} documents need manual review")

    # Generate archive script
    print("\n4. ARCHIVE SCRIPT:")
    print("   📝 Run: python scripts/archive_obsolete_docs.py")

    # Create archive script
    create_archive_script(categories)


def create_archive_script(categories):
    """Create script to archive obsolete docs"""
    script_content = '''#!/usr/bin/env python3
"""
Archive obsolete documentation files
Generated: {timestamp}
"""

import os
import shutil
from datetime import datetime

# Files to archive
ARCHIVE_FILES = {{
{files}
}}

def archive_docs():
    """Move obsolete docs to archive"""
    archive_dir = f"docs/archive/cleanup_{{datetime.now().strftime('%Y%m%d')}}"

    # Create archive directories
    os.makedirs(f"{{archive_dir}}/plans", exist_ok=True)
    os.makedirs(f"{{archive_dir}}/status", exist_ok=True)
    os.makedirs(f"{{archive_dir}}/completed", exist_ok=True)
    os.makedirs(f"{{archive_dir}}/phases", exist_ok=True)
    os.makedirs(f"{{archive_dir}}/other", exist_ok=True)

    archived_count = 0
    for src, category in ARCHIVE_FILES.items():
        if os.path.exists(src):
            # Determine destination
            if category == "PLAN":
                dst_dir = f"{{archive_dir}}/plans"
            elif category == "STATUS":
                dst_dir = f"{{archive_dir}}/status"
            elif category == "COMPLETE":
                dst_dir = f"{{archive_dir}}/completed"
            elif category in ["PHASE", "WEEK"]:
                dst_dir = f"{{archive_dir}}/phases"
            else:
                dst_dir = f"{{archive_dir}}/other"

            dst = os.path.join(dst_dir, os.path.basename(src))

            try:
                shutil.move(src, dst)
                print(f"✅ Archived: {{src}} → {{dst}}")
                archived_count += 1
            except Exception as e:
                print(f"❌ Error archiving {{src}}: {{e}}")

    # Create index
    with open(f"{{archive_dir}}/INDEX.md", "w") as f:
        f.write(f"# Documentation Archive Index\\n")
        f.write(f"Date: {{datetime.now().strftime('%Y-%m-%d')}}\\n\\n")
        f.write(f"## Summary\\n")
        f.write(f"- Total files archived: {{archived_count}}\\n")
        f.write(f"- Archive location: {{archive_dir}}\\n\\n")
        f.write(f"## Files\\n")
        for src, category in sorted(ARCHIVE_FILES.items()):
            f.write(f"- {{src}} ({{category}})\\n")

    print(f"\\n📊 Archived {{archived_count}} files")
    print(f"📝 Index created: {{archive_dir}}/INDEX.md")

if __name__ == "__main__":
    archive_docs()
'''

    # Build file list
    archive_categories = [
        "PLAN",
        "STATUS",
        "COMPLETE",
        "PHASE",
        "WEEK",
        "IMPLEMENTATION",
    ]
    files_to_archive = []

    for cat in archive_categories:
        for doc in categories.get(cat, []):
            files_to_archive.append(f'    "docs/{doc["path"]}": "{cat}",')

    # Remove trailing comma
    if files_to_archive:
        files_to_archive[-1] = files_to_archive[-1].rstrip(",")

    # Write script
    with open("scripts/archive_obsolete_docs.py", "w") as f:
        f.write(
            script_content.format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                files="\n".join(files_to_archive),
            )
        )

    os.chmod("scripts/archive_obsolete_docs.py", 0o755)


if __name__ == "__main__":
    analyze_docs()
