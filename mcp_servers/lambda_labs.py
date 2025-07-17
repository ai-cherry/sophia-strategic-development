"""
Lambda Labs MCP Server with B200 Performance Optimization

Provides high-performance inference capabilities through MCP interface:
- Sub-100ms response times with streaming
- Intelligent model routing based on complexity
- B200 GPU optimization with FP8 quantization
- Performance metrics and monitoring
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, ImageContent, EmbeddedResource,
    LogLevel, Prompt, PromptMessage, UserMessage, AssistantMessage
)

# Import our high-performance inference service
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.lambda_inference_service import (
    get_lambda_inference_service,
    ModelComplexity,
    ModelTier
)
from backend.core.auto_esc_config import get_lambda_labs_config

logger = logging.getLogger(__name__)


class LambdaLabsMCPServer:
    """
    MCP Server for Lambda Labs inference with B200 optimization
    
    Features:
    - High-performance text generation
    - Model selection based on complexity
    - Streaming responses with <100ms TTFT
    - Performance monitoring and metrics
    - Cost optimization recommendations
    """
    
    def __init__(self):
        self.server = Server("lambda-labs")
        self.inference_service = None
        self.config = get_lambda_labs_config()
        
        # Register handlers
        self._register_handlers()
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens = 0
        self.start_time = datetime.now()
        
    def _register_handlers(self):
        """Register all MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available Lambda Labs tools"""
            return [
                Tool(
                    name="generate",
                    description="Generate text using Lambda Labs B200-optimized inference",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Input prompt for generation"
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Maximum tokens to generate (default: 1000)",
                                "default": 1000
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Sampling temperature 0-2 (default: 0.7)",
                                "default": 0.7
                            },
                            "stream": {
                                "type": "boolean",
                                "description": "Stream the response (default: true)",
                                "default": True
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="generate_advanced",
                    description="Generate with advanced B200 optimization options",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Input prompt"
                            },
                            "model": {
                                "type": "string",
                                "description": "Force specific model (auto-selected by default)",
                                "enum": [
                                    "llama-8b-fp8",
                                    "llama-70b-fp8", 
                                    "llama-405b",
                                    "deepseek-v3",
                                    "qwen-72b"
                                ]
                            },
                            "use_speculative": {
                                "type": "boolean",
                                "description": "Enable speculative decoding for 2-3x speedup",
                                "default": True
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Request priority 0-10 (higher = faster)",
                                "default": 0
                            },
                            "max_tokens": {
                                "type": "integer",
                                "default": 1000
                            },
                            "temperature": {
                                "type": "number",
                                "default": 0.7
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="analyze_complexity",
                    description="Analyze prompt complexity for optimal model routing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Prompt to analyze"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="get_performance_stats",
                    description="Get current performance statistics and B200 metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="health_check",
                    description="Check Lambda Labs service health and GPU status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute Lambda Labs tools"""
            
            # Ensure service is initialized
            if self.inference_service is None:
                self.inference_service = await get_lambda_inference_service()
            
            try:
                if name == "generate":
                    return await self._handle_generate(arguments)
                elif name == "generate_advanced":
                    return await self._handle_generate_advanced(arguments)
                elif name == "analyze_complexity":
                    return await self._handle_analyze_complexity(arguments)
                elif name == "get_performance_stats":
                    return await self._handle_get_performance_stats()
                elif name == "health_check":
                    return await self._handle_health_check()
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available prompt templates"""
            return [
                Prompt(
                    name="code_generation",
                    description="Optimized prompt for code generation with B200",
                    arguments=[
                        {
                            "name": "language",
                            "description": "Programming language",
                            "required": True
                        },
                        {
                            "name": "task",
                            "description": "Code task description",
                            "required": True
                        }
                    ]
                ),
                Prompt(
                    name="analysis",
                    description="Complex analysis prompt leveraging 405B model",
                    arguments=[
                        {
                            "name": "topic",
                            "description": "Analysis topic",
                            "required": True
                        },
                        {
                            "name": "depth",
                            "description": "Analysis depth (basic/detailed/comprehensive)",
                            "required": False
                        }
                    ]
                ),
                Prompt(
                    name="chat",
                    description="Conversational prompt with optimal latency",
                    arguments=[
                        {
                            "name": "message",
                            "description": "User message",
                            "required": True
                        }
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, Any]) -> PromptMessage:
            """Get specific prompt template"""
            
            if name == "code_generation":
                language = arguments.get("language", "Python")
                task = arguments.get("task", "")
                
                return PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""You are an expert {language} developer. 
Task: {task}

Please provide clean, efficient, well-documented code following best practices.
Include error handling and type hints where appropriate."""
                    )
                )
                
            elif name == "analysis":
                topic = arguments.get("topic", "")
                depth = arguments.get("depth", "detailed")
                
                depth_instructions = {
                    "basic": "Provide a concise overview",
                    "detailed": "Provide a thorough analysis with examples",
                    "comprehensive": "Provide an exhaustive analysis with multiple perspectives"
                }
                
                return PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analyze the following topic: {topic}

