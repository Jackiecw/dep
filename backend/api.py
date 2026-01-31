from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List

from models import User, Task, Report
from schemas import UserCreate, UserResponse, Token, TaskCreate, TaskResponse, TaskUpdate, ReportCreate, ReportResponse
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uuid

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await User.get_or_none(username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_obj = await User.create(
        username=user.username,
        password_hash=get_password_hash(user.password),
        display_name=user.display_name,
        role=user.role
    )
    return user_obj

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def read_users(current_user: User = Depends(get_current_user)):
    # Simple list for assignment
    return await User.all()

# Tasks
@router.post("/tasks", response_model=str)
async def create_tasks(task: TaskCreate, current_user: User = Depends(get_current_user)):
    # Batch creation using bulk_create for performance
    batch_id = uuid.uuid4() if len(task.assignee_ids) > 1 else None
    
    tasks_to_create = []
    for assignee_id in task.assignee_ids:
        Assignee = await User.get_or_none(id=assignee_id)
        if not Assignee:
            continue
        
        tasks_to_create.append(Task(
            batch_id=batch_id,
            title=task.title,
            content=task.content,
            assignee=Assignee,
            creator=current_user
        ))
    
    if tasks_to_create:
        await Task.bulk_create(tasks_to_create)
        return "Tasks created successfully"
    return "No valid assignees found"

@router.get("/tasks", response_model=List[TaskResponse])
async def read_tasks(current_user: User = Depends(get_current_user)):
    return await Task.filter(assignee=current_user).order_by("-created_at")

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user)):
    task = await Task.get_or_none(id=task_id, assignee=current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.status == "done" and task.status != "done":
        task.status = "done"
        task.completed_at = datetime.utcnow()
    
    await task.save()
    return task

# Reports
@router.post("/reports", response_model=ReportResponse)
async def create_report(report: ReportCreate, current_user: User = Depends(get_current_user)):
    # Check if late
    # Logic: Deadline is Friday 17:00? 
    # For MVP, let's just mark if submitted after Friday of that week?
    # Or simpler: assume server time. 
    # For now, simplistic logic: just save.
    
    # Calculate is_late based on system settings or fixed rule (e.g. Friday 17:00)
    # We will implement dynamic check in Phase 2.
    is_late = False 
    
    report_obj = await Report.create(
        user=current_user,
        week_num=report.week_num,
        content_done=report.content_done,
        content_plan=report.content_plan,
        content_issues=report.content_issues,
        is_late=is_late
    )
    return report_obj

@router.get("/reports", response_model=List[ReportResponse])
async def read_reports(current_user: User = Depends(get_current_user)):
    # User sees own reports only, unless admin?
    # Plan says "Admin Power" in Phase 2.
    if current_user.role == "admin":
        return await Report.all().prefetch_related("user").order_by("-week_num")
    return await Report.filter(user=current_user).order_by("-week_num")

# Dashboard Stats
@router.get("/stats/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Pie Chart: Task Status
    total = await Task.all().count()
    done = await Task.filter(status="done").count()
    pending = await Task.filter(status="pending").count()
    # Late logic is complex without due dates, for now assume all pending are just pending
    
    # Bar Chart: Last 7 days completion
    today = datetime.now().date()
    week_stats = []
    days = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        count = await Task.filter(
            status="done", 
            completed_at__gte=day_start, 
            completed_at__lte=day_end
        ).count()
        
        days.append(day.strftime("%a"))
        week_stats.append(count)
        
    return {
        "pie": [
            {"value": done, "name": "Done"},
            {"value": pending, "name": "Pending"}
        ],
        "bar": {
            "days": days,
            "counts": week_stats
        }
    }
