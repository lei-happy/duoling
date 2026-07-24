"""开放平台 Pydantic Schemas（控制面）"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


# ---------------- 接入应用 ----------------

class AppCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="应用名称")
    description: str = Field("", max_length=255, description="用途备注")


class AppUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, description="enabled / disabled")


class AppOut(BaseModel):
    id: int
    name: str
    description: str
    status: str
    credential_count: int = 0
    created_at: Optional[datetime] = None


# ---------------- 接入凭证 ----------------

class CredentialCreate(BaseModel):
    cred_type: str = Field("api", description="api / mcp")
    scope: List[str] = Field(default_factory=list, description="可用能力码白名单")
    ip_whitelist: str = Field("", max_length=512, description="来源 IP 白名单，逗号分隔")
    expires_at: Optional[datetime] = Field(None, description="到期时间，空=长期有效")


class CredentialScopeUpdate(BaseModel):
    scope: List[str] = Field(default_factory=list)
    ip_whitelist: Optional[str] = None


class CredentialOut(BaseModel):
    id: int
    app_id: int
    cred_type: str
    access_key: str
    scope: List[str] = Field(default_factory=list)
    ip_whitelist: str = ""
    status: str
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class CredentialSecretOut(CredentialOut):
    """仅在创建/重置时返回一次明文 secret。"""

    secret: str = Field(..., description="接入密钥明文（仅展示一次，请妥善保管）")


# ---------------- MCP 配置 ----------------

class McpConfigCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=64, description="连接名称（可自定义）")
    enabled_capabilities: List[str] = Field(default_factory=list, description="开放给 AI 的能力码")


class McpConfigUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=64)
    enabled_capabilities: Optional[List[str]] = None
    status: Optional[str] = None


class McpConfigOut(BaseModel):
    id: int
    display_name: str
    server_slug: str
    enabled_capabilities: List[str] = Field(default_factory=list)
    status: str
    url: str = ""
    created_at: Optional[datetime] = None


class McpConfigCreatedOut(McpConfigOut):
    """创建时附带一次性 token 与可复制配置 JSON。"""

    token: str = Field(..., description="MCP Token 明文（仅展示一次）")
    config_json: dict = Field(default_factory=dict, description="可粘贴进 AI 工具的配置")


# ---------------- 能力目录 ----------------

class CapabilityOut(BaseModel):
    code: str
    name: str
    category: str
    description: str
    channels: List[str] = Field(default_factory=list)
    read_only: bool = True
    risk_level: str = "low"
    stability: str = "stable"
    version: str = "v1"
    input_schema: Optional[dict] = None
    output_fields: Optional[List[str]] = None
