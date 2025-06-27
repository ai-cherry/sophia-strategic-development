#!/usr/bin/env python3
"""
Enhanced Coding Workflow Integration for Sophia AI
Combines the best of Zencoder, cursor-companion, and Sophia AI capabilities
"""

import json
import asyncio
import requests
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SophiaEnhancedCodingWorkflow:
    """
    Enhanced coding workflow that integrates:
    - Zencoder-style platform integration (GitHub, Jira, etc.)
    - cursor-companion-style prompt/rule management
    - Sophia AI's advanced business intelligence
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.workspace_root = Path.cwd()
        self.sophia_dir = self.workspace_root / ".sophia"
        self.prompts_dir = self.sophia_dir / "prompts"
        self.rules_dir = self.sophia_dir / "rules"
        self.context_dir = self.sophia_dir / "context"
        
        # Platform integrations (Zencoder-style)
        self.platform_integrations = {
            "github": {
                "api_base": "https://api.github.com",
                "endpoints": ["issues", "pull_requests", "commits"],
                "context_fields": ["title", "body", "labels", "comments"]
            },
            "jira": {
                "api_base": "https://{domain}.atlassian.net/rest/api/3",
                "endpoints": ["issue", "search"],
                "context_fields": ["summary", "description", "status", "assignee"]
            },
            "linear": {
                "api_base": "https://api.linear.app/graphql",
                "endpoints": ["issues", "projects"],
                "context_fields": ["title", "description", "state", "team"]
            },
            "slack": {
                "api_base": "https://slack.com/api",
                "endpoints": ["conversations", "messages"],
                "context_fields": ["text", "user", "channel", "thread_ts"]
            }
        }
        
        # Initialize directories
        self._init_workspace()
    
    def _init_workspace(self):
        """Initialize Sophia workspace structure"""
        for dir_path in [self.sophia_dir, self.prompts_dir, self.rules_dir, self.context_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Create default configuration
        config_file = self.sophia_dir / "config.json"
        if not config_file.exists():
            default_config = {
                "version": "1.0.0",
                "sophia_ai": {
                    "models": {
                        "primary": "claude-3-5-sonnet-20241119",
                        "coding": "claude-3-5-sonnet-20241119",
                        "analysis": "claude-3-5-sonnet-20241119"
                    },
                    "endpoints": {
                        "backend": "http://localhost:8000",
                        "unified_assistant": "python unified_ai_assistant.py",
                        "claude_cli": "./claude-cli-integration/claude chat"
                    }
                },
                "integrations": {
                    "enabled": ["github", "linear", "slack"],
                    "context_gathering": True,
                    "auto_prompt_generation": True
                },
                "workflow": {
                    "auto_context": True,
                    "intelligent_routing": True,
                    "business_context": True,
                    "security_scanning": True
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    async def init_project(self, project_type: str = "full-stack"):
        """Initialize enhanced coding workflow for project"""
        print("🚀 Initializing Sophia AI Enhanced Coding Workflow...")
        
        # Install default prompts based on project type
        await self._install_default_prompts(project_type)
        
        # Install default rules
        await self._install_default_rules(project_type)
        
        # Set up platform integrations
        await self._setup_platform_integrations()
        
        print("✅ Sophia AI Enhanced Coding Workflow initialized!")
        return True
    
    async def _install_default_prompts(self, project_type: str):
        """Install default prompts for project type"""
        prompts = {
            "full-stack": [
                {
                    "name": "react-component",
                    "description": "Generate React components with TypeScript",
                    "template": """Generate a React component with the following requirements:
- Use TypeScript with proper type definitions
- Follow modern React patterns (hooks, functional components)
- Include proper error handling
- Add accessibility features (ARIA labels, keyboard navigation)
- Use Sophia AI's glassmorphism design system
- Include comprehensive JSDoc comments
- Add prop validation

Component: {component_name}
Purpose: {purpose}
Props: {props}

Additional Context from Sophia AI:
{business_context}
{design_context}
{performance_requirements}"""
                },
                {
                    "name": "python-api",
                    "description": "Generate Python API endpoints with FastAPI",
                    "template": """Generate a Python API endpoint with these specifications:
