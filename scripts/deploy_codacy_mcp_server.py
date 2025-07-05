#!/usr/bin/env python3
"""
Deploy and Test Codacy MCP Server
Ensures the Codacy MCP server is properly configured and running
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import aiohttp


class CodacyMCPDeployer:
    """Deploy and test Codacy MCP server"""

    def __init__(self):
        self.port = 3008  # Standard Codacy port
        self.server_path = Path("mcp-servers/codacy/simple_codacy_server.py")
        self.config_path = Path("config/cursor_enhanced_mcp_config.json")
        self.process = None

    async def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")

        # Check if server file exists
        if not self.server_path.exists():
            print(f"❌ Server file not found: {self.server_path}")
            return False

        # Check if port is available
        if await self.is_port_in_use(self.port):
            print(f"⚠️  Port {self.port} is already in use")
            # Try to stop existing process
            await self.stop_existing_server()
            await asyncio.sleep(2)

            if await self.is_port_in_use(self.port):
                print(f"❌ Could not free port {self.port}")
                return False

        print("✅ Prerequisites check passed")
        return True

    async def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            # Fallback method
            import socket

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    return False
                except:
                    return True

    async def stop_existing_server(self):
        """Stop any existing Codacy server"""
        print("🛑 Stopping existing Codacy server...")

        # Try to find and kill process on port
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{self.port}"], capture_output=True, text=True
            )
            if result.stdout:
                pid = result.stdout.strip()
                subprocess.run(["kill", "-9", pid])
                print(f"✅ Killed process {pid} on port {self.port}")
        except:
            pass

    def update_cursor_config(self):
        """Update cursor MCP configuration"""
        print("📝 Updating cursor MCP configuration...")

        # Load existing config
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}

        # Update Codacy configuration
        config["mcpServers"]["codacy"] = {
            "command": "python",
            "args": [str(self.server_path)],
            "env": {"ENVIRONMENT": "prod", "PYTHONPATH": ".", "PORT": str(self.port)},
            "port": self.port,
            "cwd": ".",
            "capabilities": [
                "code_analysis",
                "security_scanning",
                "complexity_analysis",
                "quality_metrics",
            ],
            "health_endpoint": "/health",
        }

        # Save updated config
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Updated cursor configuration")

    async def start_server(self) -> bool:
        """Start the Codacy MCP server"""
        print(f"🚀 Starting Codacy MCP server on port {self.port}...")

        # Set environment variables
        env = os.environ.copy()
        env.update({"PYTHONPATH": ".", "ENVIRONMENT": "prod", "PORT": str(self.port)})

        # Start the server
        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.server_path)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for server to start
            print("⏳ Waiting for server to start...")
            await asyncio.sleep(3)

            # Check if process is still running
            if self.process.poll() is not None:
                # Process terminated
                stdout, stderr = self.process.communicate()
                print("❌ Server failed to start")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False

            print("✅ Server process started")
            return True

        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    async def test_health_endpoint(self) -> bool:
        """Test the health endpoint"""
        print("🏥 Testing health endpoint...")

        url = f"http://localhost:{self.port}/health"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Health check passed: {data}")
                        return True
                    else:
                        print(f"❌ Health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    async def test_code_analysis(self) -> bool:
        """Test code analysis functionality"""
        print("🔍 Testing code analysis...")

        # Sample code with various issues
        test_code = """
def calculate_password(user_input):
    password = "hardcoded123"  # Security issue
    result = eval(user_input)  # Critical security issue

    # Complex nested function
    def process_data(data):
        if data:
            if len(data) > 0:
                if data[0]:
                    if data[0] > 10:
                        if data[0] < 100:
                            return data[0] * 2
        return 0

    return process_data([result])
"""

        url = f"http://localhost:{self.port}/api/v1/analyze/code"
        payload = {
            "code": test_code,
            "filename": "test_sample.py",
            "language": "python",
            "include_suggestions": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Code analysis successful")
                        print(f"   - Issues found: {len(data['issues'])}")
                        print(
                            f"   - Security score: {data['metrics']['security_score']}"
                        )
                        print(f"   - Overall score: {data['metrics']['overall_score']}")

                        # Show some issues
                        for issue in data["issues"][:3]:
                            print(f"   - {issue['severity']}: {issue['title']}")

                        return True
                    else:
                        print(f"❌ Code analysis failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Code analysis error: {e}")
            return False

    async def test_security_scan(self) -> bool:
        """Test security scanning"""
        print("🔒 Testing security scan...")

        # Code with security issues
        security_test_code = """
