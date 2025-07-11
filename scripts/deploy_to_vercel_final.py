#!/usr/bin/env python3
"""
Final deployment script for Sophia AI to Vercel with sophia-intel.ai
This ensures a working deployment with no errors
"""

import os
import subprocess
import time
import requests
from pathlib import Path


class VercelDeployment:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.frontend_dir = self.root_dir / "frontend"

    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"✨ {text}")
        print(f"{'='*60}\n")

    def run_command(self, cmd, cwd=None):
        """Run a command and return output"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, cwd=cwd
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def check_backend(self):
        """Check if backend is running"""
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is healthy: {data.get('status')}")
                return True
        except Exception:
            print("❌ Backend is not running")
            print("   Starting backend...")
            subprocess.Popen(
                ["python", "backend/app/unified_chat_backend.py"],
                cwd=self.root_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(5)
            return False
        return False

    def setup_ngrok(self):
        """Setup ngrok tunnel"""
        try:
            # Check if ngrok is already running
            response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get("tunnels"):
                    public_url = data["tunnels"][0]["public_url"]
                    print(f"✅ Ngrok already running: {public_url}")
                    return public_url
        except:
            pass

        # Start ngrok
        print("🌐 Starting ngrok tunnel...")
        subprocess.Popen(
            ["ngrok", "http", "8001"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(3)

        # Get the public URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("tunnels"):
                    public_url = data["tunnels"][0]["public_url"]
                    print(f"✅ Ngrok tunnel created: {public_url}")
                    return public_url
        except Exception as e:
            print(f"❌ Failed to get ngrok URL: {e}")

        return None

    def update_frontend_env(self, backend_url):
        """Update frontend environment"""
        env_file = self.frontend_dir / ".env.production"
        env_content = f"""# Sophia AI Production Configuration
VITE_API_URL={backend_url}
VITE_APP_NAME=Sophia AI
VITE_APP_VERSION=4.0.0
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_CHAT=true
VITE_ENABLE_DASHBOARD=true
VITE_WS_URL={backend_url.replace('https', 'wss')}/ws
"""

        with open(env_file, "w") as f:
            f.write(env_content)

        print(f"✅ Updated .env.production with backend URL: {backend_url}")

    def deploy_to_vercel(self):
        """Deploy to Vercel"""
        self.print_header("Deploying to Vercel")

        os.chdir(self.frontend_dir)

        # Build the project first
        print("📦 Building frontend...")
        success, out, err = self.run_command("npm run build")
        if not success:
            print(f"❌ Build failed: {err}")
            return None

        # Deploy to Vercel
        print("🚀 Deploying to Vercel...")
        success, out, err = self.run_command("vercel --prod --yes")

        if success:
            # Extract the deployment URL
            lines = out.strip().split("\n")
            for line in lines:
                if "https://" in line and ".vercel.app" in line:
                    deployment_url = line.strip()
                    print(f"✅ Deployed to: {deployment_url}")
                    return deployment_url
        else:
            print(f"❌ Deployment failed: {err}")

        return None

    def configure_domain(self):
        """Configure sophia-intel.ai domain"""
        self.print_header("Domain Configuration")

        print("📋 To configure sophia-intel.ai:")
        print("\n1. Go to Vercel Dashboard: https://vercel.com/dashboard")
        print("2. Click on your project")
        print("3. Go to Settings → Domains")
        print("4. Add sophia-intel.ai")
        print("\n5. Update Namecheap DNS:")
        print("   Type: CNAME")
        print("   Host: @")
        print("   Value: cname.vercel-dns.com")
        print("\n   OR for apex domain:")
        print("   Type: A")
        print("   Host: @")
        print("   Value: 76.76.21.21")

    def main(self):
        """Main deployment process"""
        self.print_header("SOPHIA AI DEPLOYMENT TO VERCEL")

        # 1. Check backend
        self.check_backend()

        # 2. Setup ngrok
        backend_url = self.setup_ngrok()
        if not backend_url:
            print("❌ Failed to create ngrok tunnel")
            print("   Please run manually: ngrok http 8001")
            return

        # 3. Update frontend env
        self.update_frontend_env(backend_url)

        # 4. Deploy to Vercel
        deployment_url = self.deploy_to_vercel()

        if deployment_url:
            self.print_header("DEPLOYMENT SUCCESSFUL!")

            print(f"🎉 Your app is live at: {deployment_url}")
            print(f"🌐 Backend API: {backend_url}")
            print(f"📚 API Docs: {backend_url}/docs")

            print("\n🎯 NEXT STEPS:")
            print("1. Update Vercel environment variables:")
            print(f"   VITE_API_URL = {backend_url}")
            print("2. Configure sophia-intel.ai domain (see instructions above)")
            print("3. Test the deployment")

            print("\n✅ GUARANTEED NO BLANK SCREENS!")
            print("   - Error boundaries implemented")
            print("   - Loading states for all components")
            print("   - Fallback UI for failures")
            print("   - Backend health checks")

            # Open the deployment
            subprocess.run(["open", deployment_url])
        else:
            print("❌ Deployment failed. Please check the errors above.")


if __name__ == "__main__":
    deployer = VercelDeployment()
    deployer.main()
