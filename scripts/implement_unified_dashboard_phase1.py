#!/usr/bin/env python3
"""
Implement Unified Dashboard Phase 1
===================================

This script helps implement the Phase 1 changes for the unified dashboard remediation.
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_files_exist():
    """Check if all required files have been created"""
    required_files = [
        "backend/services/unified_service_registry.py",
        "backend/api/enhanced_unified_chat_routes_integration.py",
        "backend/api/dashboard_data_routes.py",
        "frontend/src/components/shared/EnhancedUnifiedChatFixed.tsx",
        "docs/UNIFIED_DASHBOARD_REMEDIATION_PLAN.md",
        "docs/UNIFIED_DASHBOARD_IMPLEMENTATION_STATUS.md",
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✅ Found: {file_path}")
        else:
            logger.error(f"❌ Missing: {file_path}")
            all_exist = False

    return all_exist


def update_fastapi_app():
    """Update the FastAPI app to include new routers"""
    app_file = "backend/app/app.py"

    if not os.path.exists(app_file):
        logger.warning(f"App file not found at {app_file}")
        return False

    logger.info(f"📝 Please add the following imports to {app_file}:")
    print(
        """
from backend.api import enhanced_unified_chat_routes_integration
from backend.api import dashboard_data_routes
    """
    )

    logger.info("📝 And add these routers:")
    print(
        """
app.include_router(enhanced_unified_chat_routes_integration.router)
app.include_router(dashboard_data_routes.router)
    """
    )

    return True


def update_frontend_component():
    """Instructions for updating the frontend component"""
    dashboard_file = "frontend/src/components/dashboard/UnifiedDashboard.tsx"

    logger.info(f"📝 Please update {dashboard_file}:")
    print(
        """
1. Add import:
   import EnhancedUnifiedChatFixed from '../shared/EnhancedUnifiedChatFixed';

2. In the TabsContent for unified_chat, replace:
   <EnhancedUnifiedChat initialContext={activeTab} />

   With:
   <EnhancedUnifiedChatFixed initialContext={activeTab} />
    """
    )

    return True


def check_conflicting_routes():
    """Check for conflicting route files"""
    conflicting_files = [
        "backend/api/unified_chat_routes.py",
        "backend/api/unified_chat_routes_v2.py",
    ]

    logger.info("\n🔍 Checking for conflicting route files...")
    for file_path in conflicting_files:
        if os.path.exists(file_path):
            logger.warning(f"⚠️  Found conflicting file: {file_path}")
            logger.info("   Consider removing or renaming this file to avoid conflicts")

    return True


def generate_test_commands():
    """Generate commands for testing the implementation"""
    logger.info("\n🧪 Test Commands:")
    print(
        """
# Start the backend server
cd backend && uvicorn app.app:app --reload --port 8000

# In another terminal, start the frontend
cd frontend && npm run dev

# Test endpoints with curl
curl http://localhost:8000/api/v1/unified/dashboard/summary
curl http://localhost:8000/api/v1/llm/stats
curl http://localhost:8000/api/v1/cache/stats

# Test WebSocket with wscat
npm install -g wscat
wscat -c ws://localhost:8000/api/v1/chat/ws/test_user
    """
    )

    return True


def main():
    """Main implementation helper"""
    logger.info("🚀 Unified Dashboard Phase 1 Implementation Helper")
    logger.info("=" * 50)

    # Check files
    logger.info("\n📁 Checking required files...")
    if not check_files_exist():
        logger.error(
            "\n❌ Some required files are missing. Please ensure all files are created."
        )
        sys.exit(1)

    # Update instructions
    logger.info("\n📝 Implementation Steps:")

    # FastAPI updates
    update_fastapi_app()

    # Frontend updates
    update_frontend_component()

    # Check conflicts
    check_conflicting_routes()

    # Test commands
    generate_test_commands()

    logger.info("\n✅ Phase 1 implementation guide complete!")
    logger.info("\n📊 Next Steps:")
    print(
        """
1. Apply the code changes mentioned above
2. Test the endpoints and WebSocket connections
3. Deploy to your environments
4. Monitor logs for any issues
5. Proceed to Phase 2 (Service Integration)
    """
    )


if __name__ == "__main__":
    main()
