"""Inline Documentation System for Sophia AI.

Provides real-time help and examples within Cursor IDE
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class CommandExample:
    """Example of a command with expected output."""

    command: str
    description: str
    expected_output: str
    tags: List[str]


@dataclass
class AgentDocumentation:
    """Documentation for an agent."""name: str.

    description: str
    capabilities: List[str]
    command_patterns: List[str]
    examples: List[CommandExample]
    best_practices: List[str]
    common_errors: List[Tuple[str, str]]  # (error, solution)


class InlineDocumentationSystem:
    """Provides context-aware documentation and help within Cursor IDE."""def __init__(self):.

        self.agent_docs = self._initialize_agent_documentation()
        self.workflow_docs = self._initialize_workflow_documentation()
        self.quick_reference = self._initialize_quick_reference()

    def _initialize_agent_documentation(self) -> Dict[str, AgentDocumentation]:
        """Initialize documentation for all agents."""return {.

            "docker_agent": AgentDocumentation(
                name="Docker Agent",
                description="Manages Docker containers, images, and development environments",
                capabilities=[
                    "Build and manage Docker images",
                    "Run containers with proper configuration",
                    "Create development environments",
                    "Manage Docker networks and volumes",
                    "Monitor container health and logs",
                ],
                command_patterns=[
                    "build [image_name] from [dockerfile_path]",
                    "run [container_name] from [image]",
                    "stop/start/restart [container]",
                    "show logs for [container]",
                    "create dev environment for [project]",
                ],
                examples=[
                    CommandExample(
                        command="build sophia-app:latest from ./Dockerfile",
                        description="Build a Docker image from Dockerfile",
                        expected_output="Successfully built image sophia-app:latest",
                        tags=["build", "image"],
                    ),
                    CommandExample(
                        command="run sophia-dev from sophia-app:latest with ports 8000:8000",
                        description="Run a container with port mapping",
                        expected_output="Container sophia-dev started on port 8000",
                        tags=["run", "container", "ports"],
                    ),
                    CommandExample(
                        command="create Python dev environment with PostgreSQL and Redis",
                        description="Create a complete development environment",
                        expected_output="Development environment created with 3 containers",
                        tags=["dev", "environment", "compose"],
                    ),
                ],
                best_practices=[
                    "Always tag images with meaningful versions",
                    "Use multi-stage builds for smaller images",
                    "Mount volumes for development hot-reload",
                    "Set resource limits for containers",
                    "Use health checks for production containers",
                ],
                common_errors=[
                    (
                        "Port already in use",
                        "Check for running containers with: docker ps",
                    ),
                    (
                        "Cannot connect to Docker daemon",
                        "Ensure Docker Desktop is running",
                    ),
                    (
                        "No space left on device",
                        "Clean up unused images: docker system prune",
                    ),
                ],
            ),
            "pulumi_agent": AgentDocumentation(
                name="Pulumi Agent",
                description="Infrastructure as Code management with AI-powered assistance",
                capabilities=[
                    "Deploy and manage cloud infrastructure",
                    "Preview infrastructure changes",
                    "Generate IaC code from natural language",
                    "Manage multiple stacks and environments",
                    "Handle secrets and configuration",
                ],
                command_patterns=[
                    "deploy stack [name]",
                    "preview changes for [stack]",
                    "create [resource_type] named [name]",
                    "destroy stack [name]",
                    "refresh state for [stack]",
                ],
                examples=[
                    CommandExample(
                        command="deploy stack production",
                        description="Deploy infrastructure to production",
                        expected_output="Successfully deployed 15 resources to production",
                        tags=["deploy", "production"],
                    ),
                    CommandExample(
                        command="create AWS Lambda function for image processing",
                        description="Generate Lambda function infrastructure",
                        expected_output="Generated Lambda function with S3 trigger and IAM role",
                        tags=["create", "lambda", "aws"],
                    ),
                    CommandExample(
                        command="preview changes for staging environment",
                        description="Preview infrastructure changes before deployment",
                        expected_output="3 resources to create, 2 to update, 0 to delete",
                        tags=["preview", "staging"],
                    ),
                ],
                best_practices=[
                    "Always preview before deploying to production",
                    "Use separate stacks for different environments",
                    "Store sensitive config in Pulumi ESC",
                    "Tag all resources for cost tracking",
                    "Implement proper RBAC for team access",
                ],
                common_errors=[
                    ("No Pulumi.yaml found", "Run 'pulumi new' to initialize project"),
                    ("Authentication failed", "Run 'pulumi login' to authenticate"),
                    (
                        "Resource already exists",
                        "Import existing resources or use different names",
                    ),
                ],
            ),
            "claude_agent": AgentDocumentation(
                name="Claude Agent",
                description="AI-powered code analysis, generation, and review",
                capabilities=[
                    "Generate code from natural language",
                    "Review code for best practices",
                    "Analyze security vulnerabilities",
                    "Refactor and optimize code",
                    "Create comprehensive documentation",
                ],
                command_patterns=[
                    "review code in [file/directory]",
                    "generate [type] for [purpose]",
                    "analyze security in [path]",
                    "optimize [file] for [metric]",
                    "document [code_path]",
                ],
                examples=[
                    CommandExample(
                        command="review code in backend/api/ for best practices",
                        description="Review code for Python best practices",
                        expected_output="Found 5 suggestions: 2 performance, 3 readability",
                        tags=["review", "best-practices"],
                    ),
                    CommandExample(
                        command="generate REST API for user management with authentication",
                        description="Generate complete REST API code",
                        expected_output="Generated 8 files: models, routes, middleware, tests",
                        tags=["generate", "api", "auth"],
                    ),
                    CommandExample(
                        command="analyze security vulnerabilities in dependencies",
                        description="Security scan of project dependencies",
                        expected_output="Found 2 high, 3 medium severity vulnerabilities",
                        tags=["security", "dependencies"],
                    ),
                ],
                best_practices=[
                    "Provide clear context for code generation",
                    "Review generated code before using in production",
                    "Use specific optimization goals (speed, memory, etc.)",
                    "Combine with tests for refactoring confidence",
                    "Iterate on generated code for best results",
                ],
                common_errors=[
                    (
                        "Generated code doesn't compile",
                        "Provide more specific requirements",
                    ),
                    ("Review too generic", "Specify particular aspects to review"),
                    (
                        "Rate limit exceeded",
                        "Implement caching or reduce request frequency",
                    ),
                ],
            ),
        }

    def _initialize_workflow_documentation(self) -> Dict[str, Dict[str, Any]]:
        """Initialize documentation for workflows."""return {.

            "deployment": {
                "name": "Deployment Workflow",
                "description": "Complete deployment pipeline from build to production",
                "steps": [
                    "Build Docker image",
                    "Run tests in container",
                    "Preview infrastructure changes",
                    "Deploy infrastructure",
                    "Deploy application",
                    "Verify deployment health",
                ],
                "example": "execute deployment workflow for staging",
                "prerequisites": [
                    "Docker daemon running",
                    "Pulumi authenticated",
                    "Valid AWS/Cloud credentials",
                ],
            },
            "code_review": {
                "name": "Code Review Workflow",
                "description": "Comprehensive code analysis and review",
                "steps": [
                    "Security vulnerability scan",
                    "Code quality analysis",
                    "Performance profiling",
                    "Generate review report",
                ],
                "example": "execute code review workflow for backend/",
                "prerequisites": ["Code files accessible", "Claude API available"],
            },
        }

    def _initialize_quick_reference(self) -> Dict[str, List[str]]:
        """Initialize quick reference commands."""return {.

            "docker": [
                "build [image] from [dockerfile]",
                "run [container] from [image]",
                "stop/start/restart [container]",
                "show logs for [container]",
                "list running containers",
            ],
            "pulumi": [
                "deploy stack [name]",
                "preview stack [name]",
                "destroy stack [name]",
                "list stacks",
                "show stack outputs",
            ],
            "claude": [
                "review code in [path]",
                "generate [type] for [purpose]",
                "analyze security in [path]",
                "optimize [file]",
                "explain [code/concept]",
            ],
            "workflow": [
                "execute [workflow_name]",
                "list available workflows",
                "show workflow status",
                "cancel workflow [id]",
            ],
        }

    def get_help(self, query: str) -> Dict[str, Any]:
        """Get context-aware help based on query."""query_lower = query.lower().

        # Determine which agent or topic
        if any(word in query_lower for word in ["docker", "container", "image"]):
            agent = "docker_agent"
        elif any(
            word in query_lower
            for word in ["pulumi", "infrastructure", "deploy", "stack"]
        ):
            agent = "pulumi_agent"
        elif any(
            word in query_lower for word in ["claude", "review", "generate", "analyze"]
        ):
            agent = "claude_agent"
        else:
            # Return general help
            return self._get_general_help()

        # Get specific help
        doc = self.agent_docs[agent]

        # Find relevant examples
        relevant_examples = [
            ex for ex in doc.examples if any(tag in query_lower for tag in ex.tags)
        ]

        return {
            "agent": doc.name,
            "description": doc.description,
            "relevant_commands": self._find_relevant_commands(
                query_lower, doc.command_patterns
            ),
            "examples": [
                {
                    "command": ex.command,
                    "description": ex.description,
                    "expected": ex.expected_output,
                }
                for ex in relevant_examples[:3]
            ],
            "tips": doc.best_practices[:3],
            "quick_reference": self.quick_reference.get(agent.split("_")[0], []),
        }

    def _find_relevant_commands(self, query: str, patterns: List[str]) -> List[str]:
        """Find command patterns relevant to query."""relevant = [].

        for pattern in patterns:
            if any(word in pattern.lower() for word in query.split()):
                relevant.append(pattern)
        return relevant[:5]

    def _get_general_help(self) -> Dict[str, Any]:
        """Get general help information."""return {.

            "title": "Sophia AI Help",
            "description": "Natural language interface for development operations",
            "available_agents": [
                {
                    "name": doc.name,
                    "description": doc.description,
                    "example": doc.examples[0].command if doc.examples else "",
                }
                for doc in self.agent_docs.values()
            ],
            "workflows": list(self.workflow_docs.keys()),
            "tips": [
                "Use natural language to describe what you want",
                "Be specific about environments and configurations",
                "Check 'show recent commands' for history",
                "Use 'explain [concept]' for detailed information",
            ],
        }

    def get_inline_suggestion(self, partial_command: str) -> List[Dict[str, str]]:
        """Get inline suggestions based on partial command."""suggestions = [].

        partial_lower = partial_command.lower()

        # Check all command patterns
        for agent_name, doc in self.agent_docs.items():
            for pattern in doc.command_patterns:
                if partial_lower in pattern.lower():
                    suggestions.append(
                        {
                            "completion": pattern,
                            "agent": doc.name,
                            "description": f"Use {doc.name} to {pattern}",
                        }
                    )

        # Check examples
        for agent_name, doc in self.agent_docs.items():
            for example in doc.examples:
                if partial_lower in example.command.lower():
                    suggestions.append(
                        {
                            "completion": example.command,
                            "agent": doc.name,
                            "description": example.description,
                        }
                    )

        return suggestions[:5]  # Return top 5 suggestions

    def get_error_help(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Get help for specific error messages."""error_lower = error_message.lower().

        for agent_name, doc in self.agent_docs.items():
            for error, solution in doc.common_errors:
                if error.lower() in error_lower:
                    return {
                        "agent": doc.name,
                        "error": error,
                        "solution": solution,
                        "related_commands": self.quick_reference.get(
                            agent_name.split("_")[0], []
                        ),
                    }

        return None

    def format_for_cursor(self, help_data: Dict[str, Any]) -> str:
        """Format help data for display in Cursor IDE."""lines = [].

        if "agent" in help_data:
            lines.append(f"## {help_data['agent']}")
            lines.append(f"{help_data['description']}\n")

        if "relevant_commands" in help_data:
            lines.append("### Relevant Commands")
            for cmd in help_data["relevant_commands"]:
                lines.append(f"- `{cmd}`")
            lines.append("")

        if "examples" in help_data:
            lines.append("### Examples")
            for ex in help_data["examples"]:
                lines.append(f"**{ex['description']}**")
                lines.append("```")
                lines.append(ex["command"])
                lines.append("```")
                lines.append(f"Expected: {ex['expected']}\n")

        if "tips" in help_data:
            lines.append("### Tips")
            for tip in help_data["tips"]:
                lines.append(f"- {tip}")

        return "\n".join(lines)


# Global instance
inline_docs = InlineDocumentationSystem()


# Helper functions for Cursor integration
def get_help(query: str) -> str:
    """Get formatted help for a query."""help_data = inline_docs.get_help(query).

    return inline_docs.format_for_cursor(help_data)


def suggest_completions(partial: str) -> List[str]:
    """Get command completions."""suggestions = inline_docs.get_inline_suggestion(partial).

    return [s["completion"] for s in suggestions]


def help_with_error(error: str) -> Optional[str]:
    """Get help for an error."""
    error_help = inline_docs.get_error_help(error)
    if error_help:
        return f"Error: {error_help['error']}\nSolution: {error_help['solution']}"
    return None
