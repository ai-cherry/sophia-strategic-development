"""
RBAC API Routes for Sophia AI Platform

This module provides API routes for managing RBAC components:
- Roles
- Permissions
- Role assignments
- Users

These routes allow administrators to manage the RBAC system through a REST API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from backend.security.audit_logger import AuditEventType, info
from backend.security.rbac.dependencies import require_permission, require_system_admin
from backend.security.rbac.models import (
    ActionType,
    Permission,
    ResourceType,
    Role,
    RoleAssignment,
    User,
)
from backend.security.rbac.service import get_rbac_service

# Create router
router = APIRouter(prefix="/api/v3/rbac", tags=["RBAC"])


# Request and response models

class PermissionCreate(BaseModel):
    """Model for creating a permission"""
    resource_type: ResourceType
    actions: List[ActionType]
    resource_id: Optional[str] = None
    attributes: Optional[List[str]] = None
    condition: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class RoleCreate(BaseModel):
    """Model for creating a role"""
    name: str
    permissions: List[PermissionCreate]
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    """Model for updating a role"""
    name: Optional[str] = None
    permissions: Optional[List[PermissionCreate]] = None
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """Model for role response"""
    id: str
    name: str
    permissions: List[Permission]
    description: Optional[str] = None
    is_system_role: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Model for creating a user"""
    id: str
    email: str
    name: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    is_system_admin: bool = False


class UserUpdate(BaseModel):
    """Model for updating a user"""
    email: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    is_system_admin: Optional[bool] = None


class UserResponse(BaseModel):
    """Model for user response"""
    id: str
    email: str
    name: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    is_system_admin: bool
    created_at: datetime
    updated_at: datetime


class RoleAssignmentCreate(BaseModel):
    """Model for creating a role assignment"""
    user_id: str
    role_id: str
    scope_type: Optional[ResourceType] = None
    scope_id: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class RoleAssignmentUpdate(BaseModel):
    """Model for updating a role assignment"""
    scope_type: Optional[ResourceType] = None
    scope_id: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class RoleAssignmentResponse(BaseModel):
    """Model for role assignment response"""
    id: str
    user_id: str
    role_id: str
    scope_type: Optional[ResourceType] = None
    scope_id: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    created_by: Optional[str] = None


class PermissionCheckRequest(BaseModel):
    """Model for permission check request"""
    user_id: str
    resource_type: ResourceType
    action: ActionType
    resource_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PermissionCheckResponse(BaseModel):
    """Model for permission check response"""
    has_permission: bool
    user_id: str
    resource_type: ResourceType
    action: ActionType
    resource_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# Role routes

@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.READ)),
) -> List[Role]:
    """
    Get all roles.
    
    Returns:
        List of roles
    """
    rbac_service = get_rbac_service()
    return rbac_service.get_roles()


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str = Path(..., description="ID of the role to get"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.READ)),
) -> Role:
    """
    Get a role by ID.
    
    Args:
        role_id: ID of the role to get
    
    Returns:
        Role
    
    Raises:
        HTTPException: If the role is not found
    """
    rbac_service = get_rbac_service()
    role = rbac_service.get_role(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {role_id}",
        )
    
    return role


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_create: RoleCreate,
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.CREATE)),
) -> Role:
    """
    Create a new role.
    
    Args:
        role_create: Role creation data
    
    Returns:
        Created role
    """
    rbac_service = get_rbac_service()
    
    # Convert permissions
    permissions = [
        Permission(
            resource_type=p.resource_type,
            actions=p.actions,
            resource_id=p.resource_id,
            attributes=p.attributes,
            condition=p.condition,
            description=p.description,
        )
        for p in role_create.permissions
    ]
    
    # Create the role
    role = rbac_service.create_role(
        name=role_create.name,
        permissions=permissions,
        description=role_create.description,
    )
    
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_update: RoleUpdate,
    role_id: str = Path(..., description="ID of the role to update"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.UPDATE)),
) -> Role:
    """
    Update a role.
    
    Args:
        role_update: Role update data
        role_id: ID of the role to update
    
    Returns:
        Updated role
    
    Raises:
        HTTPException: If the role is not found or is a system role
    """
    rbac_service = get_rbac_service()
    
    # Check if the role exists
    role = rbac_service.get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {role_id}",
        )
    
    # Check if the role is a system role
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot update system role: {role.name}",
        )
    
    # Convert permissions if provided
    permissions = None
    if role_update.permissions is not None:
        permissions = [
            Permission(
                resource_type=p.resource_type,
                actions=p.actions,
                resource_id=p.resource_id,
                attributes=p.attributes,
                condition=p.condition,
                description=p.description,
            )
            for p in role_update.permissions
        ]
    
    # Update the role
    updated_role = rbac_service.update_role(
        role_id=role_id,
        name=role_update.name,
        permissions=permissions,
        description=role_update.description,
    )
    
    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {role_id}",
        )
    
    return updated_role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str = Path(..., description="ID of the role to delete"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.DELETE)),
) -> None:
    """
    Delete a role.
    
    Args:
        role_id: ID of the role to delete
    
    Raises:
        HTTPException: If the role is not found or is a system role
    """
    rbac_service = get_rbac_service()
    
    # Check if the role exists
    role = rbac_service.get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {role_id}",
        )
    
    # Check if the role is a system role
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot delete system role: {role.name}",
        )
    
    # Delete the role
    success = rbac_service.delete_role(role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {role_id}",
        )


