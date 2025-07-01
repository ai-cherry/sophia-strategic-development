"""
Role-Based Access Control (RBAC) Models for Sophia AI Platform

This module defines the core RBAC models and structures for the Sophia AI platform,
including roles, permissions, resources, and actions.

Key components:
- Permission: Defines what actions can be performed on which resources
- Role: A collection of permissions assigned to users
- RoleAssignment: Links users to roles with optional context
- PermissionCheck: Functions for checking if a user has permission for an action
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    """Types of resources that can be protected by RBAC"""

    # Core resources
    SYSTEM = "system"
    USER = "user"
    ROLE = "role"

    # AI resources
    LLM = "llm"
    AGENT = "agent"
    TOOL = "tool"
    PROMPT = "prompt"

    # Data resources
    DOCUMENT = "document"
    VECTOR_DB = "vector_db"
    KNOWLEDGE_BASE = "knowledge_base"

    # Integration resources
    MCP = "mcp"
    API = "api"
    INTEGRATION = "integration"

    # Business resources
    PROJECT = "project"
    ORGANIZATION = "organization"
    DEPARTMENT = "department"

    # Custom resource
    CUSTOM = "custom"


class ActionType(str, Enum):
    """Types of actions that can be performed on resources"""

    # Basic CRUD operations
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    # Special operations
    EXECUTE = "execute"  # For tools, agents, etc.
    MANAGE = "manage"    # Administrative actions
    SHARE = "share"      # Sharing with others
    APPROVE = "approve"  # Approval workflows
    ASSIGN = "assign"    # Assigning to users

    # AI-specific operations
    TRAIN = "train"      # Training models
    DEPLOY = "deploy"    # Deploying models
    PROMPT = "prompt"    # Sending prompts

    # System operations
    CONFIGURE = "configure"
    MONITOR = "monitor"
    AUDIT = "audit"

    # Custom action
    CUSTOM = "custom"


class Permission(BaseModel):
    """
    Permission model defining what actions can be performed on which resources.

    A permission can be:
    1. Resource-level: applies to all instances of a resource type
    2. Instance-level: applies to specific instances of a resource type
    3. Attribute-level: applies to specific attributes of resource instances
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType
    actions: list[ActionType]

    # For instance-level permissions (optional)
    resource_id: str | None = None

    # For attribute-level permissions (optional)
    attributes: list[str] | None = None

    # For conditional permissions (optional)
    condition: dict[str, Any] | None = None

    # Metadata
    description: str | None = None

    class Config:
        use_enum_values = True

    def matches_resource(self, resource_type: ResourceType, resource_id: str | None = None) -> bool:
        """Check if this permission applies to the given resource"""
        if self.resource_type != resource_type:
            return False

        # If this is an instance-level permission, check resource_id
        if self.resource_id is not None:
            return self.resource_id == resource_id

        # This is a resource-level permission, so it applies to all instances
        return True

    def allows_action(self, action: ActionType) -> bool:
        """Check if this permission allows the given action"""
        return action in self.actions

    def check_condition(self, context: dict[str, Any]) -> bool:
        """Check if the condition for this permission is satisfied"""
        if not self.condition:
            return True

        # Simple condition checking (can be expanded for more complex conditions)
        for key, value in self.condition.items():
            if key not in context or context[key] != value:
                return False

        return True


class Role(BaseModel):
    """
    Role model representing a collection of permissions.

    Roles can be:
    1. System roles: predefined roles with special privileges
    2. Custom roles: user-defined roles for specific use cases
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    permissions: list[Permission]

    # Role metadata
    description: str | None = None
    is_system_role: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def has_permission(
        self,
        resource_type: ResourceType,
        action: ActionType,
        resource_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if this role has the given permission"""
        context = context or {}

        for permission in self.permissions:
            if (permission.matches_resource(resource_type, resource_id) and
                permission.allows_action(action) and
                permission.check_condition(context)):
                return True

        return False


