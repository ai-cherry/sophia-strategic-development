# 🏗️ Phase 2: Foundation Implementation Plan

**Building the Core Infrastructure for Natural Language Code Modification**

## 🎯 Primary Goals

1. **Code Modification Through Chat** - Modify actual code files through natural language
2. **Contextualized Memory** - Leverage AI memory for intelligent assistance
3. **V1 Dashboard Deployment** - Get the unified interface live
4. **MCP Server Infrastructure** - Deploy critical MCP servers
5. **System Integration** - Connect all pieces into a working system

## 📋 Implementation Phases

### Phase 2.1: Core Infrastructure Setup (Days 1-3)

#### 1. Enhanced Intent Engine Foundation

```python
# backend/services/sophia_intent_engine.py

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

from backend.services.smart_ai_service import SmartAIService
from backend.services.unified_chat_service import ChatContext
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer

class IntentCategory(Enum):
    CODE_MODIFICATION = "code_modification"
    CODE_GENERATION = "code_generation"
    INFRASTRUCTURE = "infrastructure"
    BUSINESS_QUERY = "business_query"
    SYSTEM_COMMAND = "system_command"
    HELP = "help"

@dataclass
class CodeModificationIntent:
    action: str  # modify, create, delete, refactor
    target_file: Optional[str]
    description: str
    constraints: Dict[str, Any]
    requires_approval: bool

class SophiaIntentEngine:
    """
    Core intent classification engine
    """

    def __init__(self):
        self.smart_ai = SmartAIService()
        self.ai_memory = EnhancedAiMemoryMCPServer()
        self.code_patterns = self._load_code_patterns()

    async def classify_intent(self, message: str, context: ChatContext) -> Tuple[IntentCategory, Any]:
        """
        Classify user intent with code modification detection
        """
        # Check for code modification patterns
        if self._is_code_modification(message):
            intent = await self._parse_code_intent(message, context)
            return IntentCategory.CODE_MODIFICATION, intent

        # Other intent classifications...
        return await self._classify_general_intent(message, context)

    def _is_code_modification(self, message: str) -> bool:
        """Detect code modification requests"""
        code_keywords = [
            "change", "modify", "update", "fix", "refactor",
            "add", "create", "implement", "write",
            "delete", "remove", "rename"
        ]

        file_indicators = [
            ".py", ".ts", ".tsx", ".js", ".jsx",
            "file", "function", "class", "method"
        ]

        message_lower = message.lower()
        has_code_keyword = any(kw in message_lower for kw in code_keywords)
        has_file_indicator = any(ind in message_lower for ind in file_indicators)

        return has_code_keyword and has_file_indicator
```

#### 2. Code Modification Service

```python
# backend/services/code_modification_service.py

import os
import ast
import difflib
from pathlib import Path
from typing import Dict, Any, Optional, List

from backend.services.smart_ai_service import SmartAIService
from backend.core.config_manager import ConfigManager

class CodeModificationService:
    """
    Service for modifying code through natural language
    """

    def __init__(self):
        self.smart_ai = SmartAIService()
        self.config = ConfigManager()
        self.workspace_root = Path(os.getcwd())

    async def modify_code(
        self,
        file_path: str,
        instructions: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modify code based on natural language instructions
        """
        # Read current code
        full_path = self.workspace_root / file_path
        if not full_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        current_code = full_path.read_text()

        # Generate modifications using AI
        modified_code = await self._generate_modifications(
            current_code,
            instructions,
            file_path,
            context
        )

        # Create diff for review
        diff = self._create_diff(current_code, modified_code)

        # Validate modifications
        validation = await self._validate_modifications(
            file_path,
            current_code,
            modified_code
        )

        return {
            "success": True,
            "file_path": file_path,
            "diff": diff,
            "validation": validation,
            "modified_code": modified_code,
            "requires_approval": self._requires_approval(diff)
        }

    async def _generate_modifications(
        self,
        current_code: str,
        instructions: str,
        file_path: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate code modifications using AI"""

        prompt = f"""
        Modify the following code based on these instructions:

        File: {file_path}
        Instructions: {instructions}

        Current code:
        ```
        {current_code}
        ```

        Context:
        - Project: Sophia AI
        - Language: {self._detect_language(file_path)}
        - Recent changes: {context.get('recent_changes', 'None')}

        Generate the complete modified code following best practices.
        """

        return await self.smart_ai.generate_code(prompt)
```

#### 3. Memory-Enhanced Chat Service

