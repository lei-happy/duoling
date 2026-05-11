"""
批量生成「运价合同 + 运价明细」Mock 数据（biz_freight_contract + biz_freight_rate）

字段与模型 `FreightContract` / `FreightRate` 一致：
- 合同：contract_no（唯一）、contract_name、customer_id、customer_name、effective_date、
  expiry_date、status(0/1/2)、remark
- 运价：contract_id、customer_id、origin/origin_code、destination/destination_code、
  vehicle_brand、vehicle_model（选填）、billing_mode(0/1/2)、distance_km（单公里时）、
  unit_price、price_type、effective_date、expiry_date（选填）、status(默认启用)

主数据从当前租户库随机抽取（与 mock_tenant_waybills 一致思路）：
- 客户：biz_customer（未删除、状态正常）
- 出发地/目的地：biz_region（编码 + 展示名为省/市/区链）
- 品牌/车型：biz_vehicle_brand + biz_vehicle_series（可选填充运价行）

路径：backend/scripts/mockdata/mock_tenant_freight_contracts.py

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_freight_contracts.py --tenant-code demo --count 10
  python scripts/mockdata/mock_tenant_freight_contracts.py --tenant-code demo --count 3 --dry-run
  python scripts/mockdata/mock_tenant_freight_contracts.py --tenant-code demo --count 5 --rates-min 1 --rates-max 8 --seed 42

可选：--rates-min / --rates-max（每条合同下运价行数，默认 2~6）、--fetch-limit
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.billing.freight_contract import FreightContract  # noqa: E402
from app.modules.client.models.billing.freight_rate import FreightRate  # noqa: E402
from app.modules.client.models.partner.customer import Customer  # noqa: E402
from app.modules.client.models.region.biz_region import BizRegion  # noqa: E402
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import (  # noqa: E402
    BizVehicleBrand,
)
from app.modules.client.models.vehicle_basic.biz_vehicle_series import (  # noqa: E402
    BizVehicleSeries,
)


def _load_customers(session: Session, limit: int) -> list[tuple[int, str]]:
    rows = session.execute(
        select(Customer.id, Customer.customer_name).where(
            Customer.is_deleted == 0,
            Customer.status == 1,
        ).limit(limit)
    ).all()
    return [(int(r[0]), str(r[1])) for r in rows if r[0] is not None and r[1]]


def _load_brand_series_pairs(session: Session, limit: int) -> list[tuple[str, str]]:
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


def _load_region_index(session: Session, limit: int) -> tuple[dict[str, dict[str, Any]], list[str]]:
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


def _new_contract_no(session: Session, rng: random.Random, seq: int) -> str:
    for _ in range(80):
        cn = (
            f"HT{datetime.now().strftime('%Y%m%d%H%M%S')}"
            f"{rng.randint(1000, 9999)}{seq % 10000}"
        )
        cn = cn[:100]
        taken = session.execute(
            select(FreightContract.id).where(
                FreightContract.contract_no == cn,
                FreightContract.is_deleted == 0,
            )
        ).first()
        if not taken:
            return cn
        seq += 17
    raise RuntimeError("无法生成唯一合同编号")


def _random_contract_status(rng: random.Random) -> int:
    return int(rng.choices([0, 1, 2], weights=[2, 5, 2], k=1)[0])


def _contract_date_range(rng: random.Random) -> tuple[date, date]:
    today = date.today()
    start_off = rng.randint(-60, 30)
    eff = today + timedelta(days=start_off)
    span = rng.randint(180, 540)
    exp = eff + timedelta(days=span)
    if exp <= eff:
        exp = eff + timedelta(days=30)
    return eff, exp


def generate_contracts_and_rates(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
    fetch_limit: int,
    rates_min: int,
    rates_max: int,
) -> tuple[int, int]:
    customers = _load_customers(session, fetch_limit)
    brand_series = _load_brand_series_pairs(session, fetch_limit)
    by_region, region_codes = _load_region_index(session, fetch_limit * 2)

    missing: list[str] = []
    if not customers:
        missing.append("客户(biz_customer)")
    if len(region_codes) < 2:
        missing.append("行政区(biz_region)至少2条")
    if missing:
        raise RuntimeError("以下主数据为空或不足，无法生成合同/运价：" + "、".join(missing))

    contracts_n = 0
    rates_n = 0
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i in range(count):
        cust_id, cust_name = rng.choice(customers)
        contract_no = _new_contract_no(session, rng, i)
        eff_d, exp_d = _contract_date_range(rng)
        st = _random_contract_status(rng)
        name_short = (cust_name[:24] + "…") if len(cust_name) > 24 else cust_name
        contract_name = f"[mockdata]运价合同-{name_short}-{i + 1:04d}"
        remark = f"[mockdata] freight contract ts={ts} seed_contract={i}"

        n_rates = rng.randint(rates_min, rates_max)

        if dry_run:
            print(
                f"[dry-run] {contract_no} {contract_name[:40]} "
                f"cust_id={cust_id} status={st} valid={eff_d}~{exp_d} rates={n_rates}"
            )
            contracts_n += 1
            rates_n += n_rates
            continue

        contract = FreightContract(
            contract_no=contract_no,
            contract_name=contract_name[:200],
            customer_id=cust_id,
            customer_name=cust_name[:100],
            effective_date=eff_d,
            expiry_date=exp_d,
            status=st,
            remark=remark[:2000] if len(remark) > 2000 else remark,
        )
        session.add(contract)
        session.flush()
        contracts_n += 1
        cid = int(contract.id)

        for r in range(n_rates):
            o_code, d_code = _pick_two_distinct_codes(rng, region_codes)
            origin_txt = _region_display_path(o_code, by_region)
            dest_txt = _region_display_path(d_code, by_region)
            billing_mode = int(rng.choices([0, 1, 2], weights=[5, 3, 2], k=1)[0])
            distance_km: Optional[Decimal] = None
            if billing_mode == 1:
                distance_km = Decimal(str(round(rng.uniform(50.0, 1200.0), 2)))
            if billing_mode == 0:
                unit_price = Decimal(str(round(rng.uniform(800.0, 8000.0), 2)))
            elif billing_mode == 1:
                unit_price = Decimal(str(round(rng.uniform(1.5, 8.5), 2)))
            else:
                unit_price = Decimal(str(round(rng.uniform(2000.0, 35000.0), 2)))

            price_type = int(rng.choices([0, 1], weights=[8, 2], k=1)[0])
            vb: Optional[str] = None
            vm: Optional[str] = None
            if billing_mode != 2 and brand_series:
                if rng.random() < 0.65:
                    vb, vm = rng.choice(brand_series)
                    vb = vb[:100]
                    vm = vm[:100]

            rate_eff: Optional[date] = None
            rate_exp: Optional[date] = None
            if rng.random() < 0.4:
                rate_eff = eff_d
                rate_exp = exp_d

            rate = FreightRate(
                contract_id=cid,
                customer_id=cust_id,
                origin=origin_txt,
                origin_code=o_code[:20],
                destination=dest_txt,
                destination_code=d_code[:20],
                vehicle_brand=vb,
                vehicle_model=vm,
                billing_mode=billing_mode,
                distance_km=distance_km,
                unit_price=unit_price,
                price_type=price_type,
                effective_date=rate_eff,
                expiry_date=rate_exp,
                status=1 if rng.random() < 0.9 else 0,
            )
            session.add(rate)
            rates_n += 1

        session.flush()

    if not dry_run:
        session.commit()
    return contracts_n, rates_n


def main() -> None:
    parser = argparse.ArgumentParser(
        description="向租户库批量插入运价合同及运价明细 Mock（biz_freight_contract / biz_freight_rate）"
    )
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="生成合同条数（每条下挂若干运价行）",
    )
    parser.add_argument("--rates-min", type=int, default=2, help="每合同最少运价行数")
    parser.add_argument("--rates-max", type=int, default=6, help="每合同最多运价行数")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="仅打印摘要，不写库")
    parser.add_argument(
        "--fetch-limit",
        type=int,
        default=800,
        help="客户/品牌/地区等主数据查询上限",
    )
    args = parser.parse_args()

    if args.rates_min < 0 or args.rates_max < args.rates_min:
        raise SystemExit("rates-min / rates-max 不合法")

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        c_n, r_n = generate_contracts_and_rates(
            session,
            args.count,
            rng,
            dry_run=args.dry_run,
            fetch_limit=args.fetch_limit,
            rates_min=args.rates_min,
            rates_max=args.rates_max,
        )

    action = "预览" if args.dry_run else "已写入"
    print(
        f"[OK] 租户 {args.tenant_code}：{action} 合同 {c_n} 条、运价 {r_n} 条 "
        f"（biz_freight_contract / biz_freight_rate）。"
    )


if __name__ == "__main__":
    main()
