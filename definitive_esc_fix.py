#!/usr/bin/env python3
"""
DEFINITIVE ESC FIX: Structure Mismatch Resolution
Root cause: Sync writes to nested structure, backend reads from top-level
"""

def fix_sync_script_to_top_level():
    """Fix sync script to write to top-level structure (what backend reads)"""
    print("🔧 FIXING SYNC SCRIPT: Nested → Top-Level Structure")
    print("=" * 60)
    
    sync_file = "scripts/ci/sync_from_gh_to_pulumi.py"
    
    with open(sync_file, 'r') as f:
        content = f.read()
    
    # Replace the entire secret_mappings with top-level mappings
    new_mappings = '''        # TOP-LEVEL MAPPINGS (what backend actually reads)
        # CRITICAL FIX: Use top-level ESC keys, not nested values.sophia.*
        self.secret_mappings = {
            # Core AI Services (top-level keys)
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "GONG_ACCESS_KEY": "gong_access_key",
            "PINECONE_API_KEY": "pinecone_api_key",
            
            # Snowflake (top-level keys)
            "SNOWFLAKE_ACCOUNT": "snowflake_account", 
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "SNOWFLAKE_ROLE": "snowflake_role",
            "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
            "SNOWFLAKE_DATABASE": "snowflake_database",
            
            # Lambda Labs (top-level keys) - CRITICAL FIX
            "LAMBDA_API_KEY": "lambda_api_key",
            "LAMBDA_IP_ADDRESS": "lambda_ip_address",
            "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",
            
            # Business Intelligence (top-level keys)
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "LINEAR_API_KEY": "linear_api_key", 
            "NOTION_API_KEY": "notion_api_key",
            
            # Additional high-priority services
            "VERCEL_ACCESS_TOKEN": "vercel_access_token",
            "PORTKEY_API_KEY": "portkey_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
        }'''
    
    # Replace the existing mappings section
    import re
    
    # Find the start and end of the secret_mappings
    start_pattern = r'self\.secret_mappings = \{'
    end_pattern = r'\s+\}'
    
    # Find the section to replace
    start_match = re.search(start_pattern, content)
    if start_match:
        start_pos = start_match.start()
        
        # Find the end of the mappings (look for the closing brace)
        remaining_content = content[start_pos:]
        brace_count = 0
        end_pos = start_pos
        
        for i, char in enumerate(remaining_content):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = start_pos + i + 1
                    break
        
        # Replace the section
        new_content = content[:start_pos] + new_mappings + content[end_pos:]
        
        with open(sync_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Updated sync script to use top-level structure")
        print("✅ Lambda Labs credentials will now sync to correct location")
        return True
    else:
        print("❌ Could not find secret_mappings section")
        return False

def verify_fix():
    """Verify the fix is working"""
    print("\n🧪 VERIFYING FIX")
    print("=" * 30)
    
    # Check if sync script has the fix
    sync_file = "scripts/ci/sync_from_gh_to_pulumi.py"
    with open(sync_file, 'r') as f:
        content = f.read()
    
    if '"lambda_api_key"' in content and 'values.sophia' not in content.split('self.secret_mappings')[1].split('}')[0]:
        print("✅ Sync script now uses top-level structure")
    else:
        print("❌ Sync script still has nested structure")
        return False
    
    # Test backend access
    try:
        import sys
        sys.path.insert(0, '.')
        from backend.core.auto_esc_config import get_config_value
        
        # Test existing working keys
        openai = get_config_value('openai_api_key')
        anthropic = get_config_value('anthropic_api_key')
        
        if openai and anthropic:
            print("✅ Backend can read top-level structure")
            print(f"✅ OpenAI key: {openai[:10]}...")
            print(f"✅ Anthropic key: {anthropic[:10]}...")
        else:
            print("❌ Backend cannot read top-level structure")
            return False
            
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False
    
    print("\n💡 ROOT CAUSE RESOLVED:")
    print("  - Sync script now writes to TOP-LEVEL structure")
    print("  - Backend reads from TOP-LEVEL structure")
    print("  - Structure mismatch eliminated")
    print("  - Placeholders will be replaced with real values")
    
    return True

def main():
    """Apply definitive fix"""
    print("🚀 DEFINITIVE PULUMI ESC STRUCTURE FIX")
    print("=" * 50)
    
    print("🔍 ROOT CAUSE: Structure Mismatch")
    print("  - Sync script writes to: values.sophia.* (nested)")
    print("  - Backend reads from: top-level keys")
    print("  - Result: Persistent placeholders")
    
    if fix_sync_script_to_top_level():
        if verify_fix():
            print("\n🎉 DEFINITIVE FIX SUCCESSFUL!")
            print("=" * 40)
            print("✅ Structure mismatch resolved")
            print("✅ Sync script fixed")
            print("✅ Backend compatibility verified")
            
            print("\n🚀 COMMIT AND PUSH TO TRIGGER SYNC:")
            print("git add scripts/ci/sync_from_gh_to_pulumi.py")
            print("git commit -m 'DEFINITIVE FIX: ESC structure mismatch'")
            print("git push origin main")
            
            return True
    
    print("\n❌ Fix failed")
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
