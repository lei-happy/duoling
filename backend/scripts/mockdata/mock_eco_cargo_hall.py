"""
批量生成「货源大厅」Mock 挂牌（写入平台库）

脚本路径：backend/scripts/mockdata/mock_eco_cargo_hall.py

写入表：
- sys_eco_post（post_type=1，status=3 展示中）
- sys_eco_cargo_post
- sys_eco_post_dest
- sys_eco_tenant_profile / sys_eco_tenant_credit（发布方名片与信誉，按需 upsert）

说明：
- 数据落在**平台库**，不是租户库；大厅列表排除当前租户自己的挂牌。
- 约 1/3 归属 ``--tenant-code``（可在「我发布的」看到），其余归属其它企业（大厅可见）。
- 不写 biz_eco_post_ref / 不创建租户侧任务单，仅用于大厅浏览与「我发布的」联调。

用法（在 backend 目录下执行）:
  python scripts/mockdata/mock_eco_cargo_hall.py --tenant-code demo --count 20
  python scripts/mockdata/mock_eco_cargo_hall.py --tenant-code demo --count 5 --dry-run
  python scripts/mockdata/mock_eco_cargo_hall.py --tenant-code demo --count 15 --seed 42
"""

from __future__ import annotations

import argparse
import importlib.util
import random
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost  # noqa: E402
from app.modules.console.models.ecosystem.constants import (  # noqa: E402
    CargoCategory,
    CooperationType,
    PriceType,
    PostType,
    SettleType,
    VehicleCondition,
)
from app.modules.console.models.ecosystem.post import SysEcoPost  # noqa: E402
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest  # noqa: E402


