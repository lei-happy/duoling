"""
批量生成「社会运力」Mock 数据（写入指定租户库）

脚本路径：backend/scripts/mockdata/mock_tenant_social_capacities.py

用法（在 backend 目录下执行）:
  python scripts/mockdata/mock_tenant_social_capacities.py --tenant-code demo --count 20
  python scripts/mockdata/mock_tenant_social_capacities.py --tenant-code demo --count 5 --dry-run
  python scripts/mockdata/mock_tenant_social_capacities.py --tenant-code demo --count 10 --accounts 2

数据饱和度（按 ORM 业务字段尽量写满）：
- biz_social_capacity：social_code、冗余检索字段、来源、双状态、评级预留、备注等
- biz_social_capacity_vehicle：车辆规格、挂车内嵌、资质日期、四类证照 URL
- biz_social_capacity_driver：驾驶员基础信息、资质、四类证件 URL
- biz_social_capacity_account：每位社会运力 1~N 条结算账户（默认 1，--accounts 可调）

号牌规则与 mock_tenant_vehicles / mock_tenant_trailers 一致：
- 主车：蓝/黄/新能源格式
- 含挂车时挂车号牌为「…挂」后缀

字典优先从 biz_dict_item 读取：vehicle_type、trailer_type、social_capacity_source。
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

from sqlalchemy import create_engine, func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.constants.plate_category import (
    PLATE_CATEGORY_BLUE,
    PLATE_CATEGORY_NEW_ENERGY,
    PLATE_CATEGORY_YELLOW,
)
from app.modules.client.models.biz_dict import BizDict, BizDictItem  # noqa: E402
from app.modules.client.models.capacity.social_capacity import (  # noqa: E402
    SocialCapacity,
    SocialCapacityAccount,
    SocialCapacityDriver,
    SocialCapacityVehicle,
)

DEFAULT_VEHICLE_TYPES = (
    "heavy_truck",
    "medium_truck",
    "light_truck",
    "mini_truck",
)
DEFAULT_TRAILER_TYPES = (
    "flatbed",
    "van",
    "skeleton",
    "lowbed",
    "tank",
    "container",
)
DEFAULT_SOURCES = (
    "referral",
    "platform",
    "self",
    "partner_fleet",
    "other",
)

BRANDS = ("解放", "东风", "重汽", "陕汽", "福田", "江淮", "红岩", "北奔")
COLORS = ("红", "蓝", "白", "银灰", "绿", "黄", "黑")
LICENSE_TYPES = ("A1", "A2", "B1", "B2", "C1", "C2")
BANK_NAMES = (
    "中国工商银行",
    "中国建设银行",
    "中国农业银行",
    "中国银行",
    "交通银行",
    "招商银行",
)

SURNAMES = (
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
)
GIVEN_NAMES = (
    "伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平",
)

PLATE_PROVINCES = (
    "京", "津", "冀", "晋", "蒙", "辽", "吉", "黑", "沪", "苏",
    "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘", "粤", "桂",
    "琼", "渝", "川", "贵", "云", "陕", "甘", "青", "宁", "新", "藏",
)
PLATE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"

SOURCE_REMARKS = (
    "同行引荐",
    "平台撮合对接",
    "驾驶员自荐",
    "合作车队推荐",
    "线下展会获客",
    "老客户介绍",
)

# (approval_status, status) 组合，便于列表页展示多种状态
STATUS_PROFILES = (
    (2, 1),  # 已通过 + 正常
    (2, 1),
    (2, 1),
    (2, 0),  # 已通过 + 未生效
    (2, 2),  # 已通过 + 停用
    (2, 3),  # 已通过 + 黑名单
    (0, 0),  # 草稿
    (1, 0),  # 待审核
    (3, 0),  # 已驳回
)


def _dict_item_values(session: Session, dict_code: str, defaults: tuple[str, ...]) -> list[str]:
    d = session.execute(
        select(BizDict.id).where(
            BizDict.dict_code == dict_code,
            BizDict.is_deleted == 0,
        )
    ).scalar_one_or_none()
    if not d:
        return list(defaults)
    rows = session.execute(
        select(BizDictItem.item_value).where(
            BizDictItem.dict_id == d,
            BizDictItem.dict_code == dict_code,
            BizDictItem.is_deleted == 0,
            BizDictItem.status == 1,
        )
    ).all()
    vals = [str(r[0]) for r in rows if r[0]]
    return vals if vals else list(defaults)


def _next_social_code(session: Session) -> str:
    year = datetime.now().strftime("%Y")
    prefix = f"S{year}"
    subq = (
        select(SocialCapacity.id)
        .where(SocialCapacity.social_code.like(f"{prefix}%"))
        .subquery()
    )
    cnt = session.execute(select(func.count()).select_from(subq)).scalar() or 0
    return f"{prefix}{int(cnt) + 1:05d}"


def _mock_plate(rng: random.Random, seq: int) -> str:
    prov = PLATE_PROVINCES[seq % len(PLATE_PROVINCES)]
    letter = rng.choice(PLATE_LETTERS)
    base = (int(datetime.now().timestamp()) % 70000) + seq * 137
    num = 10000 + (base % 90000)
    return f"{prov}{letter}{num}"


def _mock_plate_nev(rng: random.Random, seq: int) -> str:
    prov = PLATE_PROVINCES[seq % len(PLATE_PROVINCES)]
    letter = rng.choice(PLATE_LETTERS)
    suf = "".join(
        rng.choice("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6)
    )
    return f"{prov}{letter}{suf}"


def _mock_trailer_plate(rng: random.Random, seq: int) -> str:
    prov = PLATE_PROVINCES[seq % len(PLATE_PROVINCES)]
    letter = rng.choice(PLATE_LETTERS)
    base = (int(datetime.now().timestamp()) % 7000) + seq * 137
    num = 1000 + (base % 9000)
    return f"{prov}{letter}{num}挂"


def _pick_plate(rng: random.Random, seq: int) -> tuple[str, str]:
    roll = rng.random()
    if roll < 0.2:
        return PLATE_CATEGORY_BLUE, _mock_plate(rng, seq)
    if roll < 0.65:
        return PLATE_CATEGORY_YELLOW, _mock_plate(rng, seq)
    return PLATE_CATEGORY_NEW_ENERGY, _mock_plate_nev(rng, seq)


def _random_expire(rng: random.Random, base: date, *, min_days: int = 30, max_days: int = 365 * 5) -> date:
    return base + timedelta(days=rng.randint(min_days, max_days))


def _fake_id_card_18(rng: random.Random) -> str:
    return "".join(str(rng.randint(0, 9)) for _ in range(18))


def _mock_doc_url(social_code: str, kind: str) -> str:
    return f"https://example.com/mock/social-capacity/{social_code}/{kind}.jpg"


def _exists_phone_or_plate(session: Session, phone: str, plate: str) -> bool:
    with session.no_autoflush:
        phone_hit = session.execute(
            select(SocialCapacity.id).where(
                SocialCapacity.driver_phone == phone,
                SocialCapacity.is_deleted == 0,
            )
        ).first()
        if phone_hit:
            return True
        plate_hit = session.execute(
            select(SocialCapacity.id).where(
                SocialCapacity.plate_number == plate,
                SocialCapacity.is_deleted == 0,
            )
        ).first()
    return plate_hit is not None


def generate_social_capacities(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    accounts_per: int,
    dry_run: bool,
) -> int:
    vtypes = _dict_item_values(session, "vehicle_type", DEFAULT_VEHICLE_TYPES)
    ttypes = _dict_item_values(session, "trailer_type", DEFAULT_TRAILER_TYPES)
    sources = _dict_item_values(session, "social_capacity_source", DEFAULT_SOURCES)

    base_day = date.today()
    phone_base = int(datetime.now().timestamp()) % 100_000_000
    created = 0

    for i in range(count):
        plate_category, plate = _pick_plate(rng, i)
        tail = (phone_base + i * 3 + 17) % 100_000_000
        phone = f"187{tail:08d}"

        if _exists_phone_or_plate(session, phone, plate):
            continue

        social_code = _next_social_code(session)
        name = rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES) + (
            rng.choice(GIVEN_NAMES) if rng.random() < 0.35 else ""
        )
        gender = rng.choice((1, 1, 1, 2))
        id_card = _fake_id_card_18(rng)
        vt = rng.choice(vtypes)
        brand = rng.choice(BRANDS)
        model = f"{brand}{rng.randint(1, 9)}系-{rng.randint(100, 999)}"
        lic_type = rng.choice(LICENSE_TYPES)
        has_trailer = rng.random() < 0.35
        approval_status, status = STATUS_PROFILES[i % len(STATUS_PROFILES)]
        source = rng.choice(sources)
        remark = (
            f"[mockdata] mock_tenant_social_capacities.py "
            f"social_code={social_code} ts={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if dry_run:
            print(
                f"[dry-run] {social_code} {name} {phone} {plate} "
                f"type={vt} trailer={has_trailer} "
                f"approval={approval_status} status={status} accounts={accounts_per}"
            )
            created += 1
            continue

        cap = SocialCapacity(
            social_code=social_code,
            driver_name=name,
            driver_phone=phone,
            driver_id_card=id_card,
            plate_number=plate,
            vehicle_type_label=vt,
            source=source,
            source_remark=rng.choice(SOURCE_REMARKS),
            approval_status=approval_status,
            status=status if approval_status == 2 else 0,
            rating_score=round(rng.uniform(3.0, 5.0), 1) if approval_status == 2 and rng.random() < 0.6 else None,
            rating_level=rng.choice((1, 2, 3, 4)) if approval_status == 2 and rng.random() < 0.5 else None,
            order_count=rng.randint(0, 80) if approval_status == 2 else 0,
            remark=remark,
        )
        session.add(cap)
        session.flush()

        reg = base_day - timedelta(days=rng.randint(365, 365 * 8))
        insp = _random_expire(rng, base_day, min_days=20, max_days=365)
        ins = _random_expire(rng, base_day, min_days=30, max_days=400)
        transport_expire = _random_expire(rng, base_day, min_days=60, max_days=365 * 3)

        vehicle = SocialCapacityVehicle(
            social_capacity_id=cap.id,
            plate_number=plate,
            plate_category=plate_category,
            vehicle_type=vt,
            brand=brand,
            model=model[:50],
            color=rng.choice(COLORS),
            vin=f"LZZ{rng.randint(10**11, 10**12 - 1)}"[:17],
            engine_no=f"ENG{rng.randint(10**8, 10**9 - 1)}",
            load_capacity=Decimal(str(round(rng.uniform(5, 40), 2))),
            volume_capacity=Decimal(str(round(rng.uniform(20, 120), 2))),
            length=Decimal(str(round(rng.uniform(6.0, 17.5), 2))),
            width=Decimal(str(round(rng.uniform(2.3, 2.55), 2))),
            height=Decimal(str(round(rng.uniform(2.8, 4.2), 2))),
            axle_count=rng.randint(2, 6),
            has_trailer=1 if has_trailer else 0,
            trailer_plate=_mock_trailer_plate(rng, i) if has_trailer else None,
            trailer_type=rng.choice(ttypes) if has_trailer else None,
            trailer_load_capacity=Decimal(str(round(rng.uniform(15, 45), 2))) if has_trailer else None,
            registration_date=reg,
            inspection_expire=insp,
            insurance_expire=ins,
            transport_license_no=f"YT{rng.randint(10**8, 10**9 - 1)}"[:20],
            transport_license_expire=transport_expire,
            vehicle_license_photo=_mock_doc_url(social_code, "vehicle_license"),
            vehicle_license_back_photo=_mock_doc_url(social_code, "vehicle_license_back"),
            transport_license_photo=_mock_doc_url(social_code, "transport_license"),
            vehicle_photo=_mock_doc_url(social_code, "vehicle_photo"),
        )
        session.add(vehicle)

        birth = base_day - timedelta(days=rng.randint(365 * 25, 365 * 55))
        lic_issue = base_day - timedelta(days=rng.randint(365 * 3, 365 * 20))
        driver = SocialCapacityDriver(
            social_capacity_id=cap.id,
            name=name,
            gender=gender,
            phone=phone,
            id_card=id_card,
            birth_date=birth,
            avatar=_mock_doc_url(social_code, "avatar"),
            license_type=lic_type,
            license_no=f"{rng.randint(10**11, 10**12 - 1)}"[:18],
            license_issue_date=lic_issue,
            license_expire=_random_expire(rng, base_day),
            license_class=lic_type,
            qualification_no=f"JYPER{rng.randint(10**6, 10**7 - 1)}",
            qualification_expire=_random_expire(rng, base_day),
            license_photo=_mock_doc_url(social_code, "license"),
            qualification_photo=_mock_doc_url(social_code, "qualification"),
            id_card_front_photo=_mock_doc_url(social_code, "id_front"),
            id_card_back_photo=_mock_doc_url(social_code, "id_back"),
            emergency_contact=rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES),
            emergency_phone=f"139{rng.randint(0, 10**8 - 1):08d}",
            home_address=f"Mock省Mock市测试路{rng.randint(1, 999)}号{rng.randint(1, 20)}单元",
        )
        session.add(driver)

        account_specs: list[tuple[int, str, str, str | None, str | None]] = []
        if accounts_per >= 1:
            account_specs.append(
                (
                    1,
                    "主账户",
                    name,
                    f"6222{rng.randint(10**12, 10**13 - 1)}"[:19],
                    rng.choice(BANK_NAMES),
                )
            )
        if accounts_per >= 2:
            account_specs.append(
                (
                    2,
                    "支付宝",
                    name,
                    f"1{rng.randint(30, 39)}{rng.randint(0, 10**9 - 1):09d}",
                    None,
                )
            )
        if accounts_per >= 3:
            account_specs.append(
                (
                    3,
                    "微信",
                    name,
                    f"wx_{social_code.lower()}_{rng.randint(1000, 9999)}",
                    None,
                )
            )
        if accounts_per >= 4:
            account_specs.append(
                (
                    4,
                    "其他",
                    name,
                    f"OTHER-{social_code}-{rng.randint(100, 999)}",
                    None,
                )
            )

        for idx, (acc_type, label, acc_name, acc_no, bank) in enumerate(account_specs):
            session.add(
                SocialCapacityAccount(
                    social_capacity_id=cap.id,
                    account_type=acc_type,
                    account_label=label[:50],
                    account_name=acc_name[:100],
                    account_no=acc_no[:100],
                    bank_name=bank[:100] if bank else None,
                    bank_branch=f"{bank}Mock支行"[:100] if bank else None,
                    holder_id_card=id_card if rng.random() < 0.2 else None,
                    is_default=1 if idx == 0 else 0,
                    status=1,
                    remark=f"[mockdata] {social_code} account#{idx + 1}",
                )
            )

        created += 1

    if not dry_run:
        session.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="向租户库批量插入社会运力 Mock 数据（多表饱和字段）")
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument("--count", type=int, default=20, help="生成条数")
    parser.add_argument(
        "--accounts",
        type=int,
        default=1,
        help="每位社会运力结算账户条数（1~4，默认 1）",
    )
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写库")
    args = parser.parse_args()

    accounts_per = max(1, min(4, args.accounts))

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        n = generate_social_capacities(
            session,
            args.count,
            rng,
            accounts_per=accounts_per,
            dry_run=args.dry_run,
        )

    action = "预览" if args.dry_run else "已写入"
    print(
        f"[OK] 租户 {args.tenant_code}：{action} {n} 条社会运力"
        f"（biz_social_capacity + vehicle + driver + account×{accounts_per}）。"
    )


if __name__ == "__main__":
    main()
