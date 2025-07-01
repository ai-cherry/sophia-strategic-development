"""
LLM Audit Decorator for Sophia AI Platform

Provides specialized audit logging for LLM operations, including:
- Prompt tracking
- Response logging
- Token usage metrics
- Safety and compliance checks
- Performance monitoring

This module extends the base audit_logger with LLM-specific functionality.
"""

import functools
import time
from collections.abc import Callable
from typing import Any

from backend.security.audit_logger import (
    AuditEventType,
    AuditLogLevel,
    error,
    info,
)


def audit_llm_operation(
    operation_type: str = "completion",
    include_prompt: bool = True,
    include_response: bool = True,
    include_token_usage: bool = True,
    include_model_info: bool = True,
    redact_pii: bool = True,
    log_level: AuditLogLevel = AuditLogLevel.INFO,
):
    """
    Decorator for auditing LLM operations.

    Args:
        operation_type: Type of LLM operation (e.g., "completion", "chat", "embedding")
        include_prompt: Whether to include the prompt in the audit log
        include_response: Whether to include the response in the audit log
        include_token_usage: Whether to include token usage metrics
        include_model_info: Whether to include model information
        redact_pii: Whether to redact PII from prompts and responses
        log_level: Audit log level

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Extract prompt from args or kwargs
            prompt = _extract_prompt(args, kwargs, operation_type)

            # Prepare audit details
            details = {
                "operation_type": operation_type,
                "model": _extract_model(args, kwargs),
            }

            # Include prompt if enabled
            if include_prompt and prompt:
                details["prompt"] = prompt if not redact_pii else _redact_pii(prompt)

            # Log the LLM request
            info(
                AuditEventType.LLM_REQUEST,
                f"LLM {operation_type} request",
                details,
            )

            # Track timing
            start_time = time.time()

            try:
                # Call the original function
                response = await func(*args, **kwargs)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Prepare response details
                response_details = {
                    "operation_type": operation_type,
                    "duration_ms": round(duration_ms, 2),
                }

                # Include model info if enabled
                if include_model_info:
                    response_details["model"] = _extract_model(args, kwargs)

                # Include token usage if enabled
                if include_token_usage:
                    token_usage = _extract_token_usage(response)
                    if token_usage:
                        response_details["token_usage"] = token_usage

                # Include response if enabled
                if include_response:
                    response_content = _extract_response_content(response, operation_type)
                    if response_content:
                        response_details["response"] = (
                            response_content if not redact_pii else _redact_pii(response_content)
                        )

                # Log the LLM response
                info(
                    AuditEventType.LLM_RESPONSE,
                    f"LLM {operation_type} response",
                    response_details,
                )

                return response

            except Exception as e:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log error
                error(
                    AuditEventType.ERROR,
                    f"LLM {operation_type} error: {str(e)}",
                    {
                        "operation_type": operation_type,
                        "error": str(e),
                        "duration_ms": round(duration_ms, 2),
                    },
                )

                # Re-raise the exception
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Extract prompt from args or kwargs
            prompt = _extract_prompt(args, kwargs, operation_type)

            # Prepare audit details
            details = {
                "operation_type": operation_type,
                "model": _extract_model(args, kwargs),
            }

            # Include prompt if enabled
            if include_prompt and prompt:
                details["prompt"] = prompt if not redact_pii else _redact_pii(prompt)

            # Log the LLM request
            info(
                AuditEventType.LLM_REQUEST,
                f"LLM {operation_type} request",
                details,
            )

            # Track timing
            start_time = time.time()

            try:
                # Call the original function
                response = func(*args, **kwargs)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Prepare response details
                response_details = {
                    "operation_type": operation_type,
                    "duration_ms": round(duration_ms, 2),
                }

                # Include model info if enabled
                if include_model_info:
                    response_details["model"] = _extract_model(args, kwargs)

                # Include token usage if enabled
                if include_token_usage:
                    token_usage = _extract_token_usage(response)
                    if token_usage:
                        response_details["token_usage"] = token_usage

                # Include response if enabled
                if include_response:
                    response_content = _extract_response_content(response, operation_type)
                    if response_content:
                        response_details["response"] = (
                            response_content if not redact_pii else _redact_pii(response_content)
                        )

                # Log the LLM response
                info(
                    AuditEventType.LLM_RESPONSE,
                    f"LLM {operation_type} response",
                    response_details,
                )

                return response

            except Exception as e:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log error
                error(
                    AuditEventType.ERROR,
                    f"LLM {operation_type} error: {str(e)}",
                    {
                        "operation_type": operation_type,
                        "error": str(e),
                        "duration_ms": round(duration_ms, 2),
                    },
                )

                # Re-raise the exception
                raise

        # Return appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _extract_prompt(args: tuple, kwargs: dict, operation_type: str) -> str | None:
    """Extract prompt from function arguments"""
    # Check kwargs first
    if "prompt" in kwargs:
        return kwargs["prompt"]
    elif "messages" in kwargs:
        # Handle chat messages
        return _format_chat_messages(kwargs["messages"])
    elif "input" in kwargs:
        return kwargs["input"]
    elif "text" in kwargs:
        return kwargs["text"]

    # Check args if not found in kwargs
    if len(args) > 0:
        # First argument is often the prompt
        if isinstance(args[0], str):
            return args[0]
        elif isinstance(args[0], list) and operation_type == "chat":
            # Handle chat messages
            return _format_chat_messages(args[0])

    return None


def _format_chat_messages(messages: list[dict[str, str]]) -> str:
    """Format chat messages into a string"""
    formatted = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        formatted.append(f"{role}: {content}")

    return "\n".join(formatted)


def _extract_model(args: tuple, kwargs: dict) -> str:
    """Extract model information from function arguments"""
    # Check kwargs first
    if "model" in kwargs:
        return kwargs["model"]
    elif "engine" in kwargs:
        return kwargs["engine"]
    elif "model_name" in kwargs:
        return kwargs["model_name"]

    # Default if not found
    return "unknown"


def _extract_token_usage(response: Any) -> dict[str, int] | None:
    """Extract token usage from response"""
    if not response:
        return None

    # Handle different response formats
    if hasattr(response, "usage"):
        # OpenAI-style response
        usage = response.usage
        if hasattr(usage, "to_dict"):
            return usage.to_dict()
        return {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
            "completion_tokens": getattr(usage, "completion_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
        }

    # Handle dictionary response
    if isinstance(response, dict):
        if "usage" in response:
            return response["usage"]

        # Try to extract token counts directly
        token_usage = {}
        for key in ["prompt_tokens", "completion_tokens", "total_tokens"]:
            if key in response:
                token_usage[key] = response[key]

        if token_usage:
            return token_usage

    return None


def _extract_response_content(response: Any, operation_type: str) -> str | None:
    """Extract content from response"""
    if not response:
        return None

    # Handle different response formats
    if hasattr(response, "choices") and len(getattr(response, "choices", [])) > 0:
        # OpenAI-style response
        choices = response.choices
        if operation_type == "chat":
            # Chat completion
            if hasattr(choices[0], "message"):
                return choices[0].message.content
        else:
            # Text completion
            if hasattr(choices[0], "text"):
                return choices[0].text

    # Handle dictionary response
    if isinstance(response, dict):
        if "choices" in response and len(response["choices"]) > 0:
            choices = response["choices"]
            if operation_type == "chat":
                # Chat completion
                if "message" in choices[0]:
                    return choices[0]["message"].get("content")
            else:
                # Text completion
                if "text" in choices[0]:
                    return choices[0]["text"]

        # Try direct content field
        if "content" in response:
            return response["content"]
        elif "text" in response:
            return response["text"]
        elif "output" in response:
            return response["output"]

    # Handle string response
    if isinstance(response, str):
        return response

    return None


def _redact_pii(text: str) -> str:
    """Redact PII from text"""
    import re

    # Redact email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL REDACTED]',
        text
    )

    # Redact phone numbers
    text = re.sub(
        r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        '[PHONE REDACTED]',
        text
    )

    # Redact SSNs
    text = re.sub(
        r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
        '[SSN REDACTED]',
        text
    )

    # Redact credit card numbers
    text = re.sub(
        r'\b(?:\d{4}[- ]?){3}\d{4}\b',
        '[CREDIT CARD REDACTED]',
        text
    )

    return text


# Import asyncio at the end to avoid circular imports
import asyncio

