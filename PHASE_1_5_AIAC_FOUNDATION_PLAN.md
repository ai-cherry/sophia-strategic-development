# Phase 1.5: AIaC Foundation - Detailed Implementation Plan

## Executive Summary

Phase 1.5 introduces AI-driven infrastructure management through our unified chat interface, implementing the core AIaC principles while maintaining CEO control and quality-first approach.

## Timeline: 2 Weeks

- **Week 1**: Chat Enhancement & Approval UI (40 hours)
- **Week 2**: Pulumi AIaC MCP Server & Simulation (40 hours)

## Core Principles

1. **Unified Chat as Command Center**: All infrastructure operations through natural language
2. **Human-in-the-Loop**: CEO approves all state changes
3. **Learning Integration**: Every action improves future recommendations
4. **Safety First**: Simulation before execution, rollback always available

## Component Details

### 1. AIaC Chat Integration Service (Week 1, Days 1-2)

**File**: `backend/services/aiac_chat_integration.py`

```python
class AIaCChatIntegration:
    """
    Extends unified chat to handle infrastructure commands
    """
    
    def __init__(self):
        self.mem0_service = get_mem0_service()
        self.prompt_optimizer = PromptOptimizerClient()
        self.intent_classifier = AIaCIntentClassifier()
        self.plan_generator = ExecutionPlanGenerator()
        self.approval_manager = ApprovalManager()
    
    async def process_message(self, message: str, user_id: str) -> AIaCResponse:
        # Classify intent
        intent = await self.intent_classifier.classify(message)
        
        if intent.category == "infrastructure":
            return await self.handle_infrastructure_command(message, user_id, intent)
        
        # Regular chat processing
        return await self.process_regular_chat(message, user_id)
```

**Key Features**:
- Natural language intent detection
- Infrastructure command routing
- Memory integration for context
- Prompt optimization for clarity

### 2. Approval UI Components (Week 1, Days 3-4)

**File**: `frontend/src/components/aiac/AIaCApprovalCard.tsx`

```typescript
interface ExecutionPlan {
    id: string;
    intent: string;
    steps: ExecutionStep[];
    simulation: SimulationResult;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    estimated_duration: string;
    rollback_plan: RollbackPlan;
}

const AIaCApprovalCard: React.FC<{plan: ExecutionPlan}> = ({ plan }) => {
    const [expanded, setExpanded] = useState(false);
    const [approving, setApproving] = useState(false);
    
    return (
        <Card className="aiac-approval-card glassmorphism">
            <div className="header">
                <Icon name="shield-check" className="security-icon" />
                <h3>Infrastructure Change Approval Required</h3>
                <RiskBadge level={plan.risk_level} />
            </div>
            
            <div className="intent-section">
                <h4>What you asked:</h4>
                <p className="user-intent">{plan.intent}</p>
            </div>
            
            <div className="plan-section">
                <h4>What will happen:</h4>
                <StepList steps={plan.steps} />
            </div>
            
            <SimulationResults 
                result={plan.simulation}
                expanded={expanded}
                onToggle={() => setExpanded(!expanded)}
            />
            
            <div className="approval-actions">
                <Button 
                    variant="primary" 
                    onClick={() => handleApprove(plan.id)}
                    loading={approving}
                >
                    <Icon name="check" /> Approve & Execute
                </Button>
                <Button 
                    variant="danger" 
                    onClick={() => handleReject(plan.id)}
                >
                    <Icon name="x" /> Reject
                </Button>
                <Button 
                    variant="secondary" 
                    onClick={() => requestModification(plan.id)}
                >
                    <Icon name="edit" /> Modify Plan
                </Button>
            </div>
        </Card>
    );
};
```

**UI Features**:
- Clear visual hierarchy
- Risk level indicators
- Expandable simulation details
- One-click approval/rejection
- Plan modification option

### 3. Pulumi AIaC MCP Server (Week 2, Days 1-3)

**File**: `mcp-servers/pulumi_aiac/pulumi_aiac_mcp_server.py`

