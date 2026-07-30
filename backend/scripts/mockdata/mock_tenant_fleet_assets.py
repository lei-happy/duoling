"""
批量生成车辆资产 Mock 数据（维修保养 + 续期台账 + 资产卡片字段）

路径：backend/scripts/mockdata/mock_tenant_fleet_assets.py

依赖：租户库已有自有车辆（biz_vehicle / biz_vehicle_ext）。
若车辆不足，可先执行 mock_tenant_vehicles.py。

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_fleet_assets.py --tenant-code 1001
  python scripts/mockdata/mock_tenant_fleet_assets.py --tenant-code 1001 --dry-run
  python scripts/mockdata/mock_tenant_fleet_assets.py --tenant-code 1001 --vehicles 15 --orders 30 --plans 12 --renewals 20

写入表：
- biz_vehicle_ext（补齐资产卡片字段）
- biz_fleet_work_order
- biz_fleet_maintain_plan
- biz_fleet_renewal
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.capacity.maintenance.maintain_plan import (  # noqa: E402
    FleetMaintainPlan,
)
from app.modules.client.models.capacity.maintenance.renewal import (  # noqa: E402
    FleetRenewal,
)
from app.modules.client.models.capacity.maintenance.work_order import (  # noqa: E402
    FleetWorkOrder,
)
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle  # noqa: E402
from app.modules.client.models.capacity.self_capacity.vehicle_ext import (  # noqa: E402
    VehicleExt,
)

REPAIR_TITLES = (
    "变速箱异响检修",
    "刹车片更换",
    "轮胎更换",
    "发动机检修",
    "空调故障排查",
    "电路短路检修",
    "离合器调整",
    "玻璃水箱更换",
)
MAINT_TITLES = (
    "定期保养（机油三滤）",
    "两万公里保养",
    "冷却系统保养",
    "底盘润滑保养",
)
PLAN_NAMES = (
    "常规保养计划",
    "机油周期保养",
    "刹车系统检查",
    "轮胎轮换计划",
)
WORKSHOPS = ("华通汽修", "顺达维修厂", "车友之家", "中联养车", "自有维修班组")


def _load_vehicles(session: Session, limit: int) -> list[tuple[Vehicle, VehicleExt]]:
    rows = session.execute(
        select(Vehicle, VehicleExt)
        .join(VehicleExt, VehicleExt.vehicle_id == Vehicle.id)
        .where(Vehicle.is_deleted == 0, VehicleExt.is_deleted == 0)
        .order_by(Vehicle.id.desc())
        .limit(limit)
    ).all()
    return [(v, ext) for v, ext in rows]


def _max_wo_seq(session: Session, prefix: str) -> int:
    last = session.execute(
        select(FleetWorkOrder.work_order_no)
        .where(FleetWorkOrder.work_order_no.like(f"{prefix}%"))
        .order_by(FleetWorkOrder.work_order_no.desc())
        .limit(1)
    ).scalar_one_or_none()
    if last and str(last).startswith(prefix):
        tail = str(last)[len(prefix) :]
        if tail.isdigit():
            return int(tail)
    return 0


def _next_wo_no(session: Session, rng: random.Random, seq: int) -> str:
    prefix = f"WO{datetime.now().strftime('%Y%m%d')}"
    # seq 为循环内偏移；首条用库内最大号，避免 count 撞 uk
    base = _max_wo_seq(session, prefix)
    return f"{prefix}{base + seq + 1:04d}"


def _fill_asset_cards(
    session: Session,
    pairs: list[tuple[Vehicle, VehicleExt]],
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    n = 0
    today = date.today()
    for _vehicle, ext in pairs:
        if ext.original_value is not None and ext.depreciable_months is not None:
            continue
        purchase = ext.purchase_date or (today - timedelta(days=rng.randint(365, 2200)))
        original = Decimal(str(rng.choice([180000, 220000, 280000, 350000, 420000])))
        residual = (original * Decimal("0.1")).quantize(Decimal("0.01"))
        months = rng.choice([36, 48, 60, 72])
        start = purchase.replace(day=1)
        if dry_run:
            print(
                f"[dry-run] asset-card vehicle={ext.vehicle_id} "
                f"original={original} months={months}"
            )
            n += 1
            continue
        ext.purchase_date = purchase
        ext.original_value = float(original)
        ext.residual_value = float(residual)
        ext.depreciable_months = months
        ext.depreciation_method = "straight_line"
        ext.depreciation_start_date = start
        if not ext.insurance_expire:
            ext.insurance_expire = today + timedelta(days=rng.randint(-30, 280))
        if not ext.inspection_expire:
            ext.inspection_expire = today + timedelta(days=rng.randint(-20, 300))
        n += 1
    return n


def _gen_work_orders(
    session: Session,
    pairs: list[tuple[Vehicle, VehicleExt]],
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    if not pairs:
        return 0
    today = datetime.now()
    created = 0
    for i in range(count):
        vehicle, _ext = rng.choice(pairs)
        order_type = "repair" if rng.random() < 0.65 else "maintenance"
        title = rng.choice(REPAIR_TITLES if order_type == "repair" else MAINT_TITLES)
        # 状态分布：完工为主，少量进行中/草稿/取消
        roll = rng.random()
        if roll < 0.55:
            status = "completed"
        elif roll < 0.7:
            status = "in_progress"
        elif roll < 0.88:
            status = "draft"
        else:
            status = "cancelled"

        days_ago = rng.randint(1, 120)
        started = today - timedelta(days=days_ago, hours=rng.randint(0, 10))
        finished = started + timedelta(days=rng.randint(1, 5)) if status in (
            "completed",
            "cancelled",
        ) else None
        cost = (
            Decimal(str(round(rng.uniform(300, 8000), 2)))
            if status == "completed"
            else (Decimal(str(round(rng.uniform(0, 2000), 2))) if rng.random() < 0.3 else None)
        )
        wo_no = _next_wo_no(session, rng, i)
        if dry_run:
            print(
                f"[dry-run] work-order {wo_no} {vehicle.plate_number} "
                f"{order_type}/{status} cost={cost}"
            )
            created += 1
            continue

        row = FleetWorkOrder(
            work_order_no=wo_no,
            vehicle_id=vehicle.id,
            plate_number=vehicle.plate_number,
            order_type=order_type,
            title=title,
            description=f"[mockdata] {title}",
            odometer=rng.randint(20000, 280000),
            workshop=rng.choice(WORKSHOPS),
            expect_finish_date=(started + timedelta(days=3)).date(),
            cost_amount=cost,
            cost_remark="配件+工时" if cost else None,
            status=status,
            started_at=started if status != "draft" else None,
            finished_at=finished,
            remark="[mockdata] mock_tenant_fleet_assets.py",
            created_by=1,
        )
        session.add(row)
        created += 1
    return created


def _gen_plans(
    session: Session,
    pairs: list[tuple[Vehicle, VehicleExt]],
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    if not pairs:
        return 0
    today = date.today()
    created = 0
    used: set[tuple[int, str]] = set()
    for _ in range(count * 3):
        if created >= count:
            break
        vehicle, _ext = rng.choice(pairs)
        name = rng.choice(PLAN_NAMES)
        key = (vehicle.id, name)
        if key in used:
            continue
        used.add(key)
        cycle = rng.choice(["time", "mileage", "either"])
        last_date = today - timedelta(days=rng.randint(10, 100))
        interval_days = rng.choice([60, 90, 120, 180]) if cycle != "mileage" else None
        interval_mileage = rng.choice([5000, 8000, 10000]) if cycle != "time" else None
        next_date = (
            (last_date + timedelta(days=interval_days)) if interval_days else None
        )
        # 约 35% 做成即将到期/已到期，方便看板
        if next_date and rng.random() < 0.35:
            next_date = today + timedelta(days=rng.randint(-10, 6))

        if dry_run:
            print(
                f"[dry-run] plan {vehicle.plate_number} {name} "
                f"cycle={cycle} next={next_date}"
            )
            created += 1
            continue

        session.add(
            FleetMaintainPlan(
                vehicle_id=vehicle.id,
                plate_number=vehicle.plate_number,
                name=name,
                cycle_type=cycle,
                interval_days=interval_days,
                interval_mileage=interval_mileage,
                last_maintain_date=last_date,
                last_maintain_mileage=rng.randint(10000, 200000),
                next_maintain_date=next_date,
                next_maintain_mileage=(
                    (rng.randint(10000, 200000) + (interval_mileage or 0))
                    if interval_mileage
                    else None
                ),
                remind_days=rng.choice([7, 10, 14]),
                enabled=1,
                created_by=1,
            )
        )
        created += 1
    return created


def _gen_renewals(
    session: Session,
    pairs: list[tuple[Vehicle, VehicleExt]],
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    if not pairs:
        return 0
    today = date.today()
    created = 0
    for i in range(count):
        vehicle, ext = rng.choice(pairs)
        rtype = "insurance" if rng.random() < 0.6 else "inspection"
        eff = today - timedelta(days=rng.randint(0, 200))
        expire = eff + timedelta(days=rng.randint(300, 400))
        amount = Decimal(
            str(
                round(
                    rng.uniform(3500, 16000) if rtype == "insurance" else rng.uniform(200, 900),
                    2,
                )
            )
        )
        status_roll = rng.random()
        if status_roll < 0.75:
            status = "effective"
        elif status_roll < 0.9:
            status = "draft"
        else:
            status = "cancelled"

        if dry_run:
            print(
                f"[dry-run] renewal {vehicle.plate_number} {rtype}/{status} "
                f"amount={amount}"
            )
            created += 1
            continue

        session.add(
            FleetRenewal(
                vehicle_id=vehicle.id,
                plate_number=vehicle.plate_number,
                renewal_type=rtype,
                effective_date=eff,
                expire_date=expire,
                amount=amount,
                policy_no=f"POL-MOCK-{vehicle.id}-{i:03d}" if rtype == "insurance" else None,
                status=status,
                effective_at=datetime.combine(eff, datetime.min.time())
                if status == "effective"
                else None,
                remark="[mockdata] mock_tenant_fleet_assets.py",
                created_by=1,
            )
        )
        # 生效记录回写到期日，便于证照监控与资产成本联动演示
        if status == "effective":
            if rtype == "insurance":
                ext.insurance_expire = expire
            else:
                ext.inspection_expire = expire
        created += 1
    return created


def generate(
    session: Session,
    *,
    vehicle_limit: int,
    orders: int,
    plans: int,
    renewals: int,
    rng: random.Random,
    dry_run: bool,
) -> dict[str, int]:
    pairs = _load_vehicles(session, vehicle_limit)
    if not pairs:
        raise SystemExit(
            "[ERROR] 租户库没有可用车辆。请先执行：\n"
            "  python scripts/mockdata/mock_tenant_vehicles.py --tenant-code <编码> --count 20"
        )

    stats = {
        "vehicles_used": len(pairs),
        "asset_cards": _fill_asset_cards(session, pairs, rng, dry_run=dry_run),
        "work_orders": _gen_work_orders(session, pairs, orders, rng, dry_run=dry_run),
        "plans": _gen_plans(session, pairs, plans, rng, dry_run=dry_run),
        "renewals": _gen_renewals(session, pairs, renewals, rng, dry_run=dry_run),
    }
    if not dry_run:
        session.commit()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="向租户库批量插入车辆资产 Mock 数据")
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument(
        "--vehicles", type=int, default=20, help="参与生成的车辆上限（按 id 倒序取）"
    )
    parser.add_argument("--orders", type=int, default=25, help="维保工单条数")
    parser.add_argument("--plans", type=int, default=12, help="保养计划条数")
    parser.add_argument("--renewals", type=int, default=18, help="续期台账条数")
    parser.add_argument("--seed", type=int, default=20260730, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写库")
    args = parser.parse_args()

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        stats = generate(
            session,
            vehicle_limit=args.vehicles,
            orders=args.orders,
            plans=args.plans,
            renewals=args.renewals,
            rng=rng,
            dry_run=args.dry_run,
        )

    action = "预览" if args.dry_run else "已写入"
    print(
        f"[OK] 租户 {args.tenant_code}：{action} 车辆资产 Mock\n"
        f"  车辆池={stats['vehicles_used']}  资产卡片补齐={stats['asset_cards']}\n"
        f"  工单={stats['work_orders']}  保养计划={stats['plans']}  续期={stats['renewals']}"
    )


if __name__ == "__main__":
    main()
