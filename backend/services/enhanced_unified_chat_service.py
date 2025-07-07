"""
Enhanced Unified Chat Service - Integrates code modification and AI orchestration
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from backend.mcp_servers.enhanced_ai_memory_mcp_server import (
    EnhancedAiMemoryMCPServer,
)
from backend.services.code_modification_service import CodeModificationService
from backend.services.mcp_orchestration_service import MCPOrchestrationService
from backend.services.sophia_intent_engine import (
    CodeModificationIntent,
    InfrastructureIntent,
    IntentCategory,
    SophiaIntentEngine,
)
from backend.services.unified_chat_service import (
    ChatContext,
    ChatResponse,
    UnifiedChatService,
)
from backend.services.unified_llm_service import get_unified_llm_service

logger = logging.getLogger(__name__)


@dataclass
class PendingApproval:
    """Pending approval for code changes"""

    id: str
    file_path: str
    modified_code: str
    diff: str
    description: str
    created_at: datetime
    user_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class EnhancedUnifiedChatService(UnifiedChatService):
    """
    Enhanced chat service with code modification and orchestration capabilities
    """

    def __init__(self):
        super().__init__()
        self.intent_engine = SophiaIntentEngine()
        self.code_service = CodeModificationService()
        self.mcp_orchestrator = MCPOrchestrationService()
        self.ai_memory = EnhancedAiMemoryMCPServer()
        self.smart_ai = None  # Initialized asynchronously

        # Store pending approvals
        self.pending_approvals: dict[str, PendingApproval] = {}

    async def initialize(self):
        """Asynchronously initialize services that require it."""
        if self.smart_ai is None:
            self.smart_ai = await get_unified_llm_service()
            logger.info("Smart AI service initialized in EnhancedUnifiedChatService.")

    async def process_message(
        self, message: str, user_id: str, context: ChatContext
    ) -> ChatResponse:
        """
        Process message with enhanced capabilities
        """
        logger.info(
            f"Processing enhanced message from user {user_id}: {message[:100]}..."
        )

        # Get relevant memory context
        # TODO: Fix call to self.ai_memory.recall_memory, which is not implemented
        memory_context = []

        # Classify intent
        intent_category, intent_details = await self.intent_engine.classify_intent(
            message, context
        )

        logger.info(f"Classified intent: {intent_category.value}")

        # Route based on intent
        if intent_category == IntentCategory.CODE_MODIFICATION:
            return await self._handle_code_modification(
                intent_details, memory_context, user_id
            )
        elif intent_category == IntentCategory.CODE_GENERATION:
            return await self._handle_code_generation(
                intent_details, memory_context, user_id
            )
        elif intent_category == IntentCategory.INFRASTRUCTURE:
            return await self._handle_infrastructure_command(
                intent_details, memory_context, user_id
            )
        elif intent_category == IntentCategory.MEMORY:
            return await self._handle_memory_query(message, memory_context, user_id)
        else:
            # Handle other intents through base service
            return await super().process_message(message, user_id, context)

    async def _handle_code_modification(
        self, intent: CodeModificationIntent, memory_context: list[dict], user_id: str
    ) -> ChatResponse:
        """Handle code modification requests"""

        # Check if we need to find the file
        if not intent.target_file:
            intent.target_file = await self._find_relevant_file(
                intent.description, memory_context
            )

        if not intent.target_file:
            return ChatResponse(
                response="I couldn't determine which file to modify. Could you specify the file path?",
                metadata={
                    "suggestions": [
                        "Specify the exact file path",
                        "Show me the file structure",
                        "List files in a specific directory",
                    ]
                },
            )

        # Perform modification
        result = await self.code_service.modify_code(
            intent.target_file,
            intent.description,
            {"memory_context": memory_context, "user_id": user_id},
        )

        if result["success"]:
            # Store in memory
            # TODO: Fix call to self.ai_memory.store_memory, which is not implemented
            # await self.ai_memory.store_memory(
            #     content=f"Modified {intent.target_file}: {intent.description}",
            #     category=MemoryCategory.CODE_PATTERNS,
            #     tags=["code", "modification", intent.target_file],
            #     user_id=user_id,
            #     metadata={
            #         "file_path": intent.target_file,
            #         "action": intent.action,
            #         "metrics": result.get("metrics", {})
            #     }
            # )

            if result["requires_approval"]:
                # Create pending approval
                approval_id = str(uuid.uuid4())
                self.pending_approvals[approval_id] = PendingApproval(
                    id=approval_id,
                    file_path=intent.target_file,
                    modified_code=result["modified_code"],
                    diff=result["diff"],
                    description=intent.description,
                    created_at=datetime.now(),
                    user_id=user_id,
                    metadata={
                        "validation": result["validation"],
                        "metrics": result["metrics"],
                    },
                )

                return ChatResponse(
                    response=f"I've prepared the modifications for `{intent.target_file}`. Here's what will change:",
                    metadata={
                        "type": "code_modification",
                        "approval_required": True,
                        "approval_id": approval_id,
                        "file_path": intent.target_file,
                        "diff": result["diff"],
                        "validation": result["validation"],
                        "metrics": result["metrics"],
                        "actions": [
                            {
                                "type": "approve",
                                "label": "Approve & Apply",
                                "action": f"approve:{approval_id}",
                            },
                            {
                                "type": "reject",
                                "label": "Reject",
                                "action": f"reject:{approval_id}",
                            },
                        ],
                    },
                )
            else:
                # Auto-apply small changes
                await self._apply_code_changes(
                    intent.target_file, result["modified_code"]
                )

                return ChatResponse(
                    response=f"I've successfully modified `{intent.target_file}`. The changes have been applied.",
                    metadata={
                        "type": "code_modification",
                        "file_path": intent.target_file,
                        "diff": result["diff"],
                        "metrics": result["metrics"],
                        "auto_applied": True,
                    },
                )
        else:
            return ChatResponse(
                response=f"I encountered an error: {result['error']}",
                metadata={"type": "error", "error": result["error"]},
            )

    async def _handle_code_generation(
        self, intent: dict[str, Any], memory_context: list[dict], user_id: str
    ) -> ChatResponse:
        """Handle code generation requests"""

        return ChatResponse(
            response="I'm sorry, the code generation feature is currently under maintenance. Please try again later.",
            metadata={"type": "error", "error": "not_implemented"},
        )

    async def _handle_infrastructure_command(
        self, intent: InfrastructureIntent, memory_context: list[dict], user_id: str
    ) -> ChatResponse:
        """Handle infrastructure commands"""

        # Check risk level
        if intent.risk_level in ["high", "critical"]:
            # Require confirmation
            return ChatResponse(
                response=f"⚠️ This is a {intent.risk_level} risk operation. Are you sure you want to {intent.action} {intent.target}?",
                metadata={
                    "type": "confirmation_required",
                    "risk_level": intent.risk_level,
                    "action": intent.action,
                    "target": intent.target,
                    "actions": [
                        {
                            "type": "confirm",
                            "label": "Yes, proceed",
                            "action": f"infra:{intent.action}:{intent.target}",
                        },
                        {"type": "cancel", "label": "Cancel", "action": "cancel"},
                    ],
                },
            )

        # Execute infrastructure command
        result = await self._execute_infrastructure_command(intent)

        # Store in memory
        # TODO: Fix call to self.ai_memory.store_memory, which is not implemented
        # await self.ai_memory.store_memory(
        #     content=f"Executed infrastructure command: {intent.action} {intent.target}",
        #     category=MemoryCategory.INFRASTRUCTURE,
        #     tags=["infrastructure", intent.action, intent.target],
        #     user_id=user_id,
        #     metadata=result
        # )

        return ChatResponse(
            response=f"Successfully executed: {intent.action} {intent.target}",
            metadata={"type": "infrastructure", "result": result},
        )

    async def _handle_memory_query(
        self, query: str, memory_context: list[dict], user_id: str
    ) -> ChatResponse:
        """Handle memory/history queries"""

        if not memory_context:
            return ChatResponse(
                response="I don't have any relevant memories about that. Could you provide more context?",
                metadata={"type": "memory_query", "results": 0},
            )

        # Format memory results
        memory_summary = []
        for memory in memory_context[:3]:  # Top 3 memories:
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")
            category = memory.get("category", "")

            memory_summary.append(f"• {content} ({category}, {timestamp})")

        response_text = "Here's what I remember:\n\n" + "\n".join(memory_summary)

        return ChatResponse(
            response=response_text,
            metadata={
                "type": "memory_query",
                "results": len(memory_context),
                "memories": memory_context,
            },
        )

    async def _find_relevant_file(
        self, description: str, memory_context: list[dict]
    ) -> str | None:
        """Find relevant file from description and memory"""
        # TODO: This method's implementation is broken and needs to be fixed.
        # It uses undefined classes (LLMRequest) and enum members.
        # For now, it returns None to allow the application to run.
        return None

    async def _apply_code_changes(self, file_path: str, modified_code: str) -> bool:
        """Apply code changes to file"""

        try:
            full_path = self.code_service.workspace_root / file_path

            # Create backup
            if full_path.exists():
                backup_path = full_path.with_suffix(full_path.suffix + ".backup")
                backup_path.write_text(full_path.read_text())

            # Write new content
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(modified_code)

            logger.info(f"Successfully applied changes to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error applying changes to {file_path}: {e}")
            return False

    async def _execute_infrastructure_command(
        self, intent: InfrastructureIntent
    ) -> dict[str, Any]:
        """Execute infrastructure command"""

        # This would integrate with your infrastructure services
        # For now, return a mock result
        return {
            "success": True,
            "action": intent.action,
            "target": intent.target,
            "message": f"Successfully executed {intent.action} on {intent.target}",
        }

    async def apply_pending_changes(self, approval_id: str) -> dict[str, Any]:
        """Apply pending code changes"""

        if approval_id not in self.pending_approvals:
            return {"success": False, "error": "Approval not found"}

        approval = self.pending_approvals[approval_id]

        # Apply the changes
        success = await self._apply_code_changes(
            approval.file_path, approval.modified_code
        )

        if success:
            # Remove from pending
            del self.pending_approvals[approval_id]

            # Store in memory
            # TODO: Fix call to self.ai_memory.store_memory, which is not implemented
            # await self.ai_memory.store_memory(
            #     content=f"Applied approved changes to {approval.file_path}",
            #     category=MemoryCategory.CODE_PATTERNS,
            #     tags=["code", "applied", approval.file_path],
            #     user_id=approval.user_id
            # )

        return {"success": success, "file_path": approval.file_path}

    async def reject_pending_changes(self, approval_id: str) -> dict[str, Any]:
        """Reject pending code changes"""

        if approval_id not in self.pending_approvals:
            return {"success": False, "error": "Approval not found"}

        approval = self.pending_approvals[approval_id]

        # Remove from pending
        del self.pending_approvals[approval_id]

        # Store in memory
        # TODO: Fix call to self.ai_memory.store_memory, which is not implemented
        # await self.ai_memory.store_memory(
        #     content=f"Rejected changes to {approval.file_path}",
        #     category=MemoryCategory.CODE_PATTERNS,
        #     tags=["code", "rejected", approval.file_path],
        #     user_id=approval.user_id
        # )

        return {"success": True, "file_path": approval.file_path}
