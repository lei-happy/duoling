"""
路线管理服务（租户库）
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.route import Route
from app.modules.client.schemas.route import (
    RouteCreate, RouteUpdate, RouteOut,
)


class RouteService:

    @staticmethod
    async def page_routes(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(Route).where(Route.is_deleted == 0)

        if keyword:
            base = base.where(
                (Route.route_name.contains(keyword)) |
                (Route.route_code.contains(keyword)) |
                (Route.origin.contains(keyword)) |
                (Route.destination.contains(keyword))
            )
        if status is not None:
            base = base.where(Route.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Route.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [RouteOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_route(
        db: AsyncSession, data: RouteCreate
    ) -> Route:
        if data.routeCode:
            existing = await db.execute(
                select(Route).where(
                    Route.route_code == data.routeCode,
                    Route.is_deleted == 0,
                )
            )
            if existing.scalar_one_or_none():
                raise BizException(f"路线编码 {data.routeCode} 已存在")

        route = Route(
            route_name=data.routeName,
            route_code=data.routeCode,
            origin=data.origin,
            destination=data.destination,
            distance=data.distance,
            estimated_hours=data.estimatedHours,
            waypoints=data.waypoints,
            remark=data.remark,
        )
        db.add(route)
        await db.flush()
        await db.refresh(route)
        return route

    @staticmethod
    async def update_route(
        db: AsyncSession, route_id: int, data: RouteUpdate
    ) -> Route:
        result = await db.execute(
            select(Route).where(
                Route.id == route_id,
                Route.is_deleted == 0,
            )
        )
        route = result.scalar_one_or_none()
        if not route:
            raise BizException("路线不存在")

        field_map = {
            "routeName": "route_name",
            "routeCode": "route_code",
            "origin": "origin",
            "destination": "destination",
            "distance": "distance",
            "estimatedHours": "estimated_hours",
            "waypoints": "waypoints",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(route, model_field, val)

        await db.flush()
        await db.refresh(route)
        return route

    @staticmethod
    async def delete_route(db: AsyncSession, route_id: int) -> None:
        result = await db.execute(
            select(Route).where(
                Route.id == route_id,
                Route.is_deleted == 0,
            )
        )
        route = result.scalar_one_or_none()
        if not route:
            raise BizException("路线不存在")
        route.is_deleted = 1
        await db.flush()
