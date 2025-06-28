"""
User Domain Entity

This module defines the User entity which represents a system user
in the Sophia AI system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Set


class UserRole(Enum):
    """Enumeration of user roles."""

    SALES_REP = "sales_rep"
    SALES_MANAGER = "sales_manager"
    EXECUTIVE = "executive"
    ADMIN = "admin"
    ANALYST = "analyst"


class PermissionLevel(Enum):
    """Enumeration of permission levels."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class User:
    """
    Domain entity representing a system user.

    This entity encapsulates the core business logic and rules
    related to users and their permissions.
    """

    id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool = True
    team_id: Optional[str] = None
    manager_id: Optional[str] = None
    permissions: Optional[Set[str]] = None
    owned_deal_ids: Optional[List[str]] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.permissions is None:
            self.permissions = self._get_default_permissions()
        if self.owned_deal_ids is None:
            self.owned_deal_ids = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Get formatted display name with role."""
        return f"{self.full_name} ({self.role.value.replace('_', ' ').title()})"

    def _get_default_permissions(self) -> Set[str]:
        """
        Get default permissions based on role.

        Returns:
            Set[str]: Default permissions for the user's role
        """
        base_permissions = {"read_own_data", "update_own_data"}

        role_permissions = {
            UserRole.SALES_REP: {
                "create_deals",
                "update_own_deals",
                "view_own_calls",
                "create_contacts",
            },
            UserRole.SALES_MANAGER: {
                "create_deals",
                "update_team_deals",
                "view_team_calls",
                "view_team_analytics",
                "create_contacts",
                "manage_team",
            },
            UserRole.EXECUTIVE: {
                "view_all_deals",
                "view_all_analytics",
                "view_executive_dashboard",
                "export_data",
            },
            UserRole.ADMIN: {
                "manage_users",
                "manage_permissions",
                "manage_integrations",
                "view_all_data",
                "modify_all_data",
            },
            UserRole.ANALYST: {
                "view_all_deals",
                "view_all_analytics",
                "export_data",
                "create_reports",
            },
        }

        return base_permissions.union(role_permissions.get(self.role, set()))

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: The permission to check

        Returns:
            bool: True if user has the permission
        """
        return self.permissions is not None and permission in self.permissions

    def can_view_deal(
        self, deal_owner_id: str, deal_team_id: Optional[str] = None
    ) -> bool:
        """
        Business rule: Check if user can view a specific deal.

        Args:
            deal_owner_id: The ID of the deal owner
            deal_team_id: The team ID of the deal (if applicable)

        Returns:
            bool: True if user can view the deal
        """
        # Admins and executives can view all deals
        if self.role in [UserRole.ADMIN, UserRole.EXECUTIVE]:
            return True

        # Analysts can view all deals
        if self.role == UserRole.ANALYST:
            return True

        # Sales reps can view their own deals
        if self.id == deal_owner_id:
            return True

        # Sales managers can view their team's deals
        if self.role == UserRole.SALES_MANAGER and deal_team_id == self.team_id:
            return True

        return False

    def can_modify_deal(self, deal_owner_id: str) -> bool:
        """
        Business rule: Check if user can modify a specific deal.

        Args:
            deal_owner_id: The ID of the deal owner

        Returns:
            bool: True if user can modify the deal
        """
        # Admins can modify all deals
        if self.role == UserRole.ADMIN:
            return True

        # Users can modify their own deals
        if self.id == deal_owner_id:
            return True

        # Sales managers can modify their direct reports' deals
        if self.role == UserRole.SALES_MANAGER:
            # This would need to check if deal_owner is a direct report
            # For now, simplified to team check
            return self.has_permission("update_team_deals")

        return False

    def is_manager(self) -> bool:
        """
        Check if user is in a management role.

        Returns:
            bool: True if user is a manager or executive
        """
        return self.role in [UserRole.SALES_MANAGER, UserRole.EXECUTIVE]

    def get_activity_score(self) -> float:
        """
        Calculate user activity score based on login frequency and deal ownership.

        Returns:
            float: Activity score between 0 and 1
        """
        score = 0.0

        # Login recency component (50%)
        if self.last_login:
            days_since_login = (datetime.now() - self.last_login).days
            if days_since_login == 0:
                score += 0.5
            elif days_since_login <= 7:
                score += 0.3
            elif days_since_login <= 30:
                score += 0.1

        # Deal ownership component (50%)
        if self.owned_deal_ids:
            # Normalize to a reasonable number (e.g., 10 deals = full score)
            deal_score = min(len(self.owned_deal_ids) / 10, 1.0) * 0.5
            score += deal_score

        return score

    def record_login(self) -> None:
        """Record a user login."""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()

    def add_permission(self, permission: str) -> None:
        """
        Add a permission to the user.

        Args:
            permission: The permission to add
        """
        if self.permissions is not None:
            self.permissions.add(permission)
            self.updated_at = datetime.now()

    def remove_permission(self, permission: str) -> None:
        """
        Remove a permission from the user.

        Args:
            permission: The permission to remove
        """
        if self.permissions is not None:
            self.permissions.discard(permission)
            self.updated_at = datetime.now()
