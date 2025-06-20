#!/usr/bin/env python3
"""Linear Integration Test Script
Tests Linear MCP integration functionality
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.integrations.linear_integration import linear_integration
from infrastructure.esc.linear_secrets import linear_secret_manager


async def test_linear_integration():
    """Test Linear integration functionality"""
    print("🧪 Testing Linear Integration...")

    # Test 1: Initialize integration
    print("\n1. Testing Linear integration initialization...")
    try:
        success = await linear_integration.initialize()
        if success:
            print("   ✅ Linear integration initialized successfully")
        else:
            print(
                "   ⚠️  Linear integration initialization failed (expected without credentials)"
            )
    except Exception as e:
        print(f"   ❌ Error initializing Linear integration: {e}")

    # Test 2: Health status
    print("\n2. Testing health status...")
    try:
        health = await linear_integration.get_health_status()
        print(f"   📊 Health Status: {health['status']}")
        print(f"   🔗 MCP Server URL: {health['mcp_server_url']}")
        print(f"   🔐 Authenticated: {health['authenticated']}")
    except Exception as e:
        print(f"   ❌ Error getting health status: {e}")

    # Test 3: Mock issue creation
    print("\n3. Testing issue creation (mock)...")
    try:
        issue = await linear_integration.create_issue(
            title="Test Linear Integration",
            description="Testing Linear MCP integration for Sophia AI",
            priority="High",
            labels=["test", "mcp", "integration"],
        )
        if issue:
            print(f"   ✅ Created issue: {issue.title}")
            print(f"   🆔 Issue ID: {issue.id}")
            print(f"   🔗 URL: {issue.url}")
        else:
            print("   ❌ Failed to create issue")
    except Exception as e:
        print(f"   ❌ Error creating issue: {e}")

    # Test 4: Get issues
    print("\n4. Testing get issues...")
    try:
        issues = await linear_integration.get_issues(limit=5)
        print(f"   📋 Found {len(issues)} issues")
        for issue in issues[:2]:  # Show first 2
            print(f"      • {issue.id}: {issue.title} ({issue.status})")
    except Exception as e:
        print(f"   ❌ Error getting issues: {e}")

    # Test 5: Search issues
    print("\n5. Testing issue search...")
    try:
        search_results = await linear_integration.search_issues("integration", limit=3)
        print(f"   🔍 Found {len(search_results)} issues matching 'integration'")
        for issue in search_results:
            print(f"      • {issue.id}: {issue.title}")
    except Exception as e:
        print(f"   ❌ Error searching issues: {e}")

    # Test 6: Get projects
    print("\n6. Testing get projects...")
    try:
        projects = await linear_integration.get_projects()
        print(f"   📁 Found {len(projects)} projects")
        for project in projects:
            print(
                f"      • {project.id}: {project.name} ({project.progress}% complete)"
            )
    except Exception as e:
        print(f"   ❌ Error getting projects: {e}")

    # Test 7: Get teams
    print("\n7. Testing get teams...")
    try:
        teams = await linear_integration.get_teams()
        print(f"   👥 Found {len(teams)} teams")
        for team in teams:
            print(f"      • {team.id}: {team.name} ({len(team.members or [])} members)")
    except Exception as e:
        print(f"   ❌ Error getting teams: {e}")


async def test_secret_management():
    """Test Linear secret management"""
    print("\n🔐 Testing Linear Secret Management...")

    # Test 1: Validate configuration
    print("\n1. Testing configuration validation...")
    try:
        validation = await linear_secret_manager.validate_linear_config()
        print(f"   📋 Configuration valid: {validation['valid']}")
        if not validation["valid"]:
            print(f"   ⚠️  Error: {validation['error']}")
            if "missing_fields" in validation:
                print(f"   📝 Missing fields: {validation['missing_fields']}")
    except Exception as e:
        print(f"   ❌ Error validating configuration: {e}")

    # Test 2: Get environment variables
    print("\n2. Testing environment variable generation...")
    try:
        env_vars = await linear_secret_manager.get_environment_variables()
        print(f"   🌍 Generated {len(env_vars)} environment variables")
        for key in env_vars.keys():
            value = env_vars[key]
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"      • {key}={masked_value}")
    except Exception as e:
        print(f"   ❌ Error getting environment variables: {e}")


def test_mcp_config():
    """Test MCP configuration"""
    print("\n⚙️  Testing MCP Configuration...")

    # Test 1: Check MCP config file
    print("\n1. Testing MCP config file...")
    try:
        config_path = Path("mcp_config.json")
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)

            print("   📄 MCP config file found")
            print(f"   🔧 Configured servers: {len(config.get('mcpServers', {}))}")

            if "linear" in config.get("mcpServers", {}):
                linear_config = config["mcpServers"]["linear"]
                print("   ✅ Linear MCP server configured")
                print(f"      • Command: {linear_config.get('command')}")
                print(f"      • Args: {linear_config.get('args')}")
            else:
                print("   ❌ Linear MCP server not found in config")
        else:
            print("   ❌ MCP config file not found")
    except Exception as e:
        print(f"   ❌ Error reading MCP config: {e}")


def test_docker_config():
    """Test Docker configuration"""
    print("\n🐳 Testing Docker Configuration...")

    # Test 1: Check Docker Compose file
    print("\n1. Testing Docker Compose configuration...")
    try:
        compose_path = Path("docker-compose.mcp.yml")
        if compose_path.exists():
            with open(compose_path, "r") as f:
                content = f.read()

            print("   📄 Docker Compose file found")

            if "linear:" in content:
                print("   ✅ Linear service configured in Docker Compose")
                if "LINEAR_API_TOKEN" in content:
                    print("      • Environment variables configured")
                if "healthcheck:" in content:
                    print("      • Health checks configured")
            else:
                print("   ❌ Linear service not found in Docker Compose")
        else:
            print("   ❌ Docker Compose file not found")
    except Exception as e:
        print(f"   ❌ Error reading Docker Compose file: {e}")


async def main():
    """Main test runner"""
    print("🚀 Linear MCP Integration Test Suite")
    print("=" * 50)

    # Run all tests
    await test_linear_integration()
    await test_secret_management()
    test_mcp_config()
    test_docker_config()

    print("\n" + "=" * 50)
    print("✅ Linear MCP Integration Test Suite Complete")
    print("\n📋 Next Steps:")
    print("1. Set up Linear API credentials:")
    print("   export LINEAR_API_TOKEN=your_linear_api_token")
    print("   export LINEAR_WORKSPACE_ID=your_workspace_id")
    print("2. Run: python infrastructure/esc/linear_secrets.py")
    print("3. Configure Cursor IDE with Linear MCP server")
    print("4. Test natural language commands in Cursor")


if __name__ == "__main__":
    asyncio.run(main())
