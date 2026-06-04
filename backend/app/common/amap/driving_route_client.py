"""
高德路径规划 2.0 · 驾车
文档：https://lbs.amap.com/api/webservice/guide/api/newroute
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

import httpx

from app.common.exceptions import BizException
from app.core.config import get_settings

# 高速优先（普通驾车）
STRATEGY_HIGHWAY_PRIORITY = 34


@dataclass
class DrivingRouteResult:
    distance_meters: int
    duration_seconds: int
    polyline_path: list[list[float]]


def _format_coord(lng: Decimal | float, lat: Decimal | float) -> str:
    return f"{float(lng):.6f},{float(lat):.6f}"


def _parse_polyline_point(pair: str) -> Optional[list[float]]:
    part = pair.strip()
    if not part or "," not in part:
        return None
    lng_s, lat_s = part.split(",", 1)
    try:
        return [float(lng_s.strip()), float(lat_s.strip())]
    except ValueError:
        return None


def merge_step_polylines(steps: list[dict[str, Any]]) -> list[list[float]]:
    """合并各 step 的 polyline 为 [[lng, lat], ...]。"""
    path: list[list[float]] = []
    for step in steps:
        raw = step.get("polyline")
        if not raw or not isinstance(raw, str):
            continue
        # 分号分隔坐标对；部分文档亦可能出现逗号仅分隔 lng,lat
        segments = raw.split(";")
        for seg in segments:
            pt = _parse_polyline_point(seg)
            if not pt:
                continue
            if path and path[-1][0] == pt[0] and path[-1][1] == pt[1]:
                continue
            path.append(pt)
    return path


def _extract_first_path(route: dict[str, Any]) -> dict[str, Any]:
    paths = route.get("paths")
    if paths is None:
        raise BizException("高德未返回路线方案")
    if isinstance(paths, list):
        if not paths:
            raise BizException("高德未返回路线方案")
        return paths[0]
    if isinstance(paths, dict):
        return paths
    raise BizException("高德路线方案格式无效")


def _parse_duration_seconds(path: dict[str, Any]) -> int:
    cost = path.get("cost")
    if isinstance(cost, dict) and cost.get("duration") is not None:
        try:
            return max(0, int(cost["duration"]))
        except (TypeError, ValueError):
            pass
    if path.get("duration") is not None:
        try:
            return max(0, int(path["duration"]))
        except (TypeError, ValueError):
            pass
    raise BizException("高德未返回路线耗时，请检查 show_fields 是否包含 cost")


def _parse_driving_route_response(data: dict[str, Any]) -> DrivingRouteResult:
    status = str(data.get("status", ""))
    if status != "1":
        info = data.get("info") or "高德路径规划失败"
        infocode = data.get("infocode")
        msg = f"{info}" + (f" ({infocode})" if infocode else "")
        raise BizException(msg)

    route = data.get("route")
    if not route or not isinstance(route, dict):
        raise BizException("高德未返回路线数据")

    path = _extract_first_path(route)

    try:
        distance_m = int(path.get("distance") or 0)
    except (TypeError, ValueError) as exc:
        raise BizException("高德返回的路线距离格式无效") from exc

    if distance_m <= 0:
        raise BizException("高德未计算出有效驾车距离")

    duration_s = _parse_duration_seconds(path)

    steps = path.get("steps") or []
    if not isinstance(steps, list):
        steps = []
    polyline_path = merge_step_polylines(steps)

    return DrivingRouteResult(
        distance_meters=distance_m,
        duration_seconds=duration_s,
        polyline_path=polyline_path,
    )


class AmapDrivingRouteClient:
    """驾车路径规划 2.0（高速优先）"""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        strategy: int = STRATEGY_HIGHWAY_PRIORITY,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.AMAP_WEB_SERVICE_KEY
        self.api_url = api_url or settings.AMAP_DRIVING_ROUTE_API_URL
        self.strategy = strategy

    async def plan_driving_route(
        self,
        origin_lng: Decimal | float,
        origin_lat: Decimal | float,
        dest_lng: Decimal | float,
        dest_lat: Decimal | float,
        *,
        client: Optional[httpx.AsyncClient] = None,
    ) -> DrivingRouteResult:
        if not self.api_key:
            raise BizException("未配置 AMAP_WEB_SERVICE_KEY，无法调用高德路径规划")

        params = {
            "key": self.api_key,
            "origin": _format_coord(origin_lng, origin_lat),
            "destination": _format_coord(dest_lng, dest_lat),
            "strategy": self.strategy,
            "show_fields": "cost,polyline",
            "output": "json",
        }

        owns_client = client is None
        if owns_client:
            client = httpx.AsyncClient(timeout=60.0)

        try:
            resp = await client.get(self.api_url, params=params)
            resp.raise_for_status()
            return _parse_driving_route_response(resp.json())
        except httpx.HTTPError as exc:
            raise BizException(f"高德路径规划请求失败: {exc}") from exc
        finally:
            if owns_client and client is not None:
                await client.aclose()


def meters_to_km(distance_m: int, *, precision: int = 1) -> float:
    return round(distance_m / 1000.0, precision)


def seconds_to_hours(duration_s: int, *, precision: int = 1) -> float:
    return round(duration_s / 3600.0, precision)


# 高德驾车为私家车导航；普通重卡预计用时 ≈ 私家车用时 × 该系数（限速更低 + 强制休息）
TRUCK_HEAVY_DURATION_FACTOR = 1.3


def truck_estimated_hours_from_drive_seconds(
    duration_s: int,
    *,
    factor: float = TRUCK_HEAVY_DURATION_FACTOR,
    precision: int = 1,
) -> float:
    return round(duration_s / 3600.0 * factor, precision)
