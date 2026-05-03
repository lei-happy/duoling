"""客户端对话相关 Schema"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    employeeCode: str = Field(..., description="数字员工编码")
    sessionId: Optional[int] = Field(None, description="已有会话 ID；为空时新建会话")
    content: str = Field(..., min_length=1, description="用户消息内容")
    attachments: Optional[list[dict[str, Any]]] = Field(
        None,
        description="附件列表，元素至少含 fileId / name / size / mime",
    )


class ConfirmRequest(BaseModel):
    sessionId: int = Field(..., description="会话ID")
    confirmToken: str = Field(..., description="待确认 token（confirm.required 事件中下发）")
    approved: bool = Field(True, description="是否批准执行")


class SessionOut(BaseModel):
    id: int
    sessionNo: str
    employeeCode: str
    employeeName: Optional[str] = None
    title: Optional[str] = None
    status: int
    messageCount: int = 0
    lastMessageAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "SessionOut":
        return cls(
            id=m.id,
            sessionNo=m.session_no,
            employeeCode=m.employee_code,
            employeeName=m.employee_name,
            title=m.title,
            status=m.status,
            messageCount=m.message_count or 0,
            lastMessageAt=(
                m.last_message_at.strftime("%Y-%m-%d %H:%M:%S")
                if m.last_message_at
                else None
            ),
            createdAt=(
                m.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if m.created_at
                else None
            ),
        )


class MessageOut(BaseModel):
    id: int
    role: str
    content: Optional[str] = None
    toolCalls: Optional[list] = None
    toolCallId: Optional[str] = None
    toolName: Optional[str] = None
    attachments: Optional[list] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "MessageOut":
        return cls(
            id=m.id,
            role=m.role,
            content=m.content,
            toolCalls=m.tool_calls,
            toolCallId=m.tool_call_id,
            toolName=m.tool_name,
            attachments=m.attachments,
            createdAt=(
                m.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if m.created_at
                else None
            ),
        )


class EmployeeOut(BaseModel):
    code: str
    name: str
    employeeType: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    welcomeMessage: Optional[str] = None
    suggestedQuestions: Optional[list] = None

    @classmethod
    def from_model(cls, m) -> "EmployeeOut":
        return cls(
            code=m.code,
            name=m.name,
            employeeType=m.employee_type,
            description=m.description,
            avatar=m.avatar,
            welcomeMessage=m.welcome_message,
            suggestedQuestions=m.suggested_questions,
        )


class EmployeeToolOut(BaseModel):
    code: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    riskLevel: str = "low"
    confirmRequired: bool = False
