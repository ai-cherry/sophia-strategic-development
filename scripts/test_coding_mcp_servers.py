#!/usr/bin/env python3
"""
Test Script for Coding MCP Servers
Demonstrates the capabilities of each coding-focused MCP server
"""

import asyncio
import sys

import aiohttp


class CodingMCPTester:
    def __init__(self):
        self.servers = {
            "codacy": {"port": 3008, "name": "Codacy Code Analysis"},
            "ai_memory": {"port": 9000, "name": "AI Memory Storage"},
            "github": {"port": 9003, "name": "GitHub Repository Management"},
            "ui_ux": {"port": 9002, "name": "UI/UX Component Generator"},
            "huggingface": {"port": 9016, "name": "Hugging Face AI Integration"},
        }
        self.test_results = {}

    async def test_server_health(self, server_name: str, port: int) -> dict:
        """Test if a server is running and healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                # Try common health endpoints
                endpoints = ["/health", "/", "/api/health", "/status"]

                for endpoint in endpoints:
                    try:
                        async with session.get(
                            f"http://localhost:{port}{endpoint}",
                            timeout=aiohttp.ClientTimeout(total=5),
                        ) as response:
                            if response.status == 200:
                                data = await response.text()
                                return {
                                    "status": "healthy",
                                    "port": port,
                                    "endpoint": endpoint,
                                    "response": data[:200] + "..."
                                    if len(data) > 200
                                    else data,
                                }
                    except:
                        continue

                return {
                    "status": "unreachable",
                    "port": port,
                    "error": "No valid endpoints found",
                }

        except Exception as e:
            return {"status": "error", "port": port, "error": str(e)}

    async def test_codacy_analysis(self) -> dict:
        """Test Codacy code analysis with sample problematic code"""
        test_code = """
def vulnerable_function(user_input):
    password = "hardcoded123"  # Security issue
    sql = f"SELECT * FROM users WHERE name = '{user_input}'"  # SQL injection
    for i in range(100):  # Performance issue
        for j in range(100):  # Nested loop complexity
            print(f"{i}-{j}")
    return sql