# User routes

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    _: Dict[str, Any] = Depends(require_permission(ResourceType.USER, ActionType.READ)),
) -> List[User]:
    """
    Get all users.
    
    Returns:
        List of users
    """
    rbac_service = get_rbac_service()
    return rbac_service.get_users()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(..., description="ID of the user to get"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.USER, ActionType.READ)),
) -> User:
    """
    Get a user by ID.
    
    Args:
        user_id: ID of the user to get
    
    Returns:
        User
    
    Raises:
        HTTPException: If the user is not found
    """
    rbac_service = get_rbac_service()
    user = rbac_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )
    
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    _: Dict[str, Any] = Depends(require_permission(ResourceType.USER, ActionType.CREATE)),
) -> User:
    """
    Create a new user.
    
    Args:
        user_create: User creation data
    
    Returns:
        Created user
    """
    rbac_service = get_rbac_service()
    
    # Create the user
    user = rbac_service.create_user(
        user_id=user_create.id,
        email=user_create.email,
        name=user_create.name,
        department=user_create.department,
        is_active=user_create.is_active,
        is_system_admin=user_create.is_system_admin,
    )
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: str = Path(..., description="ID of the user to update"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.USER, ActionType.UPDATE)),
) -> User:
    """
    Update a user.
    
    Args:
        user_update: User update data
        user_id: ID of the user to update
    
    Returns:
        Updated user
    
    Raises:
        HTTPException: If the user is not found
    """
    rbac_service = get_rbac_service()
    
    # Update the user
    updated_user = rbac_service.update_user(
        user_id=user_id,
        email=user_update.email,
        name=user_update.name,
        department=user_update.department,
        is_active=user_update.is_active,
        is_system_admin=user_update.is_system_admin,
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )
    
    return updated_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str = Path(..., description="ID of the user to delete"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.USER, ActionType.DELETE)),
) -> None:
    """
    Delete a user.
    
    Args:
        user_id: ID of the user to delete
    
    Raises:
        HTTPException: If the user is not found
    """
    rbac_service = get_rbac_service()
    
    # Delete the user
    success = rbac_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )


# Role assignment routes

@router.get("/assignments", response_model=List[RoleAssignmentResponse])
async def get_role_assignments(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    role_id: Optional[str] = Query(None, description="Filter by role ID"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.READ)),
) -> List[RoleAssignment]:
    """
    Get role assignments, optionally filtered by user or role.
    
    Args:
        user_id: Filter by user ID
        role_id: Filter by role ID
    
    Returns:
        List of role assignments
    """
    rbac_service = get_rbac_service()
    return rbac_service.get_role_assignments(user_id=user_id, role_id=role_id)


@router.get("/assignments/{assignment_id}", response_model=RoleAssignmentResponse)
async def get_role_assignment(
    assignment_id: str = Path(..., description="ID of the role assignment to get"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.READ)),
) -> RoleAssignment:
    """
    Get a role assignment by ID.
    
    Args:
        assignment_id: ID of the role assignment to get
    
    Returns:
        Role assignment
    
    Raises:
        HTTPException: If the role assignment is not found
    """
    rbac_service = get_rbac_service()
    assignment = rbac_service.get_role_assignment(assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role assignment not found: {assignment_id}",
        )
    
    return assignment


