from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class UserRole(str, Enum):
    """User roles in the system"""
    CEO = "CEO"
    CPO = "CPO"
    VP_STRATEGIC = "VP_Strategic"
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"

class UserStatus(str, Enum):
    """User status in the system"""
    ACTIVE = "active"
    INVITED = "invited"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.INVITED)
    department = Column(String(255), nullable=True)
    
    # Authentication fields
    password_hash = Column(String(255), nullable=True)
    salt = Column(String(255), nullable=True)
    
    # Invitation fields
    invitation_token = Column(String(255), nullable=True, unique=True)
    invitation_expires = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Session management
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(String(50), default="0")
    failed_login_attempts = Column(String(50), default="0")
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    created_users = relationship("User", remote_side=[id], backref="creator")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def can_manage_users(self) -> bool:
        """Check if user has permission to manage other users"""
        return self.role in [UserRole.CEO, UserRole.CPO, UserRole.VP_STRATEGIC, UserRole.ADMIN]

    def can_view_analytics(self) -> bool:
        """Check if user has permission to view analytics"""
        return self.role in [UserRole.CEO, UserRole.CPO, UserRole.VP_STRATEGIC, UserRole.ADMIN, UserRole.MANAGER]

    def can_access_strategic_data(self) -> bool:
        """Check if user has permission to access strategic data"""
        return self.role in [UserRole.CEO, UserRole.CPO, UserRole.VP_STRATEGIC, UserRole.ADMIN]

    def can_manage_mcp_servers(self) -> bool:
        """Check if user has permission to manage MCP servers"""
        return self.role in [UserRole.CEO, UserRole.ADMIN]

    def get_permissions(self) -> list:
        """Get list of permissions for the user"""
        permissions = ["dashboard_access", "chat_access"]
        
        if self.can_view_analytics():
            permissions.extend(["analytics_access", "performance_metrics"])
        
        if self.can_access_strategic_data():
            permissions.extend(["strategic_overview", "okr_access", "cross_platform_intelligence"])
        
        if self.can_manage_users():
            permissions.extend(["user_management", "activity_logs", "user_statistics"])
        
        if self.can_manage_mcp_servers():
            permissions.extend(["mcp_management", "system_administration"])
        
        return permissions

    def is_active(self) -> bool:
        """Check if user is active and can login"""
        return self.status == UserStatus.ACTIVE

    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "department": self.department,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "permissions": self.get_permissions()
        }

class UserActivity(Base):
    """User activity logging model"""
    __tablename__ = "user_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user_name = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False, index=True)
    resource = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="success")
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action={self.action})>"

    def to_dict(self) -> dict:
        """Convert activity to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "user_name": self.user_name,
            "action": self.action,
            "resource": self.resource,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class UserSession(Base):
    """User session management model"""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

    def is_valid(self) -> bool:
        """Check if session is valid and not expired"""
        return self.is_active and datetime.utcnow() < self.expires_at

    def to_dict(self) -> dict:
        """Convert session to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "session_token": self.session_token,
            "ip_address": self.ip_address,
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

class UserPreferences(Base):
    """User preferences and settings model"""
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Dashboard preferences
    default_tab = Column(String(50), nullable=True, default="overview")
    theme = Column(String(20), nullable=True, default="light")
    timezone = Column(String(50), nullable=True, default="UTC")
    language = Column(String(10), nullable=True, default="en")
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    browser_notifications = Column(Boolean, default=True, nullable=False)
    slack_notifications = Column(Boolean, default=False, nullable=False)
    
    # Analytics preferences
    refresh_interval = Column(String(20), nullable=True, default="30s")
    chart_type_preference = Column(String(20), nullable=True, default="line")
    
    # Strategic PM preferences
    strategic_view_preference = Column(String(50), nullable=True, default="overview")
    
    # Custom settings
    custom_settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserPreferences(id={self.id}, user_id={self.user_id})>"

    def to_dict(self) -> dict:
        """Convert preferences to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "default_tab": self.default_tab,
            "theme": self.theme,
            "timezone": self.timezone,
            "language": self.language,
            "email_notifications": self.email_notifications,
            "browser_notifications": self.browser_notifications,
            "slack_notifications": self.slack_notifications,
            "refresh_interval": self.refresh_interval,
            "chart_type_preference": self.chart_type_preference,
            "strategic_view_preference": self.strategic_view_preference,
            "custom_settings": self.custom_settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Database initialization and migration helpers
def create_user_tables(engine):
    """Create all user-related tables"""
    Base.metadata.create_all(bind=engine)

def get_user_table_names():
    """Get list of all user-related table names"""
    return [table.name for table in Base.metadata.tables.values()]

# Default data creation
def create_default_users(db_session, admin_email: str = "lynn@payready.com"):
    """Create default users for the system"""
    try:
        # Check if admin user already exists
        existing_admin = db_session.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            return existing_admin

        # Create CEO/Admin user
        admin_user = User(
            name="Lynn Patrick Musil",
            email=admin_email,
            role=UserRole.CEO,
            status=UserStatus.ACTIVE,
            department="Executive"
        )

        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)

        return admin_user

    except Exception as e:
        db_session.rollback()
        raise e 