#!/usr/bin/env python3
"""
Audit MCP Servers
Identifies which MCP servers use custom shim vs official SDK

Date: July 9, 2025
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class MCPServerAuditor:
    """Audits MCP server implementations"""
    
    def __init__(self):
        self.mcp_servers_dir = Path("mcp-servers")
        self.results = {
            "official_sdk": [],
            "custom_shim": [],
            "unknown": [],
            "missing": []
        }
        
    def audit_all_servers(self) -> Dict:
        """Audit all MCP servers"""
        print("🔍 MCP Server Implementation Audit")
        print("=" * 60)
        
        # Expected servers from sophia_mcp_unified.yaml
        expected_servers = [
            "ai_memory", "snowflake_unified", "gong_v2", "hubspot_unified",
            "slack_v2", "github_v2", "linear_v2", "asana_v2", "notion_v2",
            "codacy", "portkey_admin", "postgres", "figma_context",
            "lambda_labs_cli", "ui_ux_agent", "openrouter_search"
        ]
        
        # Check each expected server
        for server_name in expected_servers:
            self._audit_server(server_name)
            
        # Print results
        self._print_results()
        
        return self.results
    
    def _audit_server(self, server_name: str):
        """Audit a single server"""
        # Look for server directory
        server_dir = self.mcp_servers_dir / server_name
        
        if not server_dir.exists():
            # Try alternative names
            alt_names = [
                server_name.replace("_v2", ""),
                server_name.replace("_", "-"),
                server_name + "_server"
            ]
            
            for alt_name in alt_names:
                alt_dir = self.mcp_servers_dir / alt_name
                if alt_dir.exists():
                    server_dir = alt_dir
                    break
        
        if not server_dir.exists():
            self.results["missing"].append(server_name)
            return
            
        # Look for Python files
        py_files = list(server_dir.glob("*.py"))
        
        if not py_files:
            self.results["unknown"].append((server_name, "No Python files found"))
            return
            
        # Check implementation
        implementation = self._check_implementation(py_files)
        
        if implementation == "official":
            self.results["official_sdk"].append(server_name)
        elif implementation == "shim":
            self.results["custom_shim"].append(server_name)
        else:
            self.results["unknown"].append((server_name, implementation))
    
    def _check_implementation(self, py_files: List[Path]) -> str:
        """Check which implementation is used"""
        official_patterns = [
            r"from anthropic_mcp import",
            r"from external\.anthropic[_-]mcp[_-]python[_-]sdk",
            r"from mcp_servers\.base\.unified_standardized_base import",
            r"import anthropic_mcp"
        ]
        
        shim_patterns = [
            r"from backend\.mcp\.shim import",
            r"from backend\.mcp import shim",
            r"import backend\.mcp\.shim",
            r"ShimmedMCPServer"
        ]
        
        for py_file in py_files:
            try:
                content = py_file.read_text()
                
                # Check for official SDK patterns
                for pattern in official_patterns:
                    if re.search(pattern, content):
                        return "official"
                
                # Check for custom shim patterns
                for pattern in shim_patterns:
                    if re.search(pattern, content):
                        return "shim"
                        
            except Exception as e:
                continue
                
        # Check for FastAPI patterns (likely custom implementation)
        for py_file in py_files:
            try:
                content = py_file.read_text()
                if "from fastapi import" in content or "FastAPI()" in content:
                    return "shim (FastAPI-based)"
            except:
                continue
                
        return "Unable to determine"
    
    def _print_results(self):
        """Print audit results"""
        total = sum([
            len(self.results["official_sdk"]),
            len(self.results["custom_shim"]),
            len(self.results["unknown"]),
            len(self.results["missing"])
        ])
        
        print(f"\n📊 Audit Summary (Total Expected: {total})")
        print("-" * 60)
        
        print(f"\n✅ Using Official SDK ({len(self.results['official_sdk'])})")
        for server in sorted(self.results["official_sdk"]):
            print(f"  - {server}")
            
        print(f"\n⚠️  Using Custom Shim ({len(self.results['custom_shim'])})")
        for server in sorted(self.results["custom_shim"]):
            print(f"  - {server}")
            
        print(f"\n❓ Unknown Implementation ({len(self.results['unknown'])})")
        for server, reason in sorted(self.results["unknown"]):
            print(f"  - {server}: {reason}")
            
        print(f"\n❌ Missing Servers ({len(self.results['missing'])})")
        for server in sorted(self.results["missing"]):
            print(f"  - {server}")
            
        # Recommendations
        print("\n" + "=" * 60)
        print("📋 Recommendations:")
        
        if self.results["custom_shim"]:
            print(f"\n1. Migrate {len(self.results['custom_shim'])} servers from custom shim to official SDK")
            
        if self.results["missing"]:
            print(f"\n2. Investigate {len(self.results['missing'])} missing servers")
            print("   - May be in different locations")
            print("   - May need to be created")
            
        if self.results["unknown"]:
            print(f"\n3. Clarify implementation for {len(self.results['unknown'])} servers")
            
        # Priority order
        if self.results["custom_shim"]:
            print("\n🎯 Migration Priority Order:")
            # Start with least critical
            priority_order = ["ui_ux_agent", "figma_context", "openrouter_search", 
                            "lambda_labs_cli", "codacy", "postgres", "portkey_admin",
                            "notion_v2", "asana_v2", "linear_v2", "github_v2",
                            "slack_v2", "hubspot_unified", "gong_v2", 
                            "snowflake_unified", "ai_memory"]
            
            for i, server in enumerate(priority_order):
                if server in self.results["custom_shim"]:
                    print(f"  {i+1}. {server}")
                    
def main():
    """Run the audit"""
    auditor = MCPServerAuditor()
    results = auditor.audit_all_servers()
    
    # Save results
    import json
    with open("mcp_server_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full results saved to: mcp_server_audit_results.json")


if __name__ == "__main__":
    main() 