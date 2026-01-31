from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "employee"

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

# Task Schemas
class TaskCreate(BaseModel):
    title: str
    content: str
    deadline: Optional[datetime] = None
    assignee_ids: list[int]  # List of user IDs for batch creation

class TaskUpdate(BaseModel):
    status: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    content: str
    status: str
    created_at: datetime
    deadline: Optional[datetime]
    completed_at: Optional[datetime]
    assignee_id: int
    creator_id: int

# Report Schemas
class ReportCreate(BaseModel):
    week_num: int
    content_done: str
    content_plan: str
    content_issues: str

class ReportResponse(BaseModel):
    id: int
    week_num: int
    content_done: str
    content_plan: str
    content_issues: str
    submitted_at: datetime
    is_late: bool
    user: Optional[UserResponse] = None # Optional because it might not be fetched for simple list? Or always fetch.

