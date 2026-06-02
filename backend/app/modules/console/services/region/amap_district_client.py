"""
高德行政区域 Web 服务 API 客户端
文档：https://lbs.amap.com/api/webservice/guide/api/district
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

CHINA_ADCODE = "100000"

AMAP_LEVEL_MAP = {
    "province": 1,
    "city": 2,
    "district": 3,
    "street": 4,
}


@dataclass
class ParsedRegionRow:
    code: int
    name: str
    pcode: Optional[int]
    level: int
    sort_order: int
    citycode: Optional[str]
    longitude: Optional[Decimal]
    latitude: Optional[Decimal]


def parse_center(center: Optional[str]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    if not center or "," not in center:
        return None, None
    parts = center.split(",", 1)
    try:
        lng = Decimal(parts[0].strip())
        lat = Decimal(parts[1].strip())
        return lng, lat
    except Exception:
        return None, None


def make_street_code(parent_adcode: int, seq: int) -> int:
    return parent_adcode * 10000 + seq


class AmapDistrictClient:
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        max_concurrent: Optional[int] = None,
        request_delay_ms: Optional[int] = None,
        api_url: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.AMAP_WEB_SERVICE_KEY
        self.max_concurrent = max_concurrent or settings.AMAP_SYNC_MAX_CONCURRENT
        self.request_delay_ms = request_delay_ms or settings.AMAP_SYNC_REQUEST_DELAY_MS
        self.api_url = api_url or settings.AMAP_DISTRICT_API_URL
        self._semaphore = asyncio.Semaphore(max(1, self.max_concurrent))
        self._delay_sec = max(0.0, self.request_delay_ms / 1000.0)

    async def fetch_district(
        self,
        client: httpx.AsyncClient,
        *,
        keywords: str,
        subdistrict: int = 1,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("未配置 AMAP_WEB_SERVICE_KEY")

        params = {
            "key": self.api_key,
            "keywords": keywords,
            "subdistrict": subdistrict,
            "extensions": "base",
            "output": "JSON",
        }
        last_exc: Optional[Exception] = None

        async with self._semaphore:
            if self._delay_sec > 0:
                await asyncio.sleep(self._delay_sec)

            for attempt in range(1, max_retries + 1):
                try:
                    resp = await client.get(self.api_url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    if str(data.get("status")) != "1":
                        raise RuntimeError(
                            f"高德 API 错误: {data.get('info')} ({data.get('infocode')})"
                        )
                    return data
                except Exception as exc:
                    last_exc = exc
                    logger.warning(
                        "amap district fetch failed keywords=%s attempt=%s: %s",
                        keywords,
                        attempt,
                        exc,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(self._delay_sec * attempt)
            raise last_exc  # type: ignore[misc]

    def _append_tree_rows(
        self,
        node: Dict[str, Any],
        rows: List[ParsedRegionRow],
        sort_counters: Dict[Optional[int], int],
        *,
        parent_code: Optional[int] = None,
    ) -> None:
        level_key = (node.get("level") or "").strip()
        if level_key == "country":
            for child in node.get("districts") or []:
                self._append_tree_rows(child, rows, sort_counters, parent_code=None)
            return

        mapped_level = AMAP_LEVEL_MAP.get(level_key)
        if mapped_level is None:
            return

        adcode_raw = node.get("adcode")
        if not adcode_raw:
            return
        adcode = int(adcode_raw)

        pcode: Optional[int] = parent_code
        if mapped_level == 1:
            pcode = None

        sort_counters[pcode] = sort_counters.get(pcode, 0) + 1
        sort_order = sort_counters[pcode]

        lng, lat = parse_center(node.get("center"))
        citycode = node.get("citycode")
        rows.append(
            ParsedRegionRow(
                code=adcode,
                name=str(node.get("name") or "").strip(),
                pcode=pcode,
                level=mapped_level,
                sort_order=sort_order,
                citycode=str(citycode) if citycode else None,
                longitude=lng,
                latitude=lat,
            )
        )

        for child in node.get("districts") or []:
            self._append_tree_rows(
                child,
                rows,
                sort_counters,
                parent_code=adcode,
            )

    async def fetch_province_city_district(
        self, client: httpx.AsyncClient
    ) -> List[ParsedRegionRow]:
        data = await self.fetch_district(
            client, keywords=CHINA_ADCODE, subdistrict=3
        )
        districts = data.get("districts") or []
        if not districts:
            raise RuntimeError("高德返回空 districts，无法同步省/市/区县")

        rows: List[ParsedRegionRow] = []
        sort_counters: Dict[Optional[int], int] = {}
        for root in districts:
            self._append_tree_rows(root, rows, sort_counters)
        return rows

    def street_fetch_targets(self, rows: List[ParsedRegionRow]) -> List[ParsedRegionRow]:
        district_parents = {r.pcode for r in rows if r.level == 3}
        targets = [r for r in rows if r.level == 3]
        for city in rows:
            if city.level == 2 and city.code not in district_parents:
                targets.append(city)
        return targets

    async def fetch_streets_for_parent(
        self,
        client: httpx.AsyncClient,
        parent: ParsedRegionRow,
        start_sort: int = 1,
    ) -> List[ParsedRegionRow]:
        data = await self.fetch_district(
            client,
            keywords=str(parent.code),
            subdistrict=1,
        )
        districts = data.get("districts") or []
        if not districts:
            return []

        root = districts[0]
        children = root.get("districts") or []
        streets: List[ParsedRegionRow] = []
        seq = start_sort
        for child in children:
            if (child.get("level") or "").strip() != "street":
                continue
            lng, lat = parse_center(child.get("center"))
            citycode = child.get("citycode")
            streets.append(
                ParsedRegionRow(
                    code=make_street_code(parent.code, seq),
                    name=str(child.get("name") or "").strip(),
                    pcode=parent.code,
                    level=4,
                    sort_order=seq,
                    citycode=str(citycode) if citycode else None,
                    longitude=lng,
                    latitude=lat,
                )
            )
            seq += 1
        return streets

    async def fetch_all_regions(
        self,
        *,
        progress_callback=None,
    ) -> List[ParsedRegionRow]:
        rows: List[ParsedRegionRow] = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            base_rows = await self.fetch_province_city_district(client)
            rows.extend(base_rows)

            if progress_callback:
                await progress_callback(15, f"已拉取省/市/区县 {len(base_rows)} 条")

            targets = self.street_fetch_targets(base_rows)
            total_targets = len(targets)
            street_rows: List[ParsedRegionRow] = []

            for idx, parent in enumerate(targets, start=1):
                try:
                    streets = await self.fetch_streets_for_parent(client, parent)
                    street_rows.extend(streets)
                except Exception as exc:
                    logger.warning(
                        "fetch streets failed parent=%s (%s): %s",
                        parent.code,
                        parent.name,
                        exc,
                    )
                if progress_callback and (
                    idx == 1 or idx == total_targets or idx % 20 == 0
                ):
                    pct = 15 + int(75 * idx / max(total_targets, 1))
                    await progress_callback(
                        pct,
                        f"街道拉取进度 {idx}/{total_targets}，已获取 {len(street_rows)} 条街道",
                    )

            rows.extend(street_rows)

        if progress_callback:
            await progress_callback(92, f"拉取完成，共 {len(rows)} 条")

        return rows