class RoleAssignment(BaseModel):
    """
    Role assignment linking a user to a role.

    Role assignments can be:
    1. Global: apply to all resources
    2. Scoped: apply only to specific resources or contexts
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role_id: str

    # Scope (optional)
    scope_type: ResourceType | None = None
    scope_id: str | None = None

    # Constraints (optional)
    constraints: dict[str, Any] | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    created_by: str | None = None

    class Config:
        use_enum_values = True

    def is_active(self) -> bool:
        """Check if this role assignment is active (not expired)"""
        if not self.expires_at:
            return True

        return datetime.utcnow() < self.expires_at

    def applies_to_scope(
        self,
        resource_type: ResourceType | None = None,
        resource_id: str | None = None,
    ) -> bool:
        """Check if this role assignment applies to the given scope"""
        # Global assignment applies to all scopes
        if not self.scope_type and not self.scope_id:
            return True

        # If no resource is specified, but assignment has scope, it doesn't apply
        if not resource_type:
            return False

        # Check if the scope matches
        if self.scope_type != resource_type:
            return False

        # If scope_id is specified, check if it matches
        if self.scope_id and resource_id:
            return self.scope_id == resource_id

        # If scope_id is not specified, it applies to all instances of the resource type
        return True

    def check_constraints(self, context: dict[str, Any]) -> bool:
        """Check if the constraints for this role assignment are satisfied"""
        if not self.constraints:
            return True

        # Simple constraint checking (can be expanded for more complex constraints)
        for key, value in self.constraints.items():
            if key not in context or context[key] != value:
                return False

        return True


class User(BaseModel):
    """
    User model with role assignments.

    This is a simplified model for RBAC purposes.
    In a real application, this would be expanded with more user attributes.
    """

    id: str
    email: str
    name: str | None = None
    department: str | None = None
    is_active: bool = True
    is_system_admin: bool = False

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = None


# System-defined roles with predefined permissions

def create_system_admin_role() -> Role:
    """Create the system administrator role with all permissions"""
    permissions = []

    # Add permissions for all resource types and actions
    for resource_type in ResourceType:
        permissions.append(
            Permission(
                resource_type=resource_type,
                actions=list(ActionType),
                description=f"Full access to all {resource_type} resources",
            )
        )

    return Role(
        id="role_system_admin",
        name="System Administrator",
        permissions=permissions,
        description="Full access to all system resources and actions",
        is_system_role=True,
    )


def create_read_only_role() -> Role:
    """Create a read-only role with read permissions for all resources"""
    permissions = []

    # Add read permission for all resource types
    for resource_type in ResourceType:
        permissions.append(
            Permission(
                resource_type=resource_type,
                actions=[ActionType.READ],
                description=f"Read access to all {resource_type} resources",
            )
        )

    return Role(
        id="role_read_only",
        name="Read Only",
        permissions=permissions,
        description="Read-only access to all system resources",
        is_system_role=True,
    )


def create_ai_developer_role() -> Role:
    """Create an AI developer role with permissions for AI development"""
    permissions = [
        # LLM permissions
        Permission(
            resource_type=ResourceType.LLM,
            actions=[ActionType.READ, ActionType.EXECUTE, ActionType.PROMPT],
            description="Access and use LLMs",
        ),

        # Agent permissions
        Permission(
            resource_type=ResourceType.AGENT,
            actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.EXECUTE],
            description="Create and manage AI agents",
        ),

        # Tool permissions
        Permission(
            resource_type=ResourceType.TOOL,
            actions=[ActionType.READ, ActionType.EXECUTE],
            description="Use AI tools",
        ),

        # Prompt permissions
        Permission(
            resource_type=ResourceType.PROMPT,
            actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE],
            description="Create and manage prompts",
        ),

        # Knowledge base permissions
        Permission(
            resource_type=ResourceType.KNOWLEDGE_BASE,
            actions=[ActionType.READ],
            description="Read from knowledge bases",
        ),

        # Vector DB permissions
        Permission(
            resource_type=ResourceType.VECTOR_DB,
            actions=[ActionType.READ],
            description="Read from vector databases",
        ),
    ]

    return Role(
        id="role_ai_developer",
        name="AI Developer",
        permissions=permissions,
        description="Role for AI developers with permissions to create and manage AI components",
        is_system_role=True,
    )


def create_business_user_role() -> Role:
    """Create a business user role with permissions for using the system"""
    permissions = [
        # LLM permissions
        Permission(
            resource_type=ResourceType.LLM,
            actions=[ActionType.EXECUTE, ActionType.PROMPT],
            description="Use LLMs",
        ),

        # Agent permissions
        Permission(
            resource_type=ResourceType.AGENT,
            actions=[ActionType.READ, ActionType.EXECUTE],
            description="Use AI agents",
        ),

        # Tool permissions
        Permission(
            resource_type=ResourceType.TOOL,
            actions=[ActionType.READ, ActionType.EXECUTE],
            description="Use AI tools",
        ),

        # Document permissions
        Permission(
            resource_type=ResourceType.DOCUMENT,
            actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE],
            description="Create and manage documents",
        ),

        # Project permissions
        Permission(
            resource_type=ResourceType.PROJECT,
            actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE],
            description="Create and manage projects",
        ),
    ]

    return Role(
        id="role_business_user",
        name="Business User",
        permissions=permissions,
        description="Role for business users with permissions to use the system",
        is_system_role=True,
    )


def create_department_admin_role(department: str) -> Role:
    """Create a department administrator role with permissions for a specific department"""
    permissions = [
        # User permissions (limited to department)
        Permission(
            resource_type=ResourceType.USER,
            actions=[ActionType.READ, ActionType.UPDATE],
            condition={"department": department},
            description=f"Manage users in the {department} department",
        ),

        # Project permissions (limited to department)
        Permission(
            resource_type=ResourceType.PROJECT,
            actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.MANAGE],
            condition={"department": department},
            description=f"Manage projects in the {department} department",
        ),

        # Document permissions (limited to department)
        Permission(
            resource_type=ResourceType.DOCUMENT,
            actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.MANAGE],
            condition={"department": department},
            description=f"Manage documents in the {department} department",
        ),

        # Agent permissions (limited to department)
        Permission(
            resource_type=ResourceType.AGENT,
            actions=[ActionType.READ, ActionType.EXECUTE, ActionType.MANAGE],
            condition={"department": department},
            description=f"Manage AI agents in the {department} department",
        ),
    ]

    return Role(
        id=f"role_department_admin_{department.lower()}",
        name=f"{department} Administrator",
        permissions=permissions,
        description=f"Administrator role for the {department} department",
        is_system_role=True,
    )


# System-defined roles
SYSTEM_ROLES = {
    "system_admin": create_system_admin_role(),
    "read_only": create_read_only_role(),
    "ai_developer": create_ai_developer_role(),
    "business_user": create_business_user_role(),
}


# Permission checking functions

def has_permission(
    user: User,
    role_assignments: list[RoleAssignment],
    roles: dict[str, Role],
    resource_type: ResourceType,
    action: ActionType,
    resource_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> bool:
    """
    Check if a user has permission to perform an action on a resource.

    Args:
        user: The user to check permissions for
        role_assignments: List of role assignments for the user
        roles: Dictionary of roles by ID
        resource_type: Type of resource to check
        action: Action to check
        resource_id: Optional ID of the specific resource instance
        context: Optional context for conditional permissions

    Returns:
        True if the user has permission, False otherwise
    """
    # System admins have all permissions
    if user.is_system_admin:
        return True

    # Inactive users have no permissions
    if not user.is_active:
        return False

    context = context or {}

    # Check each role assignment
    for assignment in role_assignments:
        # Skip inactive assignments
        if not assignment.is_active():
            continue

        # Skip assignments that don't apply to this user
        if assignment.user_id != user.id:
            continue

        # Skip assignments that don't apply to this scope
        if not assignment.applies_to_scope(resource_type, resource_id):
            continue

        # Skip assignments that don't satisfy constraints
        if not assignment.check_constraints(context):
            continue

        # Get the role for this assignment
        role = roles.get(assignment.role_id)
        if not role:
            continue

        # Check if the role has the required permission
        if role.has_permission(resource_type, action, resource_id, context):
            return True

    # No matching permission found
    return False

