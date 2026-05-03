"""数字员工管理 Schema（Console 端）"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    code: str = Field(..., description="员工编码（全局唯一）")
    name: str
    employeeType: str = "custom"
    description: Optional[str] = None
    avatar: Optional[str] = None
    systemPrompt: Optional[str] = None
    welcomeMessage: Optional[str] = None
    suggestedQuestions: Optional[list[str]] = None
    modelConfig: Optional[dict[str, Any]] = None
    featureCode: Optional[str] = None
    sortOrder: int = 0
    status: int = 1
    toolIds: Optional[list[int]] = Field(
        None, description="绑定的工具 ID 列表（可一次性提交）"
    )


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    employeeType: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    systemPrompt: Optional[str] = None
    welcomeMessage: Optional[str] = None
    suggestedQuestions: Optional[list[str]] = None
    modelConfig: Optional[dict[str, Any]] = None
    featureCode: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[int] = None
    toolIds: Optional[list[int]] = None


class EmployeeDetailOut(BaseModel):
    id: int
    code: str
    name: str
    employeeType: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    systemPrompt: Optional[str] = None
    welcomeMessage: Optional[str] = None
    suggestedQuestions: Optional[list] = None
    modelConfig: Optional[dict] = None
    featureCode: Optional[str] = None
    sortOrder: int = 0
    status: int = 1
    toolIds: list[int] = []
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
