# 🚀 LLM-Driven Code & Infrastructure Management Implementation Plan

## Executive Summary

This document provides a concrete implementation plan for transforming Sophia AI's Unified Chat interface into a powerful command center for LLM-driven code generation, editing, review, GitHub commits, and infrastructure management via IaC.

## 🏗️ Building on Existing Architecture

### Current Foundation
- **Unified Chat Service**: Already handles multi-source orchestration via LangGraph
- **MCP Server Architecture**: StandardizedMCPServer and SimpleMCPServer base classes
- **Service Integration**: 10+ services already integrated (Gong, Slack, Linear, etc.)
- **AI Memory System**: 6-tier memory for context preservation
- **Deployment Infrastructure**: Docker Swarm on Lambda Labs (192.222.58.232)

### New Components to Add

## 📦 Phase 1: Code Management MCP Server (Week 1-2)

### 1.1 Create Code Management MCP Server

```python
# mcp-servers/code_management/code_management_mcp_server.py

from backend.mcp_servers.base.unified_mcp_base import (
    MCPServerConfig,
    StandardizedMCPServer,
    mcp_tool
)
import git
from github import Github
import ast
import black
import ruff

class CodeManagementMCPServer(StandardizedMCPServer):
    """MCP server for code management operations"""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.repo_path = "/workspace/sophia-main"
        self.github_client = None
        self.sandbox_path = "/sandbox"

    async def server_specific_init(self):
        """Initialize code management server"""
        # Initialize GitHub client
        github_token = get_config_value("github_token")
        self.github_client = Github(github_token)

        # Clone repo to sandbox
        self.repo = git.Repo.clone_from(
            "https://github.com/ai-cherry/sophia-main.git",
            self.sandbox_path
        )

    @mcp_tool(
        name="review_code",
        description="Review code for best practices and issues"
    )
    async def review_code(self, file_path: str) -> dict:
        """AI-powered code review"""
        # Read file
        with open(f"{self.sandbox_path}/{file_path}", "r") as f:
            code = f.read()

        # Run static analysis
        ruff_issues = await self._run_ruff(file_path)

        # Get AI review
        review = await self._get_ai_review(code, file_path)

        return {
            "file": file_path,
            "static_analysis": ruff_issues,
            "ai_review": review,
            "suggestions": await self._generate_suggestions(code, review)
        }

    @mcp_tool(
        name="edit_code",
        description="Edit code based on natural language instructions"
    )
    async def edit_code(self, file_path: str, instructions: str) -> dict:
        """Generate code edits from instructions"""
        # Read current code
        with open(f"{self.sandbox_path}/{file_path}", "r") as f:
            original_code = f.read()

        # Generate new code using LLM
        new_code = await self._generate_code_edit(
            original_code,
            instructions,
            file_path
        )

        # Format with Black
        formatted_code = black.format_str(new_code, mode=black.Mode())

        # Generate diff
        diff = self._generate_diff(original_code, formatted_code)

        return {
            "file": file_path,
            "original": original_code,
            "modified": formatted_code,
            "diff": diff,
            "preview": self._create_preview(diff)
        }

    @mcp_tool(
        name="commit_changes",
        description="Commit changes to GitHub with PR"
    )
    async def commit_changes(
        self,
        files: list[str],
        commit_message: str,
        branch_name: str,
        pr_title: str,
        pr_description: str
    ) -> dict:
        """Commit changes and create PR"""
        # Create new branch
        self.repo.create_head(branch_name)
        self.repo.heads[branch_name].checkout()

        # Stage files
        for file in files:
            self.repo.index.add([file])

        # Commit
        self.repo.index.commit(commit_message)

        # Push to GitHub
        origin = self.repo.remote("origin")
        origin.push(branch_name)

        # Create PR
        github_repo = self.github_client.get_repo("ai-cherry/sophia-main")
        pr = github_repo.create_pull(
            title=pr_title,
            body=pr_description,
            head=branch_name,
            base="main"
        )

        return {
            "branch": branch_name,
            "commit": self.repo.head.commit.hexsha,
            "pr_url": pr.html_url,
            "pr_number": pr.number
        }
```

### 1.2 Secure Sandbox Implementation

```yaml
# docker/code-agent-sandbox.dockerfile
FROM python:3.11-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 codeagent
USER codeagent

# Install dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Security: Read-only filesystem except workspace
VOLUME ["/workspace", "/sandbox"]
```

## 📦 Phase 2: Infrastructure Management MCP Server (Week 3-4)

