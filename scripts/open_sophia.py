#!/usr/bin/env python3
"""
Open Sophia AI in browser and provide helpful information
"""
import webbrowser
import time
import requests
import sys


def main():
    print("\n🚀 SOPHIA AI IS RUNNING!\n")
    print("=" * 60)

    # Check if services are running
    try:
        backend = requests.get("http://localhost:8001/health", timeout=2)
        frontend = requests.get("http://localhost:5173", timeout=2)

        if backend.status_code == 200 and frontend.status_code == 200:
            print("✅ All services are running correctly!")
            print("\n📍 URLs:")
            print("   Frontend Dashboard: http://localhost:5173")
            print("   Backend API: http://localhost:8001")
            print("   API Documentation: http://localhost:8001/docs")

            print("\n🌐 Opening Sophia AI in your browser...")
            webbrowser.open("http://localhost:5173")

            print("\n💡 TROUBLESHOOTING TIPS:")
            print("   If you see a blank screen:")
            print("   1. Try refreshing the page (Cmd+R or Ctrl+R)")
            print("   2. Try a hard refresh (Cmd+Shift+R or Ctrl+Shift+R)")
            print("   3. Check browser console for errors (F12 → Console tab)")
            print("   4. Try a different browser or incognito mode")
            print("   5. Clear browser cache and cookies for localhost")

            print("\n🔍 WHAT YOU SHOULD SEE:")
            print("   - A dark-themed dashboard")
            print("   - Sophia AI branding")
            print("   - Chat interface on the right")
            print("   - Various dashboard cards and metrics")

            print("\n🎯 FEATURES:")
            print("   - Chat with AI assistant")
            print("   - View system metrics")
            print("   - Access business intelligence")
            print("   - ModernStack data integration")

            print("\n✨ The dashboard uses a glassmorphism design")
            print("   with a dark theme optimized for executives.")

        else:
            print("❌ Services are not running properly!")
            print("Please run: python scripts/deploy_sophia_complete.py")

    except Exception as e:
        print(f"❌ Error checking services: {e}")
        print("Please ensure services are running.")

    print("\n" + "=" * 60)
    print("Press Ctrl+C to exit this information screen.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
