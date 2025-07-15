"""Audit logger implementation for Sophia AI."""

import json
import logging
import time
from typing import Any

from core.protocols import AuditLoggerProtocol

logger = logging.getLogger(__name__)


class AuditLogger(AuditLoggerProtocol):
    """Default audit logger implementation.

    This implementation logs audit events to standard logging
    infrastructure and can be extended to write to databases,
    SIEM systems, or other audit backends.
    """

    def __init__(self, service_name: str = "sophia-ai"):
        """Initialize audit logger.

        Args:
            service_name: Name of the service for audit context
        """
        self.service_name = service_name

    async def log_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        user_id: str | None = None,
        session_id: str | None = None,
        severity: str = "info",
    ) -> None:
        """Log an audit event.

        Args:
            event_type: Type of event
            event_data: Event-specific data
            user_id: Optional user identifier
            session_id: Optional session identifier
            severity: Event severity
        """
        audit_entry = {
            "timestamp": time.time(),
            "service": self.service_name,
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "session_id": session_id,
            "data": event_data,
        }

        log_method = getattr(logger, severity, logger.info)
        log_method(f"AUDIT: {json.dumps(audit_entry)}")

    async def log_error(
        self,
        error: Exception,
        context: dict[str, Any],
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Log an error with context.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        await self.log_event(
            event_type="error",
            event_data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
            },
            user_id=user_id,
            session_id=session_id,
            severity="error",
        )

    async def log_security_event(
        self,
        action: str,
        resource: str,
        outcome: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a security-relevant event.

        Args:
            action: Action attempted
            resource: Resource accessed
            outcome: Outcome of action
            user_id: Optional user identifier
            metadata: Additional security metadata
        """
        severity = "warning" if outcome == "failure" else "info"

        await self.log_event(
            event_type="security",
            event_data={
                "action": action,
                "resource": resource,
                "outcome": outcome,
                "metadata": metadata or {},
            },
            user_id=user_id,
            severity=severity,
        )

    async def log_workflow_event(
        self,
        workflow_id: str,
        event: str,
        state: dict[str, Any],
        error: str | None = None,
    ) -> None:
        """Log a workflow execution event.

        Args:
            workflow_id: Unique workflow identifier
            event: Workflow event
            state: Current workflow state
            error: Optional error message if failed
        """
        severity = "error" if event == "failed" else "info"

        await self.log_event(
            event_type="workflow",
            event_data={
                "workflow_id": workflow_id,
                "event": event,
                "state": state,
                "error": error,
            },
            severity=severity,
        )
