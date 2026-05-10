"""
批量生成自有运力「车辆」Mock 数据（写入指定租户库 biz_vehicle + biz_vehicle_ext）

路径：backend/scripts/mockdata/mock_tenant_vehicles.py

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_vehicles.py --tenant-code demo --count 20
  python scripts/mockdata/mock_tenant_vehicles.py --tenant-code demo --count 5 --dry-run

字段尽量写满：
- biz_vehicle：plate_number（蓝牌：省简称+字母+5 位数字，如 京A12342）、trailer_id、status、status_source
- biz_vehicle_ext：vehicle_type、brand、model、color、vin、engine_no、load_capacity、
  volume_capacity、purchase_date、insurance_expire、inspection_expire、gps_device_id、remark

车辆类型优先从租户库 biz_dict_item（dict_code=vehicle_type）读取 item_value；若无字典则使用内置编码。
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

from sqlalchemy import create_engine, delete, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.constants.plate_category import (
    PLATE_CATEGORY_BLUE,
    PLATE_CATEGORY_NEW_ENERGY,
    PLATE_CATEGORY_YELLOW,
)
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle  # noqa: E402
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt  # noqa: E402
from app.modules.client.models.capacity.self_capacity.trailer import Trailer  # noqa: E402
from app.modules.client.models.biz_dict import BizDict, BizDictItem  # noqa: E402


DEFAULT_VEHICLE_TYPES = (
    "heavy_truck",
    "medium_truck",
    "light_truck",
    "mini_truck",
)

BRANDS = ("解放", "东风", "重汽", "陕汽", "福田", "江淮", "红岩", "北奔")
COLORS = ("红", "蓝", "白", "银灰", "绿", "黄", "黑")

# 蓝牌小型车：省份简称 + 发牌机关字母(不含 I/O) + 5 位数字，如 京A12342
PLATE_PROVINCES = (
    "京",
    "津",
    "冀",
    "晋",
    "蒙",
    "辽",
    "吉",
    "黑",
    "沪",
    "苏",
    "浙",
    "皖",
    "闽",
    "赣",
    "鲁",
    "豫",
    "鄂",
    "湘",
    "粤",
    "桂",
    "琼",
    "渝",
    "川",
    "贵",
    "云",
    "陕",
    "甘",
    "青",
    "宁",
    "新",
    "藏",
)
PLATE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def _vehicle_type_values(session: Session) -> list[str]:
    d = session.execute(
        select(BizDict.id).where(
            BizDict.dict_code == "vehicle_type",
            BizDict.is_deleted == 0,
        )
    ).scalar_one_or_none()
    if not d:
        return list(DEFAULT_VEHICLE_TYPES)
    rows = session.execute(
        select(BizDictItem.item_value).where(
            BizDictItem.dict_id == d,
            BizDictItem.dict_code == "vehicle_type",
            BizDictItem.is_deleted == 0,
            BizDictItem.status == 1,
        )
    ).all()
    vals = [str(r[0]) for r in rows if r[0]]
    return vals if vals else list(DEFAULT_VEHICLE_TYPES)


def _trailer_ids(session: Session, limit: int = 200) -> list[int]:
    rows = session.execute(
        select(Trailer.id).where(Trailer.is_deleted == 0).limit(limit)
    ).all()
    return [int(r[0]) for r in rows if r[0] is not None]


def _mock_plate(rng: random.Random, seq: int) -> str:
    """蓝牌格式：省简称 + 字母 + 5 位数字（如 京A12342），长度 7，<=20。"""
    prov = PLATE_PROVINCES[seq % len(PLATE_PROVINCES)]
    letter = rng.choice(PLATE_LETTERS)
    base = (int(datetime.now().timestamp()) % 70000) + seq * 137
    num = 10000 + (base % 90000)
    return f"{prov}{letter}{num}"


def _mock_plate_nev(rng: random.Random, seq: int) -> str:
    """新能源小型车：省简称 + 字母 + 6 位序号，总长 8。"""
    prov = PLATE_PROVINCES[seq % len(PLATE_PROVINCES)]
    letter = rng.choice(PLATE_LETTERS)
    suf = "".join(
        rng.choice("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6)
    )
    return f"{prov}{letter}{suf}"


def generate_vehicles(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    vtypes = _vehicle_type_values(session)
    trailers = _trailer_ids(session)
    rng.shuffle(trailers)
    trailer_iter = iter(trailers)
    base_day = date.today()

    created = 0
    for i in range(count):
        roll = rng.random()
        if roll < 0.2:
            plate_category = PLATE_CATEGORY_BLUE
            plate = _mock_plate(rng, i)
        elif roll < 0.65:
            plate_category = PLATE_CATEGORY_YELLOW
            plate = _mock_plate(rng, i)
        else:
            plate_category = PLATE_CATEGORY_NEW_ENERGY
            plate = _mock_plate_nev(rng, i)

        with session.no_autoflush:
            exists = session.execute(
                select(Vehicle.id).where(
                    Vehicle.plate_number == plate,
                    Vehicle.is_deleted == 0,
                )
            ).first()
        if exists:
            continue

        trailer_id = None
        if trailers and rng.random() < 0.45:
            try:
                trailer_id = next(trailer_iter)
            except StopIteration:
                trailer_id = None
        vt = rng.choice(vtypes)
        brand = rng.choice(BRANDS)
        model = f"{brand}{rng.randint(1, 9)}系-{rng.randint(100, 999)}"
        remark = (
            f"[mockdata] mock_tenant_vehicles.py "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if dry_run:
            print(f"[dry-run] {plate} cat={plate_category} type={vt} trailer={trailer_id}")
            created += 1
            continue

        v = Vehicle(
            plate_number=plate,
            plate_category=plate_category,
            trailer_id=trailer_id,
            status=1,
            status_source="manual",
        )
        session.add(v)
        session.flush()
        # vehicle_id 在 ext 表唯一；若库中已有孤儿/残留行，先清掉再插
        session.execute(delete(VehicleExt).where(VehicleExt.vehicle_id == v.id))

        purchase = base_day - timedelta(days=rng.randint(180, 2000))
        ins = base_day + timedelta(days=rng.randint(30, 400))
        insp = base_day + timedelta(days=rng.randint(20, 365))

        ext = VehicleExt(
            vehicle_id=v.id,
            vehicle_type=vt,
            brand=brand,
            model=model[:50],
            color=rng.choice(COLORS),
            vin=f"LZZ{rng.randint(10**11, 10**12 - 1)}"[:17],
            engine_no=f"ENG{rng.randint(10**8, 10**9 - 1)}",
            load_capacity=Decimal(str(round(rng.uniform(5, 40), 2))),
            volume_capacity=Decimal(str(round(rng.uniform(20, 120), 2))),
            purchase_date=purchase,
            insurance_expire=ins,
            inspection_expire=insp,
            gps_device_id=f"GPS-MOCK-{v.id}-{rng.randint(1000, 9999)}",
            remark=remark[:500],
        )
        session.add(ext)
        created += 1

    if not dry_run:
        session.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="向租户库批量插入车辆 Mock 数据")
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument("--count", type=int, default=20, help="生成条数")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写库")
    args = parser.parse_args()

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        n = generate_vehicles(session, args.count, rng, dry_run=args.dry_run)

    action = "预览" if args.dry_run else "已写入"
    print(f"[OK] 租户 {args.tenant_code}：{action} {n} 条车辆（biz_vehicle + biz_vehicle_ext）。")


if __name__ == "__main__":
    main()
