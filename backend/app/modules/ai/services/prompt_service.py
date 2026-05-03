"""提示词模板服务（平台库）"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.ai.models.platform.ai_prompt_template import AiPromptTemplate
from app.modules.ai.schemas.console.prompt import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
)


class PromptService:

    @staticmethod
    async def page(
        platform_db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        scene: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(AiPromptTemplate).where(AiPromptTemplate.is_deleted == 0)
        if keyword:
            base = base.where(
                (AiPromptTemplate.code.contains(keyword))
                | (AiPromptTemplate.name.contains(keyword))
            )
        if scene:
            base = base.where(AiPromptTemplate.scene == scene)
        if status is not None:
            base = base.where(AiPromptTemplate.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await platform_db.execute(count_q)).scalar() or 0
        rows = (
            await platform_db.execute(
                base.order_by(AiPromptTemplate.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [PromptService._to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create(
        platform_db: AsyncSession, data: PromptTemplateCreate
    ) -> AiPromptTemplate:
        existing = (
            await platform_db.execute(
                select(AiPromptTemplate.id).where(
                    AiPromptTemplate.code == data.code,
                    AiPromptTemplate.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise BizException(f"模板编码 {data.code} 已存在")
        row = AiPromptTemplate(
            code=data.code,
            name=data.name,
            scene=data.scene,
            content=data.content,
            description=data.description,
            version=1,
            status=1,
        )
        platform_db.add(row)
        await platform_db.flush()
        await platform_db.commit()
        await platform_db.refresh(row)
        return row

    @staticmethod
    async def update(
        platform_db: AsyncSession,
        template_id: int,
        data: PromptTemplateUpdate,
    ) -> AiPromptTemplate:
        row = (
            await platform_db.execute(
                select(AiPromptTemplate).where(
                    AiPromptTemplate.id == template_id,
                    AiPromptTemplate.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("模板不存在")

        changed = False
        if data.name is not None and data.name != row.name:
            row.name = data.name
            changed = True
        if data.scene is not None and data.scene != row.scene:
            row.scene = data.scene
            changed = True
        if data.content is not None and data.content != row.content:
            row.content = data.content
            changed = True
        if data.description is not None and data.description != row.description:
            row.description = data.description
            changed = True
        if data.status is not None:
            row.status = data.status
        if changed:
            row.version = (row.version or 1) + 1
        await platform_db.flush()
        await platform_db.commit()
        await platform_db.refresh(row)
        return row

    @staticmethod
    async def delete(platform_db: AsyncSession, template_id: int) -> None:
        row = (
            await platform_db.execute(
                select(AiPromptTemplate).where(
                    AiPromptTemplate.id == template_id,
                    AiPromptTemplate.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("模板不存在")
        row.is_deleted = 1
        await platform_db.flush()
        await platform_db.commit()

    @staticmethod
    def _to_dict(row: AiPromptTemplate) -> dict:
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "scene": row.scene,
            "content": row.content,
            "description": row.description,
            "version": row.version,
            "status": row.status,
        }
