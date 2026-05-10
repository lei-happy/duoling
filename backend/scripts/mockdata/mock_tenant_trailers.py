"""
批量生成自有运力「挂车」Mock 数据（写入指定租户库 biz_trailer + biz_trailer_ext）

路径：backend/scripts/mockdata/mock_tenant_trailers.py

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_trailers.py --tenant-code demo --count 20
  python scripts/mockdata/mock_tenant_trailers.py --tenant-code demo --count 5 --dry-run

挂车号牌与车辆蓝牌区分：
- 车辆（mock_tenant_vehicles）：省简称 + 字母 + 5 位数字，如 京A12342
- 挂车（本脚本）：省简称 + 字母 + 4 位数字 + 后缀「挂」，如 京A1234挂

字段尽量写满：trailer_type、轴数、载重/容积、厢体长宽高、车位数、购买日期、备注等。
挂车类型优先从 biz_dict_item（dict_code=trailer_type）读取；若无则使用内置编码。
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, delete, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.capacity.self_capacity.trailer import Trailer  # noqa: E402
from app.modules.client.models.capacity.self_capacity.trailer_ext import TrailerExt  # noqa: E402
from app.modules.client.models.biz_dict import BizDict, BizDictItem  # noqa: E402


DEFAULT_TRAILER_TYPES = (
    "flatbed",
    "van",
    "skeleton",
    "lowbed",
    "tank",
    "container",
)

# 与车辆 mock 共用省份与字母表（本脚本仅车牌格式不同）
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


def _trailer_type_values(session: Session) -> list[str]:
    d = session.execute(
        select(BizDict.id).where(
            BizDict.dict_code == "trailer_type",
            BizDict.is_deleted == 0,
        )
    ).scalar_one_or_none()
    if not d:
        return list(DEFAULT_TRAILER_TYPES)
    rows = session.execute(
        select(BizDictItem.item_value).where(
            BizDictItem.dict_id == d,
            BizDictItem.dict_code == "trailer_type",
            BizDictItem.is_deleted == 0,
            BizDictItem.status == 1,
        )
    ).all()
    vals = [str(r[0]) for r in rows if r[0]]
    return vals if vals else list(DEFAULT_TRAILER_TYPES)


def _mock_trailer_plate(rng: random.Random, seq: int) -> str:
    """挂车号牌：省 + 发牌字母 + 4 位数字 + 「挂」（如 京A1234挂），与车辆蓝牌区分。"""
    prov = PLATE_PROVINCES[seq % len(PLATE_PROVINCES)]
    letter = rng.choice(PLATE_LETTERS)
    base = (int(datetime.now().timestamp()) % 7000) + seq * 137
    num = 1000 + (base % 9000)
    return f"{prov}{letter}{num}挂"


def generate_trailers(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    ttypes = _trailer_type_values(session)
    base_day = date.today()
    created = 0

    for i in range(count):
        plate = _mock_trailer_plate(rng, i)
        with session.no_autoflush:
            exists = session.execute(
                select(Trailer.id).where(
                    Trailer.plate_number == plate,
                    Trailer.is_deleted == 0,
                )
            ).first()
        if exists:
            continue

        tt = rng.choice(ttypes)
        remark = (
            f"[mockdata] mock_tenant_trailers.py "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if dry_run:
            print(f"[dry-run] {plate} type={tt}")
            created += 1
            continue

        t = Trailer(
            plate_number=plate,
            status=1,
        )
        session.add(t)
        session.flush()
        session.execute(delete(TrailerExt).where(TrailerExt.trailer_id == t.id))

        purchase = base_day - timedelta(days=rng.randint(180, 2500))
        ext = TrailerExt(
            trailer_id=t.id,
            trailer_type=tt,
            axle_count=rng.randint(2, 6),
            load_capacity=round(rng.uniform(20, 55), 2),
            volume_capacity=round(rng.uniform(60, 130), 2),
            length=round(rng.uniform(12.0, 17.5), 2),
            width=round(rng.uniform(2.45, 2.55), 2),
            height=round(rng.uniform(3.8, 4.2), 2),
            parking_spots=rng.randint(1, 3),
            purchase_date=purchase,
            remark=remark[:500],
        )
        session.add(ext)
        created += 1

    if not dry_run:
        session.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="向租户库批量插入挂车 Mock 数据")
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
        n = generate_trailers(session, args.count, rng, dry_run=args.dry_run)

    action = "预览" if args.dry_run else "已写入"
    print(f"[OK] 租户 {args.tenant_code}：{action} {n} 条挂车（biz_trailer + biz_trailer_ext）。")


if __name__ == "__main__":
    main()
