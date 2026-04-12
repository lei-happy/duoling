"""
驾驶员常跑线路服务（租户库）
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.driver.driver import Driver
from app.modules.client.models.driver.driver_route import DriverRoute
from app.modules.client.schemas.driver.driver_route import (
    DriverRouteCreate, DriverRouteOut,
)


class DriverRouteService:

    @staticmethod
    async def list_routes(
        db: AsyncSession, driver_id: int
    ) -> list[dict]:
        result = await db.execute(
            select(DriverRoute).where(
                DriverRoute.driver_id == driver_id,
                DriverRoute.is_deleted == 0,
            ).order_by(DriverRoute.id)
        )
        routes = result.scalars().all()
        return [DriverRouteOut.from_model(r).model_dump() for r in routes]

    @staticmethod
    async def save_routes(
        db: AsyncSession, driver_id: int, routes: List[DriverRouteCreate]
    ) -> list[dict]:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        if not result.scalar_one_or_none():
            raise BizException("驾驶员不存在")

        existing = await db.execute(
            select(DriverRoute).where(
                DriverRoute.driver_id == driver_id,
                DriverRoute.is_deleted == 0,
            )
        )
        for old in existing.scalars().all():
            old.is_deleted = 1

        new_routes = []
        for r in routes:
            if not r.originCode or not r.destCode:
                continue
            route = DriverRoute(
                driver_id=driver_id,
                origin_code=r.originCode,
                origin_name=r.originName,
                dest_code=r.destCode,
                dest_name=r.destName,
                status=1,
            )
            db.add(route)
            new_routes.append(route)

        await db.flush()
        return [DriverRouteOut.from_model(r).model_dump() for r in new_routes]