```python
# backend/services/enhanced_unified_chat_service.py

from backend.services.unified_chat_service import UnifiedChatService
from backend.services.sophia_intent_engine import SophiaIntentEngine, IntentCategory
from backend.services.code_modification_service import CodeModificationService
from backend.services.mcp_orchestration_service import MCPOrchestrationService

class EnhancedUnifiedChatService(UnifiedChatService):
    """
    Enhanced chat service with code modification capabilities
    """

    def __init__(self):
        super().__init__()
        self.intent_engine = SophiaIntentEngine()
        self.code_service = CodeModificationService()
        self.mcp_orchestrator = MCPOrchestrationService()

    async def process_message(
        self,
        message: str,
        user_id: str,
        context: ChatContext
    ) -> ChatResponse:
        """
        Process message with enhanced capabilities
        """
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
        else:
            # Handle other intents...
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
                suggestions=["Specify the exact file path", "Show me the file structure"]
            )

        # Perform modification
        result = await self.code_service.modify_code(
            intent.target_file,
            intent.description,
            {"memory_context": memory_context}
        )

        if result["success"]:
            # Store in memory
            await self.ai_memory.store_memory(
                content=f"Modified {intent.target_file}: {intent.description}",
                category="code_modification",
                tags=["code", "modification", intent.target_file],
                user_id=user_id
            )

            if result["requires_approval"]:
                return ChatResponse(
                    response=f"I've prepared the modifications for {intent.target_file}. Here's what will change:",
                    code_diff=result["diff"],
                    approval_required=True,
                    approval_data={
                        "file_path": intent.target_file,
                        "modified_code": result["modified_code"]
                    }
                )
            else:
                # Auto-apply small changes
                await self._apply_code_changes(
                    intent.target_file,
                    result["modified_code"]
                )

                return ChatResponse(
                    response=f"I've successfully modified {intent.target_file}. The changes have been applied.",
                    code_diff=result["diff"]
                )
        else:
            return ChatResponse(
                response=f"I encountered an error: {result['error']}",
                success=False
            )
```

### Phase 2.2: MCP Server Deployments (Days 4-5)

#### 1. Critical MCP Servers to Deploy

```yaml
# docker-compose.mcp-critical.yml

version: '3.8'

services:
  # AI Memory Server - Port 9000
  ai-memory:
    build:
      context: ./mcp-servers/ai_memory
      dockerfile: Dockerfile
    ports:
      - "9000:9000"
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
    volumes:
      - ai-memory-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Codacy Server - Port 3008
  codacy:
    build:
      context: ./mcp-servers/codacy
      dockerfile: Dockerfile
    ports:
      - "3008:3008"
    environment:
      - ENVIRONMENT=prod
      - CODACY_API_TOKEN=${CODACY_API_TOKEN}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3008/health"]

  # Code Modification Server - Port 9050
  code-modifier:
    build:
      context: ./mcp-servers/code_modifier
      dockerfile: Dockerfile
    ports:
      - "9050:9050"
    environment:
      - ENVIRONMENT=prod
      - WORKSPACE_ROOT=/workspace
    volumes:
      - ./:/workspace:rw
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9050/health"]

  # Cursor IDE Integration - Port 9051
  cursor-ide:
    build:
      context: ./mcp-servers/cursor_ide
      dockerfile: Dockerfile
    ports:
      - "9051:9051"
    environment:
      - ENVIRONMENT=prod
    volumes:
      - ./:/workspace:ro
      - cursor-config:/config

volumes:
  ai-memory-data:
  cursor-config:
```

#### 2. Code Modifier MCP Server

```python
# mcp-servers/code_modifier/code_modifier_mcp_server.py

from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from backend.mcp_servers.base.standardized_mcp_server import (
    StandardizedMCPServer,
    mcp_tool
)
from backend.services.code_modification_service import CodeModificationService

class CodeModifierMCPServer(StandardizedMCPServer):
    """
    MCP server for code modification operations
    """

    def __init__(self):
        super().__init__(
            name="code_modifier",
            port=9050,
            description="Natural language code modification"
        )
        self.code_service = CodeModificationService()
        self.workspace_root = Path(os.getenv("WORKSPACE_ROOT", "/workspace"))

    @mcp_tool(
        name="modify_file",
        description="Modify a code file based on instructions"
    )
    async def modify_file(
        self,
        file_path: str,
        instructions: str,
        preview_only: bool = True
    ) -> Dict[str, Any]:
        """Modify a file based on natural language instructions"""

        result = await self.code_service.modify_code(
            file_path,
            instructions,
            {"workspace_root": str(self.workspace_root)}
        )

        if result["success"] and not preview_only:
            # Apply the changes
            full_path = self.workspace_root / file_path
            full_path.write_text(result["modified_code"])
            result["applied"] = True
        else:
            result["applied"] = False

        return result

    @mcp_tool(
        name="create_file",
        description="Create a new file with content"
    )
    async def create_file(
        self,
        file_path: str,
        content: str,
        description: str
    ) -> Dict[str, Any]:
        """Create a new file"""

        full_path = self.workspace_root / file_path

        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate content if needed
        if not content:
            content = await self.code_service.generate_file_content(
                file_path,
                description
            )

        # Write file
        full_path.write_text(content)

        return {
            "success": True,
            "file_path": file_path,
            "size": len(content),
            "created": True
        }
```

