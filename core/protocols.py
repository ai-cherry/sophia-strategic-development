"""Core protocols for Sophia AI platform."""

from typing import Any, Optional, Protocol


class AuditLoggerProtocol(Protocol):
    """Protocol for audit logging across the platform.

    This protocol defines the interface for audit loggers that track
    important events, errors, and security-relevant activities.
    """

    async def log_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        severity: str = "info",
    ) -> None:
        """Log an audit event.

        Args:
            event_type: Type of event (e.g., "api_call", "error", "security")
            event_data: Event-specific data
            user_id: Optional user identifier
            session_id: Optional session identifier
            severity: Event severity ("debug", "info", "warning", "error", "critical")
        """
        ...

    async def log_error(
        self,
        error: Exception,
        context: dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Log an error with context.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        ...

    async def log_security_event(
        self,
        action: str,
        resource: str,
        outcome: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a security-relevant event.

        Args:
            action: Action attempted (e.g., "access", "modify", "delete")
            resource: Resource accessed
            outcome: Outcome of action ("success", "failure", "blocked")
            user_id: Optional user identifier
            metadata: Additional security metadata
        """
        ...

    async def log_workflow_event(
        self,
        workflow_id: str,
        event: str,
        state: dict[str, Any],
        error: Optional[str] = None,
    ) -> None:
        """Log a workflow execution event.

        Args:
            workflow_id: Unique workflow identifier
            event: Workflow event (e.g., "started", "completed", "failed")
            state: Current workflow state
            error: Optional error message if failed
        """
        ...
