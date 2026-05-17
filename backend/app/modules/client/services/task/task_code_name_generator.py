"""
任务单号 / 任务名称：按系统配置 JSON 生成；解析失败时回退到历史硬编码逻辑。
"""

from __future__ import annotations

import json
from datetime import date as ddate
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.task import Task
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.task.task import TaskCarrierInfo, TaskCreate


async def legacy_build_task_no(db: AsyncSession) -> str:
    """历史：T + yyyymmdd + 4 位当日序号。

    注意：扫描时 **不过滤** is_deleted —— 因为 task_no 的 UNIQUE 索引
    对软删行同样生效，已删除的单号仍占位，必须递增到未使用的序号。
    """
    today = ddate.today().strftime("%Y%m%d")
    prefix = f"T{today}"
    like = f"{prefix}%"
    res = await db.execute(
        select(Task.task_no).where(
            Task.task_no.like(like),
        )
    )
    rows = [r[0] for r in res.all()]
    max_n = 0
    plen = len(prefix)
    for tn in rows:
        if not tn or len(tn) <= plen:
            continue
        suf = tn[plen:]
        if suf.isdigit():
            max_n = max(max_n, int(suf))
    return f"{prefix}{(max_n + 1):04d}"


def legacy_default_task_name(data: TaskCreate) -> str:
    """历史：首段起止 + 计划装车时间简写"""
    parts: list[str] = []
    segs = list(data.segments or [])
    if segs:
        segs_sorted = sorted(segs, key=lambda s: s.segmentNo or 0)
        s0 = segs_sorted[0]
        a = (s0.fromLocation or "").strip()
        b = (s0.toLocation or "").strip()
        if a and b:
            parts.append(f"{a[:16]}-{b[:16]}")
        elif a or b:
            parts.append((a or b)[:32])
    dt = data.plannedLoadTime
    if dt is not None:
        if isinstance(dt, datetime):
            parts.append(dt.strftime("%m月%d日装车"))
        else:
            parts.append(str(dt)[:10])
    name = " ".join(parts) if parts else "运输任务"
    return name[:120]


