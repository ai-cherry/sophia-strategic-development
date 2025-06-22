"""
Script to set up Sentry and create a test error
This will help you get your first Sentry Issue ID
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.sentry_setup import init_sentry, create_test_error, capture_message
import sentry_sdk

def get_sentry_dsn():
    """Get Sentry DSN from user or environment."""
    dsn = os.getenv("SENTRY_DSN")
    
    if not dsn:
        print("\n🔧 Sentry Setup Helper")
        print("=" * 50)
        print("\nYou need a Sentry DSN to continue.")
        print("\nTo get your DSN:")
        print("1. Go to: https://sentry.io/organizations/pay-ready/")
        print("2. Select your project (or create one)")
        print("3. Go to Settings → Client Keys (DSN)")
        print("4. Copy the DSN value")
        print("\nIt looks like: https://xxxxx@o123456.ingest.sentry.io/123456")
        
        dsn = input("\nPaste your Sentry DSN here: ").strip()
        
        if dsn:
            # Save to environment for this session
            os.environ["SENTRY_DSN"] = dsn
            print(f"\n✅ DSN set for this session")
            
            # Also save to .env file for future use
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            with open(env_file, "a") as f:
                f.write(f"\n# Sentry Configuration\n")
                f.write(f"SENTRY_DSN={dsn}\n")
                f.write(f"SENTRY_ORGANIZATION_SLUG=pay-ready\n")
                f.write(f"SENTRY_PROJECT_SLUG=pay-ready\n")
            print(f"✅ Saved to .env file")
    
    return dsn

def create_multiple_test_errors():
    """Create multiple types of test errors."""
    errors_created = []
    
    print("\n🚨 Creating test errors for Sentry...")
    print("=" * 50)
    
    # Error 1: Division by Zero
    try:
        print("\n1. Creating ZeroDivisionError...")
        result = 1 / 0
    except ZeroDivisionError as e:
        sentry_sdk.capture_exception(e)
        errors_created.append("ZeroDivisionError")
        print("   ✅ ZeroDivisionError sent to Sentry")
    
    time.sleep(1)
    
    # Error 2: Type Error
    try:
        print("\n2. Creating TypeError...")
        result = "string" + 123
    except TypeError as e:
        sentry_sdk.capture_exception(e)
        errors_created.append("TypeError")
        print("   ✅ TypeError sent to Sentry")
    
    time.sleep(1)
    
    # Error 3: Custom Error
    try:
        print("\n3. Creating Custom SophiaAIError...")
        class SophiaAIError(Exception):
            pass
        raise SophiaAIError("Test error from Sophia AI setup script")
    except SophiaAIError as e:
        sentry_sdk.capture_exception(e)
        errors_created.append("SophiaAIError")
        print("   ✅ SophiaAIError sent to Sentry")
    
    time.sleep(1)
    
    # Error 4: With context
    print("\n4. Creating error with context...")
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("component", "sophia-ai")
        scope.set_tag("test", "true")
        scope.set_context("test_info", {
            "script": "setup_sentry_and_create_error.py",
            "purpose": "Getting first Issue ID",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        try:
            items = [1, 2, 3]
            result = items[10]  # IndexError
        except IndexError as e:
            sentry_sdk.capture_exception(e)
            errors_created.append("IndexError with context")
            print("   ✅ IndexError with context sent to Sentry")
    
    # Also send a test message
    print("\n5. Sending test message...")
    capture_message("Sophia AI Sentry integration test message", level="info")
    print("   ✅ Test message sent to Sentry")
    
    return errors_created

def main():
    """Main setup function."""
    print("\n🚀 Sophia AI - Sentry Setup Script")
    print("=" * 50)
    
    # Step 1: Get DSN
    dsn = get_sentry_dsn()
    if not dsn:
        print("\n❌ No DSN provided. Exiting.")
        return
    
    # Step 2: Initialize Sentry
    print("\n📡 Initializing Sentry...")
    if init_sentry():
        print("✅ Sentry initialized successfully!")
    else:
        print("❌ Failed to initialize Sentry")
        return
    
    # Step 3: Create test errors
    errors = create_multiple_test_errors()
    
    # Step 4: Show next steps
    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    
    print(f"\n📊 Created {len(errors)} test errors:")
    for error in errors:
        print(f"   - {error}")
    
    print("\n🔍 To find your Issue IDs:")
    print("1. Go to: https://sentry.io/organizations/pay-ready/issues/")
    print("2. You should see your new errors listed")
    print("3. Click on any error")
    print("4. The URL will contain the Issue ID")
    print("   Example: .../issues/1234567890/")
    print("   The Issue ID is: 1234567890")
    
    print("\n📝 Next Steps:")
    print("1. Copy an Issue ID from Sentry")
    print("2. Update scripts/test/test_sentry_agent.py with the Issue ID")
    print("3. Run: python scripts/test/test_sentry_agent.py")
    print("4. Deploy: docker-compose -f docker-compose.sentry.yml up -d")
    
    print("\n💡 Tip: The errors should appear in Sentry within a few seconds.")
    print("If you don't see them, check your DSN and project settings.")
    
    # Also save the DSN info for GitHub Actions
    print("\n🔐 GitHub Actions Secrets needed:")
    print(f"SENTRY_DSN={dsn}")
    print("SENTRY_API_TOKEN=<get from Sentry settings>")
    print("SENTRY_ORGANIZATION_SLUG=pay-ready")
    print("SENTRY_PROJECT_SLUG=pay-ready")

if __name__ == "__main__":
    main()
