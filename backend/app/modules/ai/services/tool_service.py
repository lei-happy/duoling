"""工具元数据服务（平台库）"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.tools.registry import get_registry


class ToolService:

    @staticmethod
    async def page(
        platform_db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(AiTool).where(AiTool.is_deleted == 0)
        if keyword:
            base = base.where(
                (AiTool.code.contains(keyword)) | (AiTool.name.contains(keyword))
            )
        if category:
            base = base.where(AiTool.category == category)
        if status is not None:
            base = base.where(AiTool.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await platform_db.execute(count_q)).scalar() or 0

        rows = (
            await platform_db.execute(
                base.order_by(AiTool.category.asc(), AiTool.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [ToolService._to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_categories(platform_db: AsyncSession) -> list[str]:
        rows = (
            await platform_db.execute(
                select(AiTool.category)
                .where(AiTool.is_deleted == 0, AiTool.category.isnot(None))
                .distinct()
            )
        ).all()
        return [r[0] for r in rows if r[0]]

    @staticmethod
    async def update_status(
        platform_db: AsyncSession, tool_id: int, status: int
    ) -> None:
        row = (
            await platform_db.execute(
                select(AiTool).where(AiTool.id == tool_id, AiTool.is_deleted == 0)
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("工具不存在")
        row.status = 1 if status == 1 else 0
        await platform_db.flush()
        await platform_db.commit()

    @staticmethod
    async def sync_from_registry(platform_db: AsyncSession) -> dict:
        """手动触发：把代码内注册表同步到 ai_tool 表"""
        return await get_registry().sync_to_db(platform_db)

    @staticmethod
    def _to_dict(row: AiTool) -> dict:
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "category": row.category,
            "description": row.description,
            "paramsSchema": row.params_schema,
            "requiredPermission": row.required_permission,
            "riskLevel": row.risk_level,
            "confirmRequired": bool(row.confirm_required),
            "isBuiltin": bool(row.is_builtin),
            "status": row.status,
        }
