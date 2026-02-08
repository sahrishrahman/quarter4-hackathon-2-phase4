from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from .base import TimestampMixin

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    completed: bool = Field(default=False, index=True)

class Task(TimestampMixin, TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="user.id")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
