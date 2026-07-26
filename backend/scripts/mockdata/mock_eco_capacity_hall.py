"""
批量生成「运力大厅」Mock 挂牌（写入平台库）

脚本路径：backend/scripts/mockdata/mock_eco_capacity_hall.py

写入表：
- sys_eco_post（post_type=2，status=3 展示中）
- sys_eco_capacity_post
- sys_eco_post_dest（任意流向时不写目的地行）
- sys_eco_tenant_profile / sys_eco_tenant_credit（发布方名片与信誉，按需 upsert）

说明：
- 数据落在**平台库**，不是租户库；大厅列表排除当前租户自己的挂牌。
- 约 1/3 归属 ``--tenant-code``（可在「我发布的」看到），其余归属其它企业（大厅可见）。
- 部分运力为「任意流向」（any_direction=1），其余写 1~3 条期望流向。
- 不写 biz_eco_post_ref / 不创建租户侧运力档案，仅用于大厅浏览与「我发布的」联调。

用法（在 backend 目录下执行）:
  python scripts/mockdata/mock_eco_capacity_hall.py --tenant-code demo --count 20
  python scripts/mockdata/mock_eco_capacity_hall.py --tenant-code demo --count 5 --dry-run
  python scripts/mockdata/mock_eco_capacity_hall.py --tenant-code demo --count 15 --seed 42
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

from app.modules.console.models.ecosystem.capacity_post import (  # noqa: E402
    SysEcoCapacityPost,
)
from app.modules.console.models.ecosystem.constants import (  # noqa: E402
    CargoCategory,
    CooperationType,
    PostGranularity,
    PriceType,
    PostType,
    SettleType,
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
CITY_POOL = _common.CITY_POOL
SLOT_COUNTS = _common.SLOT_COUNTS
SURNAMES = _common.SURNAMES
TRUCK_TYPES = _common.TRUCK_TYPES
base_post_kwargs = _common.base_post_kwargs
build_listed_times = _common.build_listed_times
load_tenant = _common.load_tenant
next_post_no = _common.next_post_no
open_platform_session = _common.open_platform_session
pick_owner_for_index = _common.pick_owner_for_index
pick_route = _common.pick_route
resolve_owners = _common.resolve_owners

PLATE_PROVINCES = (
    "浙", "苏", "粤", "川", "沪", "京", "鲁", "鄂", "湘", "陕", "闽", "渝",
)


def _mask_plate(plate: str) -> str:
    if len(plate) < 5:
        return plate
    return f"{plate[:2]}***{plate[-2:]}"


def _random_plate(rng: random.Random) -> str:
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    return (
        f"{rng.choice(PLATE_PROVINCES)}"
        f"{rng.choice(letters)}"
        f"{rng.randint(10000, 99999)}"
    )


def _pick_price(rng: random.Random) -> tuple[int, Decimal | None]:
    price_type = rng.choice(
        (
            PriceType.PACKAGE,
            PriceType.PACKAGE,
            PriceType.PER_UNIT,
            PriceType.NEGOTIABLE,
            PriceType.PER_KM,
        )
    )
    if price_type == PriceType.NEGOTIABLE:
        return price_type, None
    if price_type == PriceType.PACKAGE:
        return price_type, Decimal(str(rng.randint(2500, 10000)))
    if price_type == PriceType.PER_KM:
        return price_type, Decimal(str(round(rng.uniform(2.2, 5.8), 2)))
    return price_type, Decimal(str(rng.randint(350, 1200)))


def _capacity_title(
    from_city: str,
    *,
    any_direction: bool,
    to_city: str | None,
    slot: int,
    truck_type: str,
) -> str:
    if any_direction:
        return f"{from_city}→不限流向 {slot}位{truck_type}"
    return f"{from_city}→{to_city} {slot}位{truck_type}"


def generate_capacity_posts(
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
        any_direction = 1 if rng.random() < 0.35 else 0
        truck_type = rng.choice(TRUCK_TYPES[:3])
        slot = rng.choice(SLOT_COUNTS)
        truck_qty = 1 if rng.random() < 0.75 else rng.randint(2, 5)
        granularity = (
            PostGranularity.SPECIFIC
            if truck_qty == 1
            else PostGranularity.FLEET
        )
        price_type, price_amount = _pick_price(rng)
        coop = (
            CooperationType.LONG_TERM
            if rng.random() < 0.2
            else CooperationType.ONCE
        )
        times = build_listed_times(rng, valid_days=valid_days)

        to_prov = None if any_direction else tp
        to_city = None if any_direction else tc
        title = _capacity_title(
            fc,
            any_direction=bool(any_direction),
            to_city=tc,
            slot=slot,
            truck_type=truck_type,
        )

        plate = _random_plate(rng) if granularity == PostGranularity.SPECIFIC else None
        driver_surname = rng.choice(SURNAMES)
        post_no = next_post_no(
            session, PostType.CAPACITY, offset=i if dry_run else 0
        )
        kwargs = base_post_kwargs(
            post_no=post_no,
            post_type=PostType.CAPACITY,
            owner=owner,
            title=title,
            from_prov=fp,
            from_city=fc,
            to_prov=to_prov,
            to_city=to_city,
            any_direction=any_direction,
            times=times,
            total_quantity=slot * truck_qty,
            price_type=price_type,
            price_amount=price_amount,
            cooperation_type=coop,
            rng=rng,
        )
        kwargs["keep_listed_after_deal"] = 1 if coop == CooperationType.LONG_TERM else 0

        dest_rows: list[tuple[str, str | None]] = []
        if not any_direction:
            dest_rows.append((tp, tc))
            for _ in range(rng.randint(0, 2)):
                p, c = rng.choice(CITY_POOL)
                if (p, c) in ((tp, tc), (fp, fc)):
                    continue
                if rng.random() < 0.4:
                    dest_rows.append((p, None))
                else:
                    dest_rows.append((p, c))

        ext_kwargs = dict(
            post_granularity=granularity,
            truck_type=truck_type,
            slot_count=slot,
            truck_length=Decimal(str(rng.choice((13.75, 16.5, 17.5)))),
            truck_quantity=truck_qty,
            plate_number=plate,
            plate_masked=_mask_plate(plate) if plate else None,
            plate_public=1 if plate and rng.random() < 0.2 else 0,
            has_trailer=1 if truck_type in ("板车", "轿运车") else rng.choice((0, 1)),
            driver_name=f"{driver_surname}师傅",
            driver_display=f"{driver_surname}师傅",
            driver_years=rng.randint(3, 18),
            driver_order_count=rng.randint(20, 800),
            pickup_radius=rng.choice((50, 80, 100, 150, 200)),
            good_at_categories=rng.sample(
                [CargoCategory.VEHICLE, CargoCategory.GENERAL, CargoCategory.OTHER],
                k=rng.randint(1, 2),
            ),
            can_invoice=rng.choice((0, 1)),
            invoice_type="增值税专用发票" if rng.random() < 0.4 else None,
            has_insurance=rng.choice((0, 1)),
            settle_require=rng.choice(
                (SettleType.CASH, SettleType.MONTHLY, SettleType.PREPAY)
            ),
            service_promise=(
                "[mockdata] 准时提车，全程定位" if rng.random() < 0.35 else None
            ),
        )

        if dry_run:
            flow = "任意流向" if any_direction else f"{tp}{tc}+{max(0, len(dest_rows) - 1)}流向"
            price_label = f"{price_amount}元" if price_amount is not None else "面议"
            print(
                f"[dry-run] {post_no} | {owner.tenant_code} | {title} | "
                f"{flow} | {price_label}"
            )
            created += 1
            continue

        post = SysEcoPost(**kwargs)
        session.add(post)
        session.flush()
        session.add(SysEcoCapacityPost(post_id=post.id, **ext_kwargs))
        for order, (prov, city) in enumerate(dest_rows):
            session.add(
                SysEcoPostDest(
                    post_id=post.id,
                    post_type=PostType.CAPACITY,
                    province=prov,
                    city=city,
                    sort_order=order,
                )
            )
        created += 1

    if not dry_run:
        session.commit()
    return created, mine


def main() -> None:
    parser = argparse.ArgumentParser(description="生成运力大厅 Mock 挂牌（平台库）")
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
            n, mine = generate_capacity_posts(
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
        f"[OK] 运力大厅：{action} {n} 条挂牌"
        f"（大厅可见约 {hall_n}，我发布的 {mine}；主租户 {args.tenant_code}）"
    )


if __name__ == "__main__":
    main()
