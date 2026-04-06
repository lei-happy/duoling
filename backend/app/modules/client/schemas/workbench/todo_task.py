"""
工作台待办 Schemas（响应使用 snake_case，与现有 todo-card.vue 字段一致）
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TodoTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: int = Field(default=1, ge=0, le=2)
    status: int = Field(default=0, ge=0, le=3)
    due_time: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TodoTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=2)
    status: Optional[int] = Field(None, ge=0, le=3)
    due_time: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TodoTaskStatusBody(BaseModel):
    status: int = Field(..., ge=0, le=3)


class TodoTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_code: str
    title: str
    description: Optional[str] = None
    creator_id: int
    assignee_id: Optional[int] = None
    creator_name: Optional[str] = None
    assignee_name: Optional[str] = None
    due_time: Optional[datetime] = None
    priority: int
    status: int
    completed_time: Optional[datetime] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class TodoTaskStatsOut(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int


class TodoTaskListResult(BaseModel):
    items: List[TodoTaskOut]
    total: int
    page: int
    page_size: int
    pages: int


class AssignableUserOut(BaseModel):
    id: int
    display_name: str


class ConsoleTodoTaskOut(TodoTaskOut):
    tenant_name: Optional[str] = None
