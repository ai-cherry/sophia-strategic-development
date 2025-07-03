#!/usr/bin/env python3
"""
Test Phase 2 Foundation - Verify code modification through chat
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService
from backend.services.unified_chat_service import ChatContext


async def test_code_modification():
    """Test code modification through chat"""
    print("🧪 Testing Phase 2 Foundation: Code Modification Through Chat\n")
    
    # Initialize service
    chat_service = EnhancedUnifiedChatService()
    
    # Test cases
    test_cases = [
        {
            "message": "Add a docstring to the hello_world function in scripts/test_hello.py",
            "expected_intent": "CODE_MODIFICATION"
        },
        {
            "message": "Create a new file backend/utils/test_util.py with a simple logger setup",
            "expected_intent": "CODE_GENERATION"
        },
        {
            "message": "What did we change in the code yesterday?",
            "expected_intent": "MEMORY"
        },
        {
            "message": "Deploy the frontend to production",
            "expected_intent": "INFRASTRUCTURE"
        }
    ]
    
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['message']}")
        print("-" * 60)
        
        try:
            # Process message
            response = await chat_service.process_message(
                message=test["message"],
                user_id="test_user",
                context=ChatContext.BLENDED_INTELLIGENCE
            )
            
            print(f"✅ Response: {response.response[:200]}...")
            
            if response.metadata:
                print(f"📊 Metadata:")
                print(f"   - Type: {response.metadata.get('type', 'unknown')}")
                print(f"   - Approval Required: {response.metadata.get('approval_required', False)}")
                
                if response.metadata.get('approval_id'):
                    print(f"   - Approval ID: {response.metadata['approval_id']}")
                    
                if response.metadata.get('diff'):
                    print(f"   - Diff Preview:")
                    print("   " + "\n   ".join(response.metadata['diff'].split('\n')[:5]))
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            
    print("\n" + "=" * 60)
    print("✅ Phase 2 Foundation Test Complete!")
    

async def test_intent_classification():
    """Test intent classification"""
    print("\n🧪 Testing Intent Classification\n")
    
    from backend.services.sophia_intent_engine import SophiaIntentEngine
    
    intent_engine = SophiaIntentEngine()
    
    test_messages = [
        "Update the login function to add rate limiting",
        "Create a new React component for the dashboard",
        "Show me what we did last week",
        "Deploy to staging environment",
        "How are our sales doing?",
        "Help me understand this code"
    ]
    
    for message in test_messages:
        category, details = await intent_engine.classify_intent(
            message,
            ChatContext.BLENDED_INTELLIGENCE
        )
        print(f"Message: '{message}'")
        print(f"Intent: {category.value}")
        print(f"Details: {details}\n")
        

async def main():
    """Run all tests"""
    # First create a test file
    test_file = Path("scripts/test_hello.py")
    test_file.write_text("""
def hello_world():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
""")
    
    try:
        await test_intent_classification()
        await test_code_modification()
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print(f"\n🧹 Cleaned up test file: {test_file}")
            

if __name__ == "__main__":
    asyncio.run(main()) 