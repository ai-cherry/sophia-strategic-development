"""
Enhanced Unified Chat Service - Integrates code modification and AI orchestration
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from backend.services.unified_chat_service import (
    UnifiedChatService, 
    ChatContext, 
    ChatResponse,
    ChatRequest
)
from backend.services.sophia_intent_engine import (
    SophiaIntentEngine, 
    IntentCategory,
    CodeModificationIntent,
    InfrastructureIntent
)
from backend.services.code_modification_service import CodeModificationService
from backend.services.mcp_orchestration_service import MCPOrchestrationService
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer, MemoryCategory
from backend.services.smart_ai_service import SmartAIService, LLMRequest, TaskType

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
    metadata: Dict[str, Any] = field(default_factory=dict)


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
        self.smart_ai = SmartAIService()
        
        # Store pending approvals
        self.pending_approvals: Dict[str, PendingApproval] = {}
        
    async def process_message(
        self,
        message: str,
        user_id: str,
        context: ChatContext
    ) -> ChatResponse:
        """
        Process message with enhanced capabilities
        """
        logger.info(f"Processing enhanced message from user {user_id}: {message[:100]}...")
        
        # Get relevant memory context
        memory_context = await self.ai_memory.recall_memory(
            message,
            user_id,
            limit=5
        )
        
        # Classify intent
        intent_category, intent_details = await self.intent_engine.classify_intent(
            message,
            context
        )
        
        logger.info(f"Classified intent: {intent_category.value}")
        
        # Route based on intent
        if intent_category == IntentCategory.CODE_MODIFICATION:
            return await self._handle_code_modification(
                intent_details,
                memory_context,
                user_id
            )
        elif intent_category == IntentCategory.CODE_GENERATION:
            return await self._handle_code_generation(
                intent_details,
                memory_context,
                user_id
            )
        elif intent_category == IntentCategory.INFRASTRUCTURE:
            return await self._handle_infrastructure_command(
                intent_details,
                memory_context,
                user_id
            )
        elif intent_category == IntentCategory.MEMORY:
            return await self._handle_memory_query(
                message,
                memory_context,
                user_id
            )
        else:
            # Handle other intents through base service
            return await super().process_message(message, user_id, context)
            
    async def _handle_code_modification(
        self,
        intent: CodeModificationIntent,
        memory_context: List[Dict],
        user_id: str
    ) -> ChatResponse:
        """Handle code modification requests"""
        
        # Check if we need to find the file
        if not intent.target_file:
            intent.target_file = await self._find_relevant_file(
                intent.description,
                memory_context
            )
            
        if not intent.target_file:
            return ChatResponse(
                response="I couldn't determine which file to modify. Could you specify the file path?",
                metadata={
                    "suggestions": [
                        "Specify the exact file path",
                        "Show me the file structure",
                        "List files in a specific directory"
                    ]
                }
            )
            
        # Perform modification
        result = await self.code_service.modify_code(
            intent.target_file,
            intent.description,
            {"memory_context": memory_context, "user_id": user_id}
        )
        
        if result["success"]:
            # Store in memory
            await self.ai_memory.store_memory(
                content=f"Modified {intent.target_file}: {intent.description}",
                category=MemoryCategory.CODE_PATTERNS,
                tags=["code", "modification", intent.target_file],
                user_id=user_id,
                metadata={
                    "file_path": intent.target_file,
                    "action": intent.action,
                    "metrics": result.get("metrics", {})
                }
            )
            
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
                        "metrics": result["metrics"]
                    }
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
                                "action": f"approve:{approval_id}"
                            },
                            {
                                "type": "reject",
                                "label": "Reject",
                                "action": f"reject:{approval_id}"
                            }
                        ]
                    }
                )
            else:
                # Auto-apply small changes
                await self._apply_code_changes(
                    intent.target_file,
                    result["modified_code"]
                )
                
                return ChatResponse(
                    response=f"I've successfully modified `{intent.target_file}`. The changes have been applied.",
                    metadata={
                        "type": "code_modification",
                        "file_path": intent.target_file,
                        "diff": result["diff"],
                        "metrics": result["metrics"],
                        "auto_applied": True
                    }
                )
        else:
            return ChatResponse(
                response=f"I encountered an error: {result['error']}",
                metadata={
                    "type": "error",
                    "error": result['error']
                }
            )
            
    async def _handle_code_generation(
        self,
        intent: Dict[str, Any],
        memory_context: List[Dict],
        user_id: str
    ) -> ChatResponse:
        """Handle code generation requests"""
        
        file_path = intent.get("file_path")
        description = intent.get("description", "")
        
        if not file_path:
            # Ask for file path
            return ChatResponse(
                response="What should I name the new file?",
                metadata={
                    "type": "input_required",
                    "input_type": "file_path",
                    "suggestions": [
                        "backend/services/new_service.py",
                        "frontend/src/components/NewComponent.tsx",
                        "scripts/new_script.py"
                    ]
                }
            )
            
        # Generate file content
        content = await self.code_service.generate_file_content(
            file_path,
            description
        )
        
        # Create approval for new file
        approval_id = str(uuid.uuid4())
        self.pending_approvals[approval_id] = PendingApproval(
            id=approval_id,
            file_path=file_path,
            modified_code=content,
            diff=f"New file: {file_path}\n\n{content}",
            description=f"Create new file: {description}",
            created_at=datetime.now(),
            user_id=user_id,
            metadata={
                "action": "create",
                "language": self.code_service._detect_language(file_path)
            }
        )
        
        # Store in memory
        await self.ai_memory.store_memory(
            content=f"Generated new file {file_path}: {description}",
            category=MemoryCategory.CODE_PATTERNS,
            tags=["code", "generation", file_path],
            user_id=user_id
        )
        
        return ChatResponse(
            response=f"I've generated the code for `{file_path}`. Here's what I created:",
            metadata={
                "type": "code_generation",
                "approval_required": True,
                "approval_id": approval_id,
                "file_path": file_path,
                "content": content,
                "actions": [
                    {
                        "type": "approve",
                        "label": "Create File",
                        "action": f"approve:{approval_id}"
                    },
                    {
                        "type": "reject",
                        "label": "Cancel",
                        "action": f"reject:{approval_id}"
                    }
                ]
            }
        )
        
    async def _handle_infrastructure_command(
        self,
        intent: InfrastructureIntent,
        memory_context: List[Dict],
        user_id: str
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
                            "action": f"infra:{intent.action}:{intent.target}"
                        },
                        {
                            "type": "cancel",
                            "label": "Cancel",
                            "action": "cancel"
                        }
                    ]
                }
            )
            
        # Execute infrastructure command
        result = await self._execute_infrastructure_command(intent)
        
        # Store in memory
        await self.ai_memory.store_memory(
            content=f"Executed infrastructure command: {intent.action} {intent.target}",
            category=MemoryCategory.INFRASTRUCTURE,
            tags=["infrastructure", intent.action, intent.target],
            user_id=user_id,
            metadata=result
        )
        
        return ChatResponse(
            response=f"Successfully executed: {intent.action} {intent.target}",
            metadata={
                "type": "infrastructure",
                "result": result
            }
        )
        
    async def _handle_memory_query(
        self,
        query: str,
        memory_context: List[Dict],
        user_id: str
    ) -> ChatResponse:
        """Handle memory/history queries"""
        
        if not memory_context:
            return ChatResponse(
                response="I don't have any relevant memories about that. Could you provide more context?",
                metadata={
                    "type": "memory_query",
                    "results": 0
                }
            )
            
        # Format memory results
        memory_summary = []
        for memory in memory_context[:3]:  # Top 3 memories
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
                "memories": memory_context
            }
        )
        
    async def _find_relevant_file(
        self,
        description: str,
        memory_context: List[Dict]
    ) -> Optional[str]:
        """Find relevant file from description and memory"""
        
        # Check memory for recent file modifications
        for memory in memory_context:
            metadata = memory.get("metadata", {})
            if "file_path" in metadata:
                return metadata["file_path"]
                
        # Use AI to suggest file
        prompt = f"""
        Based on this description: "{description}"
        
        And the context that this is for the Sophia AI project,
        what file path is most likely being referenced?
        
        Common patterns:
        - Backend services: backend/services/*.py
        - Frontend components: frontend/src/components/*.tsx
        - API routes: backend/api/*.py
        - Scripts: scripts/*.py
        
        Respond with just the file path, or "unknown" if unclear.
        """
        
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            task_type=TaskType.ROUTINE_QUERIES,
            user_id="system",
            temperature=0.3,
            max_tokens=100
        )
        
        response = await self.smart_ai.generate_response(request)
        file_path = response.content.strip()
        
        if file_path and file_path != "unknown":
            return file_path
            
        return None
        
    async def _apply_code_changes(
        self,
        file_path: str,
        modified_code: str
    ) -> bool:
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
        self,
        intent: InfrastructureIntent
    ) -> Dict[str, Any]:
        """Execute infrastructure command"""
        
        # This would integrate with your infrastructure services
        # For now, return a mock result
        return {
            "success": True,
            "action": intent.action,
            "target": intent.target,
            "message": f"Successfully executed {intent.action} on {intent.target}"
        }
        
    async def apply_pending_changes(self, approval_id: str) -> Dict[str, Any]:
        """Apply pending code changes"""
        
        if approval_id not in self.pending_approvals:
            return {
                "success": False,
                "error": "Approval not found"
            }
            
        approval = self.pending_approvals[approval_id]
        
        # Apply the changes
        success = await self._apply_code_changes(
            approval.file_path,
            approval.modified_code
        )
        
        if success:
            # Remove from pending
            del self.pending_approvals[approval_id]
            
            # Store in memory
            await self.ai_memory.store_memory(
                content=f"Applied approved changes to {approval.file_path}",
                category=MemoryCategory.CODE_PATTERNS,
                tags=["code", "applied", approval.file_path],
                user_id=approval.user_id
            )
            
        return {
            "success": success,
            "file_path": approval.file_path
        }
        
    async def reject_pending_changes(self, approval_id: str) -> Dict[str, Any]:
        """Reject pending code changes"""
        
        if approval_id not in self.pending_approvals:
            return {
                "success": False,
                "error": "Approval not found"
            }
            
        approval = self.pending_approvals[approval_id]
        
        # Remove from pending
        del self.pending_approvals[approval_id]
        
        # Store in memory
        await self.ai_memory.store_memory(
            content=f"Rejected changes to {approval.file_path}",
            category=MemoryCategory.CODE_PATTERNS,
            tags=["code", "rejected", approval.file_path],
            user_id=approval.user_id
        )
        
        return {
            "success": True,
            "file_path": approval.file_path
        }
