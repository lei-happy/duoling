"""
汽车之家全量同步：品牌（getbrand API）+ 报价页车系列表 + Logo/车系图下载到 uploads。

图片目录与 Console 上传一致：brand_logo → uploads/brand_logo，car_series → uploads/car_series。

参配（能源类型、长/宽/高、轴距、轮距、接近/离去角、整备质量等）：
默认请求 car.autohome.com.cn 车系参配页解析首个代表车型 embedded `var config` JSON；
若车系页无车型链接则尝试年代子页。可通过任务 payload `fetchSpecs: false` 关闭以缩短耗时。

增量：`incrementalOnly: true` 时，已存在的品牌（autohome_brand_id）不拉 Logo、不写品牌行；
已存在车系（autohome_series_id）不拉车系图与参配、不写车系行；仍会请求各品牌报价页以发现新车系。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.local_image_upload import save_scene_image
from app.core.database import db_manager
from app.modules.console.models.basicdata.basicdata_brand import BasicdataBrand
from app.modules.console.models.basicdata.basicdata_car_series import BasicdataCarSeries
from app.modules.console.models.ops.autohome_sync_job import AutohomeSyncJob

from app.modules.console.services.ops.autohome_crawl_runner import (
    DEFAULT_USER_AGENT,
    _append_log,
    fetch_with_retries,
)
from app.modules.console.services.ops.autohome_spec_scrape import (
    ParsedSeriesSpecs,
    fetch_series_specs_snapshot,
)

logger = logging.getLogger(__name__)

URL_GETBRAND = "https://www.autohome.com.cn/web-main/car/brand/getbrand"
URL_PRICE_BRAND = "https://www.autohome.com.cn/price/brandid_{brandid}"

SERIES_RE_FULL = re.compile(
    r'"seriesid"\s*:\s*(\d+)\s*,\s*"seriesname"\s*:\s*"((?:[^"\\]|\\.)*?)"\s*,\s*'
    r'"seriesimg"\s*:\s*"((?:[^"\\]|\\.)*?)"\s*,\s*"seriesminprice"\s*:\s*(\d+)\s*,\s*'
    r'"seriesmaxprice"\s*:\s*(\d+)',
)
SERIES_RE_SIMPLE = re.compile(
    r'"seriesid"\s*:\s*(\d+)\s*,\s*"seriesname"\s*:\s*"((?:[^"\\]|\\.)*?)"\s*,\s*'
    r'"seriesimg"\s*:\s*"((?:[^"\\]|\\.)*?)"',
)


def _unescape_json_string(s: str) -> str:
    return s.replace(r"\\/", "/").replace(r"\"", '"').replace(r"\\", "\\")


def _normalize_media_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if u.startswith("//"):
        return "https:" + u
    return u


def _fmt_price_wan(lo: Optional[int], hi: Optional[int]) -> Optional[str]:
    if lo is None or hi is None:
        return None
    try:
        a, b = int(lo), int(hi)
        return f"{a / 10000:.2f}-{b / 10000:.2f}万"
    except (TypeError, ValueError):
        return None


def _guess_ext_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for e in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"):
        if path.endswith(e):
            return e
    return ""


def _guess_ext_from_bytes(content: bytes) -> str:
    if len(content) >= 8 and content[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if len(content) >= 2 and content[:2] == b"\xff\xd8":
        return ".jpg"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ".webp"
    if len(content) >= 6 and content[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    return ""


def _pick_filename_ext(url: str, content: bytes) -> str:
    u = _guess_ext_from_url(url)
    b = _guess_ext_from_bytes(content)
    if b:
        return b
    if u:
        return u
    return ".png"


def parse_series_from_price_html(html: str) -> List[Dict[str, Any]]:
    """从报价页 HTML 提取车系（含 seriesid / 名称 / 图 / 指导价）。"""
    seen: Dict[int, Dict[str, Any]] = {}
    for m in SERIES_RE_FULL.finditer(html):
        sid = int(m.group(1))
        seen[sid] = {
            "seriesid": sid,
            "seriesname": _unescape_json_string(m.group(2)),
            "seriesimg": _unescape_json_string(m.group(3)),
            "seriesminprice": int(m.group(4)),
            "seriesmaxprice": int(m.group(5)),
        }
    for m in SERIES_RE_SIMPLE.finditer(html):
        sid = int(m.group(1))
        if sid in seen:
            continue
        seen[sid] = {
            "seriesid": sid,
            "seriesname": _unescape_json_string(m.group(2)),
            "seriesimg": _unescape_json_string(m.group(3)),
            "seriesminprice": None,
            "seriesmaxprice": None,
        }
    return list(seen.values())


def parse_brand_list_json(text: str) -> List[Dict[str, Any]]:
    data = json.loads(text)
    if data.get("returncode") != 0:
        raise ValueError(data.get("message") or "getbrand 接口 returncode 非 0")
    result = data.get("result") or {}
    return list(result.get("brandlist") or [])


async def _download_bytes(client: httpx.AsyncClient, url: str) -> Optional[bytes]:
    u = _normalize_media_url(url)
    if not u:
        return None
    try:
        r = await client.get(
            u,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Referer": "https://www.autohome.com.cn/",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            },
            timeout=45.0,
            follow_redirects=True,
        )
        if r.status_code != 200:
            return None
        return r.content
    except Exception as e:
        logger.debug("download fail %s: %s", u, e)
        return None


def _save_image_bytes(content: bytes, scene: str, url_hint: str) -> Optional[str]:
    if not content:
        return None
    ext = _pick_filename_ext(url_hint, content)
    try:
        out = save_scene_image(content, scene, f"autohome{ext}")
        return out.get("url")
    except Exception as e:
        logger.warning("save_scene_image: %s", e)
        return None


async def _upsert_brand(
    session: AsyncSession,
    autohome_brand_id: int,
    name_cn: str,
    country: Optional[str],
    logo_rel: Optional[str],
) -> BasicdataBrand:
    r = await session.execute(
        select(BasicdataBrand).where(
            BasicdataBrand.autohome_brand_id == autohome_brand_id
        )
    )
    row = r.scalar_one_or_none()
    if row:
        row.brand_name_cn = name_cn
        if country is not None:
            row.brand_country = country
        if logo_rel:
            row.brand_logo = logo_rel
        await session.flush()
        return row
    row = BasicdataBrand(
        autohome_brand_id=autohome_brand_id,
        brand_name_cn=name_cn,
        brand_country=country,
        brand_logo=logo_rel,
    )
    session.add(row)
    await session.flush()
    return row


def _apply_series_specs(row: BasicdataCarSeries, specs: Optional[ParsedSeriesSpecs]) -> None:
    if not specs:
        return
    if specs.energy_type:
        row.energy_type = specs.energy_type
    if specs.length_mm is not None:
        row.length_mm = specs.length_mm
    if specs.width_mm is not None:
        row.width_mm = specs.width_mm
    if specs.height_mm is not None:
        row.height_mm = specs.height_mm
    if specs.wheelbase_mm is not None:
        row.wheelbase_mm = specs.wheelbase_mm
    if specs.front_track_mm is not None:
        row.front_track_mm = specs.front_track_mm
    if specs.rear_track_mm is not None:
        row.rear_track_mm = specs.rear_track_mm
    if specs.approach_angle is not None:
        row.approach_angle = specs.approach_angle
    if specs.departure_angle is not None:
        row.departure_angle = specs.departure_angle
    if specs.curb_weight_kg is not None:
        row.curb_weight_kg = specs.curb_weight_kg


async def _upsert_series(
    session: AsyncSession,
    brand_id: int,
    autohome_series_id: int,
    series_name: str,
    price: Optional[str],
    series_image: Optional[str],
    specs: Optional[ParsedSeriesSpecs] = None,
) -> BasicdataCarSeries:
    r = await session.execute(
        select(BasicdataCarSeries).where(
            BasicdataCarSeries.autohome_series_id == autohome_series_id
        )
    )
    row = r.scalar_one_or_none()
    if row:
        row.brand_id = brand_id
        row.series_name = series_name
        if price is not None:
            row.price = price
        if series_image:
            row.series_image = series_image
        _apply_series_specs(row, specs)
        await session.flush()
        return row
    row = BasicdataCarSeries(
        brand_id=brand_id,
        autohome_series_id=autohome_series_id,
        series_name=series_name,
        price=price,
        series_image=series_image,
    )
    _apply_series_specs(row, specs)
    session.add(row)
    await session.flush()
    return row


async def _load_job(
    session: AsyncSession, job_id: int
) -> Optional[AutohomeSyncJob]:
    r = await session.execute(
        select(AutohomeSyncJob).where(AutohomeSyncJob.job_id == job_id)
    )
    return r.scalar_one_or_none()


async def _commit_job(session: AsyncSession, job: AutohomeSyncJob) -> None:
    await session.flush()
    await session.commit()


async def _preload_incremental_sets(
    session: AsyncSession,
) -> Tuple[Set[int], Dict[int, int], Set[int]]:
    """返回：已有汽车之家品牌 ID 集合、autohome_brand_id→本地 brand_id、已有汽车之家车系 ID 集合。"""
    r = await session.execute(
        select(BasicdataBrand.autohome_brand_id, BasicdataBrand.brand_id).where(
            BasicdataBrand.autohome_brand_id.isnot(None)
        )
    )
    brand_autohome_to_local: Dict[int, int] = {}
    for aid, lid in r.all():
        if aid is None or lid is None:
            continue
        brand_autohome_to_local[int(aid)] = int(lid)
    existing_brand_ids = set(brand_autohome_to_local.keys())

    r2 = await session.execute(
        select(BasicdataCarSeries.autohome_series_id).where(
            BasicdataCarSeries.autohome_series_id.isnot(None)
        )
    )
    existing_series_ids = {int(x) for x in r2.scalars().all() if x is not None}
    return existing_brand_ids, brand_autohome_to_local, existing_series_ids


async def run_full_sync_job(job_id: int) -> None:
    factory = db_manager._platform_session_factory
    if factory is None:
        logger.error("platform session factory not ready, job %s", job_id)
        return

    payload: Dict[str, Any] = {
        "maxBrands": None,
        "delayMs": 400,
        "includeInactiveBrands": False,
        "fetchSpecs": True,
        "incrementalOnly": False,
    }

    async with factory() as session:
        job = await _load_job(session, job_id)
        if not job:
            return
        if job.payload_json:
            try:
                payload.update(json.loads(job.payload_json))
            except json.JSONDecodeError:
                pass
        job.status = "running"
        job.progress_pct = 2
        job.log_text = _append_log(job.log_text, "[full] 全量同步开始")
        await _commit_job(session, job)

    max_brands = payload.get("maxBrands")
    delay_ms = int(payload.get("delayMs") or 400)
    include_inactive = bool(payload.get("includeInactiveBrands"))
    fetch_specs = payload.get("fetchSpecs", True)
    if isinstance(fetch_specs, str):
        fetch_specs = fetch_specs.strip().lower() in ("1", "true", "yes")
    fetch_specs = bool(fetch_specs)

    incremental_only = payload.get("incrementalOnly", False)
    if isinstance(incremental_only, str):
        incremental_only = incremental_only.strip().lower() in ("1", "true", "yes")
    incremental_only = bool(incremental_only)

    try:
        status, brand_text = await fetch_with_retries(URL_GETBRAND, timeout_sec=60.0)
        if status != 200:
            raise RuntimeError(f"getbrand HTTP {status}")
        brands = parse_brand_list_json(brand_text)
        if not include_inactive:
            brands = [b for b in brands if int(b.get("state") or 0) == 1]
        if max_brands is not None:
            brands = brands[: max(0, int(max_brands))]

        total = len(brands)

        existing_brand_ids: Set[int] = set()
        brand_autohome_to_local: Dict[int, int] = {}
        existing_series_ids: Set[int] = set()

        async with factory() as session:
            job = await _load_job(session, job_id)
            if job:
                job.log_text = _append_log(
                    job.log_text,
                    f"[full] 待同步品牌数: {total}（含未在售={include_inactive}）",
                )
                if incremental_only:
                    eb, bm, es = await _preload_incremental_sets(session)
                    existing_brand_ids = eb
                    brand_autohome_to_local = bm
                    existing_series_ids = set(es)
                    job.log_text = _append_log(
                        job.log_text,
                        f"[full] 增量模式已开启：库内已有品牌 {len(existing_brand_ids)} 个，"
                        f"已有车系 {len(existing_series_ids)} 个（仅新增写入，不覆盖已有图片与字段）",
                    )
                await _commit_job(session, job)

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(60.0),
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "text/html,application/json,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
            },
        ) as client:
            for idx, b in enumerate(brands):
                bid = int(b["id"])
                bname = str(b.get("name") or "").strip() or f"品牌{bid}"
                _c = b.get("country")
                country = str(_c).strip() if _c else None
                logo_url = _normalize_media_url(str(b.get("logo") or ""))

                skip_brand_logo = incremental_only and bid in existing_brand_ids
                logo_rel: Optional[str] = None
                if not skip_brand_logo and logo_url:
                    img = await _download_bytes(client, logo_url)
                    if img:
                        logo_rel = _save_image_bytes(img, "brand_logo", logo_url)

                price_url = URL_PRICE_BRAND.format(brandid=bid)
                try:
                    pr, html = await fetch_with_retries(
                        price_url, timeout_sec=60.0
                    )
                    series_list = parse_series_from_price_html(html) if pr == 200 else []
                except Exception as e:
                    logger.exception("price page %s", bid)
                    series_list = []
                    async with factory() as session:
                        job = await _load_job(session, job_id)
                        if job:
                            job.log_text = _append_log(
                                job.log_text,
                                f"[full] 报价页失败 brand={bid}: {e!s}",
                            )
                            await _commit_job(session, job)

                async with factory() as session:
                    skip_brand_upsert = incremental_only and bid in existing_brand_ids
                    local_brand_id: Optional[int] = None
                    if skip_brand_upsert:
                        local_brand_id = brand_autohome_to_local.get(bid)
                        if local_brand_id is None:
                            rid = await session.execute(
                                select(BasicdataBrand.brand_id).where(
                                    BasicdataBrand.autohome_brand_id == bid
                                )
                            )
                            lid = rid.scalar_one_or_none()
                            if lid is not None:
                                local_brand_id = int(lid)
                                brand_autohome_to_local[bid] = local_brand_id
                                existing_brand_ids.add(bid)

                    if local_brand_id is None:
                        brand_row = await _upsert_brand(
                            session, bid, bname, country, logo_rel
                        )
                        await session.refresh(brand_row)
                        local_brand_id = brand_row.brand_id
                        if incremental_only:
                            existing_brand_ids.add(bid)
                            brand_autohome_to_local[bid] = local_brand_id

                    n_new_series = 0
                    n_skip_series = 0
                    for s in series_list:
                        sid = int(s["seriesid"])
                        if incremental_only and sid in existing_series_ids:
                            n_skip_series += 1
                            continue
                        sname = str(s.get("seriesname") or "").strip() or f"车系{sid}"
                        p = _fmt_price_wan(
                            s.get("seriesminprice"), s.get("seriesmaxprice")
                        )
                        simg_url = _normalize_media_url(str(s.get("seriesimg") or ""))
                        simg_rel: Optional[str] = None
                        if simg_url:
                            ib = await _download_bytes(client, simg_url)
                            if ib:
                                simg_rel = _save_image_bytes(
                                    ib, "car_series", simg_url
                                )
                        spec_snap: Optional[ParsedSeriesSpecs] = None
                        if fetch_specs:
                            spec_snap = await fetch_series_specs_snapshot(client, sid)
                        await _upsert_series(
                            session,
                            local_brand_id,
                            sid,
                            sname,
                            p,
                            simg_rel,
                            spec_snap,
                        )
                        if incremental_only:
                            existing_series_ids.add(sid)
                        n_new_series += 1
                        await asyncio.sleep(delay_ms / 1000.0)

                    job = await _load_job(session, job_id)
                    if job:
                        if incremental_only:
                            line = (
                                f"[full] ({idx+1}/{total}) 品牌 {bname} id={bid}，"
                                f"新增车系 {n_new_series}，跳过已存在 {n_skip_series}"
                            )
                        else:
                            line = (
                                f"[full] ({idx+1}/{total}) 品牌 {bname} id={bid}，"
                                f"写入车系 {n_new_series} 条"
                            )
                        job.log_text = _append_log(job.log_text, line)
                        job.progress_pct = max(
                            3,
                            min(
                                97,
                                3 + int(94 * (idx + 1) / max(total, 1)),
                            ),
                        )
                    await session.commit()

                await asyncio.sleep(delay_ms / 1000.0)

        async with factory() as session:
            job = await _load_job(session, job_id)
            if job:
                job.status = "success"
                job.progress_pct = 100
                job.error_message = None
                job.log_text = _append_log(job.log_text, "[full] 全量同步完成")
                await _commit_job(session, job)

    except Exception as e:
        logger.exception("full sync job %s", job_id)
        async with factory() as session:
            job = await _load_job(session, job_id)
            if job:
                job.status = "failed"
                job.progress_pct = 100
                job.error_message = str(e)[:2000]
                job.log_text = _append_log(job.log_text, f"[full] 失败: {e!s}")
                await _commit_job(session, job)


async def schedule_full_sync_job(job_id: int) -> None:
    asyncio.create_task(run_full_sync_job(job_id))