- Use FastAPI with async/await patterns
- Include proper Pydantic models for request/response
- Add comprehensive error handling with proper HTTP status codes
- Include authentication/authorization if needed
- Add logging with structured format
- Include type hints for all functions
- Add OpenAPI documentation
- Follow Sophia AI backend patterns

Endpoint: {endpoint_name}
Method: {http_method}
Purpose: {purpose}
Parameters: {parameters}

Business Context from Sophia AI:
{business_requirements}
{security_requirements}
{integration_requirements}"""
                },
                {
                    "name": "database-query",
                    "description": "Generate optimized database queries",
                    "template": """Generate an optimized database query for:
- Database: {database_type}
- Query Type: {query_type}
- Purpose: {purpose}
- Tables: {tables}
- Requirements: {requirements}

Sophia AI Context:
{performance_requirements}
{security_requirements}
{business_logic}

Ensure the query follows best practices:
- Use proper indexing strategies
- Include performance optimization
- Add security measures (SQL injection prevention)
- Include error handling
- Add comprehensive comments
- Consider scalability implications"""
                }
            ],
            "business-intelligence": [
                {
                    "name": "snowflake-analysis",
                    "description": "Generate Snowflake analysis queries",
                    "template": """Generate Snowflake analysis query for business intelligence:
- Analysis Type: {analysis_type}
- Business Question: {business_question}
- Data Sources: {data_sources}
- Time Period: {time_period}

Sophia AI Business Context:
{kpi_requirements}
{stakeholder_needs}
{reporting_frequency}

