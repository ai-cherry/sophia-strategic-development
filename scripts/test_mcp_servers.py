#!/usr/bin/env python3
"""
Test MCP Server Connections and Configuration
Validates all MCP servers can connect with Pulumi ESC configuration
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "auto_esc_config", 
    str(Path(__file__).parent.parent / "backend" / "core" / "auto_esc_config.py")
)
if spec and spec.loader:
    auto_esc_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auto_esc_module)
    EnhancedAutoESCConfig = auto_esc_module.EnhancedAutoESCConfig
else:
    raise ImportError("Failed to load auto_esc_config module")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results storage
test_results = {
    'servers': {},
    'summary': {
        'total': 0,
        'connected': 0,
        'failed': 0,
        'warnings': 0
    },
    'timestamp': datetime.utcnow().isoformat()
}


class MCPServerTester:
    """Test MCP server connections and configurations"""
    
    def __init__(self):
        self.config = EnhancedAutoESCConfig()
        self.test_timeout = 30  # seconds
        
    async def test_all_servers(self) -> Dict:
        """Test all configured MCP servers"""
        logger.info("🚀 Starting MCP Server Connection Tests...")
        
        # Generate configuration
        mcp_config = self.config.generate_mcp_json()
        servers = mcp_config.get('mcpServers', {})
        
        test_results['summary']['total'] = len(servers)
        
        # Test each server
        for server_name, server_config in servers.items():
            logger.info(f"\n📡 Testing {server_name}...")
            result = await self.test_server(server_name, server_config)
            test_results['servers'][server_name] = result
            
            # Update summary
            if result['status'] == 'connected':
                test_results['summary']['connected'] += 1
            elif result['status'] == 'failed':
                test_results['summary']['failed'] += 1
            else:
                test_results['summary']['warnings'] += 1
        
        return test_results
    
    async def test_server(self, name: str, config: Dict) -> Dict:
        """Test individual MCP server connection"""
        result = {
            'name': name,
            'status': 'unknown',
            'message': '',
            'config_valid': False,
            'env_vars_set': False,
            'connection_test': False,
            'response_time': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. Validate configuration
            logger.info(f"  ├─ Validating configuration...")
            config_validation = self.validate_server_config(name, config)
            result['config_valid'] = config_validation['valid']
            result['errors'].extend(config_validation.get('errors', []))
            result['warnings'].extend(config_validation.get('warnings', []))
            
            # 2. Check environment variables
            logger.info(f"  ├─ Checking environment variables...")
            env_check = self.check_env_vars(name, config)
            result['env_vars_set'] = env_check['valid']
            result['errors'].extend(env_check.get('errors', []))
            
            # 3. Test server startup
            logger.info(f"  ├─ Testing server startup...")
            startup_test = await self.test_server_startup(name, config)
            result['connection_test'] = startup_test['success']
            result['response_time'] = startup_test.get('response_time')
            
            if startup_test.get('error'):
                result['errors'].append(startup_test['error'])
            
            # 4. Server-specific tests
            logger.info(f"  └─ Running server-specific tests...")
            specific_test = await self.run_server_specific_tests(name, config)
            if specific_test.get('errors'):
                result['errors'].extend(specific_test['errors'])
            if specific_test.get('warnings'):
                result['warnings'].extend(specific_test['warnings'])
            
            # Determine overall status
            if result['config_valid'] and result['env_vars_set'] and result['connection_test']:
                result['status'] = 'connected'
                result['message'] = f"✅ {name} is fully operational"
                logger.info(f"  ✅ {name} passed all tests")
            elif result['config_valid'] and result['env_vars_set']:
                result['status'] = 'warning'
                result['message'] = f"⚠️  {name} configured but connection failed"
                logger.warning(f"  ⚠️  {name} has connection issues")
            else:
                result['status'] = 'failed'
                result['message'] = f"❌ {name} configuration or environment issues"
                logger.error(f"  ❌ {name} failed tests")
                
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = f"❌ {name} test failed with error"
            result['errors'].append(str(e))
            logger.error(f"  ❌ {name} test error: {e}")
        
        return result
    
    def validate_server_config(self, name: str, config: Dict) -> Dict:
        """Validate server configuration structure"""
        validation = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check required fields
        if 'command' not in config:
            validation['valid'] = False
            validation['errors'].append("Missing 'command' field")
        
        if 'args' not in config:
            validation['valid'] = False
            validation['errors'].append("Missing 'args' field")
        
        # Check environment variables
        env = config.get('env', {})
        
        # Server-specific validation
        if name == 'gong':
            required_vars = ['GONG_ACCESS_KEY', 'GONG_ACCESS_KEY_SECRET']
            for var in required_vars:
                if var not in env or not env[var]:
                    validation['valid'] = False
                    validation['errors'].append(f"Missing required {var}")
                    
        elif name == 'qdrant':
            if 'QDRANT_API_KEY' not in env:
                validation['valid'] = False
                validation['errors'].append("Missing QDRANT_API_KEY")
                
        elif name == 'lambda-labs':
            if 'LAMBDA_LABS_API_KEY' not in env:
                validation['warnings'].append("LAMBDA_LABS_API_KEY might be missing")
        
        # Generic API key check
        api_key_found = any(
            'api_key' in k.lower() or 
            'access_token' in k.lower() or 
            'token' in k.lower() 
            for k in env.keys()
        )
        
        if not api_key_found and name not in ['github']:
            validation['warnings'].append("No API key or token found in environment")
        
        return validation
    
    def check_env_vars(self, name: str, config: Dict) -> Dict:
        """Check if environment variables are properly set"""
        check = {'valid': True, 'errors': []}
        env = config.get('env', {})
        
        for var_name, var_value in env.items():
            if not var_value:
                check['valid'] = False
                check['errors'].append(f"{var_name} is empty")
            elif var_value.startswith('PLACEHOLDER'):
                check['valid'] = False
                check['errors'].append(f"{var_name} still has placeholder value")
            elif len(var_value) < 10 and 'endpoint' not in var_name.lower():
                check['errors'].append(f"{var_name} seems too short for a valid key")
        
        return check
    
    async def test_server_startup(self, name: str, config: Dict) -> Dict:
        """Test if server can start successfully"""
        startup = {'success': False, 'response_time': None, 'error': None}
        
        try:
            # Build command
            cmd = [config['command']] + config.get('args', [])
            env = {**config.get('env', {})}
            
            # Add test flag if supported
            if name in ['gong', 'slack', 'hubspot']:
                cmd.append('--test')
            
            # Start server process
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                cmd[0],
                *cmd[1:],
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup (with timeout)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=5.0
                )
                
                startup['response_time'] = time.time() - start_time
                
                # Check for success indicators
                if process.returncode == 0:
                    startup['success'] = True
                elif stderr:
                    error_msg = stderr.decode('utf-8')
                    if 'ModuleNotFoundError' in error_msg:
                        startup['error'] = "MCP server module not installed"
                    elif 'authentication' in error_msg.lower():
                        startup['error'] = "Authentication failed - check API keys"
                    else:
                        startup['error'] = f"Server error: {error_msg[:200]}"
                        
            except asyncio.TimeoutError:
                # Some servers don't exit, which is actually good
                startup['success'] = True
                startup['response_time'] = 5.0
                process.terminate()
                
        except FileNotFoundError:
            startup['error'] = f"Command not found: {config['command']}"
        except Exception as e:
            startup['error'] = f"Startup test failed: {str(e)}"
        
        return startup
    
    async def run_server_specific_tests(self, name: str, config: Dict) -> Dict:
        """Run server-specific connection tests"""
        specific = {'errors': [], 'warnings': []}
        
        if name == 'gong':
            # Check if we can import the Gong client
            try:
                import importlib
                importlib.import_module('mcp_servers.gong')
            except ImportError:
                specific['errors'].append("Gong MCP server module not found")
                
        elif name == 'qdrant':
            # Check Qdrant connection
            try:
                from qdrant_client import QdrantClient
                
                api_key = config.get('env', {}).get('QDRANT_API_KEY')
                url = config.get('env', {}).get('QDRANT_URL', 'https://cloud.qdrant.io')
                
                if api_key:
                    client = QdrantClient(url=url, api_key=api_key)
                    # Try a simple operation
                    try:
                        collections = client.get_collections()
                        specific['warnings'].append(f"Connected to Qdrant - {len(collections.collections)} collections found")
                    except Exception as e:
                        error_msg = str(e)
                        if 'unauthorized' in error_msg.lower() or '401' in error_msg:
                            specific['errors'].append("Qdrant authentication failed")
                        else:
                            specific['errors'].append(f"Qdrant connection error: {error_msg}")
            except ImportError:
                specific['errors'].append("qdrant-client not installed")
                
        elif name == 'redis':
            # Check Redis connection
            try:
                import redis
                # Import get_redis_config from the parent module
                from backend.core.auto_esc_config import get_redis_config
                redis_config = get_redis_config()
                
                r = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    password=redis_config.get('password'),
                    socket_connect_timeout=5
                )
                
                # Test connection
                r.ping()
                specific['warnings'].append("Redis connection successful")
            except ImportError as e:
                specific['errors'].append(f"Redis module not installed: {str(e)}")
            except Exception as e:
                specific['errors'].append(f"Redis connection failed: {str(e)}")
        
        return specific


def generate_health_dashboard(results: Dict) -> str:
    """Generate a health check dashboard"""
    dashboard = []
    
    # Header
    dashboard.append("# 📊 MCP Server Health Check Dashboard")
    dashboard.append(f"\n**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    dashboard.append(f"**Environment:** Production (Pulumi ESC)")
    
    # Summary
    summary = results['summary']
    dashboard.append("\n## 📈 Summary")
    dashboard.append(f"- **Total Servers:** {summary['total']}")
    dashboard.append(f"- **✅ Connected:** {summary['connected']}")
    dashboard.append(f"- **❌ Failed:** {summary['failed']}")
    dashboard.append(f"- **⚠️  Warnings:** {summary['warnings']}")
    
    # Success rate
    if summary['total'] > 0:
        success_rate = (summary['connected'] / summary['total']) * 100
        dashboard.append(f"- **Success Rate:** {success_rate:.1f}%")
    
    # Detailed Results
    dashboard.append("\n## 🔍 Detailed Results\n")
    
    # Sort servers by status
    servers_by_status = {
        'connected': [],
        'warning': [],
        'failed': []
    }
    
    for server_name, result in results['servers'].items():
        servers_by_status[result['status']].append((server_name, result))
    
    # Connected servers
    if servers_by_status['connected']:
        dashboard.append("### ✅ Connected Servers\n")
        for name, result in servers_by_status['connected']:
            response_time = result.get('response_time', 0)
            dashboard.append(f"- **{name}** - Response time: {response_time:.2f}s")
    
    # Warning servers
    if servers_by_status['warning']:
        dashboard.append("\n### ⚠️  Servers with Warnings\n")
        for name, result in servers_by_status['warning']:
            dashboard.append(f"- **{name}** - {result['message']}")
            for warning in result.get('warnings', []):
                dashboard.append(f"  - ⚠️  {warning}")
    
    # Failed servers
    if servers_by_status['failed']:
        dashboard.append("\n### ❌ Failed Servers\n")
        for name, result in servers_by_status['failed']:
            dashboard.append(f"- **{name}** - {result['message']}")
            for error in result.get('errors', []):
                dashboard.append(f"  - ❌ {error}")
    
    # Configuration Issues
    dashboard.append("\n## 🔧 Configuration Issues\n")
    
    config_issues = []
    for server_name, result in results['servers'].items():
        if not result['config_valid'] or not result['env_vars_set']:
            config_issues.append((server_name, result))
    
    if config_issues:
        for name, result in config_issues:
            dashboard.append(f"### {name}")
            if not result['config_valid']:
                dashboard.append("- **Configuration:** ❌ Invalid")
            if not result['env_vars_set']:
                dashboard.append("- **Environment Variables:** ❌ Missing or invalid")
            for error in result.get('errors', []):
                dashboard.append(f"- {error}")
    else:
        dashboard.append("✅ No configuration issues found!")
    
    # Recommended Actions
    dashboard.append("\n## 🛠️ Recommended Actions\n")
    
    if servers_by_status['failed']:
        dashboard.append("### For Failed Servers:")
        dashboard.append("1. Check API keys in Pulumi ESC / GitHub Organization Secrets")
        dashboard.append("2. Verify server modules are installed: `pip install -r requirements.txt`")
        dashboard.append("3. Run validation: `python scripts/utils/generate_mcp_config.py --validate`")
        dashboard.append("4. Check server-specific documentation")
    
    if servers_by_status['warning']:
        dashboard.append("\n### For Servers with Warnings:")
        dashboard.append("1. Review warning messages above")
        dashboard.append("2. Test individual servers manually")
        dashboard.append("3. Check network connectivity and firewall rules")
    
    # Connection Metrics
    dashboard.append("\n## 📊 Connection Metrics\n")
    
    # Calculate average response time
    response_times = [
        r['response_time'] for r in results['servers'].values() 
        if r.get('response_time') is not None
    ]
    
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        dashboard.append(f"- **Average Response Time:** {avg_response:.2f}s")
        dashboard.append(f"- **Fastest Server:** {min(response_times):.2f}s")
        dashboard.append(f"- **Slowest Server:** {max(response_times):.2f}s")
    
    return "\n".join(dashboard)


async def main():
    """Main test function"""
    print("🚀 MCP Server Connection Tester")
    print("================================\n")
    
    # Create tester
    tester = MCPServerTester()
    
    # Run tests
    results = await tester.test_all_servers()
    
    # Generate dashboard
    dashboard = generate_health_dashboard(results)
    
    # Print dashboard
    print("\n" + dashboard)
    
    # Save results
    with open('mcp_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: mcp_test_results.json")
    
    # Save dashboard
    with open('mcp_health_dashboard.md', 'w') as f:
        f.write(dashboard)
    
    print(f"📄 Dashboard saved to: mcp_health_dashboard.md")
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        print(f"\n❌ {results['summary']['failed']} servers failed tests")
        sys.exit(1)
    elif results['summary']['warnings'] > 0:
        print(f"\n⚠️  {results['summary']['warnings']} servers have warnings")
        sys.exit(0)
    else:
        print(f"\n✅ All {results['summary']['total']} servers passed tests!")
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
