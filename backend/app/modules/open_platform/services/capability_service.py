"""能力目录服务

控制面展示直接读代码注册表（永远与实现一致）；sync_to_db 把元数据同步到平台库
open_capability，供文档页与运营查询。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.open_platform.capabilities.registry import (
    list_capabilities,
    CapabilitySpec,
)
from app.modules.open_platform.models.platform.open_capability import OpenCapability


def _spec_to_out(spec: CapabilitySpec) -> dict:
    return {
        "code": spec.code,
        "name": spec.name,
        "category": spec.category,
        "description": spec.description,
        "channels": spec.channels,
        "read_only": spec.read_only,
        "risk_level": spec.risk_level,
        "stability": spec.stability,
        "version": spec.version,
        "input_schema": spec.input_schema,
        "output_fields": spec.output_fields,
    }


class CapabilityService:
    @staticmethod
    def list_for_display(channel: Optional[str] = None) -> list[dict]:
        return [_spec_to_out(s) for s in list_capabilities(channel)]

    @staticmethod
    async def sync_to_db(db: AsyncSession) -> int:
        """把注册表能力 upsert 进 open_capability，返回处理条数。"""
        count = 0
        for spec in list_capabilities():
            row = await db.scalar(
                select(OpenCapability).where(OpenCapability.code == spec.code)
            )
            if row is None:
                row = OpenCapability(code=spec.code)
                db.add(row)
            row.name = spec.name
            row.category = spec.category
            row.description = spec.description
            row.channels = spec.channels
            row.read_only = 1 if spec.read_only else 0
            row.input_schema = spec.input_schema
            row.output_fields = spec.output_fields
            row.sensitive_fields = spec.sensitive_fields
            row.risk_level = spec.risk_level
            row.stability = spec.stability
            row.version = spec.version
            row.status = "enabled"
            row.sort_order = spec.sort_order
            count += 1
        await db.flush()
        return count
