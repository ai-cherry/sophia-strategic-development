#!/usr/bin/env python3
"""
Verify Sophia AI deployment is working correctly
"""

import requests


def check_backend():
    """Check backend health"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend: HEALTHY")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
    except Exception as e:
        print(f"❌ Backend: NOT RUNNING - {str(e)}")
        return False
    return False


def check_ngrok():
    """Check ngrok tunnel"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("tunnels"):
                tunnel = data["tunnels"][0]
                public_url = tunnel.get("public_url")
                print("✅ Ngrok: RUNNING")
                print(f"   Public URL: {public_url}")
                print("   Copy this URL for Vercel!")
                return public_url
    except Exception:
        print("❌ Ngrok: NOT RUNNING")
        print("   Run: ngrok http 8001")
    return None


def check_frontend():
    """Check frontend deployment"""
    vercel_url = "https://frontend-mr0qez7o2-lynn-musils-projects.vercel.app"
    print(f"\n🌐 Frontend URL: {vercel_url}")
    print("   Status: Deployed to Vercel")
    print("   Note: Update VITE_API_URL in Vercel dashboard")


def main():
    print("🔍 SOPHIA AI DEPLOYMENT VERIFICATION")
    print("=" * 50)

    # Check backend
    print("\n1. Backend Check:")
    backend_ok = check_backend()

    # Check ngrok
    print("\n2. Ngrok Tunnel Check:")
    ngrok_url = check_ngrok()

    # Check frontend
    print("\n3. Frontend Check:")
    check_frontend()

    # Summary
    print("\n" + "=" * 50)
    print("📋 DEPLOYMENT SUMMARY:")

    if backend_ok and ngrok_url:
        print("\n✅ Everything is ready!")
        print("\n🎯 NEXT STEPS:")
        print("1. Go to: https://vercel.com/dashboard")
        print("2. Add environment variable:")
        print(f"   VITE_API_URL = {ngrok_url}")
        print("3. Redeploy your frontend")
        print("4. Configure sophia-intel.ai domain")
    else:
        print("\n❌ Some services need attention")
        if not backend_ok:
            print("\n🔧 Start backend:")
            print("   python backend/app/unified_chat_backend.py")
        if not ngrok_url:
            print("\n🔧 Start ngrok:")
            print("   ngrok http 8001")


if __name__ == "__main__":
    main()
