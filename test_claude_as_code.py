#!/usr/bin/env python3
"""
Claude as Code Integration Test Script
Tests Claude MCP integration functionality with real Anthropic API
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.integrations.claude_integration import claude_integration
from infrastructure.esc.claude_secrets import claude_secret_manager

async def test_claude_secret_management():
    """Test Claude secret management"""
    print("🔐 Testing Claude Secret Management...")
    
    # Test 1: Setup secrets
    print("\n1. Setting up Claude secrets...")
    try:
        success = await claude_secret_manager.setup_claude_secrets()
        if success:
            print("   ✅ Claude secrets setup successful")
        else:
            print("   ❌ Claude secrets setup failed")
            return False
    except Exception as e:
        print(f"   ❌ Error setting up secrets: {e}")
        return False
    
    # Test 2: Validate configuration
    print("\n2. Validating Claude configuration...")
    try:
        validation = await claude_secret_manager.validate_claude_config()
        print(f"   📋 Configuration valid: {validation['valid']}")
        if not validation['valid']:
            print(f"   ⚠️  Missing fields: {validation.get('missing_fields', [])}")
            if validation.get('errors'):
                print(f"   ❌ Errors: {validation['errors']}")
        else:
            print("   ✅ All configuration fields present")
    except Exception as e:
        print(f"   ❌ Error validating configuration: {e}")
        return False
    
    # Test 3: Get environment variables
    print("\n3. Testing environment variable generation...")
    try:
        env_vars = await claude_secret_manager.get_environment_variables()
        print(f"   🌍 Generated {len(env_vars)} environment variables")
        for key in env_vars.keys():
            value = env_vars[key]
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"      • {key}={masked_value}")
        
        # Set environment variables for testing
        for key, value in env_vars.items():
            os.environ[key] = value
            
    except Exception as e:
        print(f"   ❌ Error getting environment variables: {e}")
        return False
    
    return True

async def test_claude_integration():
    """Test Claude integration functionality"""
    print("\n🤖 Testing Claude Integration...")
    
    # Test 1: Initialize integration
    print("\n1. Testing Claude integration initialization...")
    try:
        success = await claude_integration.initialize()
        if success:
            print("   ✅ Claude integration initialized successfully")
        else:
            print("   ❌ Claude integration initialization failed")
            return False
    except Exception as e:
        print(f"   ❌ Error initializing Claude integration: {e}")
        return False
    
    # Test 2: Health status
    print("\n2. Testing health status...")
    try:
        health = await claude_integration.get_health_status()
        print(f"   📊 Health Status: {health['status']}")
        print(f"   🔐 Authenticated: {health['authenticated']}")
        print(f"   🤖 Default Model: {health['default_model']}")
        print(f"   📈 Rate Limits: {health['rate_limits']['requests_per_minute']} req/min, {health['rate_limits']['tokens_per_minute']} tokens/min")
    except Exception as e:
        print(f"   ❌ Error getting health status: {e}")
        return False
    
    # Test 3: Send message
    print("\n3. Testing message sending...")
    try:
        response = await claude_integration.send_message(
            "Hello Claude! Please respond with exactly: 'Claude integration test successful.'"
        )
        if response:
            print(f"   ✅ Message sent successfully")
            print(f"   📝 Response: {response.content[:100]}...")
            print(f"   🤖 Model: {response.model}")
            print(f"   🔢 Tokens used: {response.tokens_used}")
            
            if "successful" in response.content.lower():
                print("   ✅ Response validation passed")
            else:
                print("   ⚠️  Response validation failed")
        else:
            print("   ❌ Failed to send message")
            return False
    except Exception as e:
        print(f"   ❌ Error sending message: {e}")
        return False
    
    return True

async def test_claude_code_generation():
    """Test Claude code generation capabilities"""
    print("\n💻 Testing Claude Code Generation...")
    
    # Test 1: Generate Python function
    print("\n1. Testing Python code generation...")
    try:
        result = await claude_integration.generate_code(
            prompt="Create a Python function that calculates the factorial of a number using recursion",
            language="python"
        )
        if result:
            print(f"   ✅ Code generation successful")
            print(f"   📝 Generated {len(result.generated_code)} characters of code")
            print(f"   🤖 Model: {result.model}")
            print(f"   🔢 Tokens used: {result.tokens_used}")
            print(f"   📖 Explanation: {result.explanation[:100]}...")
            
            # Check if code contains expected elements
            if "def" in result.generated_code and "factorial" in result.generated_code:
                print("   ✅ Code validation passed")
            else:
                print("   ⚠️  Code validation failed")
        else:
            print("   ❌ Failed to generate code")
            return False
    except Exception as e:
        print(f"   ❌ Error generating code: {e}")
        return False
    
    # Test 2: Analyze code
    print("\n2. Testing code analysis...")
    try:
        test_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
"""
        response = await claude_integration.analyze_code(
            code=test_code,
            language="python",
            analysis_type="review"
        )
        if response:
            print(f"   ✅ Code analysis successful")
            print(f"   📝 Analysis: {response.content[:100]}...")
            print(f"   🤖 Model: {response.model}")
            print(f"   🔢 Tokens used: {response.tokens_used}")
        else:
            print("   ❌ Failed to analyze code")
            return False
    except Exception as e:
        print(f"   ❌ Error analyzing code: {e}")
        return False
    
    return True

