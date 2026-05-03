"""
LLM Provider 工厂

按 ai_model_provider 表配置创建 Provider 实例，带轻量缓存。
"""

from __future__ import annotations

import asyncio
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.ai.llm.base import LLMProvider
from app.modules.ai.llm.openai_compat import OpenAICompatProvider
from app.modules.ai.models.platform.ai_model_provider import AiModelProvider
from app.modules.ai.security.crypto import decrypt_api_key


class LLMProviderFactory:
    """Provider 工厂 + 缓存"""

    _cache: dict[str, LLMProvider] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def get(
        cls,
        platform_db: AsyncSession,
        provider_code: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> LLMProvider:
        """获取 Provider 实例

        - provider_code 为空时取 is_default=1 的；如都没有则报错
        - model_override 不为空时透传到 chat_stream（用于同 Provider 切模型）
        """
        cache_key = provider_code or "__default__"
        async with cls._lock:
            if cache_key in cls._cache:
                provider = cls._cache[cache_key]
                if model_override:
                    provider.model = model_override
                return provider

            row: Optional[AiModelProvider] = None
            if provider_code:
                # 指定 code：精确匹配
                row = (
                    await platform_db.execute(
                        select(AiModelProvider).where(
                            AiModelProvider.is_deleted == 0,
                            AiModelProvider.status == 1,
                            AiModelProvider.code == provider_code,
                        )
                    )
                ).scalar_one_or_none()
            else:
                # 不指定 code：先找 is_default=1，找不到再回退到任意一个启用的（按 id 升序）
                row = (
                    await platform_db.execute(
                        select(AiModelProvider).where(
                            AiModelProvider.is_deleted == 0,
                            AiModelProvider.status == 1,
                            AiModelProvider.is_default == 1,
                        )
                    )
                ).scalar_one_or_none()
                if row is None:
                    row = (
                        await platform_db.execute(
                            select(AiModelProvider)
                            .where(
                                AiModelProvider.is_deleted == 0,
                                AiModelProvider.status == 1,
                            )
                            .order_by(AiModelProvider.id.asc())
                            .limit(1)
                        )
                    ).scalar_one_or_none()
                    if row is not None:
                        logger.info(
                            f"[LLM] 未配置默认 Provider，自动回退使用启用中的 "
                            f"`{row.code}`；建议在 Console 中将其设为默认"
                        )

            if not row:
                raise BizException(
                    f"未找到可用的 LLM Provider（code={provider_code or '默认'}）。"
                    f"请在 Console 端「AI 数字员工 - 模型 Provider」中配置并启用。"
                )

            api_key = ""
            if row.api_key_encrypted:
                try:
                    api_key = decrypt_api_key(row.api_key_encrypted)
                except Exception as e:
                    logger.warning(f"[LLM] 解密 api_key 失败: {e!r}")
                    api_key = row.api_key_encrypted  # 兜底（明文存储时）

            provider = OpenAICompatProvider(
                code=row.code,
                model=model_override or row.model_name,
                api_key=api_key,
                base_url=row.base_url,
                timeout=row.timeout_seconds or 60,
                extra_params=row.extra_params or {},
            )
            cls._cache[cache_key] = provider
            return provider

    @classmethod
    async def invalidate(cls, provider_code: Optional[str] = None) -> None:
        """清理缓存（Provider 配置变更时调用）"""
        async with cls._lock:
            if provider_code is None:
                for p in list(cls._cache.values()):
                    await p.close()
                cls._cache.clear()
            else:
                p = cls._cache.pop(provider_code, None)
                if p:
                    await p.close()
                p = cls._cache.pop("__default__", None)
                if p:
                    await p.close()
