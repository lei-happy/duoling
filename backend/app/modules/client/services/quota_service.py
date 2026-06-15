"""
版本配额校验服务

产品版本上有 max_users / max_vehicles，但历史上只做展示、未在创建时拦截。
本服务在创建车辆 / 员工等资源前做硬校验，避免低版本无限录入绕过付费档位。

口径：
  - 同一租户可并行持有多个有效版本，取各版本上限的「最大值」作为有效上限；
  - 上限 <= 0 视为不限量（放行）；
  - 无任何有效版本时按 fail-closed 由调用方决定（这里返回 0=不限，避免误伤；
    真正的功能门控由 require_feature 负责）。
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.core.database import db_manager
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.tenant.tenant_product import TenantProduct


class QuotaService:
    """版本配额校验"""

    @staticmethod
    async def get_limits(tenant_code: str) -> Dict[str, int]:
        """返回租户有效版本的配额上限（取各有效版本最大值），0 表示不限。"""
        now = datetime.now()
        async for platform_db in db_manager.get_platform_session():
            version_ids = (
                await platform_db.execute(
                    select(TenantProduct.version_id).where(
                        TenantProduct.tenant_code == tenant_code,
                        TenantProduct.is_deleted == 0,
                        TenantProduct.status == 1,
                        or_(
                            TenantProduct.end_time.is_(None),
                            TenantProduct.end_time > now,
                        ),
                    )
                )
            ).scalars().all()
            if not version_ids:
                return {"max_users": 0, "max_vehicles": 0}

            row = (
                await platform_db.execute(
                    select(
                        func.max(ProductVersion.max_users),
                        func.max(ProductVersion.max_vehicles),
                    ).where(
                        ProductVersion.id.in_(version_ids),
                        ProductVersion.is_deleted == 0,
                    )
                )
            ).one()
            return {
                "max_users": int(row[0] or 0),
                "max_vehicles": int(row[1] or 0),
            }
        return {"max_users": 0, "max_vehicles": 0}

    @staticmethod
    async def ensure_vehicle_quota(db: AsyncSession, tenant_code: str) -> None:
        """新增车辆前校验配额。db 为租户库 session。"""
        limits = await QuotaService.get_limits(tenant_code)
        max_vehicles = limits["max_vehicles"]
        if max_vehicles <= 0:
            return
        from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle

        count = (
            await db.execute(
                select(func.count())
                .select_from(Vehicle)
                .where(Vehicle.is_deleted == 0)
            )
        ).scalar() or 0
        if count >= max_vehicles:
            raise BizException(
                f"车辆数量已达当前版本上限（{max_vehicles} 台），请升级版本后再新增"
            )

    @staticmethod
    async def ensure_user_quota(db: AsyncSession, tenant_code: str) -> None:
        """新增员工前校验配额。db 为租户库 session。"""
        limits = await QuotaService.get_limits(tenant_code)
        max_users = limits["max_users"]
        if max_users <= 0:
            return
        from app.modules.client.models.user.biz_user import BizUser

        count = (
            await db.execute(
                select(func.count())
                .select_from(BizUser)
                .where(BizUser.is_deleted == 0)
            )
        ).scalar() or 0
        if count >= max_users:
            raise BizException(
                f"员工数量已达当前版本上限（{max_users} 人），请升级版本后再新增"
            )