async def test_claude_advanced_features():
    """Test Claude advanced features"""
    print("\n🚀 Testing Claude Advanced Features...")
    
    # Test 1: Generate documentation
    print("\n1. Testing documentation generation...")
    try:
        test_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        response = await claude_integration.generate_documentation(
            code=test_code,
            language="python",
            doc_type="api"
        )
        if response:
            print(f"   ✅ Documentation generation successful")
            print(f"   📝 Documentation: {response.content[:100]}...")
            print(f"   🤖 Model: {response.model}")
            print(f"   🔢 Tokens used: {response.tokens_used}")
        else:
            print("   ❌ Failed to generate documentation")
            return False
    except Exception as e:
        print(f"   ❌ Error generating documentation: {e}")
        return False
    
    # Test 2: Generate tests
    print("\n2. Testing test generation...")
    try:
        test_code = """
def add_numbers(a, b):
    return a + b
"""
        result = await claude_integration.generate_tests(
            code=test_code,
            language="python",
            test_framework="pytest"
        )
        if result:
            print(f"   ✅ Test generation successful")
            print(f"   📝 Generated {len(result.generated_code)} characters of test code")
            print(f"   🤖 Model: {result.model}")
            print(f"   🔢 Tokens used: {result.tokens_used}")
            print(f"   📖 Explanation: {result.explanation[:100]}...")
            
            # Check if test code contains expected elements
            if "test_" in result.generated_code and "assert" in result.generated_code:
                print("   ✅ Test code validation passed")
            else:
                print("   ⚠️  Test code validation failed")
        else:
            print("   ❌ Failed to generate tests")
            return False
    except Exception as e:
        print(f"   ❌ Error generating tests: {e}")
        return False
    
    return True

async def test_claude_connection():
    """Test Claude API connection"""
    print("\n🔗 Testing Claude API Connection...")
    
    try:
        test_result = await claude_secret_manager.test_claude_connection()
        if test_result['success']:
            print("   ✅ Claude API connection successful")
            print(f"      • Model: {test_result.get('model', 'N/A')}")
            print(f"      • Tokens used: {test_result.get('tokens_used', 'N/A')}")
            print(f"      • Response length: {test_result.get('response_length', 'N/A')} characters")
        else:
            print(f"   ❌ Claude API connection failed: {test_result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing Claude connection: {e}")
        return False
    
    return True

def test_mcp_config():
    """Test MCP configuration"""
    print("\n⚙️  Testing MCP Configuration...")
    
    # Test 1: Check MCP config file
    print("\n1. Testing MCP config file...")
    try:
        config_path = Path("mcp_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print(f"   📄 MCP config file found")
            print(f"   🔧 Configured servers: {len(config.get('mcpServers', {}))}")
            
            if 'claude' in config.get('mcpServers', {}):
                claude_config = config['mcpServers']['claude']
                print(f"   ✅ Claude MCP server configured")
                print(f"      • Command: {claude_config.get('command')}")
                print(f"      • Args: {claude_config.get('args')}")
                print(f"      • Environment variables: {len(claude_config.get('env', {}))}")
            else:
                print(f"   ❌ Claude MCP server not found in config")
                return False
        else:
            print(f"   ❌ MCP config file not found")
            return False
    except Exception as e:
        print(f"   ❌ Error reading MCP config: {e}")
        return False
    
    return True

def test_docker_config():
    """Test Docker configuration"""
    print("\n🐳 Testing Docker Configuration...")
    
    # Test 1: Check Docker Compose file
    print("\n1. Testing Docker Compose configuration...")
    try:
        compose_path = Path("docker-compose.mcp.yml")
        if compose_path.exists():
            with open(compose_path, 'r') as f:
                content = f.read()
            
            print(f"   📄 Docker Compose file found")
            
            if 'claude:' in content:
                print(f"   ✅ Claude service configured in Docker Compose")
                if 'ANTHROPIC_API_KEY' in content:
                    print(f"      • Environment variables configured")
                if 'healthcheck:' in content:
                    print(f"      • Health checks configured")
                if 'sophia-claude-mcp' in content:
                    print(f"      • Container name configured")
            else:
                print(f"   ❌ Claude service not found in Docker Compose")
                return False
        else:
            print(f"   ❌ Docker Compose file not found")
            return False
    except Exception as e:
        print(f"   ❌ Error reading Docker Compose file: {e}")
        return False
    
    return True

async def main():
    """Main test runner"""
    print("🚀 Claude as Code Integration Test Suite")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Secret Management", test_claude_secret_management()),
        ("Claude Integration", test_claude_integration()),
        ("Code Generation", test_claude_code_generation()),
        ("Advanced Features", test_claude_advanced_features()),
        ("API Connection", test_claude_connection()),
    ]
    
    results = {}
    
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results[test_name] = result
        except Exception as e:
            print(f"   ❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Run synchronous tests
    sync_tests = [
        ("MCP Configuration", test_mcp_config()),
        ("Docker Configuration", test_docker_config()),
    ]
    
    for test_name, result in sync_tests:
        results[test_name] = result
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Claude as Code integration is ready for deployment.")
        print("\n📋 Next Steps:")
        print("1. Configure Cursor IDE with Claude MCP server")
        print("2. Test natural language commands in Cursor")
        print("3. Deploy to production environment")
        print("4. Start using Claude as Code functionality")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Check Anthropic API key configuration")
        print("2. Verify Pulumi ESC setup")
        print("3. Ensure all dependencies are installed")
        print("4. Check network connectivity")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test suite interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)

