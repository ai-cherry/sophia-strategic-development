#!/usr/bin/env python3
"""
Coding Memory MCP Server - Cursor AI Integration
===============================================

MCP server that exposes the unified memory service as tools for Cursor AI.
Provides coding context retrieval, pattern storage, and AI development assistance.

Features:
- Store and retrieve coding patterns
- Context-aware code suggestions
- Development decision memory
- Performance tracking and analytics

Port: 9200 (coding-memory)
Protocol: MCP (Model Context Protocol)

Date: January 15, 2025
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import our unified memory service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.coding_mcp_unified_memory_service import (
    get_coding_memory_service,
    coding_memory_context,
    MemoryNamespace,
    CodingMemoryItem
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Coding Memory")

@mcp.tool()
async def store_coding_pattern(
    content: str,
    pattern_type: str = "general",
    language: str = "python",
    description: str = "",
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Store a coding pattern or development decision in memory.
    
    Args:
        content: The code pattern, snippet, or development decision
        pattern_type: Type of pattern (api, database, testing, security, etc.)
        language: Programming language (python, typescript, etc.)
        description: Human-readable description of the pattern
        tags: List of tags for categorization
    
    Returns:
        Dictionary with memory_id and confirmation
    """
    try:
        async with coding_memory_context() as service:
            # Determine namespace based on pattern type
            namespace_mapping = {
                "api": MemoryNamespace.CODING,
                "database": MemoryNamespace.CODING,
                "testing": MemoryNamespace.TESTING,
                "security": MemoryNamespace.CODING,
                "architecture": MemoryNamespace.ARCHITECTURE,
                "documentation": MemoryNamespace.DOCUMENTATION
            }
            
            namespace = namespace_mapping.get(pattern_type.lower(), MemoryNamespace.CODING)
            
            metadata = {
                "pattern_type": pattern_type,
                "language": language,
                "description": description,
                "tags": tags or [],
                "stored_by": "cursor_ai",
                "timestamp": datetime.now().isoformat()
            }
            
            memory_id = await service.store_coding_memory(
                content=content,
                namespace=namespace,
                metadata=metadata,
                user_id="cursor_ai_user"
            )
            
            return {
                "success": True,
                "memory_id": memory_id,
                "message": f"Stored {pattern_type} pattern in {namespace.value} namespace",
                "namespace": namespace.value,
                "tags": tags or []
            }
            
    except Exception as e:
        logger.error(f"Failed to store coding pattern: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to store coding pattern"
        }