### 2.1 Infrastructure Management Server

```python
# mcp-servers/infrastructure_management/infra_management_mcp_server.py

import pulumi
import pulumi.automation as auto
from pulumi_snowflake import Database, Schema, Table

class InfrastructureManagementMCPServer(StandardizedMCPServer):
    """MCP server for infrastructure management via Pulumi"""

    @mcp_tool(
        name="preview_infrastructure",
        description="Preview infrastructure changes"
    )
    async def preview_infrastructure(
        self,
        stack_name: str,
        changes: dict
    ) -> dict:
        """Preview Pulumi changes"""
        # Create Pulumi program
        def pulumi_program():
            # Apply changes based on input
            if "snowflake" in changes:
                self._apply_snowflake_changes(changes["snowflake"])

        # Run preview
        stack = auto.create_or_select_stack(
            stack_name=stack_name,
            project_name="sophia-ai",
            program=pulumi_program
        )

        preview_result = stack.preview()

        return {
            "stack": stack_name,
            "preview": self._format_preview(preview_result),
            "resources_to_create": preview_result.summary.create,
            "resources_to_update": preview_result.summary.update,
            "resources_to_delete": preview_result.summary.delete
        }

    @mcp_tool(
        name="deploy_infrastructure",
        description="Deploy infrastructure changes after approval"
    )
    async def deploy_infrastructure(
        self,
        stack_name: str,
        approval_token: str
    ) -> dict:
        """Deploy infrastructure with approval"""
        # Verify approval token
        if not self._verify_approval(approval_token):
            raise ValueError("Invalid approval token")

        # Get stack
        stack = auto.select_stack(
            stack_name=stack_name,
            project_name="sophia-ai"
        )

        # Deploy
        up_result = stack.up()

        return {
            "stack": stack_name,
            "result": "success",
            "outputs": up_result.outputs,
            "summary": {
                "created": up_result.summary.create,
                "updated": up_result.summary.update,
                "deleted": up_result.summary.delete
            }
        }
```

## 🔄 Phase 3: Unified Chat Integration (Week 5-6)

### 3.1 Extend Unified Chat Service

```python
# Add to backend/services/unified_chat_service.py

class UnifiedChatService:
    def __init__(self):
        # ... existing init ...

        # Add new services
        self.code_mgmt = CodeManagementService()
        self.infra_mgmt = InfrastructureManagementService()

        # Update service map
        self.service_map.update({
            "code": self.code_mgmt,
            "infrastructure": self.infra_mgmt
        })

    async def _analyze_query_context(self, query: str, ...):
        """Enhanced to detect code/infra intents"""
        # ... existing code ...

        # Add code/infra intent detection
        code_indicators = ["review", "edit", "write", "commit", "pr", "function", "class"]
        infra_indicators = ["deploy", "infrastructure", "pulumi", "snowflake schema", "lambda"]

        if any(ind in query.lower() for ind in code_indicators):
            analysis["intent"] = "code_management"
        elif any(ind in query.lower() for ind in infra_indicators):
            analysis["intent"] = "infrastructure_management"
```

### 3.2 Frontend Enhancements

```typescript
// frontend/src/components/chat/CodeDiffViewer.tsx

interface CodeDiffViewerProps {
  diff: string;
  language: string;
  onApprove: () => void;
  onReject: () => void;
  onSuggestEdit: (suggestion: string) => void;
}

export const CodeDiffViewer: React.FC<CodeDiffViewerProps> = ({
  diff, language, onApprove, onReject, onSuggestEdit
}) => {
  return (
    <div className="code-diff-container">
      <div className="diff-header">
        <h3>Proposed Changes</h3>
        <div className="diff-stats">
          {/* Show additions/deletions */}
        </div>
      </div>

      <div className="diff-content">
        <SyntaxHighlighter language={language} style={vs2015}>
          {diff}
        </SyntaxHighlighter>
      </div>

      <div className="diff-actions">
        <button onClick={onApprove} className="btn-approve">
          ✅ Approve & Apply
        </button>
        <button onClick={onReject} className="btn-reject">
          ❌ Reject
        </button>
        <button onClick={() => setShowSuggestions(true)} className="btn-suggest">
          💡 Suggest Changes
        </button>
      </div>
    </div>
  );
};
```

## 🔐 Security Implementation

### 4.1 Approval Workflow

