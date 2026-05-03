"""
EngineContext: 编排器运行时上下文

聚合 LLM Provider、当前数字员工、session、tenant Session、用户信息等，
便于 Orchestrator / Tool / PermissionGuard 共享。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenData
from app.modules.ai.llm.base import LLMProvider
from app.modules.ai.models.platform.ai_employee import AiEmployee
from app.modules.ai.models.tenant.biz_ai_session import BizAiSession


@dataclass
class EngineContext:
    user: TokenData
    tenant_code: str
    tenant_db: AsyncSession
    platform_db: AsyncSession
    employee: AiEmployee
    session: BizAiSession
    provider: LLMProvider
    enabled_tool_codes: list[str] = field(default_factory=list)
    model_config: dict = field(default_factory=dict)

    @property
    def temperature(self) -> Optional[float]:
        v = self.model_config.get("temperature")
        return float(v) if v is not None else None

    @property
    def max_tokens(self) -> Optional[int]:
        v = self.model_config.get("max_tokens")
        return int(v) if v is not None else None

    @property
    def max_tool_loops(self) -> int:
        return int(self.model_config.get("max_tool_loops") or 6)

    @property
    def context_window(self) -> int:
        return int(self.model_config.get("context_window") or 20)