"""

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "code": test_code,
                    "language": "python",
                    "file_path": "test.py",
                }

                async with session.post(
                    "http://localhost:3008/api/analyze",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "issues_found": len(result.get("issues", [])),
                            "security_issues": len(
                                [
                                    i
                                    for i in result.get("issues", [])
                                    if i.get("category") == "security"
                                ]
                            ),
                            "complexity_score": result.get("metrics", {}).get(
                                "complexity_score", 0
                            ),
                            "sample_issues": result.get("issues", [])[
                                :3
                            ],  # First 3 issues
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_ai_memory_storage(self) -> dict:
        """Test AI Memory storage and recall"""
        try:
            async with aiohttp.ClientSession() as session:
                # Store a memory
                store_payload = {
                    "content": "JWT authentication implementation with refresh tokens and httpOnly cookies for security",
                    "category": "security_pattern",
                    "tags": ["jwt", "authentication", "security", "cookies"],
                    "importance_score": 0.9,
                }

                async with session.post(
                    "http://localhost:9000/api/store_memory",
                    json=store_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        store_result = await response.json()

                        # Try to recall the memory
                        recall_payload = {"query": "JWT authentication", "limit": 3}

                        async with session.post(
                            "http://localhost:9000/api/recall_memory",
                            json=recall_payload,
                            timeout=aiohttp.ClientTimeout(total=10),
                        ) as recall_response:
                            if recall_response.status == 200:
                                recall_result = await recall_response.json()
                                return {
                                    "success": True,
                                    "memory_stored": store_result.get("success", False),
                                    "memories_recalled": len(
                                        recall_result.get("memories", [])
                                    ),
                                    "sample_memory": recall_result.get(
                                        "memories", [{}]
                                    )[0]
                                    if recall_result.get("memories")
                                    else None,
                                }

                    return {
                        "success": False,
                        "error": f"Store failed with HTTP {response.status}",
                    }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_github_integration(self) -> dict:
        """Test GitHub repository management"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"owner": "ai-cherry", "repo": "sophia-main"}

                async with session.post(
                    "http://localhost:9003/api/get_repository",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "repository_info": result.get("repository", {}),
                            "has_access_token": result.get("has_access_token", False),
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_ui_ux_generation(self) -> dict:
        """Test UI/UX component generation"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "component_type": "button",
                    "features": ["loading_state", "accessibility", "responsive"],
                    "styling": "glassmorphism",
                    "framework": "react",
                }

                async with session.post(
                    "http://localhost:9002/api/generate_component",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "component_generated": bool(result.get("component_code")),
                            "accessibility_score": result.get("accessibility_score", 0),
                            "code_length": len(result.get("component_code", "")),
                            "features_included": result.get("features_included", []),
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_huggingface_ai(self) -> dict:
        """Test Hugging Face AI capabilities"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": "This code is amazing and well-written!",
                    "task": "sentiment_analysis",
                }

                async with session.post(
                    "http://localhost:9016/api/analyze_sentiment",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "sentiment": result.get("sentiment"),
                            "confidence": result.get("confidence", 0),
                            "model_used": result.get("model", "unknown"),
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_comprehensive_test(self):
        """Run comprehensive tests on all coding MCP servers"""

        # Test server health first
        for server_name, config in self.servers.items():
            health = await self.test_server_health(server_name, config["port"])
            self.test_results[f"{server_name}_health"] = health

            if health["status"] == "healthy":
                pass
            else:
                pass

        # Test specific functionality

        # Test Codacy
        codacy_result = await self.test_codacy_analysis()
        self.test_results["codacy_analysis"] = codacy_result
        if codacy_result.get("success"):
            pass
        else:
            pass

        # Test AI Memory
        memory_result = await self.test_ai_memory_storage()
        self.test_results["ai_memory"] = memory_result
        if memory_result.get("success"):
            pass
        else:
            pass

        # Test GitHub
        github_result = await self.test_github_integration()
        self.test_results["github"] = github_result
        if github_result.get("success"):
            pass
        else:
            pass

        # Test UI/UX
        ui_result = await self.test_ui_ux_generation()
        self.test_results["ui_ux"] = ui_result
        if ui_result.get("success"):
            pass
        else:
            pass

        # Test Hugging Face
        hf_result = await self.test_huggingface_ai()
        self.test_results["huggingface"] = hf_result
        if hf_result.get("success"):
            pass
        else:
            pass

        await self.generate_report()

    async def generate_report(self):
        """Generate a comprehensive test report"""

        # Summary
        total_servers = len(self.servers)
        healthy_servers = sum(
            1
            for k, v in self.test_results.items()
            if k.endswith("_health") and v.get("status") == "healthy"
        )
        working_functions = sum(
            1
            for k, v in self.test_results.items()
            if not k.endswith("_health") and v.get("success")
        )

        # Detailed results

        for server_name, _config in self.servers.items():
            # Health status
            health = self.test_results.get(f"{server_name}_health", {})
            if health.get("status") == "healthy":
                pass
            else:
                continue

            # Functionality test
            func_result = self.test_results.get(server_name, {})
            if func_result.get("success"):
                # Server-specific details
                if (
                    server_name == "codacy"
                    or server_name == "ai_memory"
                    or server_name == "ui_ux"
                    or server_name == "huggingface"
                ):
                    pass

            else:
                pass

        if healthy_servers == total_servers:
            pass
        else:
            for server_name, _config in self.servers.items():
                health = self.test_results.get(f"{server_name}_health", {})
                if health.get("status") != "healthy":
                    pass

        if working_functions == len(self.servers):
            pass
        else:
            pass


def main():
    """Main function to run the test"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        return

    tester = CodingMCPTester()

    try:
        asyncio.run(tester.run_comprehensive_test())
    except KeyboardInterrupt:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    main()
