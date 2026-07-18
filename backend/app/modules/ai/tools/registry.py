"""
工具注册表

@register_tool 装饰器把代码内工具注册进全局表；
ToolRegistry.sync_to_db() 在应用启动时把注册表内容 upsert 到 ai_tool 表。
"""

from __future__ import annotations

import json
from typing import Optional, Type

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.tools.base import EmptyParams, ToolHandler, ToolSpec


class ToolRegistry:
    """全局工具注册表（进程级单例）"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.code in self._tools:
            logger.warning(f"[ToolRegistry] 工具 {spec.code} 重复注册，已覆盖")
        self._tools[spec.code] = spec

    def get(self, code: str) -> Optional[ToolSpec]:
        return self._tools.get(code)

    def all(self) -> list[ToolSpec]:
        return list(self._tools.values())

    async def sync_to_db(self, platform_db: AsyncSession) -> dict:
        """把代码内注册的工具同步到 ai_tool 表

        - 新工具 → INSERT
        - 已存在 → UPDATE 元数据（保留 status，避免覆盖运营手动启停）
        - 已删除（DB 有但代码没有） → 标记 is_builtin=0（不下线，留人工决断）
        """
        existing_rows = (
            await platform_db.execute(select(AiTool).where(AiTool.is_deleted == 0))
        ).scalars().all()
        existing_by_code: dict[str, AiTool] = {r.code: r for r in existing_rows}

        inserted, updated = 0, 0
        for spec in self._tools.values():
            schema_dict = spec.json_schema()
            row = existing_by_code.get(spec.code)
            if row is None:
                row = AiTool(
                    code=spec.code,
                    name=spec.name,
                    category=spec.category,
                    description=spec.description,
                    params_schema=schema_dict,
                    required_permission=spec.required_permission,
                    risk_level=spec.risk_level,
                    confirm_required=1 if spec.confirm_required else 0,
                    is_builtin=1,
                    status=1,
                )
                platform_db.add(row)
                inserted += 1
            else:
                row.name = spec.name
                row.category = spec.category
                row.description = spec.description
                row.params_schema = schema_dict
                row.required_permission = spec.required_permission
                row.risk_level = spec.risk_level
                row.confirm_required = 1 if spec.confirm_required else 0
                row.is_builtin = 1
                updated += 1

        # 代码侧已删除：标记为非内置（保留 status，运营决定是否下线）
        code_set = set(self._tools.keys())
        orphan = 0
        for code, row in existing_by_code.items():
            if code not in code_set and row.is_builtin == 1:
                row.is_builtin = 0
                orphan += 1

        await platform_db.commit()
        logger.info(
            f"[ToolRegistry] 同步完成: 新增 {inserted}, 更新 {updated}, 孤立 {orphan}"
        )
        return {"inserted": inserted, "updated": updated, "orphan": orphan}


_global_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    return _global_registry


def register_tool(
    *,
    code: str,
    name: str,
    category: str,
    description: str,
    params_schema: Optional[Type[BaseModel]] = None,
    permission: Optional[str] = None,
    risk_level: str = "low",
    confirm_required: bool = False,
):
    """工具注册装饰器

    用法：
        class WaybillSearchParams(BaseModel):
            keyword: str | None = None

        @register_tool(
            code="waybill.search",
            name="查询计划",
            category="waybill",
            description="按关键词分页查询当前租户的计划",
            params_schema=WaybillSearchParams,
            permission="biz:waybill:list",
        )
        async def search_waybill(ctx: ToolContext, **kwargs) -> ToolResult:
            ...
    """

    def decorator(handler: ToolHandler) -> ToolHandler:
        spec = ToolSpec(
            code=code,
            name=name,
            category=category,
            description=description,
            params_schema=params_schema or EmptyParams,
            handler=handler,
            required_permission=permission,
            risk_level=risk_level,
            confirm_required=confirm_required,
        )
        _global_registry.register(spec)
        return handler

    return decorator


# ---------- 工具名 wire 协议适配 ----------
# OpenAI / Kimi 校验：function.name 必须 ^[a-zA-Z][a-zA-Z0-9_-]{0,63}$
# 我们工具内部 code 用点号分段（如 waybill.search），需要在送进 LLM 前
# 把点号转成双下划线，回包后再反向还原。我们的 code 内部不包含双下划线，
# 因此这是一个可逆映射。
_DOT_PLACEHOLDER = "__"


def encode_tool_name(code: str) -> str:
    """业务 code → LLM wire name（waybill.search → waybill__search）"""
    if not code:
        return code
    return code.replace(".", _DOT_PLACEHOLDER)


def decode_tool_name(wire_name: str) -> str:
    """LLM wire name → 业务 code（waybill__search → waybill.search）

    幂等：传入未编码的 code 也能还原（因为 code 不含 __）。
    """
    if not wire_name:
        return wire_name
    return wire_name.replace(_DOT_PLACEHOLDER, ".")


def serialize_for_log(value) -> str:
    """工具结果摘要序列化（截断 + 安全）"""
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        text = str(value)
    if len(text) > 2000:
        return text[:2000] + "...(truncated)"
    return text
