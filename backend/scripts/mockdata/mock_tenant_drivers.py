"""
批量生成自有运力「驾驶员」Mock 数据（写入指定租户库）

脚本路径：backend/scripts/mockdata/mock_tenant_drivers.py

用法（在 backend 目录下执行）:
  python scripts/mockdata/mock_tenant_drivers.py --tenant-code demo --count 30
  python scripts/mockdata/mock_tenant_drivers.py --tenant-code demo --count 5 --dry-run

依赖：与主应用相同的 .env / 环境变量（get_settings().tenant_db_url_sync）。

数据饱和度（按 ORM 业务字段尽量写满）：
- biz_driver：除自增 id / 时间戳 / is_deleted 外，写入 driver_code、name、gender、phone、
  id_card、avatar、emergency_contact、emergency_phone、home_address、status、remark
  （user_id 为可选业务关联，Mock 不伪造外键，保持 NULL）
- biz_driver_license：资质字段 + 四类证件图 URL
- biz_driver_operation：department_id（若有部门）、driver_type、operation_status、
  resident_areas（JSON）、common_routes（文本）
- biz_driver_account：每位司机 3 条（银行卡 / 油气款 / 积分），含 enterprise_id、
  account_type、account_name、account_no、balance、status
- biz_driver_route：每位司机 2 条常跑线路，含 origin/dest code/name、status
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# backend 根目录：.../backend/scripts/mockdata/this_file.py -> parents[2] == backend
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver  # noqa: E402
from app.modules.client.models.capacity.self_capacity.driver.driver_license import (  # noqa: E402
    DriverLicense,
)
from app.modules.client.models.capacity.self_capacity.driver.driver_operation import (  # noqa: E402
    DriverOperation,
)
from app.modules.client.models.capacity.self_capacity.driver.driver_account import (  # noqa: E402
    DriverAccount,
)
from app.modules.client.models.capacity.self_capacity.driver.driver_route import (  # noqa: E402
    DriverRoute,
)
from app.modules.client.models.organization.biz_department import BizDepartment  # noqa: E402


SURNAMES = (
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
)
GIVEN_NAMES = (
    "伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平",
)
LICENSE_TYPES = ("A1", "A2", "B1", "B2", "C1", "C2")

# 与前端 RegionsSelect 常见省市区编码风格一致（仅作测试数据）
ROUTE_PAIRS = (
    ("110000,110100", "北京市", "310000,310100", "上海市"),
    ("330000,330100", "杭州市", "440000,440100", "广州市"),
    ("510000,510100", "成都市", "420000,420100", "武汉市"),
    ("610000,610100", "西安市", "370000,370100", "济南市"),
)


def _next_driver_code(session: Session) -> str:
    year = datetime.now().strftime("%Y")
    prefix = f"D{year}"
    subq = select(Driver.id).where(Driver.driver_code.like(f"{prefix}%")).subquery()
    cnt = session.execute(select(func.count()).select_from(subq)).scalar() or 0
    return f"{prefix}{int(cnt) + 1:04d}"


def _pick_department_ids(session: Session, limit: int) -> list[int]:
    rows = session.execute(
        select(BizDepartment.id).where(BizDepartment.is_deleted == 0).limit(limit)
    ).all()
    return [int(r[0]) for r in rows if r[0] is not None]


def _random_expire(rng: random.Random, base: date) -> date:
    return base + timedelta(days=rng.randint(180, 365 * 5))


def _fake_id_card_18(rng: random.Random) -> str:
    """18 位数字形态（测试用，不保证校验位算法正确）。"""
    return "".join(str(rng.randint(0, 9)) for _ in range(18))


def _mock_avatar_url(driver_code: str) -> str:
    return f"https://example.com/mock/driver/{driver_code}/avatar.jpg"


def _mock_doc_url(driver_code: str, kind: str) -> str:
    return f"https://example.com/mock/driver/{driver_code}/{kind}.jpg"


def _mock_resident_areas(rng: random.Random) -> list[dict[str, str]]:
    pools = (
        ("320000", "320100"),
        ("330000", "330100"),
        ("440000", "440300"),
        ("510000", "510100"),
    )
    p, c = rng.choice(pools)
    return [{"province": p, "city": c}]


def _mock_common_routes(rng: random.Random) -> str:
    routes = (
        "北京-上海;天津-南京",
        "广州-深圳;东莞-佛山",
        "成都-重庆;西安-兰州",
        "武汉-长沙;郑州-石家庄",
    )
    return routes[rng.randint(0, len(routes) - 1)]


def generate_drivers(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> int:
    dept_ids = _pick_department_ids(session, 200)
    base = date.today()
    phone_base = int(datetime.now().timestamp()) % 100_000_000

    created = 0
    for i in range(count):
        name = rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES) + (
            rng.choice(GIVEN_NAMES) if rng.random() < 0.35 else ""
        )
        tail = (phone_base + i) % 100_000_000
        phone = f"188{tail:08d}"

        exists = session.execute(
            select(Driver.id).where(Driver.phone == phone, Driver.is_deleted == 0)
        ).first()
        if exists:
            continue

        driver_code = _next_driver_code(session)
        gender = rng.choice((1, 1, 1, 2))
        dept_id = rng.choice(dept_ids) if dept_ids else None
        driver_type = rng.choice(("own", "own", "outsourced", "temporary"))
        operation_status = rng.choice((1, 1, 2, 3, 4))
        lic_type = rng.choice(LICENSE_TYPES)
        lic_no = f"{rng.randint(10**11, 10**12 - 1)}"[:18]
        qual_no = f"JYPER{rng.randint(10**6, 10**7 - 1)}"
        remark = (
            f"[mockdata] 脚本生成 driver_code={driver_code} "
            f"ts={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if dry_run:
            print(
                f"[dry-run] {driver_code} {name} {phone} "
                f"dept={dept_id} lic={lic_type} routes=2 accounts=3"
            )
            created += 1
            continue

        driver = Driver(
            driver_code=driver_code,
            name=name,
            gender=gender,
            phone=phone,
            id_card=_fake_id_card_18(rng),
            avatar=_mock_avatar_url(driver_code),
            emergency_contact=rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES),
            emergency_phone=f"139{rng.randint(0, 10**8 - 1):08d}",
            home_address=f"Mock省Mock市测试路{rng.randint(1, 999)}号{rng.randint(1, 20)}单元",
            status=1,
            remark=remark[:500] if len(remark) > 500 else remark,
        )
        session.add(driver)
        session.flush()

        lic = DriverLicense(
            driver_id=driver.id,
            license_type=lic_type,
            license_no=lic_no,
            license_expire=_random_expire(rng, base),
            qualification_no=qual_no[:50],
            qualification_expire=_random_expire(rng, base),
            license_photo=_mock_doc_url(driver_code, "license"),
            qualification_photo=_mock_doc_url(driver_code, "qualification"),
            id_card_front_photo=_mock_doc_url(driver_code, "id_front"),
            id_card_back_photo=_mock_doc_url(driver_code, "id_back"),
        )
        session.add(lic)

        resident = _mock_resident_areas(rng)
        common_txt = _mock_common_routes(rng)
        op = DriverOperation(
            driver_id=driver.id,
            department_id=dept_id,
            driver_type=driver_type,
            resident_areas=resident,
            common_routes=common_txt[:500],
            operation_status=operation_status,
        )
        session.add(op)

        # 三类账户各一条，字段写满（enterprise_id 无关联时不填）
        account_specs = (
            (1, "工资卡", lambda: f"6222{rng.randint(10**12, 10**13 - 1)}"[:19], Decimal("12888.66")),
            (2, "油气账户", lambda: f"YQ{driver_code}{rng.randint(1000, 9999)}", Decimal("3500.00")),
            (3, "积分账户", lambda: f"PT{driver.id}{rng.randint(100, 999)}", Decimal("0.00")),
        )
        for acc_type, acc_name, no_fn, bal in account_specs:
            session.add(
                DriverAccount(
                    driver_id=driver.id,
                    enterprise_id=None,
                    account_type=acc_type,
                    account_name=acc_name[:100],
                    account_no=no_fn()[:50],
                    balance=bal,
                    status=1,
                )
            )

        pair_a = ROUTE_PAIRS[i % len(ROUTE_PAIRS)]
        pair_b = ROUTE_PAIRS[(i + 1) % len(ROUTE_PAIRS)]
        for ridx, (oc, on, dc, dn) in enumerate((pair_a, pair_b)):
            session.add(
                DriverRoute(
                    driver_id=driver.id,
                    origin_code=oc[:20],
                    origin_name=on[:100],
                    dest_code=dc[:20],
                    dest_name=dn[:100],
                    status=1 if ridx == 0 else rng.choice((0, 1)),
                )
            )

        created += 1

    if not dry_run:
        session.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="向租户库批量插入驾驶员 Mock 数据（多表饱和字段）")
    parser.add_argument(
        "--tenant-code",
        required=True,
        help="租户编码，与平台侧租户一致，用于解析租户库名",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="计划生成条数（若手机号冲突会自动跳过）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机种子，便于复现同一批数据",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印将要写入的摘要，不写库",
    )
    args = parser.parse_args()

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        n = generate_drivers(session, args.count, rng, dry_run=args.dry_run)

    action = "预览" if args.dry_run else "已写入"
    print(f"[OK] 租户 {args.tenant_code}：{action} {n} 条驾驶员（含 license / operation / account×3 / route×2）。")


if __name__ == "__main__":
    main()
