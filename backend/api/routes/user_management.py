from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel, EmailStr

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User, UserRole, UserStatus, UserActivity
from backend.services.email_service import EmailService
from backend.utils.logging import get_logger

logger = get_logger(__name__)

# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.USER
    department: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    status: UserStatus
    department: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserActivityResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    action: str
    resource: str
    ip_address: Optional[str]
    timestamp: datetime
    status: str
    details: Optional[dict] = None

    class Config:
        from_attributes = True

class InviteUserRequest(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.ADMIN  # Default to Admin as requested
    department: Optional[str] = None
    send_email: bool = True

# Initialize router
router = APIRouter(prefix="/api/users", tags=["user_management"])
security = HTTPBearer()

# User Management Routes

@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    role_filter: Optional[UserRole] = None,
    status_filter: Optional[UserStatus] = None,
    search: Optional[str] = None
):
    """Get all users with filtering and pagination"""
    try:
        # Verify user has permission to view users
        if not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view users"
            )

        query = db.query(User)
        
        # Apply filters
        if role_filter:
            query = query.filter(User.role == role_filter)
        if status_filter:
            query = query.filter(User.status == status_filter)
        if search:
            query = query.filter(
                (User.name.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )

        users = query.offset(skip).limit(limit).all()
        
        # Log activity
        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="VIEW_USERS",
            resource="user_list",
            details={"filters": {"role": role_filter, "status": status_filter, "search": search}}
        )

        return users

    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific user by ID"""
    try:
        # Check if user can view this user (self or has permission)
        if current_user.id != user_id and not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view this user"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="VIEW_USER",
            resource=f"user:{user_id}"
        )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.post("/invite", response_model=UserResponse)
async def invite_user(
    user_data: InviteUserRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invite a new user to the system"""
    try:
        # Verify user has permission to invite users
        if not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to invite users"
            )

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Generate invitation token
        invitation_token = secrets.token_urlsafe(32)
        invitation_expires = datetime.utcnow() + timedelta(days=7)

        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            status=UserStatus.INVITED,
            department=user_data.department,
            invitation_token=invitation_token,
            invitation_expires=invitation_expires,
            created_by=current_user.id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log activity
        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="INVITE_USER",
            resource=f"user:{new_user.id}",
            details={"invited_email": user_data.email, "role": user_data.role.value}
        )

        # Send invitation email in background
        if user_data.send_email:
            background_tasks.add_task(
                send_invitation_email,
                user_email=user_data.email,
                user_name=user_data.name,
                invitation_token=invitation_token,
                inviter_name=current_user.name
            )

        logger.info(f"User invited successfully: {user_data.email} by {current_user.email}")
        return new_user

    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inviting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite user"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information"""
    try:
        # Check permissions
        if current_user.id != user_id and not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update this user"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        # Log activity
        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="UPDATE_USER",
            resource=f"user:{user_id}",
            details={"updated_fields": list(update_data.keys())}
        )

        logger.info(f"User updated successfully: {user_id} by {current_user.email}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete/deactivate a user"""
    try:
        # Verify user has permission to delete users
        if not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete users"
            )

        # Prevent self-deletion
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Soft delete - set status to inactive
        user.status = UserStatus.INACTIVE
        user.updated_at = datetime.utcnow()
        db.commit()

        # Log activity
        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="DELETE_USER",
            resource=f"user:{user_id}",
            details={"deleted_email": user.email}
        )

        logger.info(f"User deleted successfully: {user_id} by {current_user.email}")
        return {"message": "User deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

# User Activity Routes

@router.get("/activity/log", response_model=List[UserActivityResponse])
async def get_user_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None
):
    """Get user activity logs"""
    try:
        # Verify user has permission to view activity logs
        if not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view activity logs"
            )

        query = db.query(UserActivity).join(User)
        
        # Apply filters
        if user_id:
            query = query.filter(UserActivity.user_id == user_id)
        if action:
            query = query.filter(UserActivity.action.ilike(f"%{action}%"))

        activities = query.order_by(UserActivity.timestamp.desc()).offset(skip).limit(limit).all()

        # Log activity
        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="VIEW_ACTIVITY_LOG",
            resource="activity_log",
            details={"filters": {"user_id": user_id, "action": action}}
        )

        return activities

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activity logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity logs"
        )

# Helper Functions

async def log_user_activity(
    db: Session,
    user_id: str,
    action: str,
    resource: str,
    ip_address: Optional[str] = None,
    status: str = "success",
    details: Optional[dict] = None
):
    """Log user activity"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        activity = UserActivity(
            user_id=user_id,
            user_name=user.name,
            action=action,
            resource=resource,
            ip_address=ip_address,
            status=status,
            details=details,
            timestamp=datetime.utcnow()
        )

        db.add(activity)
        db.commit()

    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        db.rollback()

async def send_invitation_email(
    user_email: str,
    user_name: str,
    invitation_token: str,
    inviter_name: str
):
    """Send invitation email to new user"""
    try:
        email_service = EmailService()
        
        subject = "Welcome to Sophia AI - Complete Your Registration"
        
        # Generate invitation link
        invitation_link = f"https://sophia.payready.com/auth/accept-invitation?token={invitation_token}"
        
        body = f"""
        Hello {user_name},

        You've been invited to join the Sophia AI platform by {inviter_name}.

        Sophia AI is Pay Ready's executive AI orchestrator that provides strategic project management 
        and business intelligence across our entire organization.

        To complete your registration and set up your account, please click the link below:
        
        {invitation_link}

        This invitation will expire in 7 days.

        If you have any questions, please contact your administrator.

        Best regards,
        The Sophia AI Team
        """

        await email_service.send_email(
            to_email=user_email,
            subject=subject,
            body=body
        )

        logger.info(f"Invitation email sent successfully to {user_email}")

    except Exception as e:
        logger.error(f"Error sending invitation email to {user_email}: {e}")

# User Statistics Routes

@router.get("/stats/summary")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user statistics summary"""
    try:
        if not current_user.can_manage_users():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view user statistics"
            )

        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
        invited_users = db.query(User).filter(User.status == UserStatus.INVITED).count()
        inactive_users = db.query(User).filter(User.status == UserStatus.INACTIVE).count()

        # Role distribution
        role_counts = {}
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            role_counts[role.value] = count

        # Recent activity count (last 24 hours)
        recent_activity_count = db.query(UserActivity).filter(
            UserActivity.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()

        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "invited_users": invited_users,
            "inactive_users": inactive_users,
            "role_distribution": role_counts,
            "recent_activity_count": recent_activity_count
        }

        # Log activity
        await log_user_activity(
            db=db,
            user_id=current_user.id,
            action="VIEW_USER_STATS",
            resource="user_statistics"
        )

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        ) 