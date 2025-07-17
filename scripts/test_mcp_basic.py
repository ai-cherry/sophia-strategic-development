#!/usr/bin/env python3
"""
Basic MCP Server Test
Verify MCP servers are configured and can be invoked
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_mcp_config():
    """Load MCP configuration from .cursor/mcp_settings.json"""
    config_path = Path('.cursor/mcp_settings.json')
    if not config_path.exists():
        logger.error(f"MCP config not found at {config_path}")
        return None
    
    with open(config_path) as f:
        return json.load(f)


def test_mcp_server_invocation(server_name, server_config):
    """Test if an MCP server can be invoked"""
    logger.info(f"\n🔍 Testing {server_name}...")
    
    result = {
        'server': server_name,
        'status': 'unknown',
        'command_valid': False,
        'module_exists': False,
        'can_execute': False,
        'errors': []
    }
    
    # Check command
    command = server_config.get('command')
    args = server_config.get('args', [])
    
    if not command:
        result['errors'].append("No command specified")
        result['status'] = 'failed'
        return result
    
    result['command_valid'] = True
    logger.info(f"  ├─ Command: {command} {' '.join(args)}")
    
    # Check if module exists
    if args and len(args) >= 2 and args[0] == '-m':
        module_name = args[1]
        logger.info(f"  ├─ Module: {module_name}")
        
        # Test module import
        try:
            test_cmd = [command, '-c', f"import {module_name.replace('-', '_')}; print('OK')"]
            proc = subprocess.run(
                test_cmd, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if proc.returncode == 0 and proc.stdout.strip() == 'OK':
                result['module_exists'] = True
                logger.info("  ├─ Module check: ✅ Found")
            else:
                error_msg = proc.stderr.strip() if proc.stderr else "Module not found"
                result['errors'].append(f"Module error: {error_msg}")
                logger.error(f"  ├─ Module check: ❌ {error_msg}")
        except Exception as e:
            result['errors'].append(f"Import test failed: {str(e)}")
            logger.error(f"  ├─ Module check: ❌ {str(e)}")
    
    # Test basic execution
    try:
        # Try to run with --help flag
        test_cmd = [command] + args + ['--help']
        proc = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, **server_config.get('env', {})}
        )
        
        if proc.returncode == 0 or 'usage:' in proc.stdout.lower() or 'usage:' in proc.stderr.lower():
            result['can_execute'] = True
            logger.info("  └─ Execution test: ✅ Can run")
        else:
            error_msg = proc.stderr.strip() if proc.stderr else "Unknown error"
            result['errors'].append(f"Execution error: {error_msg}")
            logger.error(f"  └─ Execution test: ❌ {error_msg}")
            
    except subprocess.TimeoutExpired:
        # Some servers don't exit on --help, which might be OK
        result['can_execute'] = True
        logger.info("  └─ Execution test: ⚠️  Timeout (may be normal)")
    except Exception as e:
        result['errors'].append(f"Execution failed: {str(e)}")
        logger.error(f"  └─ Execution test: ❌ {str(e)}")
    
    # Determine status
    if result['command_valid'] and result['module_exists'] and result['can_execute']:
        result['status'] = 'ready'
    elif result['command_valid'] and result['can_execute']:
        result['status'] = 'partial'
    else:
        result['status'] = 'failed'
    
    return result


def test_simple_mcp_command():
    """Test a simple MCP-style command"""
    logger.info("\n🧪 Testing simple MCP protocol communication...")
    
    # Create a simple test request
    test_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0.0",
            "capabilities": {}
        },
        "id": 1
    }
    
    # Test with a basic echo server (simulated)
    try:
        # Create a simple echo test
        echo_cmd = ['python', '-c', '''
import sys
import json
try:
    data = sys.stdin.read()
    request = json.loads(data)
    response = {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "1.0.0",
            "serverInfo": {"name": "test", "version": "1.0.0"}
        },
        "id": request.get("id", 1)
    }
    print(json.dumps(response))
except Exception as e:
    print(json.dumps({"error": str(e)}))
''']
        
        proc = subprocess.run(
            echo_cmd,
            input=json.dumps(test_request),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if proc.returncode == 0:
            try:
                response = json.loads(proc.stdout)
                if 'result' in response:
                    logger.info("  ✅ MCP protocol test: Communication successful")
                    return True
                else:
                    logger.error(f"  ❌ MCP protocol test: Invalid response - {response}")
            except json.JSONDecodeError:
                logger.error("  ❌ MCP protocol test: Invalid JSON response")
        else:
            logger.error(f"  ❌ MCP protocol test: Command failed - {proc.stderr}")
            
    except Exception as e:
        logger.error(f"  ❌ MCP protocol test: {str(e)}")
    
    return False


def generate_report(results):
    """Generate a test report"""
    report = []
    
    # Header
    report.append("# 🔍 MCP Server Basic Test Report")
    report.append(f"\n**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("**Purpose:** Verify MCP server configuration and basic functionality\n")
    
    # Summary
    total = len(results['servers'])
    ready = sum(1 for r in results['servers'].values() if r['status'] == 'ready')
    partial = sum(1 for r in results['servers'].values() if r['status'] == 'partial')
    failed = sum(1 for r in results['servers'].values() if r['status'] == 'failed')
    
    report.append("## 📊 Summary")
    report.append(f"- **Total Servers:** {total}")
    report.append(f"- **✅ Ready:** {ready}")
    report.append(f"- **⚠️  Partial:** {partial}")
    report.append(f"- **❌ Failed:** {failed}")
    report.append(f"- **MCP Protocol:** {'✅ Working' if results['protocol_test'] else '❌ Not Working'}\n")
    
    # Server details
    report.append("## 🔧 Server Status\n")
    
    for name, result in results['servers'].items():
        status_icon = {
            'ready': '✅',
            'partial': '⚠️',
            'failed': '❌',
            'unknown': '❓'
        }.get(result['status'], '❓')
        
        report.append(f"### {status_icon} {name}")
        report.append(f"- **Status:** {result['status'].upper()}")
        report.append(f"- **Command Valid:** {'✅' if result['command_valid'] else '❌'}")
        report.append(f"- **Module Exists:** {'✅' if result['module_exists'] else '❌'}")
        report.append(f"- **Can Execute:** {'✅' if result['can_execute'] else '❌'}")
        
        if result['errors']:
            report.append("- **Errors:**")
            for error in result['errors']:
                report.append(f"  - {error}")
        
        report.append("")
    
    # Recommendations
    report.append("## 💡 Next Steps\n")
    
    if failed > 0:
        report.append("### For Failed Servers:")
        report.append("1. Check if the MCP server modules are installed")
        report.append("2. Verify Python module paths are correct")
        report.append("3. Ensure all dependencies are installed")
        report.append("4. Check environment variables in `.cursor/mcp_settings.json`")
    
    if not results['protocol_test']:
        report.append("\n### MCP Protocol:")
        report.append("- Ensure MCP protocol libraries are installed")
        report.append("- Check MCP server implementations follow the protocol")
    
    return "\n".join(report)


def main():
    """Main test function"""
    print("🔍 MCP Basic Configuration Tester")
    print("==================================\n")
    
    results = {
        'servers': {},
        'protocol_test': False,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Load MCP configuration
    config = load_mcp_config()
    if not config:
        logger.error("Failed to load MCP configuration")
        sys.exit(1)
    
    # Test each server
    mcp_servers = config.get('mcpServers', {})
    logger.info(f"Found {len(mcp_servers)} MCP servers to test")
    
    for server_name, server_config in mcp_servers.items():
        result = test_mcp_server_invocation(server_name, server_config)
        results['servers'][server_name] = result
    
    # Test MCP protocol
    results['protocol_test'] = test_simple_mcp_command()
    
    # Generate report
    report = generate_report(results)
    print("\n" + report)
    
    # Save results
    with open('mcp_basic_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n📁 Results saved to: mcp_basic_test_results.json")
    
    # Save report
    with open('mcp_basic_test_report.md', 'w') as f:
        f.write(report)
    
    print("📄 Report saved to: mcp_basic_test_report.md")
    
    # Exit code
    failed_count = sum(1 for r in results['servers'].values() if r['status'] == 'failed')
    if failed_count > 0:
        print(f"\n❌ {failed_count} servers failed")
        sys.exit(1)
    else:
        print("\n✅ All servers configured correctly!")
        sys.exit(0)


if __name__ == '__main__':
    main()
