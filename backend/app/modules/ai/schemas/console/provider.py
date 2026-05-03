"""LLM Provider Schema（Console 端）"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ProviderCreate(BaseModel):
    code: str = Field(..., description="Provider 编码（如 default/qwen/deepseek）")
    name: str
    providerType: str = "openai_compat"
    baseUrl: Optional[str] = None
    apiKey: Optional[str] = Field(None, description="新建/修改时填写明文，落库时加密")
    modelName: str = Field(..., description="默认模型名（如 qwen-plus / deepseek-chat）")
    extraParams: Optional[dict[str, Any]] = None
    timeoutSeconds: int = 60
    isDefault: bool = False
    status: int = 1


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    providerType: Optional[str] = None
    baseUrl: Optional[str] = None
    apiKey: Optional[str] = Field(None, description="不传则不更新；传则覆盖（明文）")
    modelName: Optional[str] = None
    extraParams: Optional[dict[str, Any]] = None
    timeoutSeconds: Optional[int] = None
    isDefault: Optional[bool] = None
    status: Optional[int] = None


class ProviderOut(BaseModel):
    id: int
    code: str
    name: str
    providerType: str
    baseUrl: Optional[str] = None
    apiKeyMasked: Optional[str] = None  # 仅展示后4位
    modelName: str
    extraParams: Optional[dict] = None
    timeoutSeconds: int = 60
    isDefault: bool = False
    status: int = 1
