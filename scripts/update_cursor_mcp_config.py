#!/usr/bin/env python3
"""
Update Cursor MCP Configuration
Automatically update cursor_mcp_config.json with optimizations
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CursorMCPConfigUpdater:
    """Update and optimize Cursor MCP configuration"""
    
    def __init__(self, config_file: str = "cursor_mcp_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load existing configuration"""
        if not self.config_file.exists():
            logger.info("Creating new cursor_mcp_config.json")
            return {"mcpServers": {}}
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"✅ Configuration saved to {self.config_file}")
    
    def update_ai_memory_server(self):
        """Update AI Memory MCP server configuration"""
        ai_memory_config = {
            "command": "python",
            "args": ["-m", "backend.mcp.ai_memory_mcp_server"],
            "env": {
                "PULUMI_ORG": "scoobyjava-org",
                "PULUMI_STACK": "sophia-ai-production"
            },
            "capabilities": {
                "semantic_search": True,
                "auto_discovery": True,
                "context_awareness": True,
                "intelligent_categorization": True
            },
            "auto_triggers": {
                "on_file_save": True,
                "on_commit": True,
                "on_branch_switch": True,
                "on_architecture_discussion": True
            },
            "workflow_automation": {
                "auto_store_context": True,
                "smart_recall": True,
                "file_specific_memory": True,
                "pattern_recognition": True
            },
            "performance": {
                "cache_enabled": True,
                "batch_operations": True,
                "async_processing": True
            }
        }
        
        self.config["mcpServers"]["ai_memory"] = ai_memory_config
        logger.info("✅ Updated AI Memory server configuration")
    
    def update_codacy_server(self):
        """Update Codacy MCP server configuration"""
        codacy_config = {
            "command": "python",
            "args": ["-m", "mcp-servers.codacy.codacy_mcp_server"],
            "capabilities": {
                "real_time_analysis": True,
                "security_scanning": True,
                "ast_analysis": True,
                "quality_metrics": True,
                "fix_suggestions": True
            },
            "auto_triggers": {
                "on_file_save": True,
                "on_code_change": True,
                "on_security_review": True
            },
            "analysis_settings": {
                "complexity_threshold": 10,
                "security_level": "strict",
                "style_checking": True,
                "performance_analysis": True
            },
            "integration": {
                "github_integration": True,
                "pr_comments": True,
                "automated_fixes": False
            }
        }
        
        self.config["mcpServers"]["codacy"] = codacy_config
        logger.info("✅ Updated Codacy server configuration")
    
    def update_snowflake_admin_server(self):
        """Update Snowflake Admin MCP server configuration"""
        snowflake_admin_config = {
            "command": "python",
            "args": ["-m", "mcp-servers.snowflake_admin.snowflake_admin_mcp_server"],
            "env": {
                "PULUMI_ORG": "scoobyjava-org",
                "PULUMI_STACK": "sophia-ai-production"
            },
            "capabilities": {
                "sql_agent": True,
                "multi_environment": True,
                "safety_checks": True,
                "natural_language": True
            },
            "security": {
                "dangerous_operation_detection": True,
                "confirmation_required": True,
                "environment_restrictions": True,
                "audit_logging": True
            },
            "environments": {
                "dev": {
                    "restrictions": "minimal",
                    "confirmation_required": False
                },
                "staging": {
                    "restrictions": "moderate",
                    "confirmation_required": True
                },
                "production": {
                    "restrictions": "strict",
                    "confirmation_required": True,
                    "read_only": True
                }
            }
        }
        
        self.config["mcpServers"]["snowflake_admin"] = snowflake_admin_config
        logger.info("✅ Updated Snowflake Admin server configuration")
    
    def update_asana_server(self):
        """Update Asana MCP server configuration"""
        asana_config = {
            "command": "python",
            "args": ["-m", "mcp-servers.asana.asana_mcp_server"],
            "env": {
                "PULUMI_ORG": "scoobyjava-org",
                "PULUMI_STACK": "sophia-ai-production"
            },
            "capabilities": {
                "task_management": True,
                "project_tracking": True,
                "team_collaboration": True,
                "progress_monitoring": True
            },
            "integration": {
                "github_issues": True,
                "development_workflow": True,
                "automated_updates": True
            }
        }
        
        self.config["mcpServers"]["asana"] = asana_config
        logger.info("✅ Updated Asana server configuration")
    
    def update_notion_server(self):
        """Update Notion MCP server configuration"""
        notion_config = {
            "command": "python",
            "args": ["-m", "mcp-servers.notion.notion_mcp_server"],
            "env": {
                "PULUMI_ORG": "scoobyjava-org",
                "PULUMI_STACK": "sophia-ai-production"
            },
            "capabilities": {
                "document_management": True,
                "knowledge_base": True,
                "project_documentation": True,
                "team_wiki": True
            },
            "auto_triggers": {
                "on_architecture_decision": True,
                "on_documentation_update": True,
                "on_project_milestone": True
            }
        }
        
        self.config["mcpServers"]["notion"] = notion_config
        logger.info("✅ Updated Notion server configuration")
    
    def add_github_integration_settings(self):
        """Add GitHub integration specific settings"""
        github_settings = {
            "github_integration": {
                "auto_sync": True,
                "branch_awareness": True,
                "pr_integration": True,
                "issue_linking": True,
                "workflow_triggers": {
                    "on_push": ["ai_memory", "codacy"],
                    "on_pr": ["codacy", "ai_memory"],
                    "on_branch_switch": ["ai_memory"],
                    "on_commit": ["ai_memory", "codacy"]
                }
            }
        }
        
        self.config.update(github_settings)
        logger.info("✅ Added GitHub integration settings")
    
    def add_cursor_optimizations(self):
        """Add Cursor-specific optimizations"""
        cursor_optimizations = {
            "cursor_optimizations": {
                "intelligent_code_completion": True,
                "context_aware_suggestions": True,
                "ai_powered_refactoring": True,
                "automated_documentation": True,
                "smart_error_handling": True,
                "performance_monitoring": True
            },
            "development_workflow": {
                "auto_format_on_save": True,
                "lint_on_change": True,
                "test_on_commit": True,
                "security_scan_on_pr": True
            },
            "ai_assistance": {
                "natural_language_commands": True,
                "contextual_help": True,
                "code_explanation": True,
                "optimization_suggestions": True
            }
        }
        
        self.config.update(cursor_optimizations)
        logger.info("✅ Added Cursor optimizations")
    
    def add_performance_settings(self):
        """Add performance optimization settings"""
        performance_settings = {
            "performance": {
                "connection_pooling": True,
                "request_batching": True,
                "async_operations": True,
                "caching": {
                    "enabled": True,
                    "ttl": 300,
                    "max_size": 1000
                },
                "timeouts": {
                    "connection": 10,
                    "request": 30,
                    "keepalive": 60
                }
            }
        }
        
        self.config.update(performance_settings)
        logger.info("✅ Added performance settings")
    
    def add_monitoring_settings(self):
        """Add monitoring and logging settings"""
        monitoring_settings = {
            "monitoring": {
                "health_checks": True,
                "performance_metrics": True,
                "error_tracking": True,
                "usage_analytics": True
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "correlation_ids": True,
                "structured_logging": True
            }
        }
        
        self.config.update(monitoring_settings)
        logger.info("✅ Added monitoring settings")
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return issues"""
        issues = []
        
        # Check required servers
        required_servers = ["ai_memory", "codacy", "snowflake_admin"]
        for server in required_servers:
            if server not in self.config.get("mcpServers", {}):
                issues.append(f"Missing required server: {server}")
        
        # Check server configurations
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            if "command" not in server_config:
                issues.append(f"Server {server_name} missing command")
            
            if "args" not in server_config:
                issues.append(f"Server {server_name} missing args")
        
        # Check GitHub integration
        if "github_integration" not in self.config:
            issues.append("Missing GitHub integration settings")
        
        # Check performance settings
        if "performance" not in self.config:
            issues.append("Missing performance settings")
        
        return issues
    
    def optimize_for_development(self):
        """Optimize configuration for development environment"""
        dev_optimizations = {
            "development": {
                "auto_reload": True,
                "debug_mode": True,
                "verbose_logging": True,
                "fast_feedback": True
            }
        }
        
        self.config.update(dev_optimizations)
        
        # Enable more aggressive auto-triggers for development
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            if "auto_triggers" in server_config:
                server_config["auto_triggers"]["on_file_change"] = True
                server_config["auto_triggers"]["on_save"] = True
        
        logger.info("✅ Applied development optimizations")
    
    def optimize_for_production(self):
        """Optimize configuration for production environment"""
        prod_optimizations = {
            "production": {
                "auto_reload": False,
                "debug_mode": False,
                "verbose_logging": False,
                "performance_priority": True
            }
        }
        
        self.config.update(prod_optimizations)
        
        # Reduce auto-triggers for production
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            if "auto_triggers" in server_config:
                server_config["auto_triggers"]["on_file_change"] = False
                server_config["auto_triggers"]["on_save"] = False
        
        logger.info("✅ Applied production optimizations")
    
    def generate_configuration_report(self) -> str:
        """Generate configuration report"""
        report = []
        report.append("# 🔧 Cursor MCP Configuration Report")
        report.append("")
        
        # Server Summary
        servers = self.config.get("mcpServers", {})
        report.append(f"## 📊 Server Summary ({len(servers)} servers)")
        for server_name in servers.keys():
            report.append(f"- ✅ {server_name}")
        report.append("")
        
        # Feature Summary
        report.append("## 🚀 Features Enabled")
        
        if self.config.get("github_integration", {}).get("auto_sync"):
            report.append("- ✅ GitHub Integration")
        
        if self.config.get("cursor_optimizations", {}).get("intelligent_code_completion"):
            report.append("- ✅ Cursor Optimizations")
        
        if self.config.get("performance", {}).get("caching", {}).get("enabled"):
            report.append("- ✅ Performance Caching")
        
        if self.config.get("monitoring", {}).get("health_checks"):
            report.append("- ✅ Health Monitoring")
        
        report.append("")
        
        # Validation Results
        issues = self.validate_configuration()
        if issues:
            report.append("## ⚠️ Configuration Issues")
            for issue in issues:
                report.append(f"- ❌ {issue}")
        else:
            report.append("## ✅ Configuration Valid")
            report.append("All configuration checks passed!")
        
        report.append("")
        
        # Recommendations
        report.append("## 🎯 Recommendations")
        report.append("- Regularly update server configurations")
        report.append("- Monitor server performance and health")
        report.append("- Test configuration changes in development first")
        report.append("- Keep GitHub integration settings up to date")
        
        return "\n".join(report)
    
    def update_all_servers(self):
        """Update all MCP server configurations"""
        logger.info("🔄 Updating all MCP server configurations")
        
        self.update_ai_memory_server()
        self.update_codacy_server()
        self.update_snowflake_admin_server()
        self.update_asana_server()
        self.update_notion_server()
        
        self.add_github_integration_settings()
        self.add_cursor_optimizations()
        self.add_performance_settings()
        self.add_monitoring_settings()
        
        logger.info("✅ All server configurations updated")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Cursor MCP Configuration")
    parser.add_argument("--config", default="cursor_mcp_config.json", help="Config file path")
    parser.add_argument("--server", help="Update specific server only")
    parser.add_argument("--environment", choices=["development", "production"], 
                       help="Optimize for specific environment")
    parser.add_argument("--validate", action="store_true", help="Validate configuration only")
    parser.add_argument("--report", action="store_true", help="Generate configuration report")
    
    args = parser.parse_args()
    
    try:
        updater = CursorMCPConfigUpdater(args.config)
        
        if args.validate:
            issues = updater.validate_configuration()
            if issues:
                print("❌ Configuration Issues:")
                for issue in issues:
                    print(f"  - {issue}")
                return 1
            else:
                print("✅ Configuration is valid!")
                return 0
        
        if args.report:
            report = updater.generate_configuration_report()
            print(report)
            return 0
        
        if args.server:
            # Update specific server
            if args.server == "ai_memory":
                updater.update_ai_memory_server()
            elif args.server == "codacy":
                updater.update_codacy_server()
            elif args.server == "snowflake_admin":
                updater.update_snowflake_admin_server()
            elif args.server == "asana":
                updater.update_asana_server()
            elif args.server == "notion":
                updater.update_notion_server()
            else:
                logger.error(f"Unknown server: {args.server}")
                return 1
        else:
            # Update all servers
            updater.update_all_servers()
        
        # Apply environment-specific optimizations
        if args.environment == "development":
            updater.optimize_for_development()
        elif args.environment == "production":
            updater.optimize_for_production()
        
        # Save configuration
        updater._save_config()
        
        # Validate final configuration
        issues = updater.validate_configuration()
        if issues:
            logger.warning("⚠️ Configuration has issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ Configuration updated and validated successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Failed to update configuration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 