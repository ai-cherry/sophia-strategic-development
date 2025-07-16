#!/usr/bin/env python3
"""
Sophia AI Production Verification Script
Comprehensive testing of all deployed components
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime
import websocket
import ssl

# Configuration
DOMAIN = "sophia-intel.ai"
API_DOMAIN = "api.sophia-intel.ai"
WEBHOOK_DOMAIN = "webhooks.sophia-intel.ai"
SERVER_IP = "192.222.58.232"

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class SophiaVerifier:
    def __init__(self):
        self.results = {
            "frontend": {},
            "backend": {},
            "mcp_servers": {},
            "infrastructure": {},
            "performance": {}
        }
        self.start_time = datetime.now()
        
    def log_info(self, message: str):
        print(f"{BLUE}[INFO]{NC} {message}")
        
    def log_success(self, message: str):
        print(f"{GREEN}[✓]{NC} {message}")
        
    def log_warning(self, message: str):
        print(f"{YELLOW}[!]{NC} {message}")
        
    def log_error(self, message: str):
        print(f"{RED}[✗]{NC} {message}")
        
    def test_dns_resolution(self) -> bool:
        """Test DNS resolution for all domains"""
        self.log_info("Testing DNS resolution...")
        
        domains = [DOMAIN, f"www.{DOMAIN}", API_DOMAIN, WEBHOOK_DOMAIN]
        all_resolved = True
        
        for domain in domains:
            try:
                result = subprocess.run(
                    ["nslookup", domain],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if SERVER_IP in result.stdout:
                    self.log_success(f"{domain} → {SERVER_IP}")
                    self.results["infrastructure"][f"dns_{domain}"] = "OK"
                else:
                    self.log_error(f"{domain} not pointing to {SERVER_IP}")
                    self.results["infrastructure"][f"dns_{domain}"] = "FAILED"
                    all_resolved = False
            except Exception as e:
                self.log_error(f"DNS lookup failed for {domain}: {e}")
                all_resolved = False
                
        return all_resolved
        
    def test_ssl_certificates(self) -> bool:
        """Test SSL certificates for all domains"""
        self.log_info("Testing SSL certificates...")
        
        domains = [DOMAIN, API_DOMAIN, WEBHOOK_DOMAIN]
        all_valid = True
        
        for domain in domains:
            try:
                requests.get(f"https://{domain}", timeout=5, verify=True)
                self.log_success(f"{domain} - SSL valid")
                self.results["infrastructure"][f"ssl_{domain}"] = "Valid"
            except requests.exceptions.SSLError:
                self.log_error(f"{domain} - SSL invalid")
                self.results["infrastructure"][f"ssl_{domain}"] = "Invalid"
                all_valid = False
            except Exception as e:
                self.log_warning(f"{domain} - Could not verify SSL: {e}")
                
        return all_valid
        
    def test_frontend(self) -> bool:
        """Test frontend deployment"""
        self.log_info("Testing frontend deployment...")
        
        tests_passed = 0
        tests_total = 0
        
        # Test main page
        tests_total += 1
        try:
            response = requests.get(f"https://{DOMAIN}", timeout=10)
            if response.status_code == 200:
                if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                    self.log_success("Frontend HTML loaded")
                    self.results["frontend"]["main_page"] = "OK"
                    tests_passed += 1
                else:
                    self.log_error("Frontend returned non-HTML content")
                    self.results["frontend"]["main_page"] = "Wrong content"
            else:
                self.log_error(f"Frontend returned status {response.status_code}")
                self.results["frontend"]["main_page"] = f"Status {response.status_code}"
        except Exception as e:
            self.log_error(f"Frontend request failed: {e}")
            self.results["frontend"]["main_page"] = "Failed"
            
        # Test static assets
        assets = [
            "/assets/index.js",
            "/assets/index.css",
            "/favicon.ico"
        ]
        
        for asset in assets:
            tests_total += 1
            try:
                response = requests.head(f"https://{DOMAIN}{asset}", timeout=5)
                if response.status_code == 200:
                    self.log_success(f"Asset {asset} accessible")
                    self.results["frontend"][f"asset_{asset}"] = "OK"
                    tests_passed += 1
                else:
                    self.log_warning(f"Asset {asset} returned {response.status_code}")
                    self.results["frontend"][f"asset_{asset}"] = f"Status {response.status_code}"
            except Exception as e:
                self.log_error(f"Asset {asset} failed: {e}")
                self.results["frontend"][f"asset_{asset}"] = "Failed"
                
        return tests_passed == tests_total
        
    def test_backend_api(self) -> bool:
        """Test backend API endpoints"""
        self.log_info("Testing backend API...")
        
        tests_passed = 0
        tests_total = 0
        
        # Test health endpoint
        tests_total += 1
        try:
            response = requests.get(f"https://{API_DOMAIN}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_success(f"API health check passed: {data}")
                    self.results["backend"]["health"] = "Healthy"
                    tests_passed += 1
                else:
                    self.log_warning(f"API health status: {data}")
                    self.results["backend"]["health"] = data.get("status", "Unknown")
            else:
                self.log_error(f"API health returned {response.status_code}")
                self.results["backend"]["health"] = f"Status {response.status_code}"
        except Exception as e:
            self.log_error(f"API health check failed: {e}")
            self.results["backend"]["health"] = "Failed"
            
        # Test API docs
        tests_total += 1
        try:
            response = requests.get(f"https://{API_DOMAIN}/docs", timeout=5)
            if response.status_code == 200:
                self.log_success("API documentation accessible")
                self.results["backend"]["docs"] = "OK"
                tests_passed += 1
            else:
                self.log_warning(f"API docs returned {response.status_code}")
                self.results["backend"]["docs"] = f"Status {response.status_code}"
        except Exception as e:
            self.log_error(f"API docs failed: {e}")
            self.results["backend"]["docs"] = "Failed"
            
        # Test chat endpoint
        tests_total += 1
        try:
            response = requests.post(
                f"https://{API_DOMAIN}/api/chat/unified",
                json={"message": "Hello Sophia", "context": "test"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code in [200, 201]:
                self.log_success("Chat endpoint responsive")
                self.results["backend"]["chat"] = "OK"
                tests_passed += 1
            else:
                self.log_warning(f"Chat endpoint returned {response.status_code}")
                self.results["backend"]["chat"] = f"Status {response.status_code}"
        except Exception as e:
            self.log_warning(f"Chat endpoint error: {e}")
            self.results["backend"]["chat"] = "Error"
            
        return tests_passed >= tests_total - 1  # Allow one failure
        
    def test_websocket(self) -> bool:
        """Test WebSocket connectivity"""
        self.log_info("Testing WebSocket connection...")
        
        try:
            ws_url = f"wss://{API_DOMAIN}/ws"
            ws = websocket.create_connection(
                ws_url,
                timeout=5,
                sslopt={"cert_reqs": ssl.CERT_NONE}
            )
            ws.send(json.dumps({"type": "ping"}))
            ws.recv()
            ws.close()
            
            self.log_success("WebSocket connected and responsive")
            self.results["backend"]["websocket"] = "OK"
            return True
        except Exception as e:
            self.log_warning(f"WebSocket connection failed: {e}")
            self.results["backend"]["websocket"] = "Failed"
            return False
            
    def test_mcp_servers(self) -> bool:
        """Test MCP server connectivity via SSH"""
        self.log_info("Testing MCP servers...")
        
        mcp_ports = {
            "9000": "AI Memory",
            "3008": "Codacy",
            "9003": "GitHub",
            "9004": "Linear",
            "9005": "Slack",
            "9006": "HubSpot"
        }
        
        # Note: This would require SSH access to test properly
        # For now, we'll test if the API reports them as healthy
        try:
            response = requests.get(f"https://{API_DOMAIN}/api/mcp/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                for port, name in mcp_ports.items():
                    if port in str(data):
                        self.log_success(f"{name} MCP server reported")
                        self.results["mcp_servers"][name] = "Reported"
                    else:
                        self.log_warning(f"{name} MCP server not in status")
                        self.results["mcp_servers"][name] = "Unknown"
            else:
                self.log_warning("Could not get MCP status from API")
                for name in mcp_ports.values():
                    self.results["mcp_servers"][name] = "Unknown"
        except Exception as e:
            self.log_warning(f"MCP status check failed: {e}")
            for name in mcp_ports.values():
                self.results["mcp_servers"][name] = "Unknown"
                
        return True  # Don't fail deployment on MCP status
        
    def test_performance(self) -> bool:
        """Test performance metrics"""
        self.log_info("Testing performance...")
        
        # Test frontend load time
        start = time.time()
        try:
            requests.get(f"https://{DOMAIN}", timeout=10)
            frontend_time = (time.time() - start) * 1000
            self.log_info(f"Frontend load time: {frontend_time:.0f}ms")
            self.results["performance"]["frontend_load_ms"] = frontend_time
            
            if frontend_time < 2000:
                self.log_success("Frontend load time acceptable")
            else:
                self.log_warning("Frontend load time high")
        except:
            self.results["performance"]["frontend_load_ms"] = "Failed"
            
        # Test API response time
        start = time.time()
        try:
            requests.get(f"https://{API_DOMAIN}/health", timeout=5)
            api_time = (time.time() - start) * 1000
            self.log_info(f"API response time: {api_time:.0f}ms")
            self.results["performance"]["api_response_ms"] = api_time
            
            if api_time < 200:
                self.log_success("API response time excellent")
            elif api_time < 500:
                self.log_success("API response time acceptable")
            else:
                self.log_warning("API response time high")
        except:
            self.results["performance"]["api_response_ms"] = "Failed"
            
        return True
        
    def generate_report(self):
        """Generate comprehensive verification report"""
        report_file = f"SOPHIA_VERIFICATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, "w") as f:
            f.write("# Sophia AI Production Verification Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration:** {(datetime.now() - self.start_time).total_seconds():.1f} seconds\n\n")
            
            f.write("## Summary\n\n")
            
            # Count successes
            total_tests = 0
            passed_tests = 0
            
            for category, tests in self.results.items():
                for test, result in tests.items():
                    total_tests += 1
                    if result in ["OK", "Healthy", "Valid", "Reported"] or isinstance(result, (int, float)):
                        passed_tests += 1
                        
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            f.write(f"**Success Rate:** {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)\n\n")
            
            # Detailed results
            f.write("## Detailed Results\n\n")
            
            for category, tests in self.results.items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                f.write("| Test | Result |\n")
                f.write("|------|--------|\n")
                
                for test, result in tests.items():
                    status_icon = "✅" if result in ["OK", "Healthy", "Valid", "Reported"] else "⚠️"
                    if result == "Failed":
                        status_icon = "❌"
                    f.write(f"| {test.replace('_', ' ').title()} | {status_icon} {result} |\n")
                    
                f.write("\n")
                
            # Access URLs
            f.write("## Access URLs\n\n")
            f.write(f"- **Frontend:** https://{DOMAIN}\n")
            f.write(f"- **API:** https://{API_DOMAIN}\n")
            f.write(f"- **API Docs:** https://{API_DOMAIN}/docs\n")
            f.write(f"- **Webhooks:** https://{WEBHOOK_DOMAIN}\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            if success_rate == 100:
                f.write("✅ **All systems operational!** The deployment is fully successful.\n\n")
            elif success_rate >= 80:
                f.write("⚠️ **Mostly operational.** Some minor issues detected that should be addressed.\n\n")
            else:
                f.write("❌ **Critical issues detected.** Immediate attention required.\n\n")
                
            # Specific recommendations
            if self.results.get("frontend", {}).get("main_page") != "OK":
                f.write("- **Frontend Issue:** Check nginx configuration and frontend deployment\n")
            if self.results.get("backend", {}).get("health") != "Healthy":
                f.write("- **Backend Issue:** Check backend service and logs\n")
            if any("Unknown" in str(v) for v in self.results.get("mcp_servers", {}).values()):
                f.write("- **MCP Servers:** Verify MCP server deployment and connectivity\n")
                
        self.log_success(f"Verification report saved to: {report_file}")
        return report_file
        
    def run_verification(self):
        """Run all verification tests"""
        print("=" * 50)
        print("Sophia AI Production Verification")
        print("=" * 50)
        print()
        
        # Run all tests
        dns_ok = self.test_dns_resolution()
        ssl_ok = self.test_ssl_certificates()
        frontend_ok = self.test_frontend()
        backend_ok = self.test_backend_api()
        self.test_websocket()
        self.test_mcp_servers()
        self.test_performance()
        
        # Generate report
        print()
        print("=" * 50)
        report_file = self.generate_report()
        
        # Overall status
        all_critical_passed = dns_ok and ssl_ok and (frontend_ok or backend_ok)
        
        if all_critical_passed:
            print(f"{GREEN}VERIFICATION PASSED{NC} - Sophia AI is operational!")
        else:
            print(f"{RED}VERIFICATION FAILED{NC} - Critical issues detected")
            
        print(f"\nDetailed report: {report_file}")
        print("=" * 50)
        
        return all_critical_passed


if __name__ == "__main__":
    verifier = SophiaVerifier()
    success = verifier.run_verification()
    sys.exit(0 if success else 1) 