@mcp.tool()
async def search_coding_patterns(
    query: str,
    pattern_type: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search for relevant coding patterns and development decisions.
    
    Args:
        query: Search query (natural language or keywords)
        pattern_type: Filter by pattern type (api, database, testing, etc.)
        language: Filter by programming language
        limit: Maximum number of results to return
    
    Returns:
        Dictionary with search results and metadata
    """
    try:
        async with coding_memory_context() as service:
            # Determine namespace to search
            namespace = None
            if pattern_type:
                namespace_mapping = {
                    "api": MemoryNamespace.CODING,
                    "database": MemoryNamespace.CODING,
                    "testing": MemoryNamespace.TESTING,
                    "security": MemoryNamespace.CODING,
                    "architecture": MemoryNamespace.ARCHITECTURE,
                    "documentation": MemoryNamespace.DOCUMENTATION
                }
                namespace = namespace_mapping.get(pattern_type.lower())
            
            # Enhance query with filters
            enhanced_query = query
            if language:
                enhanced_query += f" {language}"
            if pattern_type:
                enhanced_query += f" {pattern_type}"
            
            results = await service.search_coding_memory(
                query=enhanced_query,
                namespace=namespace,
                limit=limit,
                user_id="cursor_ai_user"
            )
            
            # Format results for Cursor AI
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "content": result.content,
                    "namespace": result.namespace.value,
                    "relevance_score": result.relevance_score,
                    "usage_count": result.usage_count,
                    "metadata": result.metadata,
                    "timestamp": result.timestamp.isoformat()
                }
                formatted_results.append(formatted_result)
            
            return {
                "success": True,
                "results": formatted_results,
                "total_found": len(formatted_results),
                "query": query,
                "filters": {
                    "pattern_type": pattern_type,
                    "language": language,
                    "namespace": namespace.value if namespace else "all"
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to search coding patterns: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": [],
            "message": "Failed to search coding patterns"
        }

@mcp.tool()
async def get_coding_context(
    context_type: str,
    current_file: Optional[str] = None,
    current_function: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get relevant coding context for current development task.
    
    Args:
        context_type: Type of context needed (patterns, errors, testing, api, etc.)
        current_file: Current file being worked on
        current_function: Current function being developed
    
    Returns:
        Dictionary with relevant context and suggestions
    """
    try:
        async with coding_memory_context() as service:
            # Get context from memory service
            context_results = await service.get_coding_context(
                context_type=context_type,
                namespace=MemoryNamespace.CODING,
                limit=5
            )
            
            # Format context for AI assistance
            context_items = []
            for item in context_results:
                context_items.append({
                    "pattern": item.content,
                    "description": item.metadata.get("description", ""),
                    "language": item.metadata.get("language", ""),
                    "relevance": item.relevance_score,
                    "usage_count": item.usage_count,
                    "tags": item.metadata.get("tags", [])
                })
            
            # Generate suggestions based on context
            suggestions = await _generate_context_suggestions(
                context_type, context_items, current_file, current_function
            )
            
            return {
                "success": True,
                "context_type": context_type,
                "context_items": context_items,
                "suggestions": suggestions,
                "current_context": {
                    "file": current_file,
                    "function": current_function
                },
                "total_patterns": len(context_items)
            }
            
    except Exception as e:
        logger.error(f"Failed to get coding context: {e}")
        return {
            "success": False,
            "error": str(e),
            "context_items": [],
            "message": "Failed to get coding context"
        }

@mcp.tool()
async def remember_development_decision(
    decision: str,
    reasoning: str,
    impact: str,
    alternatives_considered: List[str] = None
) -> Dict[str, Any]:
    """
    Remember an important development decision for future reference.
    
    Args:
        decision: The decision that was made
        reasoning: Why this decision was made
        impact: Expected impact of this decision
        alternatives_considered: Other options that were considered
    
    Returns:
        Dictionary with memory_id and confirmation
    """
    try:
        async with coding_memory_context() as service:
            content = f"""
DEVELOPMENT DECISION: {decision}

REASONING: {reasoning}

EXPECTED IMPACT: {impact}

ALTERNATIVES CONSIDERED: {', '.join(alternatives_considered or ['None specified'])}

DECISION DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            metadata = {
                "type": "development_decision",
                "decision": decision,
                "reasoning": reasoning,
                "impact": impact,
                "alternatives": alternatives_considered or [],
                "recorded_by": "cursor_ai",
                "importance": "high"
            }
            
            memory_id = await service.store_coding_memory(
                content=content,
                namespace=MemoryNamespace.ARCHITECTURE,
                metadata=metadata,
                user_id="cursor_ai_user"
            )
            
            return {
                "success": True,
                "memory_id": memory_id,
                "message": "Development decision recorded successfully",
                "decision": decision,
                "namespace": "architecture"
            }
            
    except Exception as e:
        logger.error(f"Failed to record development decision: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to record development decision"
        }

@mcp.tool()
async def analyze_code_quality(
    code: str,
    language: str = "python",
    check_patterns: bool = True
) -> Dict[str, Any]:
    """
    Analyze code quality and suggest improvements based on stored patterns.
    
    Args:
        code: Code to analyze
        language: Programming language of the code
        check_patterns: Whether to check against stored patterns
    
    Returns:
        Dictionary with quality analysis and suggestions
    """
    try:
        async with coding_memory_context() as service:
            suggestions = []
            pattern_matches = []
            
            if check_patterns:
                # Search for related patterns
                pattern_results = await service.search_coding_memory(
                    query=f"best practices {language} code quality",
                    namespace=MemoryNamespace.CODING,
                    limit=5
                )
                
                for pattern in pattern_results:
                    pattern_matches.append({
                        "pattern": pattern.content,
                        "description": pattern.metadata.get("description", ""),
                        "relevance": pattern.relevance_score
                    })
            
            # Basic code analysis (simplified)
            analysis = _perform_basic_code_analysis(code, language)
            
            return {
                "success": True,
                "analysis": analysis,
                "pattern_matches": pattern_matches,
                "suggestions": suggestions,
                "language": language,
                "patterns_checked": check_patterns
            }
            
    except Exception as e:
        logger.error(f"Failed to analyze code quality: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze code quality"
        }

@mcp.tool()
async def get_memory_stats() -> Dict[str, Any]:
    """
    Get statistics about the coding memory system.
    
    Returns:
        Dictionary with comprehensive memory statistics
    """
    try:
        async with coding_memory_context() as service:
            health_status = await service.get_health_status()
            
            return {
                "success": True,
                "stats": health_status,
                "service": "coding_mcp_unified_memory",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get memory statistics"
        }

# Helper functions
async def _generate_context_suggestions(
    context_type: str,
    context_items: List[Dict],
    current_file: Optional[str],
    current_function: Optional[str]
) -> List[str]:
    """Generate context-aware suggestions"""
    suggestions = []
    
    if context_type == "patterns":
        suggestions.append("Consider using established patterns from your codebase")
        if context_items:
            suggestions.append(f"Found {len(context_items)} similar patterns")
    
    elif context_type == "errors":
        suggestions.append("Check error handling patterns")
        suggestions.append("Consider adding try-catch blocks")
    
    elif context_type == "testing":
        suggestions.append("Add unit tests for new functionality")
        if current_function:
            suggestions.append(f"Create test for function: {current_function}")
    
    elif context_type == "api":
        suggestions.append("Follow REST API conventions")
        suggestions.append("Consider rate limiting and authentication")
    
    elif context_type == "database":
        suggestions.append("Use connection pooling")
        suggestions.append("Consider query optimization")
    
    elif context_type == "security":
        suggestions.append("Validate all input parameters")
        suggestions.append("Use environment variables for secrets")
    
    return suggestions

def _perform_basic_code_analysis(code: str, language: str) -> Dict[str, Any]:
    """Perform basic code analysis"""
    analysis = {
        "lines_of_code": len(code.split('\n')),
        "language": language,
        "issues": [],
        "complexity": "medium"
    }
    
    # Basic Python analysis
    if language == "python":
        if "print(" in code:
            analysis["issues"].append("Consider using logging instead of print statements")
        
        if "import *" in code:
            analysis["issues"].append("Avoid wildcard imports")
        
        if len(code.split('\n')) > 50:
            analysis["complexity"] = "high"
            analysis["issues"].append("Function is quite long, consider breaking it down")
    
    return analysis

async def main():
    """Run the Coding Memory MCP Server"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🧠 Starting Coding Memory MCP Server on port 9200")
    
    # Initialize the memory service
    try:
        async with coding_memory_context() as service:
            health = await service.get_health_status()
            logger.info(f"✅ Memory service ready: {health['status']}")
    except Exception as e:
        logger.error(f"❌ Memory service initialization failed: {e}")
        return
    
    # Run the MCP server
    async with mcp.stdio.stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="coding-memory",
                server_version="1.0.0",
                capabilities=mcp.server.ServerCapabilities(
                    tools=mcp.server.ToolsCapability(),
                )
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 