```python
# backend/services/approval_service.py

class ApprovalService:
    """Manages approval workflows for critical operations"""

    async def request_approval(
        self,
        operation_type: str,
        operation_details: dict,
        user_id: str,
        risk_level: str
    ) -> str:
        """Create approval request"""
        approval_token = self._generate_secure_token()

        # Store in Redis with TTL
        await self.redis.setex(
            f"approval:{approval_token}",
            300,  # 5 minute TTL
            json.dumps({
                "operation_type": operation_type,
                "details": operation_details,
                "user_id": user_id,
                "risk_level": risk_level,
                "created_at": datetime.utcnow().isoformat()
            })
        )

        # Send to chat UI
        await self.send_approval_request_to_ui(
            user_id=user_id,
            token=approval_token,
            details=operation_details
        )

        return approval_token
```

## 📊 Phase 4: Advanced Features (Week 7-8)

### 5.1 RAG for Code Context

```python
# backend/services/code_context_service.py

class CodeContextService:
    """Provides relevant code context via RAG"""

    async def embed_codebase(self):
        """Embed entire codebase for semantic search"""
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(('.py', '.ts', '.tsx')):
                    # Read file
                    content = self._read_file(os.path.join(root, file))

                    # Parse into chunks (functions, classes)
                    chunks = self._parse_code_chunks(content, file)

                    # Generate embeddings
                    for chunk in chunks:
                        embedding = await self.cortex.generate_embedding(
                            chunk['content']
                        )

                        # Store in vector DB
                        await self.vector_db.upsert({
                            'id': chunk['id'],
                            'embedding': embedding,
                            'metadata': {
                                'file': file,
                                'type': chunk['type'],
                                'name': chunk['name'],
                                'content': chunk['content']
                            }
                        })
```

## 🚀 Deployment Configuration

### 6.1 Docker Compose Addition

```yaml
# Add to docker-compose.unified.yml

  code-management:
    image: ${DOCKER_REGISTRY}/sophia-ai-code-mgmt:${VERSION}
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - MCP_PORT=9030
    volumes:
      - ./sandbox:/sandbox:rw
      - ./workspace:/workspace:ro
    security_opt:
      - no-new-privileges:true
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G

  infra-management:
    image: ${DOCKER_REGISTRY}/sophia-ai-infra-mgmt:${VERSION}
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - MCP_PORT=9031
      - PULUMI_ACCESS_TOKEN_FILE=/run/secrets/pulumi_token
    secrets:
      - pulumi_token
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '1'
          memory: 2G
```

## 📈 Success Metrics & Monitoring

### 7.1 Metrics to Track

```python
# backend/monitoring/code_infra_metrics.py

class CodeInfraMetrics:
    """Track code/infrastructure operation metrics"""

    # Code operations
    code_reviews_total = Counter('code_reviews_total', 'Total code reviews')
    code_edits_total = Counter('code_edits_total', 'Total code edits')
    github_commits_total = Counter('github_commits_total', 'Total GitHub commits')

    # Infrastructure operations
    infra_previews_total = Counter('infra_previews_total', 'Total previews')
    infra_deployments_total = Counter('infra_deployments_total', 'Total deployments')

    # Quality metrics
    code_quality_score = Gauge('code_quality_score', 'Code quality score')
    deployment_success_rate = Gauge('deployment_success_rate', 'Deployment success rate')
```

## 🎯 Implementation Timeline

### Week 1-2: Code Management
- [ ] Set up code management MCP server
- [ ] Implement secure sandbox
- [ ] Add GitHub integration
- [ ] Test code review/edit capabilities

### Week 3-4: Infrastructure Management
- [ ] Create infrastructure MCP server
- [ ] Integrate Pulumi automation
- [ ] Add Snowflake DDL support
- [ ] Implement approval workflows

### Week 5-6: Chat Integration
- [ ] Extend unified chat service
- [ ] Add frontend components
- [ ] Implement approval UI
- [ ] End-to-end testing

### Week 7-8: Advanced Features
- [ ] Deploy RAG for code context
- [ ] Add automated testing
- [ ] Implement monitoring
- [ ] Production deployment

## 🚨 Risk Mitigation

1. **Code Execution Safety**
   - All code runs in isolated containers
   - No network access from sandbox
   - Resource limits enforced

2. **Approval Requirements**
   - All commits require approval
   - All deployments require approval
   - Approval tokens expire in 5 minutes

3. **Rollback Capability**
   - Git revert for code changes
   - Pulumi rollback for infrastructure
   - Automated backup before changes

This implementation plan builds on Sophia AI's existing architecture to add powerful code and infrastructure management capabilities while maintaining security and reliability.
