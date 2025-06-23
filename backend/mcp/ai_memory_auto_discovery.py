"""
AI Memory Auto-Discovery for Cursor IDE Integration
Automatically detects and stores development context, patterns, and decisions
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

from backend.mcp.ai_memory_mcp_server import AiMemoryMCPServer, MemoryCategory

logger = logging.getLogger(__name__)


class CursorContextDetector:
    """Detects development context from Cursor IDE interactions"""
    
    def __init__(self, ai_memory: AiMemoryMCPServer):
        self.ai_memory = ai_memory
        self.patterns = {
            'architecture_keywords': [
                'architecture', 'design pattern', 'microservice', 'database schema',
                'api design', 'system design', 'infrastructure', 'deployment',
                'scalability', 'performance', 'security architecture'
            ],
            'bug_keywords': [
                'bug', 'error', 'exception', 'traceback', 'fix', 'debug',
                'issue', 'problem', 'crash', 'failure', 'broken'
            ],
            'decision_keywords': [
                'decision', 'choose', 'selected', 'approach', 'strategy',
                'implementation', 'solution', 'alternative', 'trade-off'
            ],
            'workflow_keywords': [
                'workflow', 'process', 'procedure', 'steps', 'methodology',
                'best practice', 'convention', 'standard', 'guideline'
            ]
        }
        self.recent_contexts: List[Dict[str, Any]] = []
        self.context_window = timedelta(minutes=30)
    
    def detect_context_type(self, content: str) -> str:
        """Detect the type of development context from content"""
        content_lower = content.lower()
        
        # Count keyword matches for each category
        scores = {}
        for category, keywords in self.patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return MemoryCategory.CODE_DECISION
        
        # Return category with highest score
        max_category = max(scores.items(), key=lambda x: x[1])[0]
        
        # Map to memory categories
        category_mapping = {
            'architecture_keywords': MemoryCategory.ARCHITECTURE,
            'bug_keywords': MemoryCategory.BUG_SOLUTION,
            'decision_keywords': MemoryCategory.CODE_DECISION,
            'workflow_keywords': MemoryCategory.WORKFLOW
        }
        
        return category_mapping.get(max_category, MemoryCategory.CODE_DECISION)
    
    def extract_tags(self, content: str, file_path: Optional[str] = None) -> List[str]:
        """Extract relevant tags from content and context"""
        tags = set()
        content_lower = content.lower()
        
        # Technology tags
        tech_patterns = {
            'python': r'\\b(python|py|fastapi|django|flask)\\b',
            'javascript': r'\\b(javascript|js|node|react|vue|angular)\\b',
            'typescript': r'\\b(typescript|ts)\\b',
            'docker': r'\\b(docker|container|dockerfile)\\b',
            'database': r'\\b(database|sql|postgresql|redis|mongodb)\\b',
            'api': r'\\b(api|rest|graphql|endpoint)\\b',
            'mcp': r'\\b(mcp|server|tool)\\b',
            'ai': r'\\b(ai|llm|openai|anthropic|model)\\b'
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, content_lower):
                tags.add(tech)
        
        # File-based tags
        if file_path:
            file_path_obj = Path(file_path)
            tags.add(file_path_obj.suffix[1:] if file_path_obj.suffix else 'unknown')
            
            # Directory-based tags
            parts = file_path_obj.parts
            if 'backend' in parts:
                tags.add('backend')
            if 'frontend' in parts:
                tags.add('frontend')
            if 'mcp' in parts:
                tags.add('mcp-server')
            if 'api' in parts:
                tags.add('api')
        
        # Add timestamp-based tags
        now = datetime.now()
        tags.add(f"week-{now.strftime('%Y-W%U')}")
        tags.add(f"month-{now.strftime('%Y-%m')}")
        
        return list(tags)
    
    def should_store_automatically(self, content: str, context: Dict[str, Any]) -> bool:
        """Determine if content should be automatically stored"""
        content_lower = content.lower()
        
        # Always store if it contains decision-making language
        decision_indicators = [
            'decided to', 'chose to', 'implemented', 'solution is',
            'approach is', 'will use', 'best practice', 'pattern'
        ]
        
        if any(indicator in content_lower for indicator in decision_indicators):
            return True
        
        # Store if it's a substantial technical discussion
        if len(content.split()) > 50:  # More than 50 words
            tech_score = sum(1 for keyword in [
                'implementation', 'architecture', 'design', 'pattern',
                'solution', 'approach', 'strategy', 'framework'
            ] if keyword in content_lower)
            
            if tech_score >= 2:
                return True
        
        # Store if it contains code examples
        if '```' in content or 'def ' in content or 'class ' in content:
            return True
        
        return False
    
    async def process_cursor_interaction(
        self, 
        content: str, 
        interaction_type: str = "chat",
        file_path: Optional[str] = None,
        user_intent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Process a Cursor IDE interaction and potentially store it"""
        
        # Clean and prepare content
        cleaned_content = self._clean_content(content)
        
        if not cleaned_content or len(cleaned_content.strip()) < 20:
            return None
        
        # Detect context
        context_type = self.detect_context_type(cleaned_content)
        tags = self.extract_tags(cleaned_content, file_path)
        
        # Add interaction-specific tags
        if interaction_type:
            tags.append(f"interaction-{interaction_type}")
        if user_intent:
            tags.append(f"intent-{user_intent}")
        
        # Check if we should store automatically
        should_store = self.should_store_automatically(cleaned_content, {
            'type': interaction_type,
            'file_path': file_path,
            'intent': user_intent
        })
        
        if should_store:
            # Create enriched content with metadata
            enriched_content = self._create_enriched_content(
                cleaned_content, interaction_type, file_path, user_intent
            )
            
            # Store in AI memory
            result = await self.ai_memory.store_memory(
                enriched_content, context_type, tags
            )
            
            logger.info(f"Auto-stored memory: {result['id']} (category: {context_type})")
            return result
        
        return None
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content for storage"""
        # Remove excessive whitespace
        content = re.sub(r'\\s+', ' ', content.strip())
        
        # Remove cursor-specific artifacts
        content = re.sub(r'@\\w+\\s*', '', content)  # Remove @mentions
        content = re.sub(r'^\\s*User:\\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\\s*Assistant:\\s*', '', content, flags=re.MULTILINE)
        
        return content
    
    def _create_enriched_content(
        self, 
        content: str, 
        interaction_type: str,
        file_path: Optional[str],
        user_intent: Optional[str]
    ) -> str:
        """Create enriched content with metadata"""
        metadata = {
            'original_content': content,
            'interaction_type': interaction_type,
            'timestamp': datetime.now().isoformat(),
            'file_context': file_path,
            'user_intent': user_intent,
            'source': 'cursor-ide'
        }
        
        enriched = f"""
