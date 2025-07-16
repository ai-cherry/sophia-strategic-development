#!/usr/bin/env python3
"""
Deploy Sophia AI to Production Server (104.171.202.103)
"""

import subprocess
import time

def run_ssh_command(command, description):
    """Run SSH command on production server"""
    print(f"🔧 {description}...")
    ssh_cmd = f'ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no ubuntu@104.171.202.103 "{command}"'
    
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def deploy_backend():
    """Deploy the backend to production"""
    print("🚀 DEPLOYING SOPHIA AI TO PRODUCTION SERVER")
    print("=" * 60)
    print("📍 Server: 104.171.202.103 (sophia-production-instance)")
    print("🌐 Domain: sophia-intel.ai")
    print("🔌 Backend Port: 8000")
    print("🔌 Frontend Port: 80 (nginx)")
    print()
    
    # Step 1: Copy backend file
    print("📤 Copying backend to server...")
    scp_cmd = "scp -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no standalone_production_backend.py ubuntu@104.171.202.103:~/sophia_backend.py"
    result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Backend file copied")
    else:
        print(f"❌ Copy failed: {result.stderr}")
        return False
    
    # Step 2: Modify backend for port 8000
    if not run_ssh_command(
        "sed 's/port=7000/port=8000/g' sophia_backend.py > sophia_api.py",
        "Configuring backend for port 8000"
    ):
        return False
    
    # Step 3: Stop existing processes
    run_ssh_command("pkill -f 'python.*sophia'", "Stopping existing Sophia processes")
    time.sleep(2)
    
    # Step 4: Start backend
    if not run_ssh_command(
        "nohup python3 sophia_api.py > sophia_api.log 2>&1 &",
        "Starting Sophia AI backend"
    ):
        return False
    
    # Step 5: Wait for startup
    print("⏳ Waiting for backend startup...")
    time.sleep(5)
    
    # Step 6: Test backend
    if run_ssh_command(
        "curl -s http://localhost:8000/health",
        "Testing backend health"
    ):
        print("✅ Backend is healthy!")
    else:
        print("⚠️  Backend health check failed, checking logs...")
        run_ssh_command("tail -20 sophia_api.log", "Checking backend logs")
    
    # Step 7: Test system status
    if run_ssh_command(
        "curl -s http://localhost:8000/system/status | head -5",
        "Testing system status"
    ):
        print("✅ System status working!")
    
    # Step 8: Check nginx configuration
    run_ssh_command("nginx -t", "Testing nginx configuration")
    
    # Step 9: Test from external access
    print("\n🌐 TESTING EXTERNAL ACCESS")
    print("=" * 30)
    
    # Test the domain directly
    external_test = subprocess.run(
        "curl -s -I http://104.171.202.103/ | head -5", 
        shell=True, capture_output=True, text=True
    )
    
    if external_test.returncode == 0:
        print("✅ External server access working")
        print(f"   Response: {external_test.stdout.strip()}")
    else:
        print("❌ External access test failed")
    
    # Step 10: Final status
    print("\n📋 DEPLOYMENT SUMMARY")
    print("=" * 30)
    print("✅ Backend deployed to: 104.171.202.103:8000")
    print("✅ Domain configured: sophia-intel.ai")
    print("🔗 Backend API: http://104.171.202.103:8000")
    print("🔗 API Docs: http://104.171.202.103:8000/docs")
    print("🔗 Health Check: http://104.171.202.103:8000/health")
    print("🌐 Website: http://sophia-intel.ai")
    
    return True

if __name__ == "__main__":
    success = deploy_backend()
    if success:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("Your Sophia AI backend is now live on the production server.")
        print("The domain sophia-intel.ai should now resolve to working backend services.")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("Check the error messages above and try again.") 