"""
Claude MCP Server
MCP server for Claude/Anthropic API integration with "Claude as Code" functionality
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# MCP imports
from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, GetResourceRequest, ListResourcesRequest, ListToolsRequest
)

# Sophia AI imports
from backend.integrations.claude_integration import claude_integration
from infrastructure.esc.claude_secrets import claude_secret_manager

logger = logging.getLogger(__name__)

class ClaudeMCPServer:
    """
    MCP Server for Claude/Anthropic API integration
    
    Provides comprehensive "Claude as Code" functionality through MCP protocol
    """
    
    def __init__(self):
        self.server = Server("claude-mcp-server")
        self.claude = claude_integration
        self.secret_manager = claude_secret_manager
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        # Resource handlers
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available Claude resources"""
            return [
                Resource(
                    uri="claude://health",
                    name="Claude Health Status",
                    description="Current health and status of Claude integration",
                    mimeType="application/json"
                ),
                Resource(
                    uri="claude://config",
                    name="Claude Configuration",
                    description="Current Claude API configuration and settings",
                    mimeType="application/json"
                ),
                Resource(
                    uri="claude://models",
                    name="Available Claude Models",
                    description="List of available Claude models and their capabilities",
                    mimeType="application/json"
                ),
                Resource(
                    uri="claude://usage",
                    name="Claude Usage Statistics",
                    description="Current API usage and rate limit status",
                    mimeType="application/json"
                )
            ]
        
        @self.server.get_resource()
        async def get_resource(request: GetResourceRequest) -> str:
            """Get specific Claude resource"""
            uri = request.uri
            
            if uri == "claude://health":
                health_status = await self.claude.get_health_status()
                return json.dumps(health_status, indent=2)
            
            elif uri == "claude://config":
                config = await self.secret_manager.get_claude_config()
                # Mask sensitive information
                if config and "api_key" in config:
                    config["api_key"] = config["api_key"][:8] + "..." if config["api_key"] else None
                return json.dumps(config or {}, indent=2)
            
            elif uri == "claude://models":
                models = {
                    "available_models": [
                        {
                            "name": "claude-3-5-sonnet-20241022",
                            "description": "Most capable model for complex tasks",
                            "max_tokens": 8192,
                            "capabilities": ["text", "code", "analysis", "reasoning"]
                        },
                        {
                            "name": "claude-3-haiku-20240307",
                            "description": "Fastest model for simple tasks",
                            "max_tokens": 4096,
                            "capabilities": ["text", "code", "quick_responses"]
                        },
                        {
                            "name": "claude-3-opus-20240229",
                            "description": "Most powerful model for complex reasoning",
                            "max_tokens": 4096,
                            "capabilities": ["text", "code", "complex_reasoning", "analysis"]
                        }
                    ],
                    "current_model": self.claude.default_model,
                    "last_updated": datetime.now().isoformat()
                }
                return json.dumps(models, indent=2)
            
            elif uri == "claude://usage":
                usage_stats = {
                    "rate_limits": {
                        "requests_per_minute": self.claude.rate_limit_requests,
                        "tokens_per_minute": self.claude.rate_limit_tokens,
                        "current_requests": len(self.claude.request_timestamps),
                        "current_tokens": sum(tokens for _, tokens in self.claude.token_usage)
                    },
                    "session_stats": {
                        "authenticated": self.claude._authenticated,
                        "session_active": self.claude._session is not None
                    },
                    "last_updated": datetime.now().isoformat()
                }
                return json.dumps(usage_stats, indent=2)
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        # Tool handlers
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Claude tools"""
            return [
                Tool(
                    name="claude_send_message",
                    description="Send a message to Claude and get a response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send to Claude"
                            },
                            "model": {
                                "type": "string",
                                "description": "Claude model to use (optional)",
                                "default": "claude-3-5-sonnet-20241022"
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Maximum tokens in response (optional)",
                                "default": 4096
                            },
                            "system_prompt": {
                                "type": "string",
                                "description": "System prompt to guide Claude's behavior (optional)"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="claude_generate_code",
                    description="Generate code using Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Description of the code to generate"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "default": "python"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for code generation (optional)"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="claude_analyze_code",
                    description="Analyze code using Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to analyze"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "default": "python"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis",
                                "enum": ["review", "explain", "optimize", "debug"],
                                "default": "review"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="claude_refactor_code",
                    description="Refactor code using Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to refactor"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "default": "python"
                            },
                            "refactor_goal": {
                                "type": "string",
                                "description": "Goal of refactoring",
                                "default": "improve readability"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="claude_generate_documentation",
                    description="Generate documentation for code using Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to document"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "default": "python"
                            },
                            "doc_type": {
                                "type": "string",
                                "description": "Type of documentation",
                                "enum": ["api", "readme", "inline"],
                                "default": "api"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="claude_generate_tests",
                    description="Generate tests for code using Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to generate tests for"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "default": "python"
                            },
                            "test_framework": {
                                "type": "string",
                                "description": "Testing framework to use",
                                "default": "pytest"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="claude_explain_concept",
                    description="Ask Claude to explain a concept or technology",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "concept": {
                                "type": "string",
                                "description": "Concept or technology to explain"
                            },
                            "level": {
                                "type": "string",
                                "description": "Explanation level",
                                "enum": ["beginner", "intermediate", "advanced"],
                                "default": "intermediate"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the explanation (optional)"
                            }
                        },
                        "required": ["concept"]
                    }
                ),
                Tool(
                    name="claude_debug_issue",
                    description="Help debug an issue using Claude",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_description": {
                                "type": "string",
                                "description": "Description of the issue"
                            },
                            "code": {
                                "type": "string",
                                "description": "Relevant code (optional)"
                            },
                            "error_message": {
                                "type": "string",
                                "description": "Error message (optional)"
                            },
                            "environment": {
                                "type": "string",
                                "description": "Environment details (optional)"
                            }
                        },
                        "required": ["issue_description"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> List[TextContent]:
            """Handle tool calls"""
            tool_name = request.params.name
            args = request.params.arguments or {}
            
            try:
                # Ensure Claude is initialized
                if not self.claude._authenticated:
                    await self.claude.initialize()
                
                if tool_name == "claude_send_message":
                    response = await self.claude.send_message(
                        message=args["message"],
                        model=args.get("model"),
                        max_tokens=args.get("max_tokens"),
                        system_prompt=args.get("system_prompt")
                    )
                    
                    if response:
                        result = {
                            "response": response.content,
                            "model": response.model,
                            "tokens_used": response.tokens_used,
                            "timestamp": response.timestamp
                        }
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to get response from Claude")]
                
                elif tool_name == "claude_generate_code":
                    result = await self.claude.generate_code(
                        prompt=args["prompt"],
                        language=args.get("language", "python"),
                        context=args.get("context")
                    )
                    
                    if result:
                        response = {
                            "generated_code": result.generated_code,
                            "explanation": result.explanation,
                            "language": result.language,
                            "model": result.model,
                            "tokens_used": result.tokens_used,
                            "created_at": result.created_at
                        }
                        return [TextContent(type="text", text=json.dumps(response, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to generate code")]
                
                elif tool_name == "claude_analyze_code":
                    response = await self.claude.analyze_code(
                        code=args["code"],
                        language=args.get("language", "python"),
                        analysis_type=args.get("analysis_type", "review")
                    )
                    
                    if response:
                        result = {
                            "analysis": response.content,
                            "analysis_type": args.get("analysis_type", "review"),
                            "language": args.get("language", "python"),
                            "model": response.model,
                            "tokens_used": response.tokens_used,
                            "timestamp": response.timestamp
                        }
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to analyze code")]
                
                elif tool_name == "claude_refactor_code":
                    result = await self.claude.refactor_code(
                        code=args["code"],
                        language=args.get("language", "python"),
                        refactor_goal=args.get("refactor_goal", "improve readability")
                    )
                    
                    if result:
                        response = {
                            "refactored_code": result.generated_code,
                            "explanation": result.explanation,
                            "language": result.language,
                            "refactor_goal": args.get("refactor_goal", "improve readability"),
                            "model": result.model,
                            "tokens_used": result.tokens_used,
                            "created_at": result.created_at
                        }
                        return [TextContent(type="text", text=json.dumps(response, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to refactor code")]
                
                elif tool_name == "claude_generate_documentation":
                    response = await self.claude.generate_documentation(
                        code=args["code"],
                        language=args.get("language", "python"),
                        doc_type=args.get("doc_type", "api")
                    )
                    
                    if response:
                        result = {
                            "documentation": response.content,
                            "doc_type": args.get("doc_type", "api"),
                            "language": args.get("language", "python"),
                            "model": response.model,
                            "tokens_used": response.tokens_used,
                            "timestamp": response.timestamp
                        }
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to generate documentation")]
                
                elif tool_name == "claude_generate_tests":
                    result = await self.claude.generate_tests(
                        code=args["code"],
                        language=args.get("language", "python"),
                        test_framework=args.get("test_framework", "pytest")
                    )
                    
                    if result:
                        response = {
                            "test_code": result.generated_code,
                            "explanation": result.explanation,
                            "language": result.language,
                            "test_framework": args.get("test_framework", "pytest"),
                            "model": result.model,
                            "tokens_used": result.tokens_used,
                            "created_at": result.created_at
                        }
                        return [TextContent(type="text", text=json.dumps(response, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to generate tests")]
                
                elif tool_name == "claude_explain_concept":
                    system_prompt = f"""You are an expert technical educator. Explain the concept at a {args.get('level', 'intermediate')} level.