import os
import pickle
import subprocess

api_key = "sk-1234567890abcdef"
password = "admin123"

def unsafe_function(user_input):
    # SQL injection risk
    query = f"SELECT * FROM users WHERE id = {user_input}"

    # Command injection risk
    os.system(f"echo {user_input}")

    # Shell injection risk
    subprocess.call(user_input, shell=True)

    # Unsafe deserialization
    data = pickle.loads(user_input)

    return query
"""

        url = f"http://localhost:{self.port}/api/v1/security/scan"
        payload = {"code": security_test_code, "filename": "security_test.py"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Security scan successful")
                        print(f"   - Security issues: {data['total_issues']}")
                        print(
                            f"   - Critical: {data['severity_breakdown'].get('critical', 0)}"
                        )
                        print(f"   - High: {data['severity_breakdown'].get('high', 0)}")
                        return True
                    else:
                        print(f"❌ Security scan failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Security scan error: {e}")
            return False

    async def analyze_sophia_codebase(self):
        """Analyze a sample from Sophia AI codebase"""
        print("\n🎯 Analyzing Sophia AI code sample...")

        # Read a real file from the codebase
        sample_file = Path("backend/services/unified_ai_orchestration_service.py")
        if sample_file.exists():
            with open(sample_file) as f:
                # Read first 100 lines
                lines = f.readlines()[:100]
                code_sample = "".join(lines)

            url = f"http://localhost:{self.port}/api/v1/analyze/code"
            payload = {
                "code": code_sample,
                "filename": str(sample_file),
                "language": "python",
                "include_suggestions": True,
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            print("✅ Sophia AI code analysis complete")
                            print(f"   - File: {sample_file}")
                            print(
                                f"   - Overall score: {data['metrics']['overall_score']}/100"
                            )
                            print(
                                f"   - Security score: {data['metrics']['security_score']}/100"
                            )
                            print(f"   - Issues: {len(data['issues'])}")

                            if data["suggestions"]:
                                print("   - Suggestions:")
                                for suggestion in data["suggestions"][:3]:
                                    print(f"     • {suggestion}")

                            return True
            except Exception as e:
                print(f"❌ Sophia AI analysis error: {e}")

        return False

    async def deploy(self):
        """Main deployment process"""
        print("=" * 60)
        print("🚀 Codacy MCP Server Deployment")
        print("=" * 60)

        # Check prerequisites
        if not await self.check_prerequisites():
            print("\n❌ Prerequisites check failed")
            return False

        # Update configuration
        self.update_cursor_config()

        # Start server
        if not await self.start_server():
            print("\n❌ Failed to start server")
            return False

        # Test health
        health_ok = await self.test_health_endpoint()
        if not health_ok:
            print("\n⚠️  Health check failed, but continuing tests...")

        # Test functionality
        print("\n" + "=" * 60)
        print("🧪 Running Functionality Tests")
        print("=" * 60)

        tests_passed = 0
        tests_total = 3

        if await self.test_code_analysis():
            tests_passed += 1

        if await self.test_security_scan():
            tests_passed += 1

        if await self.analyze_sophia_codebase():
            tests_passed += 1

        # Summary
        print("\n" + "=" * 60)
        print("📊 Deployment Summary")
        print("=" * 60)
        print(f"✅ Server running on port: {self.port}")
        print(f"✅ Configuration updated: {self.config_path}")
        print(f"✅ Tests passed: {tests_passed}/{tests_total}")

        if tests_passed == tests_total:
            print("\n🎉 Codacy MCP server deployed successfully!")
            print("\n📝 Usage in Cursor:")
            print("   - Use @codacy to analyze code")
            print(
                "   - Commands: 'analyze this code', 'check security', 'scan for issues'"
            )
        else:
            print("\n⚠️  Some tests failed, but server is running")

        print("\n💡 Server logs:")
        print("-" * 40)

        # Keep server running and show logs
        if self.process:
            try:
                while True:
                    line = self.process.stdout.readline()
                    if line:
                        print(f"[SERVER] {line.strip()}")
                    await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                self.process.terminate()
                self.process.wait()

        return True

    def cleanup(self):
        """Cleanup resources"""
        if self.process:
            self.process.terminate()
            self.process.wait()


async def main():
    """Main entry point"""
    deployer = CodacyMCPDeployer()

    try:
        success = await deployer.deploy()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted")
        deployer.cleanup()
    except Exception as e:
        print(f"\n❌ Deployment error: {e}")
        deployer.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
