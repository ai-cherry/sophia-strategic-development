"""
Project Models - Stub Implementation
Basic data models for project management
"""

from datetime import datetime

from pydantic import BaseModel

class Project(BaseModel):
    """Project model"""

    id: str
    title: str
    description: str | None = None
    status: str = "active"
    priority: str = "medium"
    created_at: datetime
    updated_at: datetime
    owner_id: str

    class Config:
        from_attributes = True

class Task(BaseModel):
    """Task model"""

    id: str
    title: str
    description: str | None = None
    status: str = "todo"
    priority: str = "medium"
    project_id: str
    assignee_id: str | None = None
    due_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TeamMember(BaseModel):
    """Team member model"""

    id: str
    name: str
    email: str
    role: str = "member"
    department: str | None = None
    productivity_score: float = 0.0
    tasks_completed: int = 0
    active_tasks: int = 0

    class Config:
        from_attributes = True

class SprintVelocity(BaseModel):
    """Sprint velocity model"""

    id: str
    sprint_name: str
    project_id: str
    start_date: datetime
    end_date: datetime
    planned_points: int = 0
    completed_points: int = 0
    velocity: float = 0.0

    class Config:
        from_attributes = True
