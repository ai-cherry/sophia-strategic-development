#!/usr/bin/env python3
"""
RBAC System Test Script

This script tests the RBAC system implementation for the Sophia AI platform.
It verifies:
- Role creation and management
- Permission checking
- Role assignment
- User management
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.security.rbac.models import (
    ActionType,
    Permission,
    ResourceType,
)
from backend.security.rbac.service import RBACService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rbac_test")


class RBACTester:
    """Test harness for RBAC system"""

    def __init__(self):
        """Initialize the RBAC tester"""
        # Create a temporary storage path for testing
        self.storage_path = os.path.join(os.getcwd(), "tests", "rbac_test.json")

        # Create the RBAC service
        self.rbac_service = RBACService(
            storage_path=self.storage_path,
            load_system_roles=True,
            auto_save=True,
        )

        logger.info(f"Initialized RBAC tester with storage at {self.storage_path}")

    def cleanup(self):
        """Clean up test data"""
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
            logger.info(f"Removed test storage file: {self.storage_path}")

    def test_system_roles(self):
        """Test system roles"""
        logger.info("Testing system roles...")

        # Get all roles
        roles = self.rbac_service.get_roles()

        # Check if system roles are loaded
        system_roles = [role for role in roles if role.is_system_role]
        logger.info(f"Found {len(system_roles)} system roles")

        # Verify system admin role
        admin_role = self.rbac_service.get_role("role_system_admin")
        assert admin_role is not None, "System admin role not found"
        assert admin_role.is_system_role, "System admin role should be a system role"

        # Verify read-only role
        read_only_role = self.rbac_service.get_role("role_read_only")
        assert read_only_role is not None, "Read-only role not found"
        assert read_only_role.is_system_role, "Read-only role should be a system role"

        logger.info("✅ System roles test passed")

    def test_custom_roles(self):
        """Test custom role creation and management"""
        logger.info("Testing custom roles...")

        # Create a custom role
        custom_role = self.rbac_service.create_role(
            name="Test Role",
            permissions=[
                Permission(
                    resource_type=ResourceType.DOCUMENT,
                    actions=[ActionType.READ, ActionType.CREATE],
                    description="Read and create documents",
                ),
                Permission(
                    resource_type=ResourceType.KNOWLEDGE_BASE,
                    actions=[ActionType.READ],
                    description="Read knowledge bases",
                ),
            ],
            description="Test role for RBAC testing",
        )

        logger.info(f"Created custom role: {custom_role.name} ({custom_role.id})")

        # Verify the role was created
        retrieved_role = self.rbac_service.get_role(custom_role.id)
        assert retrieved_role is not None, "Custom role not found after creation"
        assert retrieved_role.name == "Test Role", "Custom role name mismatch"
        assert len(retrieved_role.permissions) == 2, "Custom role should have 2 permissions"

        # Update the role
        updated_role = self.rbac_service.update_role(
            role_id=custom_role.id,
            name="Updated Test Role",
            description="Updated description",
        )

        assert updated_role is not None, "Role update failed"
        assert updated_role.name == "Updated Test Role", "Role name not updated"
        assert updated_role.description == "Updated description", "Role description not updated"

        logger.info(f"Updated custom role: {updated_role.name}")

        # Delete the role
        deleted = self.rbac_service.delete_role(custom_role.id)
        assert deleted, "Role deletion failed"

        # Verify the role was deleted
        deleted_role = self.rbac_service.get_role(custom_role.id)
        assert deleted_role is None, "Role still exists after deletion"

        logger.info("✅ Custom roles test passed")

    def test_users(self):
        """Test user management"""
        logger.info("Testing user management...")

        # Create test users
        admin_user = self.rbac_service.create_user(
            user_id="admin123",
            email="admin@example.com",
            name="Admin User",
            is_system_admin=True,
        )

        regular_user = self.rbac_service.create_user(
            user_id="user123",
            email="user@example.com",
            name="Regular User",
            department="Engineering",
        )

        logger.info(f"Created users: {admin_user.name}, {regular_user.name}")

        # Verify users were created
        retrieved_admin = self.rbac_service.get_user(admin_user.id)
        assert retrieved_admin is not None, "Admin user not found after creation"
        assert retrieved_admin.is_system_admin, "Admin user should be a system admin"

        retrieved_user = self.rbac_service.get_user(regular_user.id)
        assert retrieved_user is not None, "Regular user not found after creation"
        assert retrieved_user.department == "Engineering", "User department mismatch"

        # Update a user
        updated_user = self.rbac_service.update_user(
            user_id=regular_user.id,
            department="Product",
            name="Updated User",
        )

        assert updated_user is not None, "User update failed"
        assert updated_user.department == "Product", "User department not updated"
        assert updated_user.name == "Updated User", "User name not updated"

        logger.info(f"Updated user: {updated_user.name} ({updated_user.department})")

        # Get all users
        users = self.rbac_service.get_users()
        assert len(users) >= 2, "Should have at least 2 users"

        logger.info("✅ User management test passed")

    def test_role_assignments(self):
        """Test role assignments"""
        logger.info("Testing role assignments...")

        # Create test users if they don't exist
        admin_user = self.rbac_service.get_user("admin123")
        if not admin_user:
            admin_user = self.rbac_service.create_user(
                user_id="admin123",
                email="admin@example.com",
                name="Admin User",
                is_system_admin=True,
            )

        regular_user = self.rbac_service.get_user("user123")
        if not regular_user:
            regular_user = self.rbac_service.create_user(
                user_id="user123",
                email="user@example.com",
                name="Regular User",
                department="Engineering",
            )

        # Get roles
        read_only_role = self.rbac_service.get_role("role_read_only")
        assert read_only_role is not None, "Read-only role not found"

        # Create a custom role for testing
        custom_role = self.rbac_service.create_role(
            name="Project Manager",
            permissions=[
                Permission(
                    resource_type=ResourceType.PROJECT,
                    actions=[ActionType.READ, ActionType.UPDATE, ActionType.MANAGE],
                    description="Manage projects",
                ),
                Permission(
                    resource_type=ResourceType.DOCUMENT,
                    actions=[ActionType.READ, ActionType.CREATE, ActionType.UPDATE],
                    description="Work with documents",
                ),
            ],
            description="Role for project managers",
        )

        # Assign roles to users
        read_only_assignment = self.rbac_service.assign_role(
            user_id=regular_user.id,
            role_id=read_only_role.id,
            created_by=admin_user.id,
        )

        assert read_only_assignment is not None, "Role assignment failed"
        logger.info(f"Assigned {read_only_role.name} to {regular_user.name}")

        # Assign custom role with scope
        project_role_assignment = self.rbac_service.assign_role(
            user_id=regular_user.id,
            role_id=custom_role.id,
            scope_type=ResourceType.PROJECT,
            scope_id="project123",
            constraints={"department": "Engineering"},
            expires_at=datetime.utcnow() + timedelta(days=30),
            created_by=admin_user.id,
        )

        assert project_role_assignment is not None, "Scoped role assignment failed"
        logger.info(
            f"Assigned {custom_role.name} to {regular_user.name} "
            f"for project123 with 30-day expiration"
        )

        # Get role assignments for user
        user_assignments = self.rbac_service.get_role_assignments(user_id=regular_user.id)
        assert len(user_assignments) >= 2, "User should have at least 2 role assignments"

        # Update a role assignment
        updated_assignment = self.rbac_service.update_role_assignment(
            assignment_id=project_role_assignment.id,
            constraints={"department": "Product"},
        )

        assert updated_assignment is not None, "Role assignment update failed"
        assert updated_assignment.constraints["department"] == "Product", "Constraint not updated"

        logger.info("✅ Role assignments test passed")

    def test_permission_checking(self):
        """Test permission checking"""
        logger.info("Testing permission checking...")

        # Create test users if they don't exist
        admin_user = self.rbac_service.get_user("admin123")
        if not admin_user:
            admin_user = self.rbac_service.create_user(
                user_id="admin123",
                email="admin@example.com",
                name="Admin User",
                is_system_admin=True,
            )

        regular_user = self.rbac_service.get_user("user123")
        if not regular_user:
            regular_user = self.rbac_service.create_user(
                user_id="user123",
                email="user@example.com",
                name="Regular User",
                department="Engineering",
            )

        # Test admin permissions (should have all permissions)
        has_permission = self.rbac_service.check_permission(
            user_id=admin_user.id,
            resource_type=ResourceType.SYSTEM,
            action=ActionType.MANAGE,
        )

        assert has_permission, "Admin should have system manage permission"

        # Test regular user permissions
        has_permission = self.rbac_service.check_permission(
            user_id=regular_user.id,
            resource_type=ResourceType.DOCUMENT,
            action=ActionType.READ,
        )

        assert has_permission, "User should have document read permission"

        # Test permission with scope
        has_permission = self.rbac_service.check_permission(
            user_id=regular_user.id,
            resource_type=ResourceType.PROJECT,
            action=ActionType.MANAGE,
            resource_id="project123",
            context={"department": "Product"},
        )

        assert has_permission, "User should have project manage permission with correct context"

        # Test permission with wrong scope
        has_permission = self.rbac_service.check_permission(
            user_id=regular_user.id,
            resource_type=ResourceType.PROJECT,
            action=ActionType.MANAGE,
            resource_id="project456",
        )

        assert not has_permission, "User should not have permission for different project"

        # Test permission with wrong context
        has_permission = self.rbac_service.check_permission(
            user_id=regular_user.id,
            resource_type=ResourceType.PROJECT,
            action=ActionType.MANAGE,
            resource_id="project123",
            context={"department": "Marketing"},
        )

        assert not has_permission, "User should not have permission with wrong context"

        logger.info("✅ Permission checking test passed")

    def run_all_tests(self):
        """Run all RBAC tests"""
        logger.info("Starting RBAC system tests...")

        try:
            self.test_system_roles()
            self.test_custom_roles()
            self.test_users()
            self.test_role_assignments()
            self.test_permission_checking()

            logger.info("🎉 All RBAC tests passed!")
            return True

        except AssertionError as e:
            logger.error(f"❌ Test failed: {e}")
            return False

        finally:
            # Save the final state
            self.rbac_service.save_to_storage()


async def main():
    """Main entry point"""
    tester = RBACTester()

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)

    finally:
        # Uncomment to clean up test data
        # tester.cleanup()
        pass


if __name__ == "__main__":
    asyncio.run(main())

