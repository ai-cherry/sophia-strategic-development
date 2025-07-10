#!/usr/bin/env python3
"""
Wire V4 Orchestrator Script

This script helps integrate the new v4 orchestrator API routes
into the main FastAPI application.

Date: July 9, 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def find_main_app_file():
    """Find the main FastAPI application file"""
    candidates = [
        "backend/app/fastapi_app.py",
        "backend/app/main.py",
        "backend/app/app.py",
        "backend/main.py",
        "api/app/main.py",
    ]

    for candidate in candidates:
        path = project_root / candidate
        if path.exists():
            return path

    return None


def check_if_already_wired(file_path: Path) -> bool:
    """Check if v4 routes are already included"""
    content = file_path.read_text()
    return "orchestrator_v4_routes" in content


def wire_v4_routes(file_path: Path):
    """Add v4 orchestrator routes to the application"""
    content = file_path.read_text()

    # Find where other routers are imported
    import_section_end = content.rfind("from")
    if import_section_end == -1:
        import_section_end = content.rfind("import")

    # Add import after other imports
    import_line = "\nfrom backend.api.orchestrator_v4_routes import router as orchestrator_v4_router"

    # Find where routers are included
    include_section = content.find("app.include_router")
    if include_section == -1:
        print("❌ Could not find router inclusion section")
        return False

    # Find the last include_router call
    last_include = content.rfind("app.include_router")
    next_line = content.find("\n", last_include)

    # Add the new router inclusion
    include_line = "\napp.include_router(orchestrator_v4_router)"

    # Build new content
    new_content = (
        content[
            : import_section_end
            + len(content[import_section_end : content.find("\n", import_section_end)])
        ]
        + import_line
        + content[
            import_section_end
            + len(
                content[import_section_end : content.find("\n", import_section_end)]
            ) : next_line
        ]
        + include_line
        + content[next_line:]
    )

    # Write back
    file_path.write_text(new_content)
    return True


def main():
    """Main execution"""
    print("🔧 V4 Orchestrator Wiring Script")
    print("=" * 50)

    # Find main app file
    app_file = find_main_app_file()
    if not app_file:
        print("❌ Could not find main FastAPI application file")
        print("Please manually add the following to your main app:")
        print("\n```python")
        print(
            "from backend.api.orchestrator_v4_routes import router as orchestrator_v4_router"
        )
        print("app.include_router(orchestrator_v4_router)")
        print("```")
        return

    print(f"✅ Found main app file: {app_file}")

    # Check if already wired
    if check_if_already_wired(app_file):
        print("✅ V4 routes already wired!")
        return

    # Create backup
    backup_path = app_file.with_suffix(".backup")
    backup_path.write_text(app_file.read_text())
    print(f"✅ Created backup: {backup_path}")

    # Wire the routes
    if wire_v4_routes(app_file):
        print("✅ Successfully wired V4 orchestrator routes!")
        print("\nNext steps:")
        print("1. Start the FastAPI application")
        print("2. Test the new endpoints:")
        print("   - GET  /api/v4/orchestrator/health")
        print("   - POST /api/v4/orchestrate")
        print("   - POST /api/v4/orchestrate/stream")
    else:
        print("❌ Failed to wire routes automatically")
        print("Please add manually as shown above")


if __name__ == "__main__":
    main()