@router.post(
    "/assignments",
    response_model=RoleAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role_assignment(
    assignment_create: RoleAssignmentCreate,
    auth_context: Dict[str, Any] = Depends(
        require_permission(ResourceType.ROLE, ActionType.ASSIGN)
    ),
) -> RoleAssignment:
    """
    Create a new role assignment.
    
    Args:
        assignment_create: Role assignment creation data
        auth_context: Authentication context
    
    Returns:
        Created role assignment
    
    Raises:
        HTTPException: If the user or role is not found
    """
    rbac_service = get_rbac_service()
    
    # Check if the user exists
    user = rbac_service.get_user(assignment_create.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {assignment_create.user_id}",
        )
    
    # Check if the role exists
    role = rbac_service.get_role(assignment_create.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {assignment_create.role_id}",
        )
    
    # Create the role assignment
    assignment = rbac_service.assign_role(
        user_id=assignment_create.user_id,
        role_id=assignment_create.role_id,
        scope_type=assignment_create.scope_type,
        scope_id=assignment_create.scope_id,
        constraints=assignment_create.constraints,
        expires_at=assignment_create.expires_at,
        created_by=auth_context["user"].id,
    )
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create role assignment",
        )
    
    return assignment


@router.put("/assignments/{assignment_id}", response_model=RoleAssignmentResponse)
async def update_role_assignment(
    assignment_update: RoleAssignmentUpdate,
    assignment_id: str = Path(..., description="ID of the role assignment to update"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.UPDATE)),
) -> RoleAssignment:
    """
    Update a role assignment.
    
    Args:
        assignment_update: Role assignment update data
        assignment_id: ID of the role assignment to update
    
    Returns:
        Updated role assignment
    
    Raises:
        HTTPException: If the role assignment is not found
    """
    rbac_service = get_rbac_service()
    
    # Update the role assignment
    updated_assignment = rbac_service.update_role_assignment(
        assignment_id=assignment_id,
        scope_type=assignment_update.scope_type,
        scope_id=assignment_update.scope_id,
        constraints=assignment_update.constraints,
        expires_at=assignment_update.expires_at,
    )
    
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role assignment not found: {assignment_id}",
        )
    
    return updated_assignment


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_assignment(
    assignment_id: str = Path(..., description="ID of the role assignment to delete"),
    _: Dict[str, Any] = Depends(require_permission(ResourceType.ROLE, ActionType.DELETE)),
) -> None:
    """
    Delete a role assignment.
    
    Args:
        assignment_id: ID of the role assignment to delete
    
    Raises:
        HTTPException: If the role assignment is not found
    """
    rbac_service = get_rbac_service()
    
    # Delete the role assignment
    success = rbac_service.remove_role_assignment(assignment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role assignment not found: {assignment_id}",
        )


# Permission checking routes

@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission(
    check_request: PermissionCheckRequest,
    _: Dict[str, Any] = Depends(require_system_admin),
) -> PermissionCheckResponse:
    """
    Check if a user has permission to perform an action on a resource.
    
    Args:
        check_request: Permission check request
    
    Returns:
        Permission check response
    """
    rbac_service = get_rbac_service()
    
    # Check permission
    has_permission = rbac_service.check_permission(
        user_id=check_request.user_id,
        resource_type=check_request.resource_type,
        action=check_request.action,
        resource_id=check_request.resource_id,
        context=check_request.context,
    )
    
    # Log the permission check
    info(
        AuditEventType.CUSTOM,
        f"Permission check: {check_request.action} {check_request.resource_type}",
        {
            "user_id": check_request.user_id,
            "resource_type": check_request.resource_type,
            "action": check_request.action,
            "resource_id": check_request.resource_id,
            "has_permission": has_permission,
        },
    )
    
    # Return the result
    return PermissionCheckResponse(
        has_permission=has_permission,
        user_id=check_request.user_id,
        resource_type=check_request.resource_type,
        action=check_request.action,
        resource_id=check_request.resource_id,
        context=check_request.context,
    )

