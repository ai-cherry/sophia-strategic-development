"""
Sophia Intent Engine - Core intent classification for natural language commands
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import asyncio
import logging

from backend.services.unified_llm_service import get_unified_llm_service, TaskType, LLMRequest, TaskType
from backend.services.unified_chat_service import ChatContext
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer

logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    CODE_MODIFICATION = "code_modification"
    CODE_GENERATION = "code_generation"
    INFRASTRUCTURE = "infrastructure"
    BUSINESS_QUERY = "business_query"
    SYSTEM_COMMAND = "system_command"
    HELP = "help"
    SEARCH = "search"
    MEMORY = "memory"


@dataclass
class CodeModificationIntent:
    action: str  # modify, create, delete, refactor, fix
    target_file: Optional[str]
    description: str
    constraints: Dict[str, Any]
    requires_approval: bool
    confidence: float


@dataclass
class InfrastructureIntent:
    action: str  # deploy, scale, configure, monitor
    target: str  # service, server, database
    parameters: Dict[str, Any]
    risk_level: str  # low, medium, high, critical


class SophiaIntentEngine:
    """
    Core intent classification engine for Sophia AI
    """

    def __init__(self):
        self.smart_ai = await get_unified_llm_service()
        self.ai_memory = EnhancedAiMemoryMCPServer()
        self.code_patterns = self._load_code_patterns()
        self.infrastructure_patterns = self._load_infrastructure_patterns()

    async def classify_intent(
        self,
        message: str,
        context: ChatContext
    ) -> Tuple[IntentCategory, Any]:
        """
        Classify user intent with advanced pattern matching and AI
        """
        logger.info(f"Classifying intent for message: {message[:100]}...")

        # Quick pattern matching for common intents
        if self._is_code_modification(message):
            intent = await self._parse_code_intent(message, context)
            return IntentCategory.CODE_MODIFICATION, intent

        if self._is_infrastructure_command(message):
            intent = await self._parse_infrastructure_intent(message, context)
            return IntentCategory.INFRASTRUCTURE, intent

        if self._is_memory_query(message):
            return IntentCategory.MEMORY, {"query": message}

        # Use AI for complex classification
        return await self._classify_with_ai(message, context)

    def _is_code_modification(self, message: str) -> bool:
        """Detect code modification requests"""
        code_keywords = [
            r'\b(change|modify|update|fix|refactor|add|create|implement|write|delete|remove|rename)\b',
            r'\b(function|class|method|variable|import|export|component)\b',
            r'\b(file|module|package|library)\b'
        ]

        file_patterns = [
            r'\b\w+\.(py|ts|tsx|js|jsx|java|cpp|go|rs|rb|php)\b',
            r'`[^`]+`',  # Code in backticks
            r'"[^"]+\.(py|ts|tsx|js|jsx|java|cpp|go|rs|rb|php)"',  # Quoted filenames
        ]

        message_lower = message.lower()

        # Check for code keywords
        has_code_keyword = any(
            re.search(pattern, message_lower)
            for pattern in code_keywords
        )

        # Check for file references
        has_file_reference = any(
            re.search(pattern, message, re.IGNORECASE)
            for pattern in file_patterns
        )

        return has_code_keyword or has_file_reference

    def _is_infrastructure_command(self, message: str) -> bool:
        """Detect infrastructure commands"""
        infra_keywords = [
            r'\b(deploy|scale|configure|restart|stop|start|monitor)\b',
            r'\b(server|service|container|kubernetes|k8s|docker|pulumi)\b',
            r'\b(database|redis|postgres|snowflake)\b',
            r'\b(lambda|vercel|aws|gcp|azure)\b'
        ]

        message_lower = message.lower()
        return any(
            re.search(pattern, message_lower)
            for pattern in infra_keywords
        )

    def _is_memory_query(self, message: str) -> bool:
        """Detect memory/history queries"""
        memory_patterns = [
            r'\b(what|when|how) did (i|we)',
            r'\b(remember|recall|history|previous|last)\b',
            r'\b(show|find|search) (me )?(previous|past|earlier)\b'
        ]

        message_lower = message.lower()
        return any(
            re.search(pattern, message_lower)
            for pattern in memory_patterns
        )

    async def _parse_code_intent(
        self,
        message: str,
        context: ChatContext
    ) -> CodeModificationIntent:
        """Parse code modification intent from message"""

        # Extract file path if mentioned
        file_path = self._extract_file_path(message)

        # Determine action
        action = self._determine_code_action(message)

        # Extract constraints
        constraints = {
            "preserve_functionality": "don't break" not in message.lower(),
            "add_tests": "test" in message.lower(),
            "add_docs": "document" in message.lower() or "docs" in message.lower(),
            "style_guide": "pep8" in message.lower() or "black" in message.lower()
        }

        # Determine if approval is needed
        requires_approval = self._requires_approval(action, file_path)

        # Calculate confidence
        confidence = 0.9 if file_path else 0.6

        return CodeModificationIntent(
            action=action,
            target_file=file_path,
            description=message,
            constraints=constraints,
            requires_approval=requires_approval,
            confidence=confidence
        )

    def _extract_file_path(self, message: str) -> Optional[str]:
        """Extract file path from message"""
        # Look for quoted paths
        quoted_pattern = r'["\']([^"\']+\.(py|ts|tsx|js|jsx|java|cpp|go|rs|rb|php))["\']'
        match = re.search(quoted_pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

        # Look for backtick paths
        backtick_pattern = r'`([^`]+\.(py|ts|tsx|js|jsx|java|cpp|go|rs|rb|php))`'
        match = re.search(backtick_pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

        # Look for unquoted paths
        path_pattern = r'\b([\w/]+\.(py|ts|tsx|js|jsx|java|cpp|go|rs|rb|php))\b'
        match = re.search(path_pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def _determine_code_action(self, message: str) -> str:
        """Determine the code action from message"""
        message_lower = message.lower()

        action_map = {
            "create": ["create", "add", "new", "implement"],
            "modify": ["modify", "change", "update", "edit"],
            "fix": ["fix", "repair", "correct", "resolve"],
            "refactor": ["refactor", "restructure", "reorganize", "clean"],
            "delete": ["delete", "remove", "drop"],
            "rename": ["rename", "move"],
        }

        for action, keywords in action_map.items():
            if any(keyword in message_lower for keyword in keywords):
                return action

        return "modify"  # Default action

    def _requires_approval(self, action: str, file_path: Optional[str]) -> bool:
        """Determine if action requires approval"""
        # Always require approval for deletions
        if action == "delete":
            return True

        # Require approval for critical files
        if file_path:
            critical_patterns = [
                r'(config|settings|env)',
                r'(main|app|index)\.',
                r'(requirements|package|gemfile)',
                r'(docker|compose)',
                r'\.github',
            ]

            if any(re.search(pattern, file_path, re.IGNORECASE) for pattern in critical_patterns):
                return True

        # Default based on action
        return action in ["delete", "rename", "refactor"]

    async def _parse_infrastructure_intent(
        self,
        message: str,
        context: ChatContext
    ) -> InfrastructureIntent:
        """Parse infrastructure intent from message"""

        # Determine action
        action = "deploy"  # Default
        if "scale" in message.lower():
            action = "scale"
        elif "restart" in message.lower():
            action = "restart"
        elif "stop" in message.lower():
            action = "stop"
        elif "configure" in message.lower():
            action = "configure"

        # Extract target
        target = self._extract_infrastructure_target(message)

        # Extract parameters
        parameters = {}

        # Determine risk level
        risk_level = self._assess_infrastructure_risk(action, target)

        return InfrastructureIntent(
            action=action,
            target=target,
            parameters=parameters,
            risk_level=risk_level
        )

    def _extract_infrastructure_target(self, message: str) -> str:
        """Extract infrastructure target from message"""
        targets = {
            "mcp": ["mcp", "server"],
            "database": ["database", "db", "postgres", "redis"],
            "api": ["api", "backend", "fastapi"],
            "frontend": ["frontend", "dashboard", "ui"],
            "all": ["everything", "all", "system"]
        }

        message_lower = message.lower()
        for target, keywords in targets.items():
            if any(keyword in message_lower for keyword in keywords):
                return target

        return "unknown"

    def _assess_infrastructure_risk(self, action: str, target: str) -> str:
        """Assess risk level of infrastructure action"""
        high_risk_actions = ["delete", "stop", "scale"]
        critical_targets = ["database", "all"]

        if action in high_risk_actions and target in critical_targets:
            return "critical"
        elif action in high_risk_actions or target in critical_targets:
            return "high"
        elif action in ["restart", "configure"]:
            return "medium"
        else:
            return "low"

    async def _classify_with_ai(
        self,
        message: str,
        context: ChatContext
    ) -> Tuple[IntentCategory, Dict[str, Any]]:
        """Use AI for complex intent classification"""

        prompt = f"""
        Classify the following user message into one of these categories:
        - CODE_MODIFICATION: User wants to modify, create, or delete code
        - CODE_GENERATION: User wants to generate new code from scratch
        - INFRASTRUCTURE: User wants to manage infrastructure (deploy, scale, etc)
        - BUSINESS_QUERY: User is asking about business data or metrics
        - SYSTEM_COMMAND: User wants to control the system (restart, status, etc)
        - HELP: User is asking for help or documentation
        - SEARCH: User wants to search for something
        - MEMORY: User is asking about previous interactions or history

        Message: {message}
        Context: {context.value if context else 'general'}

        Respond with just the category name and a brief explanation.
        """

        # Create proper LLMRequest
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            task_type=TaskType.ROUTINE_QUERIES,
            user_id="system",
            temperature=0.3,
            max_tokens=100
        )

        response = await self.async for chunk in smart_ai.complete(
    prompt=request.prompt if hasattr(request, 'prompt') else request.get('prompt', ''),
    task_type=TaskType.BUSINESS_INTELLIGENCE,  # TODO: Set appropriate task type
    stream=True
)

        # Parse AI response from LLMResponse object
        response_content = response.content
        category_str = response_content.split('\n')[0].strip()

        try:
            category = IntentCategory(category_str.lower())
        except ValueError:
            # Default to business query if unclear
            category = IntentCategory.BUSINESS_QUERY

        return category, {"ai_classification": response_content}

    def _load_code_patterns(self) -> Dict[str, List[str]]:
        """Load code modification patterns"""
        return {
            "python": [r'\.py$', r'python', r'django', r'flask', r'fastapi'],
            "typescript": [r'\.ts$', r'\.tsx$', r'typescript', r'react', r'angular'],
            "javascript": [r'\.js$', r'\.jsx$', r'javascript', r'node', r'express'],
        }

    def _load_infrastructure_patterns(self) -> Dict[str, List[str]]:
        """Load infrastructure patterns"""
        return {
            "kubernetes": [r'k8s', r'kubernetes', r'kubectl', r'pod', r'deployment'],
            "docker": [r'docker', r'container', r'dockerfile', r'compose'],
            "cloud": [r'aws', r'gcp', r'azure', r'lambda', r'vercel'],
        }
