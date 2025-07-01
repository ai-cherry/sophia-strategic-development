"""
RBAC Dependencies and Middleware for FastAPI

This module provides FastAPI dependencies and middleware for RBAC integration,
including:
- Dependencies for checking permissions
- Middleware for automatic permission checking
- Decorators for securing endpoints
"""

import functools
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from backend.security.audit_logger import AuditEventType, info, warning
from backend.security.rbac.models import ActionType, ResourceType, User
from backend.security.rbac.service import get_rbac_service

logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# User extraction

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token.
    
    In a real application, this would validate the token and fetch the user from a database.
    For now, this is a placeholder that returns a mock user.
    
    Args:
        token: OAuth2 token
    
    Returns:
        User object
    
    Raises:
        HTTPException: If authentication fails
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real application, you would validate the token and fetch the user
    # For now, we'll use a mock user
    try:
        # Get the RBAC service
        rbac_service = get_rbac_service()
        
        # Try to get the user from the RBAC service
        # In a real application, you would extract the user ID from the token
        user_id = "user123"  # Mock user ID
        user = rbac_service.get_user(user_id)
        
        if not user:
            # If the user doesn't exist in the RBAC service, create a mock user
            user = User(
                id=user_id,
                email="user@example.com",
                name="Test User",
                is_active=True,
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Get the current user from the token, or None if not authenticated.
    
    Args:
        token: OAuth2 token
    
    Returns:
        User object, or None if not authenticated
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


# Permission checking dependencies

def require_permission(
    resource_type: ResourceType,
    action: ActionType,
    resource_id: Optional[str] = None,
):
    """
    Dependency for checking if the current user has permission to perform an action.
    
    Args:
        resource_type: Type of resource to check
        action: Action to check
        resource_id: Optional ID of the specific resource instance
    
    Returns:
        Dependency function
    
    Example:
        ```python
        @app.get("/documents/{document_id}")
        async def get_document(
            document_id: str,
            _: dict = Depends(require_permission(ResourceType.DOCUMENT, ActionType.READ)),
        ):
            # This endpoint will only be accessible if the user has permission to read documents
            ...
        ```
    """
    async def check_permission(
        request: Request,
        user: User = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """Check if the user has permission"""
        # Get the RBAC service
        rbac_service = get_rbac_service()
        
        # Get the resource ID from the path parameter if not provided
        actual_resource_id = resource_id
        if not actual_resource_id and "{" in str(request.url.path):
            # Extract resource ID from path parameters
            path_params = request.path_params
            for param_name, param_value in path_params.items():
                if param_name.endswith("_id"):
                    actual_resource_id = param_value
                    break
        
        # Get context from request
        context = {
            "path": request.url.path,
            "method": request.method,
        }
        
        # Add query parameters to context
        for key, value in request.query_params.items():
            context[f"query_{key}"] = value
        
        # Check permission
        has_permission = rbac_service.check_permission(
            user_id=user.id,
            resource_type=resource_type,
            action=action,
            resource_id=actual_resource_id,
            context=context,
        )
        
        if not has_permission:
            # Log the permission denial
            warning(
                AuditEventType.ACCESS_DENIED,
                f"Permission denied: {action} {resource_type}",
                {
                    "user_id": user.id,
                    "resource_type": resource_type,
                    "action": action,
                    "resource_id": actual_resource_id,
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} {resource_type}",
            )
        
        # Log the permission grant
        info(
            AuditEventType.ACCESS_GRANTED,
            f"Permission granted: {action} {resource_type}",
            {
                "user_id": user.id,
                "resource_type": resource_type,
                "action": action,
                "resource_id": actual_resource_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
        
        # Return context for use in the endpoint
        return {
            "user": user,
            "resource_type": resource_type,
            "action": action,
            "resource_id": actual_resource_id,
            "context": context,
        }
    
    return check_permission


def require_system_admin(user: User = Depends(get_current_user)) -> User:
    """
    Dependency for checking if the current user is a system administrator.
    
    Args:
        user: Current user
    
    Returns:
        User object if the user is a system administrator
    
    Raises:
        HTTPException: If the user is not a system administrator
    """
    if not user.is_system_admin:
        # Log the permission denial
        warning(
            AuditEventType.ACCESS_DENIED,
            "System administrator access denied",
            {"user_id": user.id},
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System administrator access required",
        )
    
    # Log the permission grant
    info(
        AuditEventType.ACCESS_GRANTED,
        "System administrator access granted",
        {"user_id": user.id},
    )
    
    return user


# RBAC middleware

class RBACMiddleware:
    """
    Middleware for automatic RBAC permission checking.
    
    This middleware checks permissions for all requests based on route configuration.
    """
    
    def __init__(
        self,
        app: FastAPI,
        default_resource_type: Optional[ResourceType] = None,
        default_action_mapping: Optional[Dict[str, ActionType]] = None,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        Initialize the RBAC middleware.
        
        Args:
            app: FastAPI application
            default_resource_type: Default resource type for routes without explicit configuration
            default_action_mapping: Default mapping of HTTP methods to actions
            exclude_paths: List of paths to exclude from RBAC checking
        """
        self.app = app
        self.default_resource_type = default_resource_type
        self.default_action_mapping = default_action_mapping or {
            "GET": ActionType.READ,
            "POST": ActionType.CREATE,
            "PUT": ActionType.UPDATE,
            "PATCH": ActionType.UPDATE,
            "DELETE": ActionType.DELETE,
        }
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json"]
        
        # Route configuration for RBAC
        self.route_config: Dict[str, Dict[str, Any]] = {}
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and check permissions.
        
        Args:
            request: FastAPI request
            call_next: Next middleware in the chain
        
        Returns:
            FastAPI response
        """
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get route configuration
        route_config = self.get_route_config(request)
        if not route_config:
            # No RBAC configuration for this route, skip checking
            return await call_next(request)
        
        # Extract configuration
        resource_type = route_config.get("resource_type", self.default_resource_type)
        action = route_config.get("action", self.default_action_mapping.get(request.method))
        resource_id = route_config.get("resource_id")
        
        if not resource_type or not action:
            # Missing configuration, skip checking
            return await call_next(request)
        
        try:
            # Get the current user
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                # No token, skip checking (will be handled by the endpoint)
                return await call_next(request)
            
            # Get the RBAC service
            rbac_service = get_rbac_service()
            
            # Extract user ID from token
            # In a real application, you would validate the token and extract the user ID
            user_id = "user123"  # Mock user ID
            
            # Get the resource ID from the path parameter if not provided
            actual_resource_id = resource_id
            if not actual_resource_id and "{" in str(request.url.path):
                # Extract resource ID from path parameters
                path_params = request.path_params
                for param_name, param_value in path_params.items():
                    if param_name.endswith("_id"):
                        actual_resource_id = param_value
                        break
            
            # Get context from request
            context = {
                "path": request.url.path,
                "method": request.method,
            }
            
            # Add query parameters to context
            for key, value in request.query_params.items():
                context[f"query_{key}"] = value
            
            # Check permission
            has_permission = rbac_service.check_permission(
                user_id=user_id,
                resource_type=resource_type,
                action=action,
                resource_id=actual_resource_id,
                context=context,
            )
            
            if not has_permission:
                # Log the permission denial
                warning(
                    AuditEventType.ACCESS_DENIED,
                    f"Permission denied: {action} {resource_type}",
                    {
                        "user_id": user_id,
                        "resource_type": resource_type,
                        "action": action,
                        "resource_id": actual_resource_id,
                        "path": request.url.path,
                        "method": request.method,
                    },
                )
                
                # Return 403 Forbidden
                return Response(
                    content=json.dumps({
                        "detail": f"Permission denied: {action} {resource_type}"
                    }),
                    status_code=status.HTTP_403_FORBIDDEN,
                    media_type="application/json",
                )
            
            # Log the permission grant
            info(
                AuditEventType.ACCESS_GRANTED,
                f"Permission granted: {action} {resource_type}",
                {
                    "user_id": user_id,
                    "resource_type": resource_type,
                    "action": action,
                    "resource_id": actual_resource_id,
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            
            # Continue processing the request
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"RBAC middleware error: {e}")
            return await call_next(request)
    
    def get_route_config(self, request: Request) -> Dict[str, Any]:
        """
        Get RBAC configuration for a route.
        
        Args:
            request: FastAPI request
        
        Returns:
            RBAC configuration for the route
        """
        # Get the route path
        path = request.url.path
        method = request.method
        
        # Check if we have a configuration for this exact path and method
        key = f"{method}:{path}"
        if key in self.route_config:
            return self.route_config[key]
        
        # Check if we have a configuration for this path with any method
        key = f"*:{path}"
        if key in self.route_config:
            return self.route_config[key]
        
        # No configuration found
        return {}
    
    def configure_route(
        self,
        path: str,
        method: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[ActionType] = None,
        resource_id: Optional[str] = None,
    ):
        """
        Configure RBAC for a route.
        
        Args:
            path: Route path
            method: HTTP method (or None for all methods)
            resource_type: Resource type for the route
            action: Action for the route
            resource_id: Resource ID for the route
        """
        # Create the configuration
        config = {
            "resource_type": resource_type,
            "action": action,
            "resource_id": resource_id,
        }
        
        # Store the configuration
        key = f"{method or '*'}:{path}"
        self.route_config[key] = config


# Decorators

T = TypeVar("T", bound=Callable)


def requires_permission(
    resource_type: ResourceType,
    action: ActionType,
    resource_id: Optional[str] = None,
) -> Callable[[T], T]:
    """
    Decorator for requiring permission to access an endpoint.
    
    Args:
        resource_type: Type of resource to check
        action: Action to check
        resource_id: Optional ID of the specific resource instance
    
    Returns:
        Decorator function
    
    Example:
        ```python
        @app.get("/documents/{document_id}")
        @requires_permission(ResourceType.DOCUMENT, ActionType.READ)
        async def get_document(document_id: str):
            # This endpoint will only be accessible if the user has permission to read documents
            ...
        ```
    """
    def decorator(func: T) -> T:
        # Add dependency to the endpoint
        dependency = require_permission(resource_type, action, resource_id)
        
        # Get the original dependencies
        if hasattr(func, "dependencies"):
            original_dependencies = getattr(func, "dependencies")
            dependencies = list(original_dependencies)
        else:
            dependencies = []
        
        # Add the new dependency
        dependencies.append(Depends(dependency))
        
        # Update the function dependencies
        setattr(func, "dependencies", dependencies)
        
        return func
    
    return decorator


def requires_system_admin(func: T) -> T:
    """
    Decorator for requiring system administrator access to an endpoint.
    
    Args:
        func: Endpoint function
    
    Returns:
        Decorated function
    
    Example:
        ```python
        @app.get("/admin/users")
        @requires_system_admin
        async def get_users():
            # This endpoint will only be accessible to system administrators
            ...
        ```
    """
    # Add dependency to the endpoint
    dependency = Depends(require_system_admin)
    
    # Get the original dependencies
    if hasattr(func, "dependencies"):
        original_dependencies = getattr(func, "dependencies")
        dependencies = list(original_dependencies)
    else:
        dependencies = []
    
    # Add the new dependency
    dependencies.append(dependency)
    
    # Update the function dependencies
    setattr(func, "dependencies", dependencies)
    
    return func


# Setup function for FastAPI

def setup_rbac(
    app: FastAPI,
    storage_path: Optional[str] = None,
    load_system_roles: bool = True,
    auto_save: bool = True,
    default_resource_type: Optional[ResourceType] = None,
    default_action_mapping: Optional[Dict[str, ActionType]] = None,
    exclude_paths: Optional[List[str]] = None,
    use_middleware: bool = False,
) -> None:
    """
    Set up RBAC for a FastAPI application.
    
    Args:
        app: FastAPI application
        storage_path: Path to store RBAC data (if None, data is only in memory)
        load_system_roles: Whether to load system-defined roles
        auto_save: Whether to automatically save changes to storage
        default_resource_type: Default resource type for routes without explicit configuration
        default_action_mapping: Default mapping of HTTP methods to actions
        exclude_paths: List of paths to exclude from RBAC checking
        use_middleware: Whether to use the RBAC middleware for automatic permission checking
    """
    from backend.security.rbac.service import initialize_rbac_service
    
    # Initialize the RBAC service
    initialize_rbac_service(
        storage_path=storage_path,
        load_system_roles=load_system_roles,
        auto_save=auto_save,
    )
    
    # Add RBAC middleware if requested
    if use_middleware:
        middleware = RBACMiddleware(
            app=app,
            default_resource_type=default_resource_type,
            default_action_mapping=default_action_mapping,
            exclude_paths=exclude_paths,
        )
        
        app.add_middleware(middleware.__class__, middleware=middleware)
        
        logger.info("Added RBAC middleware to FastAPI application")
    
    # Log setup
    logger.info("Set up RBAC for FastAPI application")
    
    info(
        AuditEventType.SYSTEM_START,
        "Set up RBAC for FastAPI application",
        {
            "storage_path": storage_path,
            "load_system_roles": load_system_roles,
            "auto_save": auto_save,
            "use_middleware": use_middleware,
        },
    )

