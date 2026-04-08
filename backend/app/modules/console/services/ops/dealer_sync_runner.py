"""
汽车之家经销商同步：调用汽车之家内部 JSON API 获取经销商列表，再抓取详情页获取坐标。

流程：
  1. 调用城市列表 API 获取全国所有城市
  2. 按城市调用经销商列表 API（JSON，支持 pageIndex 分页）
  3. 对新增经销商抓取详情页（NUXT SSR）获取经纬度坐标
  4. 增量写入 basicdata_dealer_info 表

列表 API: /api/dealerlq/dealerlist/list/listPCDealers
城市 API: /api/dealerlq/car/area/groupByCityByLetter
详情页坐标存储在 window.__NUXT__ IIFE 的 pinia.app.dealerInfo 中。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.modules.console.models.basicdata.basicdata_dealer_info import (
    BasicdataDealerInfo,
)
from app.modules.console.models.ops.autohome_sync_job import AutohomeSyncJob
from app.modules.console.services.ops.autohome_crawl_runner import (
    DEFAULT_USER_AGENT,
    _append_log,
)

logger = logging.getLogger(__name__)

DEALER_BASE_URL = "https://dealernew.autohome.com.cn"
CITY_API = f"{DEALER_BASE_URL}/api/dealerlq/car/area/groupByCityByLetter?_appId=dealer&_encoding=utf8"
DEALER_LIST_API = f"{DEALER_BASE_URL}/api/dealerlq/dealerlist/list/listPCDealers"
PAGE_SIZE = 20


# ---------------------------------------------------------------------------
# NUXT payload parser (仅用于详情页坐标提取)
# ---------------------------------------------------------------------------


def _parse_nuxt_payload(html: str) -> Optional[Dict[str, Any]]:
    """从 HTML 中提取 window.__NUXT__ IIFE 并解析参数映射表。"""
    idx = html.find("window.__NUXT__=")
    if idx < 0:
        return None

    nuxt_start = idx + len("window.__NUXT__=")
    script_end = html.find("</script>", nuxt_start)
    if script_end < 0:
        return None
    payload = html[nuxt_start:script_end]

    param_match = re.match(r"\(function\(([^)]+)\)", payload)
    if not param_match:
        return None
    params = param_match.group(1).split(",")

    param_end = payload.find("){", 1)
    if param_end < 0:
        return None
    body_start = param_end + 1
    brace_depth = 0
    in_string = False
    i = body_start
    func_body_close = -1

    while i < len(payload):
        c = payload[i]
        if in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == "{":
            brace_depth += 1
        elif c == "}":
            brace_depth -= 1
            if brace_depth == 0:
                func_body_close = i
                break
        i += 1

    if func_body_close < 0:
        return None

    body = payload[body_start : func_body_close + 1]

    args_open = payload.find("(", func_body_close)
    if args_open < 0:
        return None
    args_str = payload[args_open + 1 : -1]

    args: List[Any] = []
    j = 0
    current: List[str] = []
    in_s = False
    obj_depth = 0
    while j < len(args_str):
        ch = args_str[j]
        if in_s:
            current.append(ch)
            if ch == "\\" and j + 1 < len(args_str):
                current.append(args_str[j + 1])
                j += 2
                continue
            if ch == '"':
                in_s = False
            j += 1
            continue
        if ch == '"':
            in_s = True
            current.append(ch)
            j += 1
            continue
        if ch == "{":
            obj_depth += 1
            current.append(ch)
            j += 1
            continue
        if ch == "}":
            obj_depth -= 1
            current.append(ch)
            j += 1
            continue
        if ch == "," and obj_depth == 0:
            args.append("".join(current).strip())
            current = []
            j += 1
            continue
        current.append(ch)
        j += 1
    if current:
        args.append("".join(current).strip())

    mapping: Dict[str, Any] = {}
    for k, p in enumerate(params):
        if k < len(args):
            raw = args[k]
            if isinstance(raw, str) and raw.startswith('"') and raw.endswith('"'):
                mapping[p] = raw[1:-1].replace("\\u002F", "/")
            elif raw == "true":
                mapping[p] = True
            elif raw == "false":
                mapping[p] = False
            elif raw in ("null", "void 0"):
                mapping[p] = None
            elif isinstance(raw, str) and raw.startswith("{"):
                mapping[p] = {}
            else:
                try:
                    mapping[p] = int(raw) if "." not in str(raw) else float(raw)
                except (ValueError, TypeError):
                    mapping[p] = raw

    return {"params": params, "mapping": mapping, "body": body}


def _resolve(mapping: Dict[str, Any], var_or_literal: str) -> Any:
    """将 NUXT 变量名解析为实际值；若已是字面量则直接返回。"""
    if var_or_literal in mapping:
        return mapping[var_or_literal]
    try:
        return int(var_or_literal)
    except ValueError:
        pass
    try:
        return float(var_or_literal)
    except ValueError:
        pass
    return var_or_literal


# ---------------------------------------------------------------------------
# Detail page parser (坐标提取)
# ---------------------------------------------------------------------------


def parse_dealer_detail_nuxt(html: str) -> Dict[str, Any]:
    """解析详情页 NUXT 数据，返回坐标、品牌、名称、地址。"""
    result: Dict[str, Any] = {
        "main_brand": "",
        "longitude": None,
        "latitude": None,
        "name": "",
        "address": "",
    }

    parsed = _parse_nuxt_payload(html)
    if not parsed:
        return result

    mapping = parsed["mapping"]
    body = parsed["body"]

    m = re.search(r"longitude:(\w+),latitude:(\w+)", body)
    if m:
        lng = _resolve(mapping, m.group(1))
        lat = _resolve(mapping, m.group(2))
        try:
            lng_f = float(lng)
            lat_f = float(lat)
            if 73 < lng_f < 136 and 3 < lat_f < 54:
                result["longitude"] = lng_f
                result["latitude"] = lat_f
        except (ValueError, TypeError):
            pass

    m = re.search(r'brandName:"([^"]*)"', body)
    if m:
        result["main_brand"] = m.group(1)

    m = re.search(r"dealerName:(\w+)", body)
    if m:
        name = _resolve(mapping, m.group(1))
        if isinstance(name, str) and len(name) <= 100:
            result["name"] = name

    m = re.search(r'address:"([^"]{5,})"', body)
    if m:
        result["address"] = m.group(1)

    return result


# ---------------------------------------------------------------------------
# JSON API helpers
# ---------------------------------------------------------------------------


async def _fetch_cities(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """调用汽车之家城市列表 API，返回 [{cityId, cityName, cityPinYin}, ...]。"""
    resp = await client.get(CITY_API)
    data = resp.json()
    cities: List[Dict[str, Any]] = []
    if data.get("returncode") == 0 and data.get("result"):
        for group in data["result"]:
            for city in group.get("cities", []):
                cities.append(city)
    return cities


async def _fetch_dealer_page(
    client: httpx.AsyncClient,
    city_pinyin: str,
    city_id: int,
    page_index: int,
) -> Dict[str, Any]:
    """调用经销商列表 API 获取一页数据，返回原始 JSON result。"""
    params = {
        "_appId": "dealer",
        "_encoding": "utf8",
        "cityPinyin": city_pinyin,
        "countyId": 0,
        "brandId": 0,
        "factoryId": 0,
        "pageIndex": page_index,
        "kindId": 0,
        "orderType": 0,
        "isSales": 0,
        "cityId": city_id,
        "pageSize": PAGE_SIZE,
    }
    resp = await client.get(DEALER_LIST_API, params=params)
    data = resp.json()
    if data.get("returncode") == 0 and data.get("result"):
        return data["result"]
    return {"rowcount": 0, "pagecount": 0, "pageindex": page_index, "list": []}




# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


async def _load_job(session: AsyncSession, job_id: int) -> Optional[AutohomeSyncJob]:
    r = await session.execute(
        select(AutohomeSyncJob).where(AutohomeSyncJob.job_id == job_id)
    )
    return r.scalar_one_or_none()


async def _commit_job(session: AsyncSession, job: AutohomeSyncJob) -> None:
    await session.flush()
    await session.commit()


async def _preload_existing_dealer_ids(session: AsyncSession) -> Set[int]:
    """返回已有的 autohome_dealer_id 集合。"""
    r = await session.execute(
        select(BasicdataDealerInfo.autohome_dealer_id).where(
            BasicdataDealerInfo.autohome_dealer_id.isnot(None)
        )
    )
    return {int(x) for x in r.scalars().all() if x is not None}


async def _upsert_dealer(
    session: AsyncSession,
    autohome_dealer_id: int,
    dealer_name: str,
    dealer_type: str,
    main_brand: str,
    province: str,
    city: str,
    address_detail: str,
    longitude: Optional[float],
    latitude: Optional[float],
) -> BasicdataDealerInfo:
    r = await session.execute(
        select(BasicdataDealerInfo).where(
            BasicdataDealerInfo.autohome_dealer_id == autohome_dealer_id
        )
    )
    row = r.scalar_one_or_none()
    if row:
        row.dealer_name = dealer_name
        row.dealer_type = dealer_type
        if main_brand:
            row.main_brand = main_brand
        row.province = province
        row.city = city
        if address_detail:
            row.address_detail = address_detail
        if longitude is not None:
            row.longitude = longitude
        if latitude is not None:
            row.latitude = latitude
        await session.flush()
        return row

    row = BasicdataDealerInfo(
        autohome_dealer_id=autohome_dealer_id,
        dealer_name=dealer_name,
        dealer_type=dealer_type,
        main_brand=main_brand or "未知",
        province=province,
        city=city,
        address_detail=address_detail or "待补充",
        longitude=longitude,
        latitude=latitude,
    )
    session.add(row)
    await session.flush()
    return row


# ---------------------------------------------------------------------------
# Main sync flow
# ---------------------------------------------------------------------------


async def _fetch_page(client: httpx.AsyncClient, url: str) -> Tuple[int, str]:
    """带重试的 GET 请求。"""
    last_exc: Optional[Exception] = None
    for attempt in range(1, 4):
        try:
            resp = await client.get(url)
            return resp.status_code, resp.text or ""
        except Exception as e:
            last_exc = e
            logger.warning("dealer fetch attempt %s failed for %s: %s", attempt, url, e)
            if attempt < 3:
                await asyncio.sleep(1.5 * attempt)
    raise last_exc  # type: ignore[misc]


async def run_dealer_sync_job(job_id: int) -> None:
    factory = db_manager._platform_session_factory
    if factory is None:
        logger.error("platform session factory not ready, job %s", job_id)
        return

    payload: Dict[str, Any] = {
        "maxCities": None,
        "delayMs": 400,
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
        job.progress_pct = 1
        job.log_text = _append_log(job.log_text, "[dealer] 经销商同步开始")
        await _commit_job(session, job)

    max_cities = payload.get("maxCities")
    delay_ms = int(payload.get("delayMs") or 400)

    total_new = 0
    total_skip = 0

    try:
        # 预加载已有经销商 ID
        existing_ids: Set[int] = set()
        async with factory() as session:
            existing_ids = await _preload_existing_dealer_ids(session)

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(60.0),
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "application/json,text/html,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
            },
        ) as client:
            # 从 API 获取全部城市
            try:
                all_cities = await _fetch_cities(client)
            except Exception as e:
                logger.exception("failed to fetch city list")
                async with factory() as session:
                    job = await _load_job(session, job_id)
                    if job:
                        job.status = "failed"
                        job.progress_pct = 100
                        job.error_message = f"获取城市列表失败: {e!s}"
                        job.log_text = _append_log(
                            job.log_text, f"[dealer] 获取城市列表失败: {e!s}"
                        )
                        await _commit_job(session, job)
                return

            cities = list(all_cities)
            if max_cities is not None and int(max_cities) > 0:
                cities = cities[: int(max_cities)]

            total_cities = len(cities)

            async with factory() as session:
                job = await _load_job(session, job_id)
                if job:
                    job.log_text = _append_log(
                        job.log_text,
                        f"[dealer] 待同步城市数: {total_cities}，库内已有经销商 {len(existing_ids)} 个",
                    )
                    await _commit_job(session, job)

            for city_idx, city_info in enumerate(cities):
                city_name = city_info["cityName"]
                city_pinyin = city_info["cityPinYin"]
                city_id = city_info["cityId"]
                city_new = 0
                city_skip = 0

                # 获取第一页，确定总页数
                try:
                    page_result = await _fetch_dealer_page(
                        client, city_pinyin, city_id, 1
                    )
                except Exception as e:
                    logger.exception("dealer list API %s", city_pinyin)
                    async with factory() as session:
                        job = await _load_job(session, job_id)
                        if job:
                            job.log_text = _append_log(
                                job.log_text,
                                f"[dealer] 城市 {city_name} API 请求失败: {e!s}",
                            )
                            await _commit_job(session, job)
                    continue

                total_pages = page_result.get("pagecount", 0)
                if total_pages == 0:
                    continue

                for page_num in range(1, total_pages + 1):
                    if page_num > 1:
                        try:
                            page_result = await _fetch_dealer_page(
                                client, city_pinyin, city_id, page_num
                            )
                        except Exception:
                            break
                        await asyncio.sleep(delay_ms / 1000.0)

                    dealers = page_result.get("list", [])
                    if not dealers:
                        break

                    for d in dealers:
                        did = d.get("dealerId")
                        if not did:
                            continue
                        did = int(did)
                        if did in existing_ids:
                            city_skip += 1
                            continue

                        d_name = d.get("mainDealerSimpleName", "")
                        d_type = d.get("kindStr", "4S店")
                        base = d.get("dealerInfoBaseOut") or {}
                        d_address = base.get("address", "")

                        # 抓取详情页获取坐标和主营品牌
                        detail_url = f"{DEALER_BASE_URL}/{did}/"
                        detail_info: Dict[str, Any] = {
                            "main_brand": "",
                            "longitude": None,
                            "latitude": None,
                        }
                        try:
                            ds, dhtml = await _fetch_page(client, detail_url)
                            if ds == 200:
                                detail_info = parse_dealer_detail_nuxt(dhtml)
                                if not d_name and detail_info.get("name"):
                                    d_name = detail_info["name"]
                                if not d_address and detail_info.get("address"):
                                    d_address = detail_info["address"]
                        except Exception as e:
                            logger.debug("dealer detail %s: %s", did, e)

                        await asyncio.sleep(delay_ms / 1000.0)

                        if not d_name:
                            d_name = f"经销商{did}"

                        async with factory() as session:
                            await _upsert_dealer(
                                session,
                                autohome_dealer_id=did,
                                dealer_name=d_name,
                                dealer_type=d_type,
                                main_brand=detail_info.get("main_brand", "") or "",
                                province="",
                                city=city_name,
                                address_detail=d_address,
                                longitude=detail_info.get("longitude"),
                                latitude=detail_info.get("latitude"),
                            )
                            await session.commit()

                        existing_ids.add(did)
                        city_new += 1

                total_new += city_new
                total_skip += city_skip

                async with factory() as session:
                    job = await _load_job(session, job_id)
                    if job:
                        job.log_text = _append_log(
                            job.log_text,
                            f"[dealer] ({city_idx+1}/{total_cities}) "
                            f"{city_name}({city_pinyin}) 共 {total_pages} 页，"
                            f"新增 {city_new}，跳过已存在 {city_skip}",
                        )
                        job.progress_pct = max(
                            2,
                            min(97, 2 + int(95 * (city_idx + 1) / max(total_cities, 1))),
                        )
                        await _commit_job(session, job)

                await asyncio.sleep(delay_ms / 1000.0)

        # 完成
        async with factory() as session:
            job = await _load_job(session, job_id)
            if job:
                job.status = "success"
                job.progress_pct = 100
                job.error_message = None
                job.log_text = _append_log(
                    job.log_text,
                    f"[dealer] 同步完成：共新增 {total_new}，跳过 {total_skip}",
                )
                await _commit_job(session, job)

    except Exception as e:
        logger.exception("dealer sync job %s", job_id)
        async with factory() as session:
            job = await _load_job(session, job_id)
            if job:
                job.status = "failed"
                job.progress_pct = 100
                job.error_message = str(e)[:2000]
                job.log_text = _append_log(job.log_text, f"[dealer] 失败: {e!s}")
                await _commit_job(session, job)


async def schedule_dealer_sync_job(job_id: int) -> None:
    asyncio.create_task(run_dealer_sync_job(job_id))
