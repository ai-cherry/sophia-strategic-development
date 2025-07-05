#!/usr/bin/env python3
"""
GitHub Deployment Monitor for Sophia AI

Simple monitoring script to track deployment progress
"""

import time
import subprocess
from datetime import datetime


def check_commit_age():
    """Check how long ago the deployment commit was made"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True,
            check=True
        )
        
        timestamp = int(result.stdout.strip())
        commit_time = datetime.fromtimestamp(timestamp)
        age_minutes = (datetime.now() - commit_time).total_seconds() / 60
        
        return commit_time, age_minutes
    except Exception as e:
        return None, None


def simple_connectivity_test():
    """Simple ping test to Lambda Labs server"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "165.1.69.44"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def main():
    print("🚀 GitHub Deployment Monitor for Sophia AI")
    print("="*50)
    
    commit_time, age_minutes = check_commit_age()
    if commit_time:
        print(f"📝 Latest Commit: {commit_time.strftime('%H:%M:%S')}")
        print(f"⏰ Age: {age_minutes:.1f} minutes ago")
    
    server_reachable = simple_connectivity_test()
    print(f"🌐 Lambda Labs Server: {'✅ Reachable' if server_reachable else '❌ Not reachable'}")
    
    print("\n📊 Deployment Analysis:")
    
    if age_minutes and age_minutes < 5:
        print("   🔨 Status: Likely building Docker images")
        print("   💡 Recommendation: Wait 5-10 more minutes")
    elif age_minutes and age_minutes < 15:
        print("   🚀 Status: Likely deploying services")
        print("   💡 Recommendation: Wait 5 more minutes, then test connectivity")
    elif age_minutes and age_minutes < 30:
        print("   ⚠️ Status: Deployment may have issues")
        print("   💡 Recommendation: Check GitHub Actions logs")
    else:
        print("   ❓ Status: Unknown - check manually")
    
    print(f"\n🔗 Monitoring URLs:")
    print(f"   GitHub Actions: https://github.com/ai-cherry/sophia-main/actions")
    print(f"   Codacy MCP: http://165.1.69.44:3008 (when ready)")
    
    print(f"\n💡 Manual Check Commands:")
    print(f"   python scripts/monitor_codacy_mcp_server.py")
    print(f"   python scripts/test_lambda_labs_connectivity.py")


if __name__ == "__main__":
    main() 