```python
from pulumi import automation as auto
from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import asyncio

class PulumiAIaCServer(StandardizedMCPServer):
    """
    Pulumi MCP with AIaC capabilities using Automation API
    """
    
    def __init__(self):
        super().__init__(
            name="pulumi_aiac",
            port=9040,
            description="AI-driven infrastructure management with Pulumi"
        )
        self.workspace_dir = "/workspace/infrastructure"
        self.stacks: Dict[str, auto.Stack] = {}
        
    async def startup(self):
        """Initialize Pulumi workspace and load stacks"""
        await super().startup()
        await self.load_available_stacks()
        
    async def load_available_stacks(self):
        """Load all available Pulumi stacks"""
        workspace = auto.LocalWorkspace(work_dir=self.workspace_dir)
        stack_summaries = await workspace.list_stacks()
        
        for summary in stack_summaries:
            stack = auto.select_stack(
                stack_name=summary.name,
                work_dir=self.workspace_dir
            )
            self.stacks[summary.name] = stack
            
    @mcp_tool(
        name="list_stacks",
        description="List all available Pulumi stacks",
        read_only=True
    )
    async def list_stacks(self) -> List[Dict[str, Any]]:
        """List all stacks with their current status"""
        stacks = []
        for name, stack in self.stacks.items():
            info = await stack.info()
            stacks.append({
                "name": name,
                "current": info.current,
                "url": info.url,
                "resource_count": len(info.resources) if info.resources else 0
            })
        return stacks
    
    @mcp_tool(
        name="preview_changes",
        description="Preview infrastructure changes without applying",
        read_only=True
    )
    async def preview_changes(
        self, 
        stack_name: str,
        config_updates: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Preview changes for a stack"""
        if stack_name not in self.stacks:
            raise ValueError(f"Stack {stack_name} not found")
            
        stack = self.stacks[stack_name]
        
        # Apply config updates if provided
        if config_updates:
            for key, value in config_updates.items():
                await stack.set_config(key, auto.ConfigValue(value))
        
        # Run preview
        preview_result = await stack.preview()
        
        return {
            "summary": {
                "create": preview_result.summary.create,
                "update": preview_result.summary.update,
                "delete": preview_result.summary.delete,
                "same": preview_result.summary.same
            },
            "changes": self._format_changes(preview_result.change_summary),
            "stdout": preview_result.stdout[-1000:],  # Last 1000 chars
            "warnings": self._extract_warnings(preview_result.stdout)
        }
    
    @mcp_tool(
        name="apply_changes",
        description="Apply infrastructure changes (requires approval)",
        requires_approval=True
    )
    async def apply_changes(
        self,
        stack_name: str,
        approval_token: str,
        message: str = "AI-initiated update"
    ) -> Dict[str, Any]:
        """Apply changes to infrastructure"""
        # Verify approval
        if not await self.verify_approval(approval_token):
            raise HTTPException(status_code=403, detail="Invalid approval token")
            
        stack = self.stacks[stack_name]
        
        # Store pre-update state for rollback
        pre_state = await stack.export_stack()
        
        try:
            # Apply updates
            up_result = await stack.up(message=message)
            
            # Store in memory for learning
            await self.mem0_service.store_infrastructure_change(
                stack_name=stack_name,
                changes=up_result.summary,
                success=True,
                message=message
            )
            
            return {
                "success": True,
                "summary": up_result.summary,
                "outputs": up_result.outputs,
                "duration": up_result.duration,
                "rollback_checkpoint": pre_state["checkpoint"]
            }
            
        except Exception as e:
            # Automatic rollback on failure
            logger.error(f"Update failed: {e}")
            await self.rollback_stack(stack_name, pre_state)
            raise
```

### 4. Simulation Engine (Week 2, Days 4-5)

**File**: `backend/services/aiac_simulation_engine.py`

```python
class AIaCSimulationEngine:
    """
    Simulates infrastructure changes before execution
    """
    
    def __init__(self):
        self.simulators = {
            "pulumi": PulumiSimulator(),
            "kubernetes": K8sSimulator(),
            "snowflake": SnowflakeSimulator(),
            "github": GitHubSimulator()
        }
        
    async def simulate_plan(
        self, 
        plan: ExecutionPlan
    ) -> SimulationResult:
        """
        Run simulation for an execution plan
        """
        results = []
        total_duration = 0
        risk_factors = []
        
        for step in plan.steps:
            simulator = self.simulators.get(step.service)
            if not simulator:
                raise ValueError(f"No simulator for {step.service}")
                
            # Run step simulation
            step_result = await simulator.simulate(step)
            results.append(step_result)
            
            total_duration += step_result.estimated_duration
            risk_factors.extend(step_result.risk_factors)
            
        return SimulationResult(
            success=all(r.success for r in results),
            steps=results,
            total_duration=total_duration,
            risk_assessment=self.assess_risk(risk_factors),
            recommendations=self.generate_recommendations(results)
        )
```

### 5. Intent Classifier (Week 1, Day 5)

**File**: `backend/services/aiac_intent_classifier.py`

