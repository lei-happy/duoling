"""能力注册表 —— 对外契约的单一事实源

用 @register_capability 声明一项对外能力（REST + MCP 双通道共享）。
能力 handler 是「适配器」：复用租户库领域数据，做入参校验、字段裁剪、脱敏、错误翻译。

对外契约与 AI 内部工具（@register_tool）解耦：内部重构不破坏对外契约。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from app.common.exceptions import BizException
from app.modules.open_platform.capabilities.context import OpenContext


@dataclass
class CapabilitySpec:
    code: str
    name: str
    handler: Callable
    category: str = ""
    description: str = ""
    channels: List[str] = field(default_factory=lambda: ["api", "mcp"])
    read_only: bool = True
    input_schema: Optional[dict] = None
    output_fields: Optional[List[str]] = None
    sensitive_fields: Optional[List[str]] = None
    risk_level: str = "low"
    stability: str = "stable"
    version: str = "v1"
    needs_tenant_db: bool = True
    sort_order: int = 0


_REGISTRY: Dict[str, CapabilitySpec] = {}


def register_capability(
    *,
    code: str,
    name: str,
    category: str = "",
    description: str = "",
    channels: Optional[List[str]] = None,
    read_only: bool = True,
    input_schema: Optional[dict] = None,
    output_fields: Optional[List[str]] = None,
    sensitive_fields: Optional[List[str]] = None,
    risk_level: str = "low",
    stability: str = "stable",
    version: str = "v1",
    needs_tenant_db: bool = True,
    sort_order: int = 0,
):
    def _decorator(func: Callable) -> Callable:
        if code in _REGISTRY:
            logger.warning(f"能力码重复注册，后者覆盖前者: {code}")
        _REGISTRY[code] = CapabilitySpec(
            code=code,
            name=name,
            handler=func,
            category=category,
            description=description,
            channels=channels or ["api", "mcp"],
            read_only=read_only,
            input_schema=input_schema,
            output_fields=output_fields,
            sensitive_fields=sensitive_fields,
            risk_level=risk_level,
            stability=stability,
            version=version,
            needs_tenant_db=needs_tenant_db,
            sort_order=sort_order,
        )
        return func

    return _decorator


def get_capability(code: str) -> Optional[CapabilitySpec]:
    return _REGISTRY.get(code)


def list_capabilities(channel: Optional[str] = None) -> List[CapabilitySpec]:
    specs = [s for s in _REGISTRY.values() if s.stability != "offline"]
    if channel:
        specs = [s for s in specs if channel in s.channels]
    return sorted(specs, key=lambda s: (s.sort_order, s.code))


def _mask_phone(value: str) -> str:
    s = str(value)
    if len(s) >= 7:
        return s[:3] + "****" + s[-4:]
    return "***"


def _apply_view(row: dict, spec: CapabilitySpec) -> dict:
    """字段裁剪 + 脱敏（默认对手机号类字段做掩码）。"""
    out = dict(row)
    if spec.output_fields:
        out = {k: out.get(k) for k in spec.output_fields}
    for f in spec.sensitive_fields or []:
        if out.get(f):
            out[f] = _mask_phone(out[f])
    return out


def _shape_result(result: Any, spec: CapabilitySpec) -> Any:
    """对结果里的列表行做裁剪+脱敏。约定分页结果形如 {list, total, page, pageSize}。"""
    if isinstance(result, dict) and isinstance(result.get("list"), list):
        result = dict(result)
        result["list"] = [
            _apply_view(r, spec) if isinstance(r, dict) else r for r in result["list"]
        ]
        return result
    if isinstance(result, list):
        return [_apply_view(r, spec) if isinstance(r, dict) else r for r in result]
    return result


async def dispatch(code: str, params: dict, ctx: OpenContext) -> Any:
    """按能力码执行，返回裁剪+脱敏后的结果。

    - 能力不存在/下线 → BizException(OPEN_404_CAP)
    - handler 内部异常在数据面统一翻译为对外错误码
    """
    spec = get_capability(code)
    if spec is None or spec.stability == "offline":
        raise BizException("能力不存在或已下线", code=404)

    params = params or {}

    if spec.needs_tenant_db:
        from app.core.database import db_manager

        async for db in db_manager.get_tenant_session(ctx.tenant_code):
            raw = await spec.handler(ctx, params, db)
            return _shape_result(raw, spec)
    else:
        raw = await spec.handler(ctx, params, None)
        return _shape_result(raw, spec)
