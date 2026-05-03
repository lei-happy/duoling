"""LLM Provider 服务（平台库）"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.ai.llm.factory import LLMProviderFactory
from app.modules.ai.models.platform.ai_model_provider import AiModelProvider
from app.modules.ai.schemas.console.provider import ProviderCreate, ProviderUpdate
from app.modules.ai.security.crypto import encrypt_api_key, mask_api_key


class ProviderService:

    @staticmethod
    async def page(
        platform_db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(AiModelProvider).where(AiModelProvider.is_deleted == 0)
        if keyword:
            base = base.where(
                (AiModelProvider.code.contains(keyword))
                | (AiModelProvider.name.contains(keyword))
            )
        if status is not None:
            base = base.where(AiModelProvider.status == status)
        count_q = select(func.count()).select_from(base.subquery())
        total = (await platform_db.execute(count_q)).scalar() or 0
        rows = (
            await platform_db.execute(
                base.order_by(
                    AiModelProvider.is_default.desc(), AiModelProvider.id.asc()
                )
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [ProviderService._to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create(
        platform_db: AsyncSession, data: ProviderCreate
    ) -> AiModelProvider:
        existing = (
            await platform_db.execute(
                select(AiModelProvider.id).where(
                    AiModelProvider.code == data.code,
                    AiModelProvider.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise BizException(f"Provider 编码 {data.code} 已存在")

        if data.isDefault:
            await platform_db.execute(
                update(AiModelProvider)
                .where(AiModelProvider.is_deleted == 0)
                .values(is_default=0)
            )

        row = AiModelProvider(
            code=data.code,
            name=data.name,
            provider_type=data.providerType,
            base_url=data.baseUrl,
            api_key_encrypted=encrypt_api_key(data.apiKey or ""),
            model_name=data.modelName,
            extra_params=data.extraParams,
            timeout_seconds=data.timeoutSeconds,
            is_default=1 if data.isDefault else 0,
            status=data.status,
        )
        platform_db.add(row)
        await platform_db.flush()
        await platform_db.commit()
        await LLMProviderFactory.invalidate(data.code)
        return row

    @staticmethod
    async def update(
        platform_db: AsyncSession, provider_id: int, data: ProviderUpdate
    ) -> AiModelProvider:
        row = (
            await platform_db.execute(
                select(AiModelProvider).where(
                    AiModelProvider.id == provider_id,
                    AiModelProvider.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("Provider 不存在")

        if data.isDefault is True and row.is_default != 1:
            await platform_db.execute(
                update(AiModelProvider)
                .where(AiModelProvider.is_deleted == 0)
                .values(is_default=0)
            )
            row.is_default = 1
        elif data.isDefault is False:
            row.is_default = 0

        if data.name is not None:
            row.name = data.name
        if data.providerType is not None:
            row.provider_type = data.providerType
        if data.baseUrl is not None:
            row.base_url = data.baseUrl
        if data.apiKey:
            row.api_key_encrypted = encrypt_api_key(data.apiKey)
        if data.modelName is not None:
            row.model_name = data.modelName
        if data.extraParams is not None:
            row.extra_params = data.extraParams
        if data.timeoutSeconds is not None:
            row.timeout_seconds = data.timeoutSeconds
        if data.status is not None:
            row.status = data.status

        await platform_db.flush()
        await platform_db.commit()
        await LLMProviderFactory.invalidate(row.code)
        return row

    @staticmethod
    async def set_default(platform_db: AsyncSession, provider_id: int) -> None:
        """把指定 Provider 设为默认（同时把其他 Provider 的 is_default 清零）"""
        row = (
            await platform_db.execute(
                select(AiModelProvider).where(
                    AiModelProvider.id == provider_id,
                    AiModelProvider.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("Provider 不存在")
        if row.status != 1:
            raise BizException("已停用的 Provider 不能设为默认，请先启用")

        await platform_db.execute(
            update(AiModelProvider)
            .where(AiModelProvider.is_deleted == 0)
            .values(is_default=0)
        )
        row.is_default = 1
        await platform_db.flush()
        await platform_db.commit()
        await LLMProviderFactory.invalidate(row.code)

    @staticmethod
    async def delete(platform_db: AsyncSession, provider_id: int) -> None:
        row = (
            await platform_db.execute(
                select(AiModelProvider).where(
                    AiModelProvider.id == provider_id,
                    AiModelProvider.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("Provider 不存在")
        row.is_deleted = 1
        await platform_db.flush()
        await platform_db.commit()
        await LLMProviderFactory.invalidate(row.code)

    @staticmethod
    def _to_dict(row: AiModelProvider) -> dict:
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "providerType": row.provider_type,
            "baseUrl": row.base_url,
            "apiKeyMasked": mask_api_key(row.api_key_encrypted or ""),
            "modelName": row.model_name,
            "extraParams": row.extra_params,
            "timeoutSeconds": row.timeout_seconds,
            "isDefault": bool(row.is_default),
            "status": row.status,
        }
