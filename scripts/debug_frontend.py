#!/usr/bin/env python3
"""
Debug frontend blank screen issue
"""
import requests


def test_frontend():
    print("\n🔍 DEBUGGING SOPHIA AI FRONTEND\n")
    print("=" * 60)

    # Test 1: Check if frontend is serving HTML
    print("\n1️⃣ Testing Frontend HTML Response:")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.headers.get('Content-Type', 'Unknown')}")

        # Check for key elements
        if "root" in response.text:
            print("   ✅ Found root div element")
        else:
            print("   ❌ Missing root div element")

        if "Sophia AI" in response.text:
            print("   ✅ Found Sophia AI title")
        else:
            print("   ❌ Missing Sophia AI title")

        if "/src/main.tsx" in response.text:
            print("   ✅ Found main.tsx script tag")
        else:
            print("   ❌ Missing main.tsx script tag")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Check API
    print("\n2️⃣ Testing Backend API:")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"   ✅ Backend is healthy: {response.json()}")
    except Exception as e:
        print(f"   ❌ Backend error: {e}")

    # Test 3: Check for common issues
    print("\n3️⃣ Common Issues to Check:")
    print("   • Browser Console Errors:")
    print("     - Open http://localhost:5173 in Chrome/Firefox")
    print("     - Press F12 to open Developer Tools")
    print("     - Click on 'Console' tab")
    print("     - Look for red error messages")
    print("\n   • Network Tab:")
    print("     - In Developer Tools, click 'Network' tab")
    print("     - Refresh the page (Ctrl+R or Cmd+R)")
    print("     - Check if all files load successfully (200 status)")
    print("     - Look for any 404 or 500 errors")

    # Test 4: Try to fetch main.tsx
    print("\n4️⃣ Testing JavaScript Loading:")
    try:
        response = requests.get("http://localhost:5173/src/main.tsx", timeout=5)
        if response.status_code == 200:
            print("   ✅ main.tsx is accessible")
        else:
            print(f"   ❌ main.tsx returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error fetching main.tsx: {e}")

    print("\n" + "=" * 60)
    print("\n🌐 MANUAL VERIFICATION STEPS:")
    print("\n1. Open a NEW incognito/private browser window")
    print("2. Navigate to: http://localhost:5173")
    print("3. If still blank:")
    print("   - Clear ALL browser data for localhost")
    print("   - Try a different browser (Chrome, Firefox, Safari)")
    print("   - Check if any browser extensions are blocking")
    print("\n4. Expected to see:")
    print("   - Light gray background")
    print("   - 'Sophia AI' header")
    print("   - Chat interface with input box")
    print("   - System status sidebar on the right")

    print("\n💡 QUICK FIX ATTEMPTS:")
    print("\n1. Hard refresh:")
    print("   - Windows/Linux: Ctrl + Shift + R")
    print("   - Mac: Cmd + Shift + R")
    print("\n2. Restart frontend:")
    print("   - Kill the current process: Ctrl+C")
    print("   - cd frontend && npm run dev")
    print("\n3. Check for TypeScript errors:")
    print("   - cd frontend && npm run type-check")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_frontend()