{depth_instructions.get(depth, depth_instructions['detailed'])}

Structure your response with clear sections and actionable insights."""
                    )
                )
                
            elif name == "chat":
                message = arguments.get("message", "")
                
                return PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=message
                    )
                )
                
            else:
                return PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Unknown prompt template: {name}"
                    )
                )
    
    async def _handle_generate(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle standard text generation"""
        prompt = arguments.get("prompt", "")
        max_tokens = arguments.get("max_tokens", 1000)
        temperature = arguments.get("temperature", 0.7)
        stream = arguments.get("stream", True)
        
        # Track request
        self.request_count += 1
        
        # Generate response
        response_text = ""
        token_count = 0
        
        async for token in self.inference_service.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        ):
            response_text += token
            token_count += 1
            
        # Update metrics
        self.total_tokens += token_count
        
        # Get performance metrics
        metrics = self.inference_service.get_latest_metrics()
        
        # Format response with metrics
        result = f"{response_text}\n\n"
        if metrics:
            result += f"---\nPerformance Metrics:\n"
            result += f"• Model: {metrics['model']}\n"
            result += f"• Time to First Token: {metrics['time_to_first_token_ms']:.1f}ms\n"
            result += f"• Tokens/Second: {metrics['tokens_per_second']:.1f}\n"
            result += f"• Total Latency: {metrics['total_latency_ms']:.1f}ms\n"
            
            # Highlight if we hit sub-100ms target
            if metrics['time_to_first_token_ms'] < 100:
                result += f"• ✅ Sub-100ms TTFT achieved!"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_generate_advanced(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle advanced generation with B200 optimizations"""
        prompt = arguments.get("prompt", "")
        
        # Map friendly model names to actual model values
        model_mapping = {
            "llama-8b-fp8": ModelTier.LLAMA_8B_FP8.value,
            "llama-70b-fp8": ModelTier.LLAMA_70B_FP8.value,
            "llama-405b": ModelTier.LLAMA_405B.value,
            "deepseek-v3": ModelTier.DEEPSEEK_V3.value,
            "qwen-72b": ModelTier.QWEN_72B.value
        }
        
        # Build options
        options = {
            "max_tokens": arguments.get("max_tokens", 1000),
            "temperature": arguments.get("temperature", 0.7),
            "use_speculative": arguments.get("use_speculative", True),
            "priority": arguments.get("priority", 0),
            "stream": True
        }
        
        # Add forced model if specified
        if "model" in arguments:
            force_model = model_mapping.get(arguments["model"])
            if force_model:
                options["force_model"] = force_model
        
        # Generate with advanced options
        result = await self.inference_service.generate_with_options(prompt, **options)
        
        # Extract response
        response_text = ""
        if isinstance(result["response"], str):
            response_text = result["response"]
        else:
            # Handle streaming response
            async for token in result["response"]:
                response_text += token
        
        # Format response with detailed metrics
        output = f"{response_text}\n\n"
        output += f"---\nAdvanced Generation Details:\n"
        output += f"• Model Used: {result['model_used']}\n"
        
        if result['metrics']:
            m = result['metrics']
            output += f"• Time to First Token: {m['time_to_first_token_ms']:.1f}ms\n"
            output += f"• Tokens/Second: {m['tokens_per_second']:.1f}\n"
            output += f"• Quantization: {m['quantization']}\n"
            output += f"• Batch Size: {m['batch_size']}\n"
            
            # Performance achievements
            if m['time_to_first_token_ms'] < 100:
                output += f"\n🏆 Performance Achievements:\n"
                output += f"• ✅ Sub-100ms TTFT ({m['time_to_first_token_ms']:.1f}ms)\n"
            if m['tokens_per_second'] > 100:
                output += f"• ✅ >100 tokens/second ({m['tokens_per_second']:.1f})\n"
            if m['quantization'] == "FP8":
                output += f"• ✅ FP8 quantization enabled\n"
        
        return [TextContent(type="text", text=output)]
    
    async def _handle_analyze_complexity(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Analyze prompt complexity"""
        prompt = arguments.get("prompt", "")
        
        # Analyze complexity
        complexity = self.inference_service._analyze_complexity(prompt)
        selected_model = self.inference_service._select_model(complexity)
        
        # Token estimation
        token_count = len(prompt.split())
        
        # Cost estimation (simplified)
        cost_per_1k_tokens = {
            ModelTier.LLAMA_8B_FP8.value: 0.0002,
            ModelTier.LLAMA_70B_FP8.value: 0.001,
            ModelTier.LLAMA_405B.value: 0.005,
            ModelTier.DEEPSEEK_V3.value: 0.0008,
            ModelTier.QWEN_72B.value: 0.0007
        }
        
        estimated_cost = (token_count / 1000) * cost_per_1k_tokens.get(selected_model, 0.001)
        
        result = f"Prompt Complexity Analysis:\n\n"
        result += f"• Complexity Level: {complexity.value.upper()}\n"
        result += f"• Estimated Tokens: ~{token_count}\n"
        result += f"• Recommended Model: {selected_model}\n"
        result += f"• Estimated Cost: ${estimated_cost:.4f}\n\n"
        
        result += "Model Selection Rationale:\n"
        if complexity == ModelComplexity.SIMPLE:
            result += "• Simple factual query → 8B FP8 model for fastest response\n"
            result += "• Expected TTFT: <50ms with FP8 optimization\n"
        elif complexity == ModelComplexity.MODERATE:
            result += "• Moderate reasoning task → 70B FP8 model for balance\n"
            result += "• Expected TTFT: <100ms with speculative decoding\n"
        elif complexity == ModelComplexity.COMPLEX:
            result += "• Complex multi-step problem → DeepSeek V3 for reasoning\n"
            result += "• Optimized for accuracy over speed\n"
        else:
            result += "• Extreme long context → 405B model for best quality\n"
            result += "• Maximum context window and reasoning capability\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_get_performance_stats(self) -> List[TextContent]:
        """Get performance statistics"""
        stats = self.inference_service.get_performance_stats()
        
        # Calculate session stats
        runtime = (datetime.now() - self.start_time).total_seconds()
        requests_per_minute = (self.request_count / runtime) * 60 if runtime > 0 else 0
        
        result = "Lambda Labs Performance Statistics:\n\n"
        result += f"📊 Current Session:\n"
        result += f"• Total Requests: {self.request_count}\n"
        result += f"• Total Tokens Generated: {self.total_tokens:,}\n"
        result += f"• Requests/Minute: {requests_per_minute:.1f}\n"
        result += f"• Runtime: {runtime/60:.1f} minutes\n\n"
        
        result += f"⚡ Performance Metrics:\n"
        result += f"• Avg Time to First Token: {stats['avg_time_to_first_token']:.1f}ms\n"
        result += f"• Avg Tokens/Second: {stats['avg_tokens_per_second']:.1f}\n"
        result += f"• Avg Latency: {stats['avg_latency']:.1f}ms\n"
        result += f"• P99 Latency: {stats['p99_latency']:.1f}ms\n"
        result += f"• Requests Processed: {stats['requests_processed']}\n\n"
        
        result += f"🎯 Model Usage:\n"
        for model in stats.get('models_used', []):
            result += f"• {model}\n"
        
        result += f"\n🔧 Optimization Stats:\n"
        result += f"• Avg Batch Size: {stats.get('avg_batch_size', 0):.1f}\n"
        
        quant_stats = stats.get('quantization_stats', {})
        if quant_stats:
            result += f"• FP8 Requests: {quant_stats.get('FP8', 0)}\n"
            result += f"• FP16 Requests: {quant_stats.get('FP16', 0)}\n"
        
        # Performance achievements
        if stats['avg_time_to_first_token'] < 100:
            result += f"\n🏆 Achievements:\n"
            result += f"• ✅ Sub-100ms avg TTFT achieved!\n"
        if stats['avg_tokens_per_second'] > 100:
            result += f"• ✅ >100 tokens/second average!\n"
        
        return [TextContent(type="text", text=result)]
    
    async def _handle_health_check(self) -> List[TextContent]:
        """Check service health"""
        health = await self.inference_service.health_check()
        
        result = "Lambda Labs Service Health Check:\n\n"
        result += f"• Status: {health['status'].upper()}\n"
        
        if health['status'] == 'healthy':
            result += f"• API Latency: {health['latency_ms']:.1f}ms\n"
            result += f"• Models Available: {len(health['models_available'])}\n"
            
            result += f"\n📋 Available Models:\n"
            for model in health['models_available']:
                result += f"  • {model}\n"
            
            result += f"\n⚙️ B200 Optimizations:\n"
            opts = health['b200_optimization']
            result += f"  • FP8 Quantization: {'✅' if opts['fp8_enabled'] else '❌'}\n"
            result += f"  • Speculative Decoding: {'✅' if opts['speculative_decoding'] else '❌'}\n"
            result += f"  • Continuous Batching: {'✅' if opts['continuous_batching'] else '❌'}\n"
            result += f"  • HTTP/2 Pooling: {'✅' if opts['http2_pooling'] else '❌'}\n"
            
            # Add performance summary
            if 'performance_stats' in health:
                stats = health['performance_stats']
                result += f"\n📊 Recent Performance:\n"
                result += f"  • Avg TTFT: {stats['avg_time_to_first_token']:.1f}ms\n"
                result += f"  • Avg TPS: {stats['avg_tokens_per_second']:.1f}\n"
        else:
            result += f"• Error: {health.get('error', 'Unknown error')}\n"
            result += f"\n⚠️ Service is currently unavailable\n"
        
        return [TextContent(type="text", text=result)]
    
    async def run(self):
        """Run the MCP server"""
        # Initialize inference service
        self.inference_service = await get_lambda_inference_service()
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run server
    server = LambdaLabsMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