def _escape_like(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _normalize_no_parts(raw: Any) -> Optional[List[dict]]:
    if not isinstance(raw, dict):
        return None
    parts = raw.get("parts")
    if not isinstance(parts, list):
        return None
    out: List[dict] = []
    for i in range(3):
        if i < len(parts) and isinstance(parts[i], dict):
            out.append(parts[i])
        else:
            out.append({"type": "none"})
    return out


def _render_no_part(p: dict, now: datetime) -> str:
    t = (p.get("type") or "none").lower()
    if t == "none":
        return ""
    if t == "prefix":
        v = p.get("value")
        return str(v) if v is not None else ""
    if t == "date":
        fmt = (p.get("format") or "YYYYMMDD").upper()
        if fmt == "YYYYMM":
            return now.strftime("%Y%m")
        return now.strftime("%Y%m%d")
    if t == "seq":
        return ""
    return ""


async def build_task_no(db: AsyncSession, raw_json: Optional[str]) -> str:
    if not raw_json or not str(raw_json).strip():
        return await legacy_build_task_no(db)
    try:
        obj = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        return await legacy_build_task_no(db)

    parts = _normalize_no_parts(obj)
    if not parts:
        return await legacy_build_task_no(db)

    seq_idx: Optional[int] = None
    for i, p in enumerate(parts):
        if (p.get("type") or "").lower() == "seq":
            seq_idx = i
            break
    if seq_idx is None:
        return await legacy_build_task_no(db)

    now = datetime.now()
    base_key = ""
    for p in parts[:seq_idx]:
        base_key += _render_no_part(p, now)

    seq_part = parts[seq_idx]
    digits = int(seq_part.get("digits") or 4)
    digits = max(1, min(6, digits))

    if not base_key:
        return await legacy_build_task_no(db)

    # 扫描时 **不过滤** is_deleted —— UNIQUE 索引对软删行同样生效
    esc = _escape_like(base_key)
    pattern = f"{esc}%"
    res = await db.execute(
        select(Task.task_no).where(
            Task.task_no.like(pattern, escape="\\"),
        )
    )
    rows = [r[0] for r in res.all()]

    tail = ""
    for p in parts[seq_idx + 1 :]:
        tail += _render_no_part(p, now)

    max_n = 0
    blen = len(base_key)
    tlen = len(tail)
    for tn in rows:
        if not tn or len(tn) <= blen + tlen:
            continue
        if not tn.startswith(base_key):
            continue
        # 末尾若有 tail（如 "-某客户"），需先剥掉
        body = tn[blen : len(tn) - tlen] if tail and tn.endswith(tail) else tn[blen:]
        if body.isdigit():
            max_n = max(max_n, int(body))
    next_n = max_n + 1
    suffix = str(next_n).zfill(digits)
    return f"{base_key}{suffix}{tail}"


def _sorted_segments(data: TaskCreate):
    segs = list(data.segments or [])
    return sorted(segs, key=lambda s: s.segmentNo or 0)


def _segment_route_od(data: TaskCreate) -> str:
    segs = _sorted_segments(data)
    if not segs:
        return ""
    s0 = segs[0]
    a = (s0.fromLocation or "").strip()
    b = (s0.toLocation or "").strip()
    if a and b:
        return f"{a[:16]}-{b[:16]}"
    if a or b:
        return (a or b)[:32]
    return ""


def _segment_route_origin(data: TaskCreate) -> str:
    segs = _sorted_segments(data)
    if not segs:
        return ""
    return (segs[0].fromLocation or "").strip()[:32]


def _segment_route_dest(data: TaskCreate) -> str:
    segs = _sorted_segments(data)
    if not segs:
        return ""
    return (segs[-1].toLocation or "").strip()[:32]


def _carrier_driver_plate(carrier: Optional[TaskCarrierInfo]) -> str:
    if not carrier:
        return ""
    name = (carrier.mainDriverName or "").strip()
    plate = (carrier.plateNumber or "").strip()
    if name and plate:
        return f"{name}/{plate}"[:64]
    if name:
        return name[:64]
    if plate:
        return plate[:32]
    return ""


def _carrier_company(carrier: Optional[TaskCarrierInfo]) -> str:
    if not carrier:
        return ""
    n = (carrier.carrierName or "").strip() or (
        carrier.carrierShortName or ""
    ).strip()
    return n[:64] if n else ""


def _planned_load_md(data: TaskCreate) -> str:
    dt = data.plannedLoadTime
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%m月%d日装车")
    return str(dt)[:10]


async def _vehicle_first_line(db: AsyncSession, data: TaskCreate) -> str:
    items = list(data.waybillItems or [])
    if not items:
        return ""
    first = items[0]
    wid = first.waybillCargoId
    res = await db.execute(
        select(WaybillCargo).where(
            WaybillCargo.id == int(wid),
            WaybillCargo.is_deleted == 0,
        )
    )
    cargo = res.scalar_one_or_none()
    if not cargo:
        return ""
    brand = (cargo.vehicle_brand or "").strip()
    model = (cargo.vehicle_model or "").strip()
    if brand and model:
        return f"{brand} {model}"[:64]
    if brand:
        return brand[:64]
    if model:
        return model[:64]
    return ""


def _normalize_name_parts(raw: Any) -> Optional[tuple]:
    if not isinstance(raw, dict):
        return None
    parts = raw.get("parts")
    if not isinstance(parts, list):
        return None
    joiner = raw.get("joiner")
    if not isinstance(joiner, str):
        joiner = " "
    out: List[dict] = []
    for i in range(3):
        if i < len(parts) and isinstance(parts[i], dict):
            out.append(parts[i])
        else:
            out.append({"kind": "none"})
    return joiner, out


async def build_task_name(
    db: AsyncSession,
    data: TaskCreate,
    raw_json: Optional[str],
) -> str:
    if not raw_json or not str(raw_json).strip():
        return legacy_default_task_name(data)
    try:
        obj = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        return legacy_default_task_name(data)

    parsed = _normalize_name_parts(obj)
    if not parsed:
        return legacy_default_task_name(data)
    joiner, parts = parsed

    carrier = data.carrier
    chunks: List[str] = []

    for p in parts:
        kind = (p.get("kind") or "none").lower()
        text = ""
        if kind == "none":
            text = ""
        elif kind == "route_od":
            text = _segment_route_od(data)
        elif kind == "route_origin":
            text = _segment_route_origin(data)
        elif kind == "route_dest":
            text = _segment_route_dest(data)
        elif kind == "vehicle_first":
            text = await _vehicle_first_line(db, data)
        elif kind == "carrier_driver_plate":
            text = _carrier_driver_plate(carrier)
        elif kind == "carrier_company":
            text = _carrier_company(carrier)
        elif kind == "planned_load_md":
            text = _planned_load_md(data)
        else:
            text = ""
        if text:
            chunks.append(text)

    name = joiner.join(chunks) if chunks else legacy_default_task_name(data)
    name = name.strip()
    if not name:
        name = legacy_default_task_name(data)
    return name[:120]
