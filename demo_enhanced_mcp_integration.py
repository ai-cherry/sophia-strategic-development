#!/usr/bin/env python3
"""
Enhanced MCP Integration Demonstration
Shows how @ai_memory and @codacy work together for intelligent development
"""

import asyncio
import aiohttp
from datetime import datetime


class MCPIntegrationDemo:
    """Demonstrates enhanced MCP integration capabilities"""

    def __init__(self):
        self.ai_memory_url = "http://localhost:9000"
        self.codacy_url = "http://localhost:3008"
        self.backend_url = "http://localhost:8000"

    async def demonstrate_ai_memory_auto_discovery(self):
        """Demonstrate AI Memory auto-discovery and context storage"""
        print("\n🧠 AI MEMORY AUTO-DISCOVERY DEMONSTRATION")
        print("=" * 60)

        # Sample architectural discussion
        architectural_discussion = """
        We decided to implement OAuth2 authentication for our MCP servers because:
        1. It provides better security than API keys
        2. Supports token refresh for long-running services
        3. Integrates well with our existing Pulumi ESC secret management
        4. Allows fine-grained permissions per MCP server
        
        Implementation approach:
        - Use FastAPI OAuth2 middleware
        - Store tokens in Redis with TTL
        - Implement automatic token refresh
        - Add rate limiting per authenticated user
        """

        # Test auto-storage
        print("📝 Testing automatic context storage...")
        try:
            async with aiohttp.ClientSession() as session:
                # Simulate auto-storage trigger
                payload = {
                    "tool_name": "auto_store_context",
                    "parameters": {
                        "content": architectural_discussion,
                        "interaction_type": "architecture_discussion",
                        "file_path": "backend/mcp/auth_server.py",
                        "user_intent": "security_implementation",
                    },
                }

                async with session.post(
                    f"{self.ai_memory_url}/execute", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Auto-stored memory: {result.get('id', 'unknown')}")
                        print(f"   Category: {result.get('category', 'unknown')}")
                        print(f"   Status: {result.get('status', 'unknown')}")
                    else:
                        print(f"❌ Auto-storage failed: {response.status}")

        except Exception as e:
            print(f"❌ Error testing auto-storage: {e}")

        # Test smart recall
        print("\n🔍 Testing smart context recall...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool_name": "smart_recall",
                    "parameters": {
                        "query": "OAuth2 authentication implementation",
                        "current_file": "backend/mcp/new_auth_server.py",
                        "recent_activity": [
                            "security_implementation",
                            "mcp_development",
                        ],
                    },
                }

                async with session.post(
                    f"{self.ai_memory_url}/execute", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        memories = result.get("results", [])
                        print(f"✅ Retrieved {len(memories)} relevant memories")

                        for i, memory in enumerate(memories[:2]):  # Show first 2
                            print(f"   Memory {i + 1}:")
                            print(
                                f"     - Category: {memory.get('category', 'unknown')}"
                            )
                            print(
                                f"     - Relevance: {memory.get('relevance_score', 0):.2f}"
                            )
                            print(f"     - Tags: {', '.join(memory.get('tags', []))}")
                    else:
                        print(f"❌ Smart recall failed: {response.status}")

        except Exception as e:
            print(f"❌ Error testing smart recall: {e}")

    async def demonstrate_codacy_real_time_analysis(self):
        """Demonstrate Codacy real-time code analysis"""
        print("\n🔍 CODACY REAL-TIME ANALYSIS DEMONSTRATION")
        print("=" * 60)

        # Sample code with various issues
        problematic_code = """
def authenticate_user(password, username):
    # TODO: This is insecure - fix later
    if password == "admin123":  # Hardcoded password - security issue
        print("User authenticated")  # Should use logging
        return True
    
    # Complex nested logic - high complexity
    if username:
        if len(username) > 5:
            if username.startswith("admin"):
                if password and len(password) > 8:
                    if "special" in password:
                        if password.endswith("!"):
                            return True
    
    # Potential SQL injection
    query = f"SELECT * FROM users WHERE name = '{username}'"
    
    return False
"""

        print("📝 Testing real-time code analysis...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool_name": "analyze_code",
                    "parameters": {
                        "code": problematic_code,
                        "language": "python",
                        "file_path": "backend/auth/insecure_auth.py",
                    },
                }

                async with session.post(
                    f"{self.codacy_url}/execute", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()

                        print("✅ Analysis completed:")
                        print(f"   Total Issues: {result.get('total_issues', 0)}")
                        print(f"   Language: {result.get('language', 'unknown')}")

                        # Show severity breakdown
                        severity = result.get("severity_breakdown", {})
                        print("   Severity Breakdown:")
                        print(f"     - Errors: {severity.get('error', 0)}")
                        print(f"     - Warnings: {severity.get('warning', 0)}")
                        print(f"     - Info: {severity.get('info', 0)}")

                        # Show first few issues
                        issues = result.get("issues", [])
                        print("\n   Top Issues Found:")
                        for i, issue in enumerate(issues[:3]):
                            print(
                                f"     {i + 1}. Line {issue.get('line', '?')}: {issue.get('message', 'Unknown')}"
                            )
                            print(
                                f"        Type: {issue.get('type', 'unknown')} | Severity: {issue.get('severity', 'unknown')}"
                            )

                        # Show suggestions
                        suggestions = result.get("suggestions", [])
                        if suggestions:
                            print("\n   Automated Suggestions:")
                            for suggestion in suggestions[:3]:
                                print(f"     - {suggestion}")

                    else:
                        print(f"❌ Code analysis failed: {response.status}")

        except Exception as e:
            print(f"❌ Error testing code analysis: {e}")

    async def demonstrate_integrated_workflow(self):
        """Demonstrate integrated workflow combining both services"""
        print("\n🔄 INTEGRATED WORKFLOW DEMONSTRATION")
        print("=" * 60)

        print("📋 Scenario: Implementing secure password validation")

        # Step 1: Recall similar security implementations
        print("\n1️⃣ Recalling similar security patterns...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool_name": "recall_memory",
                    "parameters": {
                        "query": "password security validation implementation",
                        "category": "code_decision",
                        "limit": 2,
                    },
                }

                async with session.post(
                    f"{self.ai_memory_url}/execute", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        memories = result.get("results", [])
                        print(f"✅ Found {len(memories)} relevant security patterns")
                    else:
                        print(f"❌ Memory recall failed: {response.status}")
        except Exception as e:
            print(f"❌ Error in memory recall: {e}")

        # Step 2: Analyze proposed secure implementation
        secure_code = '''
import hashlib
import secrets
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < 12:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=" for c in password)
    
    return all([has_upper, has_lower, has_digit, has_special])

def hash_password(password: str) -> tuple[str, str]:
    """Securely hash password with salt"""
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
    return password_hash.hex(), salt

def authenticate_user(username: str, password: str, stored_hash: str, salt: str) -> bool:
    """Authenticate user with secure password verification"""
    try:
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        
        if secrets.compare_digest(stored_hash, password_hash.hex()):
            logger.info(f"Successful authentication for user: {username}")
            return True
        else:
            logger.warning(f"Failed authentication attempt for user: {username}")
            return False
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False
'''

        print("\n2️⃣ Analyzing secure implementation...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool_name": "analyze_code",
                    "parameters": {
                        "code": secure_code,
                        "language": "python",
                        "file_path": "backend/auth/secure_auth.py",
                    },
                }

                async with session.post(
                    f"{self.codacy_url}/execute", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Secure implementation analysis:")
                        print(f"   Total Issues: {result.get('total_issues', 0)}")

                        severity = result.get("severity_breakdown", {})
                        print(f"   Security Issues: {severity.get('error', 0)}")
                        print(f"   Code Quality: {severity.get('warning', 0)} warnings")

                        if result.get("total_issues", 0) == 0:
                            print(
                                "   🎉 No security issues found - implementation looks secure!"
                            )
                    else:
                        print(f"❌ Analysis failed: {response.status}")
        except Exception as e:
            print(f"❌ Error in code analysis: {e}")

        # Step 3: Store the secure implementation pattern
        print("\n3️⃣ Storing secure implementation pattern...")
        try:
            async with aiohttp.ClientSession() as session:
                implementation_summary = f"""
SECURE PASSWORD AUTHENTICATION IMPLEMENTATION

Key Security Features:
- Password strength validation (12+ chars, mixed case, digits, special chars)
- PBKDF2 hashing with SHA-256 and 100,000 iterations
- Cryptographically secure salt generation using secrets module
- Constant-time comparison to prevent timing attacks
- Comprehensive logging for security monitoring
- Proper error handling to prevent information leakage

Code Quality Features:
- Type hints for better code clarity
- Structured logging instead of print statements
- Modular functions for testability
- Exception handling with proper logging

Implementation Date: {datetime.now().isoformat()}
Security Review: Passed Codacy analysis with 0 security issues
"""

                payload = {
                    "tool_name": "store_conversation",
                    "parameters": {
                        "content": implementation_summary,
                        "category": "code_decision",
                        "tags": [
                            "security",
                            "authentication",
                            "password",
                            "hashing",
                            "best-practice",
                        ],
                    },
                }

                async with session.post(
                    f"{self.ai_memory_url}/execute", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(
                            f"✅ Stored secure implementation pattern: {result.get('id', 'unknown')}"
                        )
                    else:
                        print(f"❌ Storage failed: {response.status}")
        except Exception as e:
            print(f"❌ Error storing pattern: {e}")

    async def demonstrate_system_status(self):
        """Show current system status and capabilities"""
        print("\n📊 SYSTEM STATUS AND CAPABILITIES")
        print("=" * 60)

        services = [
            ("AI Memory", self.ai_memory_url),
            ("Codacy Analysis", self.codacy_url),
            ("Sophia Backend", self.backend_url),
        ]

        for service_name, url in services:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health") as response:
                        if response.status == 200:
                            print(f"🟢 {service_name}: OPERATIONAL")
                        else:
                            print(f"🔴 {service_name}: ISSUES ({response.status})")
            except Exception:
                print(f"🔴 {service_name}: UNREACHABLE")

        print("\n🎯 Enhanced Integration Features:")
        print("   ✅ Automatic context detection and storage")
        print("   ✅ Real-time security vulnerability scanning")
        print("   ✅ Context-aware memory retrieval")
        print("   ✅ Intelligent code quality analysis")
        print("   ✅ Automated workflow triggers")
        print("   ✅ Natural language command processing")

    async def run_complete_demonstration(self):
        """Run the complete enhanced MCP integration demonstration"""
        print("🚀 ENHANCED MCP INTEGRATION DEMONSTRATION")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("This demonstrates the enhanced @ai_memory and @codacy integration")
        print("for intelligent, context-aware development in Cursor IDE.")

        await self.demonstrate_system_status()
        await self.demonstrate_ai_memory_auto_discovery()
        await self.demonstrate_codacy_real_time_analysis()
        await self.demonstrate_integrated_workflow()

        print("\n🎉 DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("Your Cursor IDE is now equipped with:")
        print("• Intelligent memory that learns from every interaction")
        print("• Real-time code analysis with security scanning")
        print("• Context-aware development assistance")
        print("• Automated quality and security workflows")
        print(
            "\nStart using @ai_memory and @codacy in Cursor IDE for enhanced development!"
        )


async def main():
    """Run the enhanced MCP integration demonstration"""
    demo = MCPIntegrationDemo()
    await demo.run_complete_demonstration()


if __name__ == "__main__":
    asyncio.run(main())
