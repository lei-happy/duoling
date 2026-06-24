"""
路线管理服务（租户库）
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.amap.driving_route_client import (
    AmapDrivingRouteClient,
    meters_to_km,
    truck_estimated_hours_from_drive_seconds,
)
from app.common.exceptions import BizException
from app.common.route_polyline import encode_route_polyline
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.route import Route
from app.modules.client.schemas.route import (
    RouteCreate,
    RouteDrivingMetricsOut,
    RouteOut,
    RouteRegionPointOut,
    RouteUpdate,
)
from app.modules.client.services.billing.standardize_service import (
    RegionResolution,
    StandardizeService,
)


def _format_region_path(res: RegionResolution) -> str:
    if res.chain:
        return "/".join(n.name for n in reversed(res.chain))
    return (res.region_name or "").strip()


def _format_region_path_short(res: RegionResolution) -> str:
    """线路名称用：仅保留市/区级，不含省名；直辖市整市选中时保留市名。"""
    if not res.chain:
        return (res.region_name or "").strip()
    leaf = res.chain[0]
    if leaf.level == 1 and len(res.chain) == 1:
        return leaf.name
    names = [n.name for n in reversed(res.chain) if n.level != 1]
    return "/".join(names) if names else (res.region_name or "").strip()


def _default_route_name(origin_res: RegionResolution, dest_res: RegionResolution) -> str:
    disp_o = _format_region_path_short(origin_res)
    disp_d = _format_region_path_short(dest_res)
    raw = f"{disp_o}-{disp_d}".strip("-")
    if len(raw) <= 100:
        return raw or "未命名线路"
    return raw[:100]


async def _next_route_code(db: AsyncSession) -> str:
    """当日序号在「含已软删除」的全表上取 max，避免唯一键 route_code 仍被删除行占用时重复插入。"""
    today = date.today().strftime("%Y%m%d")
    base = f"R{today}"
    res = await db.execute(
        select(Route.route_code).where(
            Route.route_code.isnot(None),
            Route.route_code.like(f"{base}%"),
        )
    )
    max_n = 0
    blen = len(base)
    for (code,) in res.all():
        if not code or len(code) <= blen:
            continue
        suf = code[blen:]
        if suf.isdigit():
            max_n = max(max_n, int(suf))
    return f"{base}{max_n + 1:04d}"


async def _assert_unique_region_pair(
    db: AsyncSession,
    origin_region_id: int,
    destination_region_id: int,
    *,
    exclude_route_id: Optional[int] = None,
) -> None:
    q = select(Route.id).where(
        Route.is_deleted == 0,
        Route.origin_region_id == origin_region_id,
        Route.destination_region_id == destination_region_id,
    )
    if exclude_route_id is not None:
        q = q.where(Route.id != exclude_route_id)
    hit = (await db.execute(q)).scalar_one_or_none()
    if hit is not None:
        raise BizException("该出发地—目的地线路已存在，请勿重复创建")


class RouteService:

    @staticmethod
    async def page_routes(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        status: Optional[int] = None,
        created_at_start: Optional[date] = None,
        created_at_end: Optional[date] = None,
    ) -> dict:
        base = select(Route).where(Route.is_deleted == 0)

        ow = (origin_keyword or "").strip()
        if ow:
            base = base.where(Route.origin.contains(ow))
        dw = (destination_keyword or "").strip()
        if dw:
            base = base.where(Route.destination.contains(dw))
        if status is not None:
            base = base.where(Route.status == status)
        if created_at_start is not None:
            start_dt = datetime.combine(created_at_start, time.min)
            base = base.where(Route.created_at >= start_dt)
        if created_at_end is not None:
            end_dt = datetime.combine(created_at_end, time.max)
            base = base.where(Route.created_at <= end_dt)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Route.created_at.desc(), Route.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [RouteOut.from_model(item).model_dump() for item in items],
            "count": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_routes(db: AsyncSession) -> list[Route]:
        result = await db.execute(
            select(Route)
            .where(Route.is_deleted == 0)
            .order_by(Route.created_at.desc(), Route.id.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_route(db: AsyncSession, data: RouteCreate) -> Route:
        res_o = await StandardizeService.resolve_region(
            db, region_id=data.originRegionId
        )
        res_d = await StandardizeService.resolve_region(
            db, region_id=data.destinationRegionId
        )
        if res_o.region_id is None:
            raise BizException("出发地无效或已删除")
        if res_d.region_id is None:
            raise BizException("目的地无效或已删除")

        await _assert_unique_region_pair(
            db, res_o.region_id, res_d.region_id,
        )

        disp_o = _format_region_path(res_o)
        disp_d = _format_region_path(res_d)
        name_in = (data.routeName or "").strip()
        route_name = name_in if name_in else _default_route_name(res_o, res_d)
        route_code = await _next_route_code(db)

        route = Route(
            route_name=route_name,
            route_code=route_code,
            origin=disp_o,
            destination=disp_d,
            origin_region_id=res_o.region_id,
            destination_region_id=res_d.region_id,
            origin_code=res_o.region_code,
            destination_code=res_d.region_code,
            distance=data.distance,
            estimated_hours=data.estimatedHours,
            route_polyline=encode_route_polyline(data.routePolyline),
            remark=data.remark,
        )
        db.add(route)
        await db.flush()
        await db.refresh(route)
        return route

    @staticmethod
    async def update_route(db: AsyncSession, route_id: int, data: RouteUpdate) -> Route:
        result = await db.execute(
            select(Route).where(
                Route.id == route_id,
                Route.is_deleted == 0,
            )
        )
        route = result.scalar_one_or_none()
        if not route:
            raise BizException("路线不存在")

        dump = data.model_dump(exclude_unset=True)

        if any(k in dump for k in ("originRegionId", "destinationRegionId")):
            oid = dump.get("originRegionId", route.origin_region_id)
            did = dump.get("destinationRegionId", route.destination_region_id)
            if oid is None or did is None:
                raise BizException("请选择出发地与目的地")
            res_o = await StandardizeService.resolve_region(db, region_id=int(oid))
            res_d = await StandardizeService.resolve_region(db, region_id=int(did))
            if res_o.region_id is None or res_d.region_id is None:
                raise BizException("出发地或目的地无效或已删除")
            await _assert_unique_region_pair(
                db, res_o.region_id, res_d.region_id,
                exclude_route_id=route.id,
            )
            route.origin_region_id = res_o.region_id
            route.destination_region_id = res_d.region_id
            route.origin_code = res_o.region_code
            route.destination_code = res_d.region_code
            route.origin = _format_region_path(res_o)
            route.destination = _format_region_path(res_d)

        if "routeName" in dump:
            val = dump["routeName"]
            if val is None:
                raise BizException("线路名称不能为空")
            rn = str(val).strip()
            if not rn:
                raise BizException("线路名称不能为空")
            route.route_name = rn

        simple_map = {
            "distance": "distance",
            "estimatedHours": "estimated_hours",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in simple_map.items():
            if schema_field in dump:
                setattr(route, model_field, dump[schema_field])

        region_changed = any(
            k in dump for k in ("originRegionId", "destinationRegionId")
        )
        if dump.get("clearRoutePolyline"):
            route.route_polyline = None
        elif "routePolyline" in dump:
            route.route_polyline = encode_route_polyline(dump.get("routePolyline"))
        elif region_changed:
            route.route_polyline = None

        await db.flush()
        await db.refresh(route)
        return route

    @staticmethod
    async def _load_region_coords(
        db: AsyncSession, region_id: int, *, label: str
    ) -> tuple[BizRegion, float, float]:
        result = await db.execute(
            select(BizRegion).where(
                BizRegion.id == region_id,
                BizRegion.is_deleted == 0,
            )
        )
        region = result.scalar_one_or_none()
        if not region:
            raise BizException(f"{label}无效或已删除")
        if region.longitude is None or region.latitude is None:
            raise BizException(
                f"{label}「{region.name}」暂无经纬度，请联系管理员同步行政区或手动填写里程"
            )
        return region, float(region.longitude), float(region.latitude)

    @staticmethod
    async def get_driving_metrics(
        db: AsyncSession,
        origin_region_id: int,
        destination_region_id: int,
    ) -> RouteDrivingMetricsOut:
        if origin_region_id == destination_region_id:
            raise BizException("出发地与目的地不能相同")

        origin_region, o_lng, o_lat = await RouteService._load_region_coords(
            db, origin_region_id, label="出发地"
        )
        dest_region, d_lng, d_lat = await RouteService._load_region_coords(
            db, destination_region_id, label="目的地"
        )

        res_o = await StandardizeService.resolve_region(
            db, region_id=origin_region_id
        )
        res_d = await StandardizeService.resolve_region(
            db, region_id=destination_region_id
        )
        origin_name = _format_region_path(res_o) or origin_region.name
        dest_name = _format_region_path(res_d) or dest_region.name

        driving = await AmapDrivingRouteClient().plan_driving_route(
            Decimal(str(o_lng)),
            Decimal(str(o_lat)),
            Decimal(str(d_lng)),
            Decimal(str(d_lat)),
        )

        return RouteDrivingMetricsOut(
            distanceKm=meters_to_km(driving.distance_meters),
            estimatedHours=truck_estimated_hours_from_drive_seconds(
                driving.duration_seconds
            ),
            origin=RouteRegionPointOut(
                regionId=origin_region_id,
                name=origin_name,
                longitude=o_lng,
                latitude=o_lat,
            ),
            destination=RouteRegionPointOut(
                regionId=destination_region_id,
                name=dest_name,
                longitude=d_lng,
                latitude=d_lat,
            ),
            polylinePath=driving.polyline_path,
        )

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
