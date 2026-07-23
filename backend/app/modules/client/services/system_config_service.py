"""
系统配置服务（租户库）
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.system_config import SystemConfig
from app.modules.client.schemas.system_config import SystemConfigOut


class SystemConfigService:

    @staticmethod
    async def ensure(
        db: AsyncSession,
        key: str,
        *,
        default_value: str,
        config_group: str,
        description: str,
        value_type: str = "string",
    ) -> None:
        """幂等补齐配置项：不存在则按默认值插入（用于存量租户懒补齐）。"""
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == key)
        )
        if result.scalar_one_or_none():
            return
        db.add(SystemConfig(
            config_key=key,
            config_value=default_value,
            config_group=config_group,
            description=description,
            value_type=value_type,
            default_value=default_value,
        ))
        await db.flush()

    @staticmethod
    async def _ensure_lazy_defaults(db: AsyncSession) -> None:
        """懒补齐随功能迭代新增、但存量租户开户种子里没有的配置项。"""
        from app.modules.client.services.finance.base.finance_stage_rules import (
            STAGE_RULES_CONFIG_GROUP,
            STAGE_RULES_CONFIG_KEY,
            STAGE_RULES_DESCRIPTION,
            default_stage_rules_json,
        )

        await SystemConfigService.ensure(
            db,
            STAGE_RULES_CONFIG_KEY,
            default_value=default_stage_rules_json(),
            config_group=STAGE_RULES_CONFIG_GROUP,
            description=STAGE_RULES_DESCRIPTION,
            value_type="json",
        )

    @staticmethod
    async def get_all(db: AsyncSession) -> list:
        await SystemConfigService._ensure_lazy_defaults(db)
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.is_deleted == 0)
            .order_by(SystemConfig.config_group, SystemConfig.id)
        )
        items = result.scalars().all()
        return [SystemConfigOut.from_model(item).model_dump() for item in items]

    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> Optional[str]:
        result = await db.execute(
            select(SystemConfig).where(
                SystemConfig.config_key == key,
                SystemConfig.is_deleted == 0,
            )
        )
        config = result.scalar_one_or_none()
        if not config:
            return None
        return config.config_value

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str) -> list:
        result = await db.execute(
            select(SystemConfig).where(
                SystemConfig.config_group == group,
                SystemConfig.is_deleted == 0,
            ).order_by(SystemConfig.id)
        )
        items = result.scalars().all()
        return [SystemConfigOut.from_model(item).model_dump() for item in items]

    @staticmethod
    async def update_value(
        db: AsyncSession, key: str, value: str
    ) -> SystemConfig:
        result = await db.execute(
            select(SystemConfig).where(
                SystemConfig.config_key == key,
                SystemConfig.is_deleted == 0,
            )
        )
        config = result.scalar_one_or_none()
        if not config:
            raise BizException("配置项不存在")

        config.config_value = value
        await db.flush()
        await db.refresh(config)
        return config
