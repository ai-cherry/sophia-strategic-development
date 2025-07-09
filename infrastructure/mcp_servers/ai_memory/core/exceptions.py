"""
AI Memory Exception Hierarchy
Comprehensive error handling with specific exception types
"""

from __future__ import annotations

from typing import Any


class MemoryError(Exception):
    """Base exception for all AI Memory operations"""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """String representation with context"""
        base_msg = f"{self.error_code}: {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        if self.cause:
            base_msg += f" (Caused by: {self.cause})"
        return base_msg


class MemoryValidationError(MemoryError):
    """Raised when memory data validation fails"""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        super().__init__(
            message, error_code="VALIDATION_ERROR", context=context, **kwargs
        )
        self.field = field
        self.value = value


class MemoryNotFoundError(MemoryError):
    """Raised when requested memory record is not found"""

    def __init__(self, memory_id: str, message: str | None = None, **kwargs):
        message = message or f"Memory record not found: {memory_id}"
        context = kwargs.get("context", {})
        context["memory_id"] = memory_id
        super().__init__(message, error_code="NOT_FOUND", context=context, **kwargs)
        self.memory_id = memory_id


class MemoryStorageError(MemoryError):
    """Raised when storage operations fail"""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        storage_type: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        if storage_type:
            context["storage_type"] = storage_type
        super().__init__(message, error_code="STORAGE_ERROR", context=context, **kwargs)
        self.operation = operation
        self.storage_type = storage_type


class MemoryEmbeddingError(MemoryError):
    """Raised when embedding operations fail"""

    def __init__(
        self,
        message: str,
        model: str | None = None,
        content_length: int | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if model:
            context["model"] = model
        if content_length:
            context["content_length"] = content_length
        super().__init__(
            message, error_code="EMBEDDING_ERROR", context=context, **kwargs
        )
        self.model = model
        self.content_length = content_length


class MemorySearchError(MemoryError):
    """Raised when search operations fail"""

    def __init__(
        self,
        message: str,
        query: str | None = None,
        search_type: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if query:
            context["query"] = query[:100] + "..." if len(query) > 100 else query
        if search_type:
            context["search_type"] = search_type
        super().__init__(message, error_code="SEARCH_ERROR", context=context, **kwargs)
        self.query = query
        self.search_type = search_type


class MemoryConfigurationError(MemoryError):
    """Raised when configuration is invalid or missing"""

    def __init__(self, message: str, config_key: str | None = None, **kwargs):
        context = kwargs.get("context", {})
        if config_key:
            context["config_key"] = config_key
        super().__init__(message, error_code="CONFIG_ERROR", context=context, **kwargs)
        self.config_key = config_key


class MemoryConnectionError(MemoryError):
    """Raised when external service connections fail"""

    def __init__(
        self,
        message: str,
        service: str | None = None,
        endpoint: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if service:
            context["service"] = service
        if endpoint:
            context["endpoint"] = endpoint
        super().__init__(
            message, error_code="CONNECTION_ERROR", context=context, **kwargs
        )
        self.service = service
        self.endpoint = endpoint


class MemoryTimeoutError(MemoryError):
    """Raised when operations timeout"""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        timeout_seconds: float | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        super().__init__(message, error_code="TIMEOUT_ERROR", context=context, **kwargs)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class MemoryCapacityError(MemoryError):
    """Raised when storage or processing capacity limits are exceeded"""

    def __init__(
        self,
        message: str,
        limit_type: str | None = None,
        current_value: Any | None = None,
        limit_value: Any | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if limit_type:
            context["limit_type"] = limit_type
        if current_value is not None:
            context["current_value"] = current_value
        if limit_value is not None:
            context["limit_value"] = limit_value
        super().__init__(
            message, error_code="CAPACITY_ERROR", context=context, **kwargs
        )
        self.limit_type = limit_type
        self.current_value = current_value
        self.limit_value = limit_value


class MemoryPermissionError(MemoryError):
    """Raised when access permissions are insufficient"""

    def __init__(
        self,
        message: str,
        resource: str | None = None,
        required_permission: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if resource:
            context["resource"] = resource
        if required_permission:
            context["required_permission"] = required_permission
        super().__init__(
            message, error_code="PERMISSION_ERROR", context=context, **kwargs
        )
        self.resource = resource
        self.required_permission = required_permission


# Exception mapping for external service errors
EXTERNAL_ERROR_MAPPING = {
    "snowflake": MemoryStorageError,
    "redis": MemoryStorageError,
    "pinecone": MemoryEmbeddingError,
    "weaviate": MemoryEmbeddingError,
    "openai": MemoryEmbeddingError,
}


def map_external_error(
    error: Exception, service: str, operation: str | None = None
) -> MemoryError:
    """Map external service errors to AI Memory exceptions"""

    error_class = EXTERNAL_ERROR_MAPPING.get(service, MemoryError)

    # Extract relevant information from the original error
    message = f"{service.title()} error: {error!s}"
    context = {
        "service": service,
        "original_error": error.__class__.__name__,
    }

    if operation:
        context["operation"] = operation

    # Handle specific error types
    if "timeout" in str(error).lower():
        return MemoryTimeoutError(
            message=message, operation=operation, context=context, cause=error
        )
    elif "connection" in str(error).lower() or "network" in str(error).lower():
        return MemoryConnectionError(
            message=message, service=service, context=context, cause=error
        )
    elif "permission" in str(error).lower() or "unauthorized" in str(error).lower():
        return MemoryPermissionError(
            message=message, resource=service, context=context, cause=error
        )
    elif "capacity" in str(error).lower() or "limit" in str(error).lower():
        return MemoryCapacityError(
            message=message, limit_type=service, context=context, cause=error
        )
    else:
        return error_class(message=message, context=context, cause=error)


def handle_async_exception(func):
    """Decorator to handle async exceptions consistently"""
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            raise MemoryTimeoutError(
                message=f"Operation timed out: {func.__name__}",
                operation=func.__name__,
                cause=e,
            )
        except Exception as e:
            if isinstance(e, MemoryError):
                raise
            else:
                raise MemoryError(
                    message=f"Unexpected error in {func.__name__}: {e!s}",
                    context={"function": func.__name__},
                    cause=e,
                )

    return wrapper
