#!/usr/bin/env python3
"""
🔥 Pulumi Access Token Smoke Test

This script validates that PULUMI_ACCESS_TOKEN is properly accessible
from GitHub Organization Secrets → Pulumi ESC → Backend auto_esc_config.

Usage:
    python scripts/smoke_test_pulumi_token.py
"""

import sys
import os
import subprocess

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_backend_config_access() -> bool:
    """Test backend auto_esc_config access"""
    print("🐍 Testing backend auto_esc_config access...")
    
    try:
        from backend.core.auto_esc_config import get_config_value, get_pulumi_config
        
        # Test Pulumi token access
        token = get_config_value('PULUMI_ACCESS_TOKEN')
        if token:
            print(f"   ✅ Pulumi token retrieved via get_config_value ({len(token)} chars)")
        else:
            print("   ❌ Pulumi token not found via get_config_value")
            return False
            
        # Test Pulumi config
        pulumi_config = get_pulumi_config()
        if pulumi_config and pulumi_config.get('access_token'):
            print(f"   ✅ Pulumi config retrieved successfully")
        else:
            print("   ❌ Pulumi config not accessible")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Backend config error: {e}")
        return False

def test_gong_real_secrets() -> bool:
    """Test that REAL Gong secrets are accessible"""
    print("🎯 Testing REAL Gong secrets access...")
    
    try:
        from backend.core.auto_esc_config import get_gong_config
        
        gong_config = get_gong_config()
        
        # Check required Gong secrets
        required_keys = ['access_key', 'access_key_secret', 'client_access_key', 'client_secret', 'base_url']
        missing_keys = []
        
        for key in required_keys:
            value = gong_config.get(key)
            if not value or value == "placeholder":
                missing_keys.append(key)
            else:
                print(f"   ✅ GONG_{key.upper()}: {len(str(value))} chars")
                
        if missing_keys:
            print(f"   ❌ Missing Gong secrets: {missing_keys}")
            return False
            
        print("   ✅ ALL real Gong secrets accessible - NO PLACEHOLDERS!")
        return True
        
    except Exception as e:
        print(f"   ❌ Gong config error: {e}")
        return False

def main():
    """Main smoke test execution"""
    print("🔥 PULUMI ACCESS TOKEN SMOKE TEST")
    print("=" * 50)
    
    tests = [
        ("Backend Config Access", test_backend_config_access),
        ("REAL Gong Secrets", test_gong_real_secrets)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print()
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print()
    print("=" * 50)
    print(f"🎯 SMOKE TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Pulumi token access working!")
        return 0
    else:
        print("🚨 TESTS FAILED - Check configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 