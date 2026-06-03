"""
高德距离测量 Web 服务 API
文档：https://lbs.amap.com/api/webservice/guide/api/direction#t8
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

import httpx

from app.common.exceptions import BizException
from app.core.config import get_settings


@dataclass
class DrivingDistanceResult:
    distance_meters: int
    duration_seconds: int


def _format_coord(lng: Decimal | float, lat: Decimal | float) -> str:
    return f"{float(lng):.6f},{float(lat):.6f}"


def _parse_driving_result(data: dict[str, Any]) -> DrivingDistanceResult:
    status = str(data.get("status", ""))
    if status != "1":
        info = data.get("info") or "高德距离测量失败"
        infocode = data.get("infocode")
        msg = f"{info}" + (f" ({infocode})" if infocode else "")
        raise BizException(msg)

    results = data.get("results") or []
    if not results:
        raise BizException("高德未返回距离结果")

    row = results[0]
    row_info = row.get("info")
    if row_info:
        code = row.get("code")
        msg = str(row_info)
        if code is not None:
            msg = f"{msg} (code={code})"
        raise BizException(msg)

    try:
        distance_m = int(row.get("distance") or 0)
        duration_s = int(row.get("duration") or 0)
    except (TypeError, ValueError) as exc:
        raise BizException("高德返回的距离或时长格式无效") from exc

    if distance_m <= 0:
        raise BizException("高德未计算出有效驾车距离")

    return DrivingDistanceResult(
        distance_meters=distance_m,
        duration_seconds=max(0, duration_s),
    )


class AmapDistanceClient:
    """驾车导航距离（type=1）"""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.AMAP_WEB_SERVICE_KEY
        self.api_url = api_url or settings.AMAP_DISTANCE_API_URL

    async def driving_distance(
        self,
        origin_lng: Decimal | float,
        origin_lat: Decimal | float,
        dest_lng: Decimal | float,
        dest_lat: Decimal | float,
        *,
        client: Optional[httpx.AsyncClient] = None,
    ) -> DrivingDistanceResult:
        if not self.api_key:
            raise BizException("未配置 AMAP_WEB_SERVICE_KEY，无法调用高德测距")

        origins = _format_coord(origin_lng, origin_lat)
        destination = _format_coord(dest_lng, dest_lat)
        params = {
            "key": self.api_key,
            "origins": origins,
            "destination": destination,
            "type": 1,
            "output": "JSON",
        }

        owns_client = client is None
        if owns_client:
            client = httpx.AsyncClient(timeout=30.0)

        try:
            resp = await client.get(self.api_url, params=params)
            resp.raise_for_status()
            return _parse_driving_result(resp.json())
        except httpx.HTTPError as exc:
            raise BizException(f"高德距离测量请求失败: {exc}") from exc
        finally:
            if owns_client and client is not None:
                await client.aclose()


def meters_to_km(distance_m: int, *, precision: int = 1) -> float:
    return round(distance_m / 1000.0, precision)


def seconds_to_hours(duration_s: int, *, precision: int = 1) -> float:
    return round(duration_s / 3600.0, precision)
