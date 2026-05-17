"""
批量生成「运单 + 货物明细」Mock 数据（biz_waybill + biz_waybill_cargo）

与前端 business/waybill 新建表单字段对齐；以下维度**均从当前租户库随机抽取**：
- 客户：biz_customer（未删除、状态正常）
- 商品车品牌/车型：biz_vehicle_brand + biz_vehicle_series（按 brand_id 关联）
- 收车门店：biz_dealer
- 出发地/目的地：biz_region（未删除、状态正常；展示名为自底向上拼接省/市/区链）

写入策略：直接 ORM 插入（与 API 不同），并设置 freight_source=1、freight_amount 随机，
避免租户配置 waybill.freight_calc_mode=auto_required 时因无运价而创建失败。
created_by 置 NULL（模型允许）。

路径：backend/scripts/mockdata/mock_tenant_waybills.py

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_waybills.py --tenant-code demo --count 20
  python scripts/mockdata/mock_tenant_waybills.py --tenant-code demo --count 5 --dry-run
  python scripts/mockdata/mock_tenant_waybills.py --tenant-code demo --count 10 --cargo-lines 2
  python scripts/mockdata/mock_tenant_waybills.py --tenant-code demo --count 30 \\
    --date-from 2026-05-01 --date-to 2026-05-20

时间范围：省略 --date-from/--date-to 时，计划下发时间随机落在「当天」自然日；
二者同时指定时，随机落在该闭区间 [date-from 00:00:00, date-to 23:59:59]。

可选：--seed、--cargo-lines（每单货物行数，默认 1~2 随机）、--fetch-limit（每类主数据最多拉取条数，默认 800）
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.partner.customer import Customer  # noqa: E402
from app.modules.client.models.region.biz_region import BizRegion  # noqa: E402
from app.modules.client.models.vehicle_basic.biz_dealer import BizDealer  # noqa: E402
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import (  # noqa: E402
    BizVehicleBrand,
)
from app.modules.client.models.vehicle_basic.biz_vehicle_series import (  # noqa: E402
    BizVehicleSeries,
)
from app.modules.client.models.waybill.waybill import Waybill  # noqa: E402
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo  # noqa: E402


def _load_customers(session: Session, limit: int) -> list[tuple[int, str]]:
    rows = session.execute(
        select(Customer.id, Customer.customer_name).where(
            Customer.is_deleted == 0,
            Customer.status == 1,
        ).limit(limit)
    ).all()
    return [(int(r[0]), str(r[1])) for r in rows if r[0] is not None and r[1]]


def _load_brand_series_pairs(session: Session, limit: int) -> list[tuple[str, str]]:
    """(brand_name_cn, series_name) 列表。"""
    q = (
        select(BizVehicleBrand.brand_name_cn, BizVehicleSeries.series_name)
        .join(BizVehicleSeries, BizVehicleSeries.brand_id == BizVehicleBrand.brand_id)
        .limit(limit)
    )
    rows = session.execute(q).all()
    out: list[tuple[str, str]] = []
    for b, s in rows:
        if b and s:
            out.append((str(b).strip(), str(s).strip()))
    return out


def _load_dealers(session: Session, limit: int) -> list[BizDealer]:
    rows = session.execute(select(BizDealer).limit(limit)).scalars().all()
    return list(rows)


def _load_region_index(session: Session, limit: int) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """code -> {name, parent_code}；codes 为候选 code 列表（优先区县）。"""
    rows = session.execute(
        select(BizRegion.code, BizRegion.name, BizRegion.parent_code, BizRegion.level).where(
            BizRegion.is_deleted == 0,
            BizRegion.status == 1,
        ).limit(limit)
    ).all()
    by_code: dict[str, dict[str, Any]] = {}
    level3: list[str] = []
    other: list[str] = []
    for code, name, parent, level in rows:
        if not code or not name:
            continue
        by_code[str(code)] = {"name": str(name), "parent": str(parent) if parent else None}
        lv = int(level) if level is not None else 0
        if lv >= 3:
            level3.append(str(code))
        else:
            other.append(str(code))
    candidates = level3 if level3 else other
    return by_code, candidates


def _region_display_path(code: str, by_code: dict[str, dict[str, Any]]) -> str:
    parts: list[str] = []
    cur: Optional[str] = code
    seen: set[str] = set()
    while cur and cur in by_code and cur not in seen:
        seen.add(cur)
        parts.append(by_code[cur]["name"])
        p = by_code[cur]["parent"]
        cur = str(p) if p else None
    return "/".join(reversed(parts))[:255]


def _pick_two_distinct_codes(rng: random.Random, codes: list[str]) -> tuple[str, str]:
    if len(codes) < 2:
        raise RuntimeError(
            "biz_region 可用行政区不足 2 条，无法随机出发地/目的地；请同步或导入地区数据。"
        )
    a, b = rng.sample(codes, 2)
    return a, b


def _parse_iso_date(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def _time_window(
    date_from: Optional[str],
    date_to: Optional[str],
) -> tuple[datetime, datetime]:
    """返回 [含起点当日 0 点, 含终点当日最后一秒]。"""
    if (date_from is None) ^ (date_to is None):
        raise ValueError("--date-from 与 --date-to 必须同时提供或同时省略")
    if date_from is None:
        d = datetime.now().date()
        start = datetime.combine(d, time.min)
        end = datetime.combine(d, time(23, 59, 59))
    else:
        df = _parse_iso_date(date_from)
        dt = _parse_iso_date(date_to)
        if df > dt:
            raise ValueError("--date-from 不能晚于 --date-to")
        start = datetime.combine(df, time.min)
        end = datetime.combine(dt, time(23, 59, 59))
    return start, end


def _random_dt_in_window(
    rng: random.Random, window_start: datetime, window_end: datetime
) -> datetime:
    span_s = int((window_end - window_start).total_seconds())
    if span_s < 0:
        raise ValueError("时间窗口无效")
    off = rng.randint(0, span_s) if span_s > 0 else 0
    return (window_start + timedelta(seconds=off)).replace(microsecond=0)


def _new_waybill_no(
    session: Session, rng: random.Random, seq: int, ref: datetime
) -> str:
    for _ in range(80):
        wn = f"YD{ref.strftime('%Y%m%d%H%M%S')}{rng.randint(1000, 9999)}{seq % 10000}"
        wn = wn[:50]
        taken = session.execute(
            select(Waybill.id).where(Waybill.waybill_no == wn, Waybill.is_deleted == 0)
        ).first()
        if not taken:
            return wn
        seq += 17
    raise RuntimeError("无法生成唯一运单号")


def generate_waybills(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
    fetch_limit: int,
    cargo_lines_min: int,
    cargo_lines_max: int,
    window_start: datetime,
    window_end: datetime,
) -> tuple[int, int]:
    customers = _load_customers(session, fetch_limit)
    brand_series = _load_brand_series_pairs(session, fetch_limit)
    dealers = _load_dealers(session, fetch_limit)
    by_region, region_codes = _load_region_index(session, fetch_limit * 2)

    missing: list[str] = []
    if not customers:
        missing.append("客户(biz_customer)")
    if not brand_series:
        missing.append("品牌+车型(biz_vehicle_brand/series)")
    if not dealers:
        missing.append("经销商(biz_dealer)")
    if len(region_codes) < 2:
        missing.append("行政区(biz_region)至少2条")
    if missing:
        raise RuntimeError("以下主数据为空或不足，无法生成运单：" + "、".join(missing))

    waybills_n = 0
    cargoes_n = 0

    for i in range(count):
        cust_id, cust_name = rng.choice(customers)
        o_code, d_code = _pick_two_distinct_codes(rng, region_codes)
        origin_txt = _region_display_path(o_code, by_region)
        dest_txt = _region_display_path(d_code, by_region)
        dealer = rng.choice(dealers)
        dealer_addr = " ".join(
            x for x in (dealer.province, dealer.city, dealer.address_detail) if x
        )[:500]

        plan_t = _random_dt_in_window(rng, window_start, window_end)
        load_t = plan_t + timedelta(hours=rng.randint(2, 24))
        deliver_t = load_t + timedelta(days=rng.randint(1, 10))

        n_lines = rng.randint(cargo_lines_min, cargo_lines_max)
        cargo_specs: list[tuple[str, str, str]] = []
        for line_idx in range(n_lines):
            b, m = rng.choice(brand_series)
            vin = (
                f"ZMOCK{int(plan_t.timestamp()) % 10**7:07d}"
                f"{i % 100000:05d}{line_idx:02d}{rng.randint(0, 10**6 - 1):06d}"
            )
            cargo_specs.append((b, m, vin))

        brand_m, model_m, qty_sum = (
            cargo_specs[0][0],
            cargo_specs[0][1],
            len(cargo_specs),
        )

        freight_amt = Decimal(str(round(rng.uniform(500.0, 25000.0), 2)))
        waybill_no = _new_waybill_no(session, rng, i, plan_t)
        remark = (
            f"[mockdata] waybill ts={plan_t.strftime('%Y-%m-%d %H:%M:%S')} "
            f"customer_id={cust_id}"
        )

        if dry_run:
            print(
                f"[dry-run] {waybill_no} plan_issue={plan_t.strftime('%Y-%m-%d %H:%M')} "
                f"cust={cust_name[:20]} origin={origin_txt[:24]} "
                f"dest={dest_txt[:24]} dealer={dealer.dealer_name[:20]} "
                f"cargoes={n_lines} freight={freight_amt}"
            )
            waybills_n += 1
            cargoes_n += n_lines
            continue

        wb = Waybill(
            waybill_no=waybill_no,
            customer_id=cust_id,
            customer_name=cust_name[:100],
            origin=origin_txt or None,
            origin_code=o_code[:20],
            destination=dest_txt or None,
            destination_code=d_code[:20],
            vehicle_brand=brand_m[:100] if brand_m else None,
            vehicle_model=model_m[:100] if model_m else None,
            quantity=qty_sum,
            plan_issue_time=plan_t,
            required_load_time=load_t,
            required_deliver_time=deliver_t,
            dealer_name=dealer.dealer_name[:200],
            dealer_contact=("门店联系人" + str(rng.randint(100, 999)))[:50],
            dealer_phone=f"1{rng.randint(3, 9)}{(int(plan_t.timestamp()) + i) % 10**9:09d}"[:20],
            dealer_address=dealer_addr,
            freight_amount=str(freight_amt),
            freight_source=1,
            contract_id=None,
            rate_id=None,
            status=0,
            remark=remark[:2000] if len(remark) > 2000 else remark,
            created_by=None,
            created_at=plan_t,
            updated_at=plan_t,
        )
        session.add(wb)
        session.flush()

        for idx, (vb, vm, vin) in enumerate(cargo_specs):
            session.add(
                WaybillCargo(
                    waybill_id=int(wb.id),
                    sort_order=idx,
                    vehicle_brand=vb[:100],
                    vehicle_model=vm[:100],
                    vin=vin[:50],
                    quantity=1,
                    created_at=plan_t,
                    updated_at=plan_t,
                )
            )
        session.flush()
        waybills_n += 1
        cargoes_n += n_lines

    if not dry_run:
        session.commit()
    return waybills_n, cargoes_n


def main() -> None:
    parser = argparse.ArgumentParser(
        description="租户库批量插入运单 Mock（主数据从库内随机选取）"
    )
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument("--count", type=int, default=15, help="运单条数")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="仅打印摘要，不写库")
    parser.add_argument(
        "--fetch-limit",
        type=int,
        default=800,
        help="客户/品牌车系/经销商/地区每类最多加载条数（用于随机池）",
    )
    parser.add_argument(
        "--cargo-lines",
        type=int,
        default=0,
        metavar="N",
        help="每单固定货物行数（>=1）；默认 0 表示每单随机 1~2 行",
    )
    parser.add_argument(
        "--date-from",
        default=None,
        metavar="YYYY-MM-DD",
        help="与 --date-to 成对使用：计划下发时间随机落在此日期区间内；均省略则为当天",
    )
    parser.add_argument(
        "--date-to",
        default=None,
        metavar="YYYY-MM-DD",
        help="与 --date-from 成对使用；闭区间含首尾两日全天",
    )
    args = parser.parse_args()

    fetch_limit = max(50, min(5000, args.fetch_limit))
    if args.cargo_lines > 0:
        lo = hi = max(1, min(20, args.cargo_lines))
    else:
        lo, hi = 1, 2

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)
    try:
        w_start, w_end = _time_window(args.date_from, args.date_to)
    except ValueError as e:
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(2)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        nw, nc = generate_waybills(
            session,
            args.count,
            rng,
            dry_run=args.dry_run,
            fetch_limit=fetch_limit,
            cargo_lines_min=lo,
            cargo_lines_max=hi,
            window_start=w_start,
            window_end=w_end,
        )

    action = "预览" if args.dry_run else "已写入"
    win_desc = (
        f"{w_start.strftime('%Y-%m-%d')} ~ {w_end.strftime('%Y-%m-%d')}"
        if args.date_from
        else f"当天 {w_start.strftime('%Y-%m-%d')}"
    )
    print(
        f"[OK] 租户 {args.tenant_code}：{action} {nw} 张运单，{nc} 条货物明细。"
        f" 计划下发时间窗口：{win_desc}。"
    )


if __name__ == "__main__":
    main()
