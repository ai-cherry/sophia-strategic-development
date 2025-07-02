#!/usr/bin/env python3
"""
Strategic Repository Expansion Script
Adds high-value repositories for future AI coding assistance
"""

import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategicRepositoryExpander:
    """Expands external repository collection strategically"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.external_dir = self.repo_root / "external"
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd: List[str], cwd: str = None) -> bool:
        """Run a command and return success status"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.repo_root,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                self.log(f"Command failed: {' '.join(cmd)}", "ERROR")
                self.log(f"Error: {result.stderr}", "ERROR")
                return False
            return True
        except Exception as e:
            self.log(f"Exception running command: {e}", "ERROR")
            return False
    
    def add_strategic_repositories(self):
        """Add strategic repositories for future AI coding assistance"""
        self.log("🚀 Adding strategic repositories for AI coding assistance")
        
        # High-value repositories to add
        strategic_repos = [
            {
                "name": "github_mcp_official",
                "url": "https://github.com/modelcontextprotocol/server-github.git",
                "priority": "CRITICAL",
                "ai_value": "GitHub integration, issue tracking, PR automation"
            },
            {
                "name": "vercel_mcp_official", 
                "url": "https://github.com/vercel/mcp-server.git",
                "priority": "HIGH",
                "ai_value": "Deployment automation, frontend optimization"
            },
            {
                "name": "linear_mcp_official",
                "url": "https://github.com/linear/mcp-server.git", 
                "priority": "HIGH",
                "ai_value": "Project management, issue tracking, team coordination"
            },
            {
                "name": "slack_mcp_official",
                "url": "https://github.com/slack-platform/mcp-server.git",
                "priority": "HIGH", 
                "ai_value": "Team communication, workflow automation"
            },
            {
                "name": "docker_mcp_community",
                "url": "https://github.com/docker/mcp-server-docker.git",
                "priority": "MEDIUM",
                "ai_value": "Container orchestration, deployment automation"
            }
        ]
        
        results = []
        for repo in strategic_repos:
            try:
                result = self.add_repository(repo)
                results.append(result)
            except Exception as e:
                self.log(f"Failed to add {repo['name']}: {e}", "ERROR")
                results.append({
                    "name": repo["name"],
                    "status": "failed", 
                    "error": str(e)
                })
        
        return results
    
    def add_repository(self, repo_info: Dict) -> Dict:
        """Add a single repository"""
        repo_name = repo_info["name"]
        repo_url = repo_info["url"]
        
        self.log(f"📦 Adding {repo_name} ({repo_info['priority']} priority)")
        self.log(f"   AI Value: {repo_info['ai_value']}")
        
        target_path = f"external/{repo_name}"
        
        # Check if already exists
        if (self.repo_root / target_path).exists():
            self.log(f"✅ {repo_name} already exists, updating...")
            success = self.run_command(["git", "pull"], cwd=self.repo_root / target_path)
            status = "updated" if success else "update_failed"
        else:
            # Add as submodule
            self.log(f"   Cloning {repo_url}")
            success = self.run_command([
                "git", "submodule", "add", repo_url, target_path
            ])
            status = "added" if success else "failed"
        
        return {
            "name": repo_name,
            "status": status,
            "priority": repo_info["priority"],
            "ai_value": repo_info["ai_value"]
        }
    
    def update_cursor_mcp_config(self):
        """Update Cursor MCP configuration for auto-discovery"""
        self.log("🔧 Updating Cursor MCP configuration for auto-discovery")
        
        cursor_config_path = self.repo_root / ".cursor" / "mcp_settings.json"
        
        if not cursor_config_path.exists():
            self.log("⚠️  Cursor MCP config not found, creating basic structure")
            cursor_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            basic_config = {
                "mcpServers": {},
                "auto_discovery": {
                    "enabled": True,
                    "scan_paths": ["external/*", "mcp-servers/*"],
                    "index_patterns": True,
                    "semantic_analysis": True
                }
            }
            
            import json
            with open(cursor_config_path, 'w') as f:
                json.dump(basic_config, f, indent=2)
        
        self.log("✅ Cursor configuration ready for auto-discovery")
    
    def create_repository_index(self):
        """Create an index of all external repositories for AI tools"""
        self.log("📚 Creating repository index for AI discovery")
        
        index = {
            "version": "1.0",
            "created": str(subprocess.run(["date"], capture_output=True, text=True).stdout.strip()),
            "purpose": "AI-assisted development reference library",
            "repositories": {}
        }
        
        # Scan external directory
        if self.external_dir.exists():
            for item in self.external_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Try to get repository info
                    repo_info = self.analyze_repository(item)
                    index["repositories"][item.name] = repo_info
        
        # Save index
        index_path = self.repo_root / "EXTERNAL_REPOSITORY_INDEX.json"
        import json
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        
        self.log(f"�� Repository index saved to {index_path}")
        return index
    
    def analyze_repository(self, repo_path: Path) -> Dict:
        """Analyze a repository to extract metadata"""
        info = {
            "name": repo_path.name,
            "path": str(repo_path.relative_to(self.repo_root)),
            "type": "unknown",
            "description": "",
            "technologies": [],
            "ai_potential": "medium"
        }
        
        # Check for README
        readme_files = list(repo_path.glob("README*"))
        if readme_files:
            try:
                with open(readme_files[0]) as f:
                    content = f.read()[:500]  # First 500 chars
                    info["description"] = content.split('\n')[0]  # First line
            except:
                pass
        
        # Check for package.json (Node.js)
        if (repo_path / "package.json").exists():
            info["technologies"].append("Node.js")
            info["type"] = "nodejs"
        
        # Check for requirements.txt or pyproject.toml (Python)
        if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists():
            info["technologies"].append("Python")
            info["type"] = "python"
        
        # Check for Dockerfile
        if (repo_path / "Dockerfile").exists():
            info["technologies"].append("Docker")
        
        # Assess AI potential based on stars/popularity indicators
        if "microsoft" in repo_path.name or "official" in repo_path.name:
            info["ai_potential"] = "high"
        elif "mcp" in repo_path.name:
            info["ai_potential"] = "high"
        
        return info
    
    def generate_expansion_report(self, results: List[Dict]):
        """Generate expansion report"""
        self.log("📊 Generating expansion report")
        
        report = []
        report.append("# Strategic Repository Expansion Report")
        report.append("")
        report.append(f"## Summary")
        report.append(f"- Total repositories processed: {len(results)}")
        
        successful = [r for r in results if r["status"] in ["added", "updated"]]
        failed = [r for r in results if r["status"] in ["failed", "update_failed"]]
        
        report.append(f"- Successfully added/updated: {len(successful)}")
        report.append(f"- Failed: {len(failed)}")
        report.append("")
        
        if successful:
            report.append("## ✅ Successfully Added/Updated")
            for repo in successful:
                report.append(f"- **{repo['name']}** ({repo['priority']})")
                report.append(f"  - AI Value: {repo['ai_value']}")
                report.append(f"  - Status: {repo['status']}")
                report.append("")
        
        if failed:
            report.append("## ❌ Failed")
            for repo in failed:
                report.append(f"- **{repo['name']}**: {repo.get('error', 'Unknown error')}")
                report.append("")
        
        report.append("## 🎯 Next Steps")
        report.append("1. Update Cursor MCP configuration for auto-discovery")
        report.append("2. Create semantic index of all repositories")
        report.append("3. Test AI coding assistance with new repositories")
        report.append("4. Monitor for additional high-value repositories")
        
        report_content = '\n'.join(report)
        report_path = self.repo_root / "REPOSITORY_EXPANSION_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        self.log(f"📄 Expansion report saved to {report_path}")
        return report_content
    
    def run_full_expansion(self):
        """Run the complete strategic expansion process"""
        self.log("🚀 Starting strategic repository expansion")
        
        try:
            # Add strategic repositories
            results = self.add_strategic_repositories()
            
            # Update Cursor configuration
            self.update_cursor_mcp_config()
            
            # Create repository index
            self.create_repository_index()
            
            # Generate report
            self.generate_expansion_report(results)
            
            self.log("🎉 Strategic repository expansion completed!")
            self.log("Your AI coding assistant now has access to a comprehensive reference library.")
            
            return results
            
        except Exception as e:
            self.log(f"❌ Expansion failed: {e}", "ERROR")
            sys.exit(1)

def main():
    """Main entry point"""
    expander = StrategicRepositoryExpander()
    expander.run_full_expansion()

if __name__ == "__main__":
    main()