Guidelines:
1. Start with a clear, concise definition
2. Provide relevant examples and use cases
3. Explain key benefits and limitations
4. Include practical applications
5. Adjust complexity based on the specified level

Level: {args.get('level', 'intermediate')}"""

                    if args.get('context'):
                        system_prompt += f"\n\nAdditional context: {args['context']}"
                    
                    response = await self.claude.send_message(
                        message=f"Please explain: {args['concept']}",
                        system_prompt=system_prompt
                    )
                    
                    if response:
                        result = {
                            "explanation": response.content,
                            "concept": args["concept"],
                            "level": args.get("level", "intermediate"),
                            "model": response.model,
                            "tokens_used": response.tokens_used,
                            "timestamp": response.timestamp
                        }
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to explain concept")]
                
                elif tool_name == "claude_debug_issue":
                    system_prompt = """You are an expert debugging assistant. Help identify and solve the issue.

Guidelines:
1. Analyze the problem systematically
2. Identify potential root causes
3. Suggest specific debugging steps
4. Provide concrete solutions
5. Include preventive measures for the future"""

                    debug_prompt = f"Issue: {args['issue_description']}"
                    
                    if args.get('code'):
                        debug_prompt += f"\n\nRelevant code:\n```\n{args['code']}\n```"
                    
                    if args.get('error_message'):
                        debug_prompt += f"\n\nError message: {args['error_message']}"
                    
                    if args.get('environment'):
                        debug_prompt += f"\n\nEnvironment: {args['environment']}"
                    
                    response = await self.claude.send_message(
                        message=debug_prompt,
                        system_prompt=system_prompt
                    )
                    
                    if response:
                        result = {
                            "debugging_help": response.content,
                            "issue_description": args["issue_description"],
                            "model": response.model,
                            "tokens_used": response.tokens_used,
                            "timestamp": response.timestamp
                        }
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    else:
                        return [TextContent(type="text", text="Failed to provide debugging help")]
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {tool_name}")]
                    
            except Exception as e:
                logger.error(f"Error in tool {tool_name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

# Global Claude MCP server instance
claude_mcp_server = ClaudeMCPServer()

async def main():
    """Run the Claude MCP server"""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Claude MCP Server...")
    
    # Initialize Claude integration
    success = await claude_integration.initialize()
    if not success:
        logger.error("Failed to initialize Claude integration")
        sys.exit(1)
    
    logger.info("Claude MCP Server initialized successfully")
    
    # Run the server
    async with claude_mcp_server.server.stdio_server() as (read_stream, write_stream):
        await claude_mcp_server.server.run(
            read_stream, write_stream, claude_mcp_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