```python
class AIaCIntentClassifier:
    """
    Classifies user messages for infrastructure operations
    """
    
    def __init__(self):
        self.infrastructure_keywords = {
            "deploy", "scale", "update", "rollback", "create",
            "delete", "modify", "infrastructure", "server",
            "database", "kubernetes", "k8s", "pulumi"
        }
        
        self.read_only_keywords = {
            "show", "list", "describe", "status", "check",
            "preview", "simulate", "what if", "would"
        }
        
    async def classify(self, message: str) -> IntentClassification:
        """
        Classify user intent from message
        """
        message_lower = message.lower()
        
        # Check for infrastructure keywords
        is_infrastructure = any(
            keyword in message_lower 
            for keyword in self.infrastructure_keywords
        )
        
        if not is_infrastructure:
            return IntentClassification(
                category="general",
                confidence=0.9
            )
            
        # Determine if read-only or state-changing
        is_read_only = any(
            keyword in message_lower 
            for keyword in self.read_only_keywords
        )
        
        # Extract specific intent
        intent_type = self.extract_intent_type(message)
        target = self.extract_target(message)
        
        return IntentClassification(
            category="infrastructure",
            intent_type=intent_type,
            is_read_only=is_read_only,
            target=target,
            confidence=0.85,
            requires_approval=not is_read_only
        )
```

## Integration Points

### 1. Unified Chat Enhancement

```python
# backend/api/enhanced_unified_chat_routes.py
@router.post("/chat")
async def unified_chat_endpoint(request: ChatRequest):
    # Existing chat logic...
    
    # Add AIaC integration
    aiac_integration = AIaCChatIntegration()
    response = await aiac_integration.process_message(
        request.message,
        request.user_id
    )
    
    if response.requires_approval:
        # Return approval UI
        return ChatResponse(
            type="approval_required",
            content=response.approval_card,
            plan_id=response.plan_id
        )
    
    # Regular response
    return response
```

### 2. Memory Integration

```python
# Store every infrastructure action for learning
await mem0_service.store_memory(
    user_id=user_id,
    memory_type="infrastructure_action",
    content={
        "intent": original_message,
        "plan": execution_plan,
        "result": execution_result,
        "duration": duration,
        "success": success
    }
)
```

### 3. Prompt Optimization

```python
# Optimize infrastructure commands for clarity
optimized_command = await prompt_optimizer.optimize(
    prompt=user_message,
    context={
        "domain": "infrastructure",
        "target": "pulumi",
        "user_role": "ceo"
    },
    optimization_level="balanced"
)
```

## Testing Strategy

### Week 1 Testing
1. **Intent Classification Accuracy**
   - Test corpus of 100+ infrastructure commands
   - Verify read-only vs state-changing detection
   - Edge case handling

2. **UI Component Testing**
   - Approval card rendering
   - User interaction flows
   - Mobile responsiveness

### Week 2 Testing
1. **Pulumi Integration**
   - Preview operations
   - Simulated updates
   - Rollback scenarios

2. **End-to-End Workflows**
   - Complete approval cycle
   - Memory persistence
   - Error handling

## Success Metrics

### Technical Metrics
- Intent classification accuracy > 90%
- Simulation accuracy > 95%
- Approval UI response time < 200ms
- Zero unauthorized state changes

### Business Metrics
- CEO can manage infrastructure via chat
- 70% reduction in context switching
- Complete audit trail maintained
- All changes reversible

## Deployment Plan

### Local Development (Days 1-8)
1. Implement all components
2. Unit testing
3. Integration testing
4. Mock infrastructure for safety

### Staging Deployment (Days 9-10)
1. Deploy to development Kubernetes
2. Test with non-critical infrastructure
3. CEO user acceptance testing

### Production Rollout (Days 11-14)
1. Deploy with read-only mode first
2. Enable state changes for dev environment
3. Gradual rollout to production
4. Documentation and training

## Risk Mitigation

### Technical Risks
1. **Accidental State Changes**
   - Mitigation: Approval required for all changes
   - Rollback: Automated rollback on failure

2. **Simulation Inaccuracy**
   - Mitigation: Conservative estimates
   - Fallback: Always show raw preview output

### Business Risks
1. **CEO Discomfort**
   - Mitigation: Extensive testing and training
   - Fallback: Traditional tools remain available

2. **Audit Compliance**
   - Mitigation: Complete logging of all actions
   - Evidence: Immutable audit trail in Snowflake

## Future Enhancements (Phase 2 Preview)

1. **N8N Background Automation**
   - Scheduled infrastructure checks
   - Drift detection and alerting
   - Automated rollbacks

2. **Multi-Service Orchestration**
   - Coordinate changes across services
   - Dependency management
   - Parallel execution

3. **Advanced Learning**
   - Predict optimal configurations
   - Suggest improvements
   - Anomaly detection

## Conclusion

Phase 1.5 transforms Sophia AI into an infrastructure command center while maintaining the CEO's complete control. By integrating AIaC principles with our unified chat interface and memory system, we create a unique platform that learns from every action and improves over time.

The implementation is designed to be completed in 2 weeks with a focus on safety, quality, and user experience. Every component has been carefully designed to support the CEO's workflow while providing enterprise-grade reliability and security. 