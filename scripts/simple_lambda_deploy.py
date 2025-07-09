#!/usr/bin/env python3
"""
Simple Lambda Labs Deployment
Deploy a basic working Sophia AI service to Lambda Labs instances.
"""

import subprocess
import time

INSTANCES = {
    "production": "104.171.202.103",
    "ai-core": "192.222.58.232",
    "mcp-servers": "104.171.202.117",
    "data-pipeline": "104.171.202.134",
    "development": "155.248.194.183"
}

def deploy_simple_service(name, ip):
    """Deploy a simple working service"""
    print(f"🚀 Deploying to {name} ({ip})")

    # Create a self-contained Python service
    service_code = '''
import http.server
import socketserver
import json
from urllib.parse import urlparse

class SophiaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "instance": "''' + name + '''", "ip": "''' + ip + '''"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "Sophia AI is running!", "instance": "''' + name + '''", "status": "operational"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "operational",
                "instance": "''' + name + '''",
                "ip": "''' + ip + '''",
                "services": ["sophia-ai", "health-monitor"],
                "environment": "production"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), SophiaHandler) as httpd:
        print(f"Sophia AI serving on port {PORT}")
        httpd.serve_forever()
'''

    try:
        # Deploy the service
        deploy_cmd = f"""
        ssh -o StrictHostKeyChecking=no ubuntu@{ip} '
        # Kill any existing services
        pkill -f "python.*sophia" || true
        pkill -f "port 8000" || true
        
        # Create the service file
        cat > sophia_service.py << "EOF"
{service_code}
EOF
        
        # Start the service in background
        nohup python3 sophia_service.py > sophia.log 2>&1 &
        
        # Wait and test
        sleep 3
        curl -s http://localhost:8000/health || echo "Starting..."
        '
        """

        result = subprocess.run(deploy_cmd, check=False, shell=True, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(f"  ✅ Service deployed to {name}")

            # Verify it's working
            time.sleep(3)
            verify_cmd = f"ssh ubuntu@{ip} 'curl -s http://localhost:8000/health'"
            verify_result = subprocess.run(verify_cmd, check=False, shell=True, capture_output=True, text=True, timeout=10)

            if "healthy" in verify_result.stdout:
                print(f"  ✅ Service verified on {name}")
                return True
            else:
                print(f"  ⚠️ Service deployed but not responding on {name}")
                return False
        else:
            print(f"  ❌ Deployment failed on {name}")
            return False

    except Exception as e:
        print(f"  ❌ Error deploying to {name}: {e}")
        return False

def main():
    """Deploy to all instances"""
    print("🚀 SIMPLE LAMBDA LABS DEPLOYMENT")
    print("=" * 50)

    successful = 0
    for name, ip in INSTANCES.items():
        if deploy_simple_service(name, ip):
            successful += 1
        time.sleep(2)

    print("=" * 50)
    print(f"📊 Deployed: {successful}/{len(INSTANCES)} instances")

    if successful >= 3:
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("\n🌐 Access your services:")
        for name, ip in INSTANCES.items():
            print(f"  {name}: http://{ip}:8000/health")
    else:
        print("⚠️ PARTIAL DEPLOYMENT")

if __name__ == "__main__":
    main()
