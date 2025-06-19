#!/usr/bin/env python3
"""
Unified Command Interface for Sophia AI
Enhanced with workflow automation, observability, and inline documentation
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import core components
from backend.agents.core.agent_router import agent_router
from backend.core.context_manager import context_manager

# Import Phase 3 components
from backend.workflows.langgraph_workflow import (
    WorkflowTemplates, workflow_manager
)
from backend.monitoring.observability import (
    structured_logger, distributed_tracer, agent_metrics, monitoring_dashboard
)
from backend.docs.inline_documentation import (
    get_help, suggest_completions, help_with_error
)

class UnifiedCommandInterface:
    """
    Main interface for natural language commands with Sophia AI
    Now with workflows, observability, and documentation
    """
    
    def __init__(self):
        self.session_id = None
        self.context = {}
        self.logger = structured_logger
        
    async def initialize(self):
        """Initialize the interface and create session"""
        self.session_id = await context_manager.create_session(
            user_id="cli_user",
            metadata={"interface": "unified_cli", "version": "3.0"}
        )
        self.logger.info("Unified interface initialized", session_id=self.session_id)
        print(f"✨ Sophia AI initialized (Session: {self.session_id})")
        print("Type 'help' for assistance or 'exit' to quit\n")
        
    async def process_command(self, command: str) -> Dict[str, Any]:
        """Process a natural language command with full observability"""
        # Start tracing
        async with distributed_tracer.trace(
            operation_name="process_command",
            tags={"command": command, "session_id": self.session_id}
        ) as span:
            try:
                start_time = datetime.utcnow()
                
                # Log command
                self.logger.info(
                    "Processing command",
                    command=command,
                    session_id=self.session_id,
                    trace_id=span.trace_id
                )
                
                # Check for special commands
                if command.lower() in ['help', '?']:
                    return await self._show_help()
                elif command.lower().startswith('help '):
                    query = command[5:]
                    return {"status": "success", "result": get_help(query)}
                elif command.lower() == 'status':
                    return await self._show_status()
                elif command.lower() == 'workflows':
                    return await self._list_workflows()
                elif command.lower().startswith('execute workflow'):
                    return await self._execute_workflow(command)
                elif command.lower() == 'metrics':
                    return await self._show_metrics()
                
                # Update context
                await context_manager.update_context(
                    self.session_id,
                    {"last_command": command, "timestamp": datetime.utcnow().isoformat()}
                )
                
                # Route to appropriate agent
                result = await agent_router.route_command(command, self.context)
                
                # Record metrics
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                await agent_metrics.record_agent_execution(
                    agent_name=result.get("agent", "unknown"),
                    duration_ms=duration_ms,
                    status=result.get("status", "unknown"),
                    command_type=self._classify_command(command)
                )
                
                # Log result
                self.logger.info(
                    "Command completed",
                    status=result.get("status"),
                    agent=result.get("agent"),
                    duration_ms=duration_ms,
                    session_id=self.session_id
                )
                
                return result
                
            except Exception as e:
                self.logger.error(
                    "Command failed",
                    error=str(e),
                    command=command,
                    session_id=self.session_id
                )
                
                # Try to get error help
                error_help = help_with_error(str(e))
                if error_help:
                    return {
                        "status": "error",
                        "error": str(e),
                        "help": error_help
                    }
                
                return {"status": "error", "error": str(e)}
    
    def _classify_command(self, command: str) -> str:
        """Classify command type for metrics"""
        command_lower = command.lower()
        if any(word in command_lower for word in ["build", "deploy", "run"]):
            return "execution"
        elif any(word in command_lower for word in ["preview", "list", "show", "get"]):
            return "query"
        elif any(word in command_lower for word in ["create", "generate"]):
            return "creation"
        elif any(word in command_lower for word in ["review", "analyze"]):
            return "analysis"
        else:
            return "other"
    
    async def _show_help(self) -> Dict[str, Any]:
        """Show general help"""
        help_text = get_help("general")
        return {"status": "success", "result": help_text}
    
    async def _show_status(self) -> Dict[str, Any]:
        """Show system status and health"""
        health = await monitoring_dashboard.get_system_health()
        
        status_text = f"""
## System Status

**Health**: {health['status'].upper()}
**Session**: {self.session_id}
**Active Sessions**: {health['metrics']['active_sessions']}

### Metrics
- Agent Success Rate: {health['metrics']['agent_success_rate']:.1f}%
- LLM Success Rate: {health['metrics']['llm_success_rate']:.1f}%
- Recent Errors: {health['metrics']['recent_errors']}

### Alerts
"""
        for alert in health['alerts']:
            status_text += f"- ⚠️  {alert['message']}\n"
        
        return {"status": "success", "result": status_text}
    
    async def _list_workflows(self) -> Dict[str, Any]:
        """List available workflows"""
        workflows_text = """
