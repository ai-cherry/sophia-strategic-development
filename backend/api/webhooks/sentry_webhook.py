"""
Sentry Webhook Handler for Sophia AI
Processes incoming webhooks from Sentry for real-time error notifications
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from backend.agents.specialized.sentry_agent import SentryAgent
from backend.agents.core.base_agent import AgentConfig, Task
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

class SentryWebhookPayload(BaseModel):
    """Sentry webhook payload structure."""
    action: str = Field(..., description="The action that triggered the webhook")
    data: Dict[str, Any] = Field(..., description="Event data")
    actor: Optional[Dict[str, Any]] = Field(None, description="User who triggered the action")
    installation: Optional[Dict[str, Any]] = Field(None, description="Installation details")

class SentryIssueData(BaseModel):
    """Sentry issue data structure."""
    id: str
    title: str
    culprit: Optional[str] = None
    permalink: str
    logger: Optional[str] = None
    level: str
    status: str
    statusDetails: Optional[Dict[str, Any]] = None
    isPublic: bool
    platform: Optional[str] = None
    project: Dict[str, Any]
    type: str
    metadata: Dict[str, Any]
    numComments: int
    assignedTo: Optional[Dict[str, Any]] = None
    isBookmarked: bool
    isSubscribed: bool
    subscriptionDetails: Optional[Dict[str, Any]] = None
    hasSeen: bool
    annotations: Optional[list] = None
    isUnhandled: bool
    count: str
    userCount: int
    firstSeen: str
    lastSeen: str

async def process_sentry_webhook(payload: SentryWebhookPayload, background_tasks: BackgroundTasks):
    """Process incoming Sentry webhook."""
    try:
        action = payload.action
        data = payload.data
        
        logger.info(f"Processing Sentry webhook: {action}")
        
        # Handle different webhook actions
        if action == "issue.created":
            await handle_issue_created(data, background_tasks)
        elif action == "issue.resolved":
            await handle_issue_resolved(data)
        elif action == "issue.assigned":
            await handle_issue_assigned(data)
        elif action == "issue.ignored":
            await handle_issue_ignored(data)
        elif action == "error.created":
            await handle_error_created(data, background_tasks)
        elif action == "installation.created":
            await handle_installation_created(data)
        else:
            logger.warning(f"Unhandled Sentry webhook action: {action}")
            
        return {"status": "processed", "action": action}
        
    except Exception as e:
        logger.error(f"Error processing Sentry webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def handle_issue_created(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle new issue creation."""
    issue = data.get("issue", {})
    issue_id = issue.get("id")
    title = issue.get("title", "Unknown Issue")
    level = issue.get("level", "error")
    project = issue.get("project", {})
    
    logger.info(f"New Sentry issue created: {issue_id} - {title}")
    
    # Create a task for the SentryAgent to analyze the issue
    agent_config = AgentConfig(
        agent_id="sentry_webhook_agent",
        agent_type="error_monitoring",
        specialization="sentry"
    )
    
    task = Task(
        task_id=f"sentry_issue_{issue_id}",
        task_type="fetch_sentry_issue_context",
        agent_id="sentry_webhook_agent",
        task_data={
            "project_slug": project.get("slug"),
            "issue_id": issue_id
        },
        status="pending",
        created_at=datetime.utcnow(),
        priority="high" if level in ["error", "fatal"] else "medium"
    )
    
    # Process in background
    background_tasks.add_task(process_issue_analysis, agent_config, task, issue)
    
    # Send notification to Slack if critical
    if level in ["error", "fatal"]:
        background_tasks.add_task(send_critical_error_notification, issue)

async def handle_issue_resolved(data: Dict[str, Any]):
    """Handle issue resolution."""
    issue = data.get("issue", {})
    issue_id = issue.get("id")
    title = issue.get("title", "Unknown Issue")
    
    logger.info(f"Sentry issue resolved: {issue_id} - {title}")
    
    # TODO: Update any tracking systems or dashboards

async def handle_issue_assigned(data: Dict[str, Any]):
    """Handle issue assignment."""
    issue = data.get("issue", {})
    issue_id = issue.get("id")
    assigned_to = issue.get("assignedTo", {})
    
    logger.info(f"Sentry issue {issue_id} assigned to {assigned_to.get('name', 'Unknown')}")
    
    # TODO: Send notification to assigned user

async def handle_issue_ignored(data: Dict[str, Any]):
    """Handle issue being ignored."""
    issue = data.get("issue", {})
    issue_id = issue.get("id")
    
    logger.info(f"Sentry issue {issue_id} marked as ignored")

async def handle_error_created(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle new error event."""
    # Similar to issue created but for individual error events
    await handle_issue_created(data, background_tasks)

async def handle_installation_created(data: Dict[str, Any]):
    """Handle Sentry integration installation."""
    installation = data.get("installation", {})
    org = installation.get("organization", {})
    
    logger.info(f"Sentry integration installed for organization: {org.get('slug')}")

async def process_issue_analysis(agent_config: AgentConfig, task: Task, issue: Dict[str, Any]):
    """Process issue analysis in the background."""
    try:
        agent = SentryAgent(agent_config)
        result = await agent.process_task(task)
        
        if result.get("success"):
            issue_context = result.get("data", {})
            
            # Analyze the issue context
            if issue_context.get("metadata", {}).get("type") == "OutOfMemoryError":
                # Trigger memory optimization workflow
                logger.warning(f"OutOfMemoryError detected in issue {issue.get('id')}")
                # TODO: Trigger memory optimization agent
                
            elif "database" in issue_context.get("culprit", "").lower():
                # Database-related error
                logger.warning(f"Database error detected in issue {issue.get('id')}")
                # TODO: Trigger database health check
                
    except Exception as e:
        logger.error(f"Error processing issue analysis: {e}", exc_info=True)

async def send_critical_error_notification(issue: Dict[str, Any]):
    """Send notification for critical errors."""
    try:
        # TODO: Integrate with Slack agent to send notifications
        logger.info(f"Would send critical error notification for issue {issue.get('id')}")
        
        # Example notification structure
        notification = {
            "channel": "#engineering-alerts",
            "text": f"🚨 Critical Error Detected",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{issue.get('title', 'Unknown Error')}*\n"
                                f"Level: {issue.get('level', 'error').upper()}\n"
                                f"Project: {issue.get('project', {}).get('name', 'Unknown')}\n"
                                f"<{issue.get('permalink')}|View in Sentry>"
                    }
                }
            ]
        }
        
        # TODO: Send via Slack agent
        
    except Exception as e:
        logger.error(f"Error sending critical error notification: {e}", exc_info=True)

@router.post("/sentry")
async def sentry_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming Sentry webhooks.
    
    Sentry sends webhooks for various events:
    - issue.created: New issue created
    - issue.resolved: Issue marked as resolved
    - issue.assigned: Issue assigned to user
    - issue.ignored: Issue marked as ignored
    - error.created: New error event
    - installation.created: Integration installed
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # TODO: Verify Sentry webhook signature
        # signature = request.headers.get("Sentry-Hook-Signature")
        # if not verify_sentry_signature(body, signature):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload_data = json.loads(body)
        payload = SentryWebhookPayload(**payload_data)
        
        # Process webhook
        result = await process_sentry_webhook(payload, background_tasks)
        
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error handling Sentry webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentry/health")
async def sentry_webhook_health():
    """Health check endpoint for Sentry webhook handler."""
    return {
        "status": "healthy",
        "service": "sentry-webhook",
        "timestamp": datetime.utcnow().isoformat()
    }