### Phase 2.3: Dashboard V1 Deployment (Days 6-7)

#### 1. Enhanced Dashboard with Chat Integration

```typescript
// frontend/src/components/dashboard/UnifiedDashboard.tsx

import React, { useState, useEffect } from 'react';
import { EnhancedUnifiedChat } from '../shared/EnhancedUnifiedChat';
import { CodeDiffViewer } from '../shared/CodeDiffViewer';
import { WorkflowVisualizer } from '../shared/WorkflowVisualizer';

export const UnifiedDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [activeWorkflows, setActiveWorkflows] = useState([]);

  // Subscribe to real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'approval_required') {
        setPendingApprovals(prev => [...prev, data]);
      } else if (data.type === 'workflow_update') {
        setActiveWorkflows(prev =>
          prev.map(w => w.id === data.workflow_id ? {...w, ...data} : w)
        );
      }
    };

    return () => ws.close();
  }, []);

  const handleApproval = async (approvalData: any) => {
    const response = await fetch('/api/v1/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(approvalData)
    });

    if (response.ok) {
      setPendingApprovals(prev =>
        prev.filter(a => a.id !== approvalData.id)
      );
    }
  };

  return (
    <div className="unified-dashboard">
      <div className="dashboard-header">
        <h1>Sophia AI Command Center</h1>
        <div className="tab-navigation">
          <button
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
          >
            AI Chat
          </button>
          <button
            className={activeTab === 'workflows' ? 'active' : ''}
            onClick={() => setActiveTab('workflows')}
          >
            Active Workflows
          </button>
          <button
            className={activeTab === 'approvals' ? 'active' : ''}
            onClick={() => setActiveTab('approvals')}
          >
            Pending Approvals ({pendingApprovals.length})
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        {activeTab === 'chat' && (
          <div className="chat-container">
            <EnhancedUnifiedChat
              onApprovalRequired={(data) => setPendingApprovals(prev => [...prev, data])}
              onWorkflowStarted={(workflow) => setActiveWorkflows(prev => [...prev, workflow])}
            />
          </div>
        )}

        {activeTab === 'workflows' && (
          <div className="workflows-container">
            <h2>Active Workflows</h2>
            {activeWorkflows.map(workflow => (
              <WorkflowVisualizer
                key={workflow.id}
                workflow={workflow}
              />
            ))}
          </div>
        )}

        {activeTab === 'approvals' && (
          <div className="approvals-container">
            <h2>Pending Approvals</h2>
            {pendingApprovals.map(approval => (
              <div key={approval.id} className="approval-card">
                <h3>{approval.title}</h3>
                <p>{approval.description}</p>
                {approval.code_diff && (
                  <CodeDiffViewer diff={approval.code_diff} />
                )}
                <div className="approval-actions">
                  <button
                    className="approve"
                    onClick={() => handleApproval({...approval, approved: true})}
                  >
                    Approve & Apply
                  </button>
                  <button
                    className="reject"
                    onClick={() => handleApproval({...approval, approved: false})}
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

#### 2. Deployment Configuration

```typescript
// infrastructure/vercel/vercel.json

{
  "name": "sophia-ai-dashboard",
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.sophia-ai.com/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "@sophia_api_url",
    "REACT_APP_WS_URL": "@sophia_ws_url"
  }
}
```

### Phase 2.4: System Integration (Days 8-9)

#### 1. Unified API Gateway

```python
# backend/api/unified_gateway.py

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService
from backend.services.mcp_orchestration_service import MCPOrchestrationService

app = FastAPI(title="Sophia AI Gateway")