## Available Workflows

### 1. Deployment Workflow
Deploy your application from build to production
```
execute workflow deployment for [environment]
```

### 2. Code Review Workflow
Comprehensive code analysis and review
```
execute workflow code_review for [path]
```

### 3. Infrastructure Update Workflow
Update infrastructure across environments
```
execute workflow infrastructure_update
```

### Recent Workflows
"""
        recent = workflow_manager.get_recent_workflows(5)
        for wf in recent:
            workflows_text += f"- {wf['workflow_id']}: {wf['status']} ({wf['completed_at']})\n"
        
        return {"status": "success", "result": workflows_text}
    
    async def _execute_workflow(self, command: str) -> Dict[str, Any]:
        """Execute a workflow based on command"""
        parts = command.lower().split()
        
        if "deployment" in command:
            # Extract environment
            env = "staging"  # default
            if "production" in command:
                env = "production"
            elif "dev" in command:
                env = "dev"
            
            workflow = WorkflowTemplates.create_deployment_workflow(env)
            self.logger.info(f"Executing deployment workflow for {env}")
            
        elif "code_review" in command or "code review" in command:
            # Extract path
            path = "backend/"  # default
            if " for " in command:
                path = command.split(" for ")[-1].strip()
            
            workflow = WorkflowTemplates.create_code_review_workflow(path)
            self.logger.info(f"Executing code review workflow for {path}")
            
        elif "infrastructure_update" in command or "infrastructure update" in command:
            workflow = WorkflowTemplates.create_infrastructure_update_workflow()
            self.logger.info("Executing infrastructure update workflow")
            
        else:
            return {
                "status": "error",
                "error": "Unknown workflow type",
                "help": "Available workflows: deployment, code_review, infrastructure_update"
            }
        
        # Execute workflow
        print(f"\n🚀 Starting workflow: {workflow.workflow_id}")
        print("This may take a few minutes...\n")
        
        state = await workflow_manager.execute_workflow(
            workflow,
            {"session_id": self.session_id, **self.context}
        )
        
        # Format result
        result_text = f"""
## Workflow Completed

**ID**: {state.workflow_id}
**Status**: {state.status.value.upper()}
**Duration**: {(state.completed_at - state.started_at).total_seconds():.1f}s

### Steps Completed
"""
        for step in state.steps_completed:
            result_text += f"- ✅ {step}\n"
        
        if state.errors:
            result_text += "\n### Errors\n"
            for error in state.errors:
                result_text += f"- ❌ {error['step']}: {error['error']}\n"
        
        return {"status": "success", "result": result_text, "workflow_state": state.to_dict()}
    
    async def _show_metrics(self) -> Dict[str, Any]:
        """Show performance metrics"""
        perf = await monitoring_dashboard.get_agent_performance()
        
        metrics_text = f"""
## Performance Metrics

**Timestamp**: {perf['timestamp']}

### Agent Performance
"""
        for agent, metrics in perf['agents'].items():
            metrics_text += f"\n**{agent}**\n"
            for metric, values in metrics.items():
                if isinstance(values, dict):
                    if 'last' in values:
                        metrics_text += f"- {metric}: {values['last']:.2f}\n"
                    if 'count' in values:
                        metrics_text += f"- Total executions: {values['count']}\n"
        
        return {"status": "success", "result": metrics_text}
    
    def format_result(self, result: Dict[str, Any]):
        """Format result for display"""
        if result["status"] == "success":
            if "result" in result and isinstance(result["result"], str):
                print(f"\n{result['result']}\n")
            else:
                print(f"\n✅ Success: {json.dumps(result.get('data', result), indent=2)}\n")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
            if "help" in result:
                print(f"\n💡 {result['help']}\n")
    
    async def run_interactive(self):
        """Run interactive command loop"""
        await self.initialize()
        
        while True:
            try:
                # Get command with autocomplete hint
                command = input("sophia> ").strip()
                
                if command.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!")
                    break
                
                if not command:
                    continue
                
                # Process command
                result = await self.process_command(command)
                
                # Display result
                self.format_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}\n")
                self.logger.error("Interactive loop error", error=str(e))
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session_id:
            await context_manager.cleanup_session(self.session_id)
            self.logger.info("Session cleaned up", session_id=self.session_id)

async def main():
    """Main entry point"""
    interface = UnifiedCommandInterface()
    
    try:
        if len(sys.argv) > 1:
            # Single command mode
            command = " ".join(sys.argv[1:])
            await interface.initialize()
            result = await interface.process_command(command)
            interface.format_result(result)
        else:
            # Interactive mode
            await interface.run_interactive()
    finally:
        await interface.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