CONTEXT: {interaction_type.title()} interaction from Cursor IDE

{content}

METADATA:
- File: {file_path or 'N/A'}
- Intent: {user_intent or 'General discussion'}
- Timestamp: {metadata['timestamp']}
- Source: Cursor IDE Auto-Discovery
        """.strip()
        
        return enriched


# Enhanced MCP Server with auto-discovery
class EnhancedAiMemoryMCPServer(AiMemoryMCPServer):
    """Enhanced AI Memory MCP Server with Cursor IDE integration"""
    
    def __init__(self):
        super().__init__()
        self.context_detector = CursorContextDetector(self)
        self.auto_discovery_enabled = True
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return enhanced tools with auto-discovery capabilities"""
        base_tools = super().get_tools()
        
        enhanced_tools = [
            {
                "name": "auto_store_context",
                "description": "Automatically store development context from Cursor IDE interactions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The interaction content to analyze and potentially store"
                        },
                        "interaction_type": {
                            "type": "string",
                            "description": "Type of interaction (chat, code_review, debug, etc.)",
                            "default": "chat"
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Current file path for context"
                        },
                        "user_intent": {
                            "type": "string",
                            "description": "User's intent or goal"
                        }
                    },
                    "required": ["content"]
                }
            }
        ]
        
        return base_tools + enhanced_tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced tools"""
        if tool_name == "auto_store_context":
            result = await self.context_detector.process_cursor_interaction(
                content=parameters.get("content", ""),
                interaction_type=parameters.get("interaction_type", "chat"),
                file_path=parameters.get("file_path"),
                user_intent=parameters.get("user_intent")
            )
            return result or {"status": "not_stored", "reason": "Content did not meet auto-storage criteria"}
        
        else:
            return await super().execute_tool(tool_name, parameters)


# Global instance for use in MCP server
enhanced_ai_memory_server = EnhancedAiMemoryMCPServer()
