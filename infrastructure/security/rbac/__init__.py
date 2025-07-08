"""
Role-Based Access Control (RBAC) Package for Sophia AI Platform

This package provides RBAC functionality for the Sophia AI platform,
including models, services, dependencies, and API routes.

Key components:
- Models: Core RBAC models (roles, permissions, etc.)
- Service: RBAC service for managing roles and permissions
- Dependencies: FastAPI dependencies for RBAC integration
- Routes: API routes for managing RBAC components
"""

from infrastructure.security.rbac.dependencies import (
    get_current_user,
    get_optional_user,
    require_permission,
    require_system_admin,
    requires_permission,
    requires_system_admin,
    setup_rbac,
)
from infrastructure.security.rbac.models import (
    SYSTEM_ROLES,
    ActionType,
    Permission,
    ResourceType,
    Role,
    RoleAssignment,
    User,
    has_permission,
)
from infrastructure.security.rbac.service import (
    RBACService,
    get_rbac_service,
    initialize_rbac_service,
)

__all__ = [
    "SYSTEM_ROLES",
    # Models
    "ActionType",
    "Permission",
    # Service
    "RBACService",
    "ResourceType",
    "Role",
    "RoleAssignment",
    "User",
    # Dependencies
    "get_current_user",
    "get_optional_user",
    "get_rbac_service",
    "has_permission",
    "initialize_rbac_service",
    "require_permission",
    "require_system_admin",
    "requires_permission",
    "requires_system_admin",
    "setup_rbac",
]
