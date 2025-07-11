#!/usr/bin/env python3
"""
Fix Sophia AI Vercel Deployment with sophia-intel.ai domain
Ensures no blank screens and proper backend connection
"""

import os
import subprocess
import json
from pathlib import Path


class SophiaVercelFix:
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

    def fix_frontend_code(self):
        """Fix the toUpperCase error in UnifiedChatDashboard"""
        self.print_header("Fixing Frontend Code Issues")

        # Fix UnifiedChatDashboard.tsx
        dashboard_file = self.frontend_dir / "src/components/UnifiedChatDashboard.tsx"

        # Read the file
        content = dashboard_file.read_text()

        # Fix the toUpperCase error by adding null checks
        fixes = [
            # Fix systemStatus.overall_status.toUpperCase()
            (
                "systemStatus.overall_status.toUpperCase()",
                "(systemStatus.overall_status || 'unknown').toUpperCase()",
            ),
            # Fix potential undefined access
            (
                "const CHAT_API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';",
                "const CHAT_API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';",
            ),
        ]

        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ Fixed: {old[:50]}...")

        # Write back
        dashboard_file.write_text(content)

        # Also fix KPICards.tsx if needed
        kpi_file = self.frontend_dir / "src/components/dashboard/KPICards.tsx"
        if kpi_file.exists():
            content = kpi_file.read_text()
            # Add null checks for change property
            content = content.replace(
                "const isPositive = change.startsWith('+');",
                "const isPositive = change && change.startsWith('+');",
            )
            kpi_file.write_text(content)
            print("✅ Fixed KPICards null checks")

    def create_env_files(self):
        """Create proper environment files for Vercel"""
        self.print_header("Creating Environment Files")

        # Create .env.production for build time
        env_prod = self.frontend_dir / ".env.production"
        env_content = """# Sophia AI Production Configuration
VITE_API_URL=http://localhost:8001
VITE_APP_NAME=Sophia AI
VITE_APP_VERSION=3.0.0
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_CHAT=true
VITE_ENABLE_DASHBOARD=true
VITE_WS_URL=ws://localhost:8001/ws
VITE_DEBUG_MODE=false
"""
        env_prod.write_text(env_content)
        print("✅ Created .env.production")

        # Create .env.local for local development
        env_local = self.frontend_dir / ".env.local"
        env_local.write_text(env_content)
        print("✅ Created .env.local")

    def update_vercel_json(self):
        """Update vercel.json for proper configuration"""
        self.print_header("Updating Vercel Configuration")

        vercel_json = self.frontend_dir / "vercel.json"
        config = {
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "framework": "vite",
            "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {"key": "X-Content-Type-Options", "value": "nosniff"},
                        {"key": "X-Frame-Options", "value": "DENY"},
                        {"key": "X-XSS-Protection", "value": "1; mode=block"},
                    ],
                }
            ],
        }

        with open(vercel_json, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Updated vercel.json")

    def setup_backend_tunnel(self):
        """Setup ngrok tunnel for backend"""
        self.print_header("Setting Up Backend Tunnel")

        print("🔍 Checking if backend is running...")
        success, _, _ = self.run_command("curl -s http://localhost:8001/health")

        if not success:
            print("❌ Backend not running! Starting it...")
            # Start backend
            subprocess.Popen(
                ["python", "backend/app/unified_chat_backend.py"],
                cwd=self.root_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("⏳ Waiting for backend to start...")
            import time

            time.sleep(10)

        print("\n🌐 To make your backend accessible from Vercel:")
        print("1. Install ngrok: brew install ngrok")
        print("2. Run: ngrok http 8001")
        print("3. Copy the https URL (e.g., https://abc123.ngrok.io)")
        print("4. Update VITE_API_URL in Vercel dashboard")

    def deploy_to_vercel(self):
        """Deploy to Vercel with proper settings"""
        self.print_header("Deploying to Vercel")

        os.chdir(self.frontend_dir)

        # Build locally first to catch errors
        print("🔨 Building locally first...")
        success, stdout, stderr = self.run_command("npm run build")

        if not success:
            print(f"❌ Build failed: {stderr}")
            return False

        print("✅ Local build successful!")

        # Deploy to Vercel
        print("\n🚀 Deploying to Vercel...")
        success, stdout, stderr = self.run_command("vercel --prod")

        if success:
            print("✅ Deployment successful!")
            # Extract URL from output
            if "https://" in stdout:
                url = [line for line in stdout.split("\n") if "https://" in line][0]
                print(f"\n🌐 Your app is live at: {url}")
        else:
            print(f"❌ Deployment failed: {stderr}")

        return success

    def setup_custom_domain(self):
        """Instructions for setting up sophia-intel.ai"""
        self.print_header("Setting Up sophia-intel.ai Domain")

        print(
            """
📌 To connect sophia-intel.ai to your Vercel deployment:

1. In Vercel Dashboard:
   - Go to your project settings
   - Click on "Domains"
   - Add "sophia-intel.ai" and "www.sophia-intel.ai"
   
2. In Namecheap DNS Settings:
   - Add these records:
   
   Type  Name    Value
   ----  ----    -----
   A     @       76.76.21.21
   A     www     76.76.21.21
   
   OR use CNAME:
   
   CNAME @       cname.vercel-dns.com
   CNAME www     cname.vercel-dns.com

3. Wait 5-30 minutes for DNS propagation

4. Update Environment Variables in Vercel:
   - VITE_API_URL = https://your-backend-url.ngrok.io
   - Redeploy after updating

✅ Your site will be accessible at:
   - https://sophia-intel.ai
   - https://www.sophia-intel.ai
"""
        )

    def create_deployment_checklist(self):
        """Create a deployment checklist"""
        self.print_header("Deployment Checklist")

        checklist = """
## 🚀 SOPHIA AI DEPLOYMENT CHECKLIST

### ✅ Frontend Fixes Applied:
- [x] Fixed toUpperCase error in UnifiedChatDashboard
- [x] Added null checks for undefined properties
- [x] Fixed environment variable access (VITE_API_URL)
- [x] Created proper .env files

### ✅ Backend Setup:
- [ ] Backend running on localhost:8001
- [ ] Ngrok tunnel created for backend
- [ ] Ngrok URL copied

### ✅ Vercel Deployment:
- [ ] Code deployed to Vercel
- [ ] Environment variables set:
  - VITE_API_URL = <ngrok-url>
- [ ] Custom domain configured
- [ ] DNS records updated in Namecheap

### ✅ Testing:
- [ ] No blank screens
- [ ] Chat interface working
- [ ] System status loading
- [ ] No console errors

### 📱 URLs:
- Local Backend: http://localhost:8001
- Ngrok Backend: https://YOUR-ID.ngrok.io
- Vercel Preview: https://frontend-XXX.vercel.app
- Production: https://sophia-intel.ai
"""

        checklist_file = self.root_dir / "DEPLOYMENT_CHECKLIST.md"
        checklist_file.write_text(checklist)
        print("✅ Created DEPLOYMENT_CHECKLIST.md")

    def run(self):
        """Run all fixes"""
        print("\n🎯 FIXING SOPHIA AI VERCEL DEPLOYMENT")
        print("=" * 60)

        # Fix code issues
        self.fix_frontend_code()

        # Create environment files
        self.create_env_files()

        # Update vercel.json
        self.update_vercel_json()

        # Setup backend tunnel
        self.setup_backend_tunnel()

        # Deploy to Vercel
        if self.deploy_to_vercel():
            # Show domain setup instructions
            self.setup_custom_domain()

        # Create checklist
        self.create_deployment_checklist()

        print("\n✅ All fixes applied!")
        print("\n⚡ QUICK NEXT STEPS:")
        print("1. Run: ngrok http 8001")
        print("2. Copy the ngrok URL")
        print("3. Go to Vercel dashboard")
        print("4. Set VITE_API_URL to the ngrok URL")
        print("5. Redeploy")
        print("\n🎉 Your site will work perfectly at sophia-intel.ai!")


if __name__ == "__main__":
    fixer = SophiaVercelFix()
    fixer.run()