Include:
- Performance-optimized SQL with proper warehousing
- Business-friendly column names and comments
- Error handling and data quality checks
- Visualization-ready output format
- Executive summary interpretation"""
                }
            ]
        }
        
        for prompt in prompts.get(project_type, []):
            prompt_file = self.prompts_dir / f"{prompt['name']}.json"
            with open(prompt_file, 'w') as f:
                json.dump(prompt, f, indent=2)
            print(f"  ✅ Installed prompt: {prompt['name']}")
    
    async def _install_default_rules(self, project_type: str):
        """Install default coding rules"""
        rules = {
            "common": [
                {
                    "name": "sophia-security",
                    "description": "Sophia AI security standards",
                    "rules": [
                        "Never hardcode API keys or secrets",
                        "Use Pulumi ESC for credential management",
                        "Implement proper input validation",
                        "Add comprehensive error handling",
                        "Include security headers for web endpoints",
                        "Use HTTPS for all external communications",
                        "Implement proper authentication/authorization"
                    ]
                },
                {
                    "name": "sophia-performance",
                    "description": "Sophia AI performance standards",
                    "rules": [
                        "API responses must be <200ms for critical paths",
                        "Database queries must be <100ms average",
                        "Use async/await for I/O operations",
                        "Implement proper caching strategies",
                        "Add performance monitoring and logging",
                        "Optimize for scalability and concurrency"
                    ]
                },
                {
                    "name": "sophia-business",
                    "description": "Sophia AI business logic standards",
                    "rules": [
                        "Always consider Pay Ready business context",
                        "Implement metrics for revenue and customer health",
                        "Focus on actionable insights for sales coaching",
                        "Prioritize real-time data processing",
                        "Include executive dashboard integration",
                        "Add comprehensive business intelligence features"
                    ]
                }
            ]
        }
        
        for rule in rules.get("common", []):
            rule_file = self.rules_dir / f"{rule['name']}.json"
            with open(rule_file, 'w') as f:
                json.dump(rule, f, indent=2)
            print(f"  ✅ Installed rule: {rule['name']}")
    
    async def _setup_platform_integrations(self):
        """Set up platform integrations"""
        integrations_file = self.sophia_dir / "integrations.json"
        
        integration_config = {
            "github": {
                "enabled": True,
                "webhook_url": f"{self.base_url}/webhooks/github",
                "events": ["issues", "pull_request", "push"],
                "context_gathering": True
            },
            "linear": {
                "enabled": True,
                "webhook_url": f"{self.base_url}/webhooks/linear", 
                "events": ["issue.create", "issue.update"],
                "context_gathering": True
            },
            "slack": {
                "enabled": True,
                "webhook_url": f"{self.base_url}/webhooks/slack",
                "events": ["message", "thread_reply"],
                "context_gathering": True
            }
        }
        
        with open(integrations_file, 'w') as f:
            json.dump(integration_config, f, indent=2)
        
        print("  ✅ Platform integrations configured")
    
    async def gather_context_from_platform(self, platform: str, resource_id: str) -> Dict[str, Any]:
        """Gather context from external platform (Zencoder-style)"""
        try:
            if platform == "github":
                return await self._gather_github_context(resource_id)
            elif platform == "jira":
                return await self._gather_jira_context(resource_id)
            elif platform == "linear":
                return await self._gather_linear_context(resource_id)
            elif platform == "slack":
                return await self._gather_slack_context(resource_id)
            else:
                return {"error": f"Unsupported platform: {platform}"}
                
        except Exception as e:
            return {"error": f"Failed to gather context from {platform}: {str(e)}"}
    
    async def _gather_github_context(self, issue_id: str) -> Dict[str, Any]:
        """Gather context from GitHub issue/PR"""
        # This would integrate with GitHub API
        # For now, return mock context
        return {
            "platform": "github",
            "type": "issue",
            "id": issue_id,
            "title": "Example GitHub Issue",
            "description": "Detailed issue description",
            "labels": ["bug", "priority-high"],
            "assignee": "developer",
            "comments": ["Comment 1", "Comment 2"],
            "related_files": ["app.py", "utils.py"],
            "sophia_context": "Business impact: Critical customer-facing feature"
        }
    
    async def generate_enhanced_prompt(self, 
                                     prompt_name: str, 
                                     context: Dict[str, Any],
                                     platform_context: Optional[Dict[str, Any]] = None) -> str:
        """Generate enhanced prompt with context (cursor-companion style + Sophia AI)"""
        
        # Load prompt template
        prompt_file = self.prompts_dir / f"{prompt_name}.json"
        if not prompt_file.exists():
            return f"Prompt '{prompt_name}' not found. Available prompts: {self.list_prompts()}"
        
        with open(prompt_file, 'r') as f:
            prompt_data = json.load(f)
        
        template = prompt_data.get("template", "")
        
        # Gather Sophia AI business context
        sophia_context = await self._gather_sophia_business_context(context)
        
        # Combine all context
        full_context = {
            **context,
            **sophia_context,
            **(platform_context or {})
        }
        
        # Format template with context
        try:
            formatted_prompt = template.format(**full_context)
            return formatted_prompt
        except KeyError as e:
            return f"Missing context variable: {e}. Please provide: {list(full_context.keys())}"
    
    async def _gather_sophia_business_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather business context from Sophia AI systems"""
        business_context = {}
        
        try:
            # Get business intelligence context
            if "business_query" in context:
                bi_response = requests.post(
                    f"{self.base_url}/api/chat/enhanced",
                    json={"message": context["business_query"], "context": "business_intelligence"},
                    timeout=10
                )
                if bi_response.status_code == 200:
                    business_context["business_intelligence"] = bi_response.json().get("response", "")
            
            # Get performance requirements
            business_context["performance_requirements"] = "Sub-200ms response times, scalable architecture"
            
            # Get security requirements  
            business_context["security_requirements"] = "Enterprise-grade security, Pulumi ESC integration"
            
            # Get design context from UI/UX agent
            try:
                design_response = requests.get(f"http://localhost:9001/api/design_system", timeout=5)
                if design_response.status_code == 200:
                    business_context["design_context"] = "Glassmorphism design system, WCAG 2.1 AA compliance"
            except Exception as e:
                logger.warning(f"Could not connect to design system MCP, using default. Error: {e}")
                business_context["design_context"] = "Modern responsive design required"
                
        except Exception as e:
            business_context["context_error"] = f"Failed to gather business context: {str(e)}"
        
        return business_context
    
    def list_prompts(self) -> List[str]:
        """List available prompts"""
        if not self.prompts_dir.exists():
            return []
        
        return [f.stem for f in self.prompts_dir.glob("*.json")]
    
    def list_rules(self) -> List[str]:
        """List available rules"""
        if not self.rules_dir.exists():
            return []
        
        return [f.stem for f in self.rules_dir.glob("*.json")]
    
    async def enhanced_code_generation(self, 
                                     prompt_name: str,
                                     context: Dict[str, Any],
                                     platform_context: Optional[Dict[str, Any]] = None) -> str:
        """Generate code using enhanced prompt with full Sophia AI context"""
        
        # Generate enhanced prompt
        enhanced_prompt = await self.generate_enhanced_prompt(prompt_name, context, platform_context)
        
        # Use Sophia AI's unified assistant for generation
        try:
            result = subprocess.run([
                "python", "unified_ai_assistant.py", enhanced_prompt
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout
            else:
                # Fallback to Claude CLI
                result = subprocess.run([
                    "./claude-cli-integration/claude", "chat", enhanced_prompt
                ], capture_output=True, text=True, timeout=60)
                
                return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Code generation failed: {str(e)}"
    
    async def workflow_automation(self, workflow_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Automate development workflows (Zencoder-style agents)"""
        
        workflows = {
            "issue_to_code": self._workflow_issue_to_code,
            "pr_review": self._workflow_pr_review,
            "bug_fix": self._workflow_bug_fix,
            "feature_implementation": self._workflow_feature_implementation,
            "business_analysis": self._workflow_business_analysis
        }
        
        if workflow_type not in workflows:
            return {"error": f"Unknown workflow: {workflow_type}"}
        
        return await workflows[workflow_type](context)
    
    async def _workflow_issue_to_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Automated workflow: Issue to Code implementation"""
        
        steps = []
        
        # 1. Gather context from issue
        if "platform" in context and "issue_id" in context:
            platform_context = await self.gather_context_from_platform(
                context["platform"], context["issue_id"]
            )
            steps.append("✅ Gathered platform context")
        else:
            platform_context = {}
        
        # 2. Analyze business impact using Sophia AI
        business_analysis = await self._gather_sophia_business_context({
            "business_query": f"Analyze business impact of: {context.get('description', '')}"
        })
        steps.append("✅ Analyzed business impact")
        
        # 3. Generate implementation plan
        planning_context = {
            "task": context.get("title", ""),
            "description": context.get("description", ""),
            "requirements": context.get("requirements", []),
            **business_analysis
        }
        
        implementation_plan = await self.enhanced_code_generation(
            "feature-implementation-plan", planning_context, platform_context
        )
        steps.append("✅ Generated implementation plan")
        
        # 4. Generate code
        if "code_type" in context:
            code_result = await self.enhanced_code_generation(
                context["code_type"], planning_context, platform_context
            )
            steps.append("✅ Generated code implementation")
        else:
            code_result = "No code type specified"
        
        return {
            "workflow": "issue_to_code",
            "steps": steps,
            "platform_context": platform_context,
            "business_analysis": business_analysis,
            "implementation_plan": implementation_plan,
            "code_result": code_result,
            "status": "completed"
        }

# CLI Interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sophia AI Enhanced Coding Workflow")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize enhanced workflow")
    init_parser.add_argument("--type", default="full-stack", help="Project type")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate code with enhanced prompts")
    gen_parser.add_argument("--prompt", required=True, help="Prompt name")
    gen_parser.add_argument("--context", help="Context JSON string")
    
    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Run automated workflow")
    workflow_parser.add_argument("--type", required=True, help="Workflow type")
    workflow_parser.add_argument("--context", help="Context JSON string")
    
    # List commands
    list_parser = subparsers.add_parser("list", help="List prompts or rules")
    list_parser.add_argument("type", choices=["prompts", "rules"], help="What to list")
    
    args = parser.parse_args()
    
    workflow = SophiaEnhancedCodingWorkflow()
    
    if args.command == "init":
        await workflow.init_project(args.type)
    
    elif args.command == "generate":
        context = json.loads(args.context) if args.context else {}
        result = await workflow.enhanced_code_generation(args.prompt, context)
        print(result)
    
    elif args.command == "workflow":
        context = json.loads(args.context) if args.context else {}
        result = await workflow.workflow_automation(args.type, context)
        print(json.dumps(result, indent=2))
    
    elif args.command == "list":
        if args.type == "prompts":
            prompts = workflow.list_prompts()
            print("Available prompts:", ", ".join(prompts))
        else:
            rules = workflow.list_rules()
            print("Available rules:", ", ".join(rules))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 