# Services
chat_service = EnhancedUnifiedChatService()
mcp_orchestrator = MCPOrchestrationService()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with code modification capabilities"""
    response = await chat_service.process_message(
        request.message,
        request.user_id,
        request.context
    )
    return response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()

    # Handle real-time communication
    async for message in websocket.iter_text():
        # Process and broadcast updates
        pass

@app.post("/api/v1/approve")
async def approve_changes(approval: ApprovalRequest):
    """Approve and apply code changes"""
    if approval.approved:
        result = await chat_service.apply_pending_changes(approval.id)
        return {"success": True, "result": result}
    else:
        await chat_service.reject_pending_changes(approval.id)
        return {"success": True, "rejected": True}

@app.get("/api/v1/mcp/status")
async def mcp_status():
    """Get status of all MCP servers"""
    return await mcp_orchestrator.get_mcp_health_status()
```

#### 2. Deployment Script

```python
# scripts/deploy_phase2_foundation.py

#!/usr/bin/env python3
"""
Deploy Phase 2 Foundation Infrastructure
"""

import asyncio
import subprocess
import sys
from pathlib import Path

class Phase2Deployer:
    def __init__(self):
        self.root = Path(__file__).parent.parent

    async def deploy(self):
        """Deploy all Phase 2 components"""

        print("🚀 Deploying Phase 2 Foundation...")

        # 1. Deploy MCP servers
        print("\n📦 Deploying MCP servers...")
        subprocess.run([
            "docker-compose",
            "-f", "docker-compose.mcp-critical.yml",
            "up", "-d"
        ], cwd=self.root)

        # 2. Start backend services
        print("\n🔧 Starting backend services...")
        subprocess.Popen([
            sys.executable,
            "backend/app/main.py"
        ], cwd=self.root)

        # 3. Deploy frontend
        print("\n🎨 Building frontend...")
        subprocess.run([
            "npm", "run", "build"
        ], cwd=self.root / "frontend")

        # 4. Deploy to Vercel
        print("\n☁️ Deploying to Vercel...")
        subprocess.run([
            "vercel", "--prod"
        ], cwd=self.root / "frontend")

        print("\n✅ Phase 2 deployment complete!")
        print("\n📋 Next steps:")
        print("1. Access dashboard at: https://app.sophia-ai.com")
        print("2. Test code modification: 'Update the UnifiedDashboard to add a new tab'")
        print("3. Check MCP status at: http://localhost:8000/api/v1/mcp/status")

if __name__ == "__main__":
    deployer = Phase2Deployer()
    asyncio.run(deployer.deploy())
```

## 🔧 Critical Configuration Files

### 1. Environment Configuration
```bash
# .env.production

ENVIRONMENT=prod
PULUMI_ORG=scoobyjava-org
API_URL=https://api.sophia-ai.com
WS_URL=wss://api.sophia-ai.com/ws
VERCEL_PROJECT_ID=your-project-id
```

### 2. MCP Configuration Update
```json
// config/cursor_enhanced_mcp_config.json

{
  "mcpServers": {
    "code_modifier": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:9050/"],
      "description": "Code modification through natural language"
    },
    "ai_memory": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:9000/"],
      "description": "Contextual memory for development"
    }
  }
}
```

## 📊 Success Metrics

### Technical Metrics
- [ ] Code modification working through chat
- [ ] Memory context being used effectively
- [ ] Dashboard deployed and accessible
- [ ] MCP servers healthy and responsive
- [ ] WebSocket real-time updates working

### User Experience Metrics
- [ ] Can modify code with natural language
- [ ] Approval workflow functioning
- [ ] Context-aware suggestions working
- [ ] Real-time progress visible

## 🚀 Testing Checklist

### 1. Code Modification Test
```
User: "Update the UnifiedDashboard.tsx to add a new 'Settings' tab"
Expected: Shows diff, requests approval, applies changes
```

### 2. Memory Context Test
```
User: "What changes did I make to the dashboard yesterday?"
Expected: Recalls previous modifications from memory
```

### 3. End-to-End Workflow Test
```
User: "Create a new API endpoint for user preferences"
Expected:
- Creates new file
- Adds route to API
- Updates types
- Shows all changes for approval
```

## 🎯 Next Phase Preview

Once Phase 2 is complete, Phase 3 will add:
- Advanced workflow orchestration
- Multi-agent coordination
- Proactive assistance
- Infrastructure management
- Performance optimization

## 🏁 Let's Build!

This foundation gives us:
1. **Natural language code modification** ✅
2. **Contextualized AI assistance** ✅
3. **Live dashboard interface** ✅
4. **Working MCP infrastructure** ✅

Ready to start implementation!