def _load_common():
    common_path = Path(__file__).resolve().parent / "eco_hall_common.py"
    spec = importlib.util.spec_from_file_location("eco_hall_common", common_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Python 3.9 dataclass 在 exec_module 前需要模块已登记
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_common = _load_common()
BRANDS = _common.BRANDS
TRUCK_TYPES = _common.TRUCK_TYPES
base_post_kwargs = _common.base_post_kwargs
build_listed_times = _common.build_listed_times
load_tenant = _common.load_tenant
next_post_no = _common.next_post_no
open_platform_session = _common.open_platform_session
pick_owner_for_index = _common.pick_owner_for_index
pick_route = _common.pick_route
resolve_owners = _common.resolve_owners


def _cargo_title(from_city: str, to_city: str, qty: int, brand: str, series: str) -> str:
    return f"{from_city}→{to_city} {qty}台 {brand}{series}"


def _pick_price(rng: random.Random) -> tuple[int, Decimal | None]:
    price_type = rng.choice(
        (
            PriceType.PER_UNIT,
            PriceType.PER_UNIT,
            PriceType.PACKAGE,
            PriceType.NEGOTIABLE,
            PriceType.PER_KM,
        )
    )
    if price_type == PriceType.NEGOTIABLE:
        return price_type, None
    if price_type == PriceType.PACKAGE:
        return price_type, Decimal(str(rng.randint(2800, 12000)))
    if price_type == PriceType.PER_KM:
        return price_type, Decimal(str(round(rng.uniform(2.5, 6.5), 2)))
    return price_type, Decimal(str(rng.randint(400, 1500)))


def generate_cargo_posts(
    session: Session,
    *,
    tenant_code: str,
    count: int,
    rng: random.Random,
    dry_run: bool,
    valid_days: int,
) -> tuple[int, int]:
    """返回 (写入条数, 归属主租户条数)。"""
    primary = load_tenant(session, tenant_code)
    owners = resolve_owners(session, primary, rng, dry_run=dry_run)
    created = 0
    mine = 0

    for i in range(count):
        owner = pick_owner_for_index(owners, i, count, rng)
        if owner.tenant_code == primary.tenant_code:
            mine += 1

        (fp, fc), (tp, tc) = pick_route(rng)
        qty = rng.choice((5, 8, 10, 12, 15, 20, 25, 30))
        brand, series = rng.choice(BRANDS)
        is_vehicle = rng.random() < 0.85
        price_type, price_amount = _pick_price(rng)
        coop = (
            CooperationType.LONG_TERM
            if rng.random() < 0.15
            else CooperationType.ONCE
        )
        times = build_listed_times(rng, valid_days=valid_days)
        title = (
            _cargo_title(fc, tc, qty, brand, series)
            if is_vehicle
            else f"{fc}→{tc} {qty}台 普货托运"
        )

        # dry-run 未落库，用 offset 避免预览编号全部相同
        post_no = next_post_no(
            session, PostType.CARGO, offset=i if dry_run else 0
        )
        kwargs = base_post_kwargs(
            post_no=post_no,
            post_type=PostType.CARGO,
            owner=owner,
            title=title,
            from_prov=fp,
            from_city=fc,
            to_prov=tp,
            to_city=tc,
            any_direction=0,
            times=times,
            total_quantity=qty,
            price_type=price_type,
            price_amount=price_amount,
            cooperation_type=coop,
            rng=rng,
        )

        if is_vehicle:
            items = [{"brand": brand, "series": series, "quantity": qty}]
            if qty >= 15 and rng.random() < 0.4:
                b2, s2 = rng.choice(BRANDS)
                split = max(1, qty // 3)
                items = [
                    {"brand": brand, "series": series, "quantity": qty - split},
                    {"brand": b2, "series": s2, "quantity": split},
                ]
            ext_kwargs = dict(
                cargo_category=CargoCategory.VEHICLE,
                cargo_items=items,
                vehicle_condition=rng.choice(
                    (VehicleCondition.NEW, VehicleCondition.NEW, VehicleCondition.USED)
                ),
                require_truck_types=rng.sample(
                    list(TRUCK_TYPES[:3]), k=rng.randint(1, 2)
                ),
                require_slot_min=rng.choice((6, 7, 8)),
                require_slot_max=rng.choice((8, 9, 10, 12)),
                allow_split=1 if qty >= 12 and rng.random() < 0.5 else 0,
                require_insurance=rng.choice((0, 1)),
                time_negotiable=rng.choice((0, 1)),
                settle_type=rng.choice(
                    (SettleType.CASH, SettleType.MONTHLY, SettleType.PREPAY)
                ),
                reference_mileage=Decimal(str(rng.randint(200, 2200))),
                segment_count=1,
                other_requirements=(
                    "[mockdata] 需准时到场装车" if rng.random() < 0.3 else None
                ),
            )
        else:
            ext_kwargs = dict(
                cargo_category=CargoCategory.GENERAL,
                cargo_name=rng.choice(("配件纸箱", "轮胎托盘", "展车道具", "办公物资")),
                cargo_weight=Decimal(str(round(rng.uniform(1.0, 12.0), 2))),
                cargo_volume=Decimal(str(round(rng.uniform(2.0, 30.0), 2))),
                package_type=rng.choice(("纸箱", "托盘", "木架")),
                require_truck_types=[rng.choice(TRUCK_TYPES[3:] or TRUCK_TYPES)],
                allow_split=0,
                require_insurance=rng.choice((0, 1)),
                time_negotiable=1,
                settle_type=SettleType.CASH,
                segment_count=1,
            )

        if dry_run:
            price_label = f"{price_amount}元" if price_amount is not None else "面议"
            print(
                f"[dry-run] {post_no} | {owner.tenant_code} | {title} | "
                f"{price_label} | until {times['valid_until']:%m-%d}"
            )
            created += 1
            continue

        post = SysEcoPost(**kwargs)
        session.add(post)
        session.flush()
        session.add(SysEcoCargoPost(post_id=post.id, **ext_kwargs))
        session.add(
            SysEcoPostDest(
                post_id=post.id,
                post_type=PostType.CARGO,
                province=tp,
                city=tc,
                sort_order=0,
            )
        )
        created += 1

    if not dry_run:
        session.commit()
    return created, mine


def main() -> None:
    parser = argparse.ArgumentParser(description="生成货源大厅 Mock 挂牌（平台库）")
    parser.add_argument(
        "--tenant-code",
        required=True,
        help="主租户编码（写「我发布的」+ 解析企业名）",
    )
    parser.add_argument("--count", type=int, default=20, help="挂牌条数，默认 20")
    parser.add_argument("--valid-days", type=int, default=7, help="展示有效天数，默认 7")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="只打印摘要，不写库")
    args = parser.parse_args()

    if args.count < 1:
        raise SystemExit("--count 须 >= 1")
    if args.valid_days < 1:
        raise SystemExit("--valid-days 须 >= 1")

    rng = random.Random(args.seed)
    engine, session = open_platform_session()
    try:
        with session:
            n, mine = generate_cargo_posts(
                session,
                tenant_code=args.tenant_code,
                count=args.count,
                rng=rng,
                dry_run=args.dry_run,
                valid_days=args.valid_days,
            )
    finally:
        engine.dispose()

    action = "预览" if args.dry_run else "已写入"
    hall_n = n - mine
    print(
        f"[OK] 货源大厅：{action} {n} 条挂牌"
        f"（大厅可见约 {hall_n}，我发布的 {mine}；主租户 {args.tenant_code}）"
    )


if __name__ == "__main__":
    main()
