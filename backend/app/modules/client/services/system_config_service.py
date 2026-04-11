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
    async def get_all(db: AsyncSession) -> list:
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
