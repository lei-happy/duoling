"""
批量生成「客户」Mock 数据（写入指定租户库 biz_customer）

与前端新建客户表单一致（partner/customer/components/customer-edit.vue）：
- 必填：customer_name、customer_type(0-4)、settlement_type(0-2)、
  contact_person、contact_phone、status(0/1)
- 选填：customer_code（留空则按 KH+日期+序号 规则生成）、short_name、credit_code、address、remark

路径：backend/scripts/mockdata/mock_tenant_customers.py

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_customers.py --tenant-code demo --count 30
  python scripts/mockdata/mock_tenant_customers.py --tenant-code demo --count 5 --dry-run
  python scripts/mockdata/mock_tenant_customers.py --tenant-code demo --count 10 --auto-code

默认每条记录不传 customer_code，由脚本按与 CustomerService._generate_customer_code 相同规则生成；
加 --auto-code 时由脚本预生成唯一编码（仍遵循 KH 前缀规则，适合 dry-run 预览编码形态）。

依赖：与主应用相同的 .env / 环境变量（get_settings().tenant_db_url_sync）。
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.modules.client.models.partner.customer import Customer  # noqa: E402


REGION_PREFIX = ("华东", "华南", "华北", "西南", "西北", "华中", "东北")
INDUSTRY = (
    "汽车物流",
    "零部件贸易",
    "整车经销",
    "冷链运输",
    "城配",
    "大宗",
    "跨境",
    "仓储",
)
ORG_SUFFIX = ("有限公司", "股份有限公司", "集团", "供应链公司", "贸易公司")

BRAND_PREFIX = (
    "顺达", "宏泰", "远航", "金穗", "联众", "汇通", "迅捷", "安达",
    "城际", "恒通", "嘉禾", "瑞丰", "德信", "新程", "众诚", "华通",
)

CITY_PREFIX = ("上海", "北京", "广州", "杭州", "成都", "深圳", "武汉", "西安", "南京", "苏州")

SURNAMES = (
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
)
GIVEN_NAMES = (
    "伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平",
)

CITIES = (
    "上海市浦东新区",
    "北京市朝阳区",
    "广州市天河区",
    "深圳市南山区",
    "杭州市余杭区",
    "成都市高新区",
    "武汉市东湖高新区",
    "西安市雁塔区",
)


def _next_customer_code(session: Session) -> str:
    """与 CustomerService._generate_customer_code 逻辑一致的同步版本。"""
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"KH{today}"
    result = session.execute(
        select(Customer.customer_code)
        .where(
            Customer.customer_code.isnot(None),
            Customer.customer_code.like(f"{prefix}%"),
            Customer.is_deleted == 0,
        )
        .order_by(Customer.customer_code.desc())
        .limit(1)
    )
    last_code = result.scalar_one_or_none()
    if last_code and len(last_code) > len(prefix):
        try:
            seq = int(last_code[len(prefix) :]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"


def _fake_credit_code_18(rng: random.Random) -> str:
    """测试用 18 位统一社会信用代码形态（数字 + 大写字母，非严格校验）。"""
    chars = "0123456789ABCDEFGHJKLMNPQRTUWXY"
    return "".join(rng.choice(chars) for _ in range(18))


def _compose_customer_display_name(rng: random.Random) -> str:
    """纯中文客户名称（公司/组织风格），不含 mock 标识或数字盐值。"""
    if rng.random() < 0.55:
        core = (
            f"{rng.choice(REGION_PREFIX)}{rng.choice(INDUSTRY)}"
            f"{rng.choice(ORG_SUFFIX)}"
        )
    else:
        core = (
            f"{rng.choice(BRAND_PREFIX)}{rng.choice(INDUSTRY)}"
            f"{rng.choice(ORG_SUFFIX)}"
        )
    if rng.random() < 0.35:
        return f"{rng.choice(CITY_PREFIX)}{core}"
    return core


def _unique_customer_name(
    session: Session,
    rng: random.Random,
    used_this_run: set[str],
) -> str:
    """与库内未删除记录及本脚本本次已用名不重复（服务层按名称唯一）。"""
    for _ in range(120):
        name = _compose_customer_display_name(rng)[:100]
        if name in used_this_run:
            continue
        exists = session.execute(
            select(Customer.id).where(
                Customer.customer_name == name,
                Customer.is_deleted == 0,
            )
        ).first()
        if not exists:
            used_this_run.add(name)
            return name
    raise RuntimeError(
        "无法在限定次数内生成唯一客户名称，请减小 --count、更换 --seed 或清理库内重名数据。"
    )


def generate_customers(
    session: Session,
    count: int,
    rng: random.Random,
    *,
    dry_run: bool,
    auto_code: bool,
) -> int:
    created = 0
    used_names: set[str] = set()
    for i in range(count):
        customer_name = _unique_customer_name(session, rng, used_names)
        short_name = customer_name[:20]
        customer_type = rng.randint(0, 4)
        settlement_type = rng.randint(0, 2)
        contact_person = rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES) + (
            rng.choice(GIVEN_NAMES) if rng.random() < 0.3 else ""
        )
        # 11 位手机号形态（第二位 3-9）
        phone_body = (int(datetime.now().timestamp()) + i * 7919) % 10**9
        contact_phone = f"1{rng.randint(3, 9)}{phone_body:09d}"
        status = rng.choice((1, 1, 1, 0))  # 多数正常
        address = f"{rng.choice(CITIES)}测试路{rng.randint(1, 999)}号"
        credit_code = _fake_credit_code_18(rng)
        remark = (
            f"脚本批量生成 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            f"type={customer_type} settlement={settlement_type}"
        )

        code: str | None
        if auto_code:
            code = _next_customer_code(session)
        else:
            code = None

        if dry_run:
            code_disp = code or "(入库时按 KH+日期+序号 生成)"
            name_disp = (
                customer_name if len(customer_name) <= 40 else f"{customer_name[:40]}…"
            )
            print(
                f"[dry-run] name={name_disp} code={code_disp} "
                f"type={customer_type} settlement={settlement_type} "
                f"contact={contact_person} phone={contact_phone} status={status}"
            )
            created += 1
            continue

        if not auto_code:
            code = _next_customer_code(session)

        customer = Customer(
            customer_code=code,
            customer_name=customer_name[:100],
            short_name=short_name[:50] if short_name else None,
            customer_type=customer_type,
            contact_person=contact_person[:50],
            contact_phone=contact_phone[:20],
            address=address[:255],
            settlement_type=settlement_type,
            credit_code=credit_code[:50],
            status=status,
            remark=remark[:2000] if len(remark) > 2000 else remark,
        )
        session.add(customer)
        session.flush()
        created += 1

    if not dry_run:
        session.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(
        description="向租户库批量插入客户 Mock 数据（biz_customer，字段与前端新建表单一致）"
    )
    parser.add_argument(
        "--tenant-code",
        required=True,
        help="租户编码，与平台侧租户一致，用于解析租户库名",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="生成条数",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机种子，便于复现",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印摘要，不写库",
    )
    parser.add_argument(
        "--auto-code",
        action="store_true",
        help="写入前为每条预分配 customer_code（与后台 KH 规则一致）；默认在 flush 前再取号",
    )
    args = parser.parse_args()

    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        n = generate_customers(
            session,
            args.count,
            rng,
            dry_run=args.dry_run,
            auto_code=args.auto_code,
        )

    action = "预览" if args.dry_run else "已写入"
    print(f"[OK] 租户 {args.tenant_code}：{action} {n} 条客户（biz_customer）。")


if __name__ == "__main__":
    main()
