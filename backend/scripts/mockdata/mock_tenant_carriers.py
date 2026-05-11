"""
批量生成「承运商 + 结算账户」Mock 数据（biz_carrier + biz_carrier_settlement）

对齐前端 partner/carrier：
- carrier-edit.vue 基础信息：carrier_type(0 公司 / 1 个体 / 2 其他)、carrier_name、
  short_name、carrier_code（可选）、contact_person、contact_phone（租户内唯一）、
  contact_email、公司 credit_code + legal_person / 个体 id_card_no、address、
  province/city/district（可选）、cooperation_start_date、status(0/1/2)、remark
- carrier-settlement-edit.vue：每条结算账户 account_label、account_type、settlement_type、
  settlement_period、bank_*、applicable_scope、is_default、status、sort_order、remark、
  settlement_day、swift_code、tax_rate（模型支持则写入）

后端约束（CarrierService）：
- contact_phone 同租户内不可重复
- 创建时 settlements 中至多一条 is_default=1（脚本仅将第一条设为默认）

路径：backend/scripts/mockdata/mock_tenant_carriers.py

用法（在 backend 目录下）:
  python scripts/mockdata/mock_tenant_carriers.py --tenant-code demo --count 20
  python scripts/mockdata/mock_tenant_carriers.py --tenant-code demo --count 5 --dry-run
  python scripts/mockdata/mock_tenant_carriers.py --tenant-code demo --count 10 --accounts 3

可选：--seed、--accounts（每位承运商结算账户条数，默认 2，范围 1~8）
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
from app.modules.client.models.partner.carrier import Carrier  # noqa: E402
from app.modules.client.models.partner.carrier_settlement import (  # noqa: E402
    CarrierSettlement,
)


# 与前端 carrier-edit.vue USCC_PATTERN 一致：2 位 + 6 位数字 + 10 位
_USCC_CHARS = "0123456789ABCDEFGHJKLMNPQRTUWXY"

SURNAMES = (
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
)
GIVEN_NAMES = (
    "伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平",
)

CARRIER_NAME_SUFFIX = (
    "物流有限公司",
    "运输车队",
    "供应链承运部",
    "货运服务部",
    "快运车队",
    "个体运输户",
)

BANK_NAMES = ("中国工商银行", "中国建设银行", "中国农业银行", "中国银行", "交通银行", "招商银行")
BANK_BRANCHES = ("某某支行", "高新支行", "开发区支行", "营业部")


def _mock_uscc18(rng: random.Random) -> str:
    """18 位统一社会信用代码，满足前端 /^[0-9A-HJ-NPQRTUWXY]{2}\\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/i"""
    head = rng.choice(_USCC_CHARS) + rng.choice(_USCC_CHARS)
    mid = f"{rng.randint(100000, 999999)}"
    tail = "".join(rng.choice(_USCC_CHARS) for _ in range(10))
    return (head + mid + tail).upper()


def _id_card_18_checksum(body17: str) -> str:
    """大陆 18 位身份证末位校验码。"""
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    s = sum(int(body17[i]) * weights[i] for i in range(17))
    return "10X98765432"[s % 11]


def _mock_id_card_18(rng: random.Random, seq: int) -> str:
    """可过前端大陆 18 位身份证正则的测试号（非真实人口库）。"""
    area = rng.choice(("110101", "310101", "440106", "330106", "510104"))
    year = rng.randint(1975, 2000)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    birth = f"{year:04d}{month:02d}{day:02d}"
    seq3 = f"{(seq * 17 + rng.randint(0, 997)) % 1000:03d}"
    body17 = f"{area}{birth}{seq3}"
    return body17 + _id_card_18_checksum(body17)


def _next_carrier_code(session: Session) -> str:
    """租户内递增承运商编码（Mock 专用前缀 CB + 日期 + 序号）。"""
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"CB{today}"
    last = session.execute(
        select(Carrier.carrier_code)
        .where(
            Carrier.carrier_code.isnot(None),
            Carrier.carrier_code.like(f"{prefix}%"),
            Carrier.is_deleted == 0,
        )
        .order_by(Carrier.carrier_code.desc())
        .limit(1)
    ).scalar_one_or_none()
    if last and len(last) > len(prefix):
        try:
            seq = int(last[len(prefix) :]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


def _alloc_unique_phone(session: Session, rng: random.Random, idx: int) -> str:
    """分配租户内未占用的 11 位手机号。"""
    for _ in range(500):
        body = (int(datetime.now().timestamp() * 1000) + idx * 9973 + rng.randint(0, 99999)) % 10**9
        phone = f"1{rng.randint(3, 9)}{body:09d}"
        exists = session.execute(
            select(Carrier.id).where(
                Carrier.contact_phone == phone,
                Carrier.is_deleted == 0,
            )
        ).first()
        if not exists:
            return phone
        idx += 1000
    raise RuntimeError("无法分配唯一联系电话，请减小 --count 或清理库内数据")


def _unique_carrier_name(rng: random.Random, seq: int) -> str:
    salt = rng.randint(1000, 9999)
    ts = datetime.now().strftime("%H%M%S")
    base = rng.choice(CARRIER_NAME_SUFFIX)
    return f"[mockdata]承运商-{base}-{ts}-{seq:04d}-{salt}"


def _mock_settlements(
    rng: random.Random,
    carrier_id: int,
    count: int,
) -> list[CarrierSettlement]:
    rows: list[CarrierSettlement] = []
    for j in range(count):
        stype = rng.choice((0, 0, 1, 2, 3))
        period = None
        if stype in (0, 3):
            period = rng.randint(7, 45)
        settlement_day = rng.randint(1, 28) if stype == 0 and rng.random() < 0.5 else None
        is_def = 1 if j == 0 else 0
        label = (
            "对公主账户" if j == 0 and rng.random() < 0.6 else f"账户-{j + 1}-{rng.choice(('干线', '城配', '临时'))}"
        )
        acc_type = rng.choice((0, 0, 1, 2))
        bank = rng.choice(BANK_NAMES)
        branch = f"{rng.choice(('上海', '北京', '广州', '杭州', '成都'))}{rng.choice(BANK_BRANCHES)}"
        acct_no = f"6222{rng.randint(10**11, 10**12 - 1)}"[:19]
        acct_name = rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES) + (
            "公司" if acc_type == 0 else ""
        )
        rows.append(
            CarrierSettlement(
                carrier_id=carrier_id,
                account_label=label[:50],
                account_type=acc_type,
                settlement_type=stype,
                settlement_period=period,
                settlement_day=settlement_day,
                bank_name=bank[:100],
                bank_branch=branch[:100],
                bank_account=acct_no[:50],
                bank_account_name=(acct_name or "测试户名")[:100],
                swift_code=f"{rng.randint(100000, 999999)}"[:20],
                tax_rate=Decimal(str(round(rng.uniform(0, 13), 2))),
                applicable_scope=rng.choice(
                    (
                        "华东干线 17.5m 厢车",
                        "城配业务线",
                        "冷链全车型",
                        "大宗煤炭线路",
                    )
                )[:255],
                is_default=is_def,
                status=1 if j == 0 or rng.random() < 0.85 else 0,
                sort_order=j,
                remark=f"[mockdata] settlement #{j + 1} carrier_id={carrier_id}",
            )
        )
    return rows


def generate_carriers(
    session: Session,
    count: int,
    accounts_per_carrier: int,
    rng: random.Random,
    *,
    dry_run: bool,
) -> tuple[int, int]:
    """返回 (承运商条数, 结算账户条数)。"""
    carriers_done = 0
    settlements_done = 0
    for i in range(count):
        carrier_type = rng.choices((0, 1, 2), weights=(0.45, 0.45, 0.10), k=1)[0]
        carrier_name = _unique_carrier_name(rng, i)[:100]
        short_name = carrier_name.replace("[mockdata]", "")[:20]
        carrier_code = _next_carrier_code(session)
        contact_person = rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES)
        contact_phone = _alloc_unique_phone(session, rng, i)
        contact_email = f"mock_carrier_{carrier_code.lower()}@example.com"[:100]

        credit_code = None
        id_card_no = None
        legal_person = None
        if carrier_type == 0:
            credit_code = _mock_uscc18(rng)[:50]
            legal_person = (rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES))[:50]
        else:
            id_card_no = _mock_id_card_18(rng, i)[:20]

        province = rng.choice(("上海市", "北京市", "广东省", "浙江省", "四川省"))[:50]
        city = rng.choice(("市辖区", "广州市", "杭州市", "深圳市", "成都市"))[:50]
        district = rng.choice(("浦东新区", "朝阳区", "天河区", "余杭区", "高新区"))[:50]
        address = f"{province}{city}{district}测试大道{rng.randint(1, 888)}号"[:255]

        coop_days = rng.randint(30, 365 * 5)
        cooperation_start_date = date.today() - timedelta(days=coop_days)
        status = rng.choices((0, 1, 2), weights=(0.08, 0.87, 0.05), k=1)[0]

        remark = (
            f"[mockdata] biz_carrier ts={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            f"type={carrier_type} settlements={accounts_per_carrier}"
        )

        if dry_run:
            fake_phone = f"1{rng.randint(3, 9)}*********"
            print(
                f"[dry-run] name={carrier_name[:40]}... phone≈{fake_phone} "
                f"type={carrier_type} credit={credit_code or '-'} idcard={id_card_no or '-'} "
                f"accounts={accounts_per_carrier}"
            )
            carriers_done += 1
            settlements_done += accounts_per_carrier
            continue

        carrier = Carrier(
            carrier_code=carrier_code,
            carrier_name=carrier_name,
            short_name=short_name,
            carrier_type=carrier_type,
            credit_code=credit_code,
            id_card_no=id_card_no,
            legal_person=legal_person,
            contact_person=contact_person[:50],
            contact_phone=contact_phone[:20],
            contact_email=contact_email,
            province=province,
            city=city,
            district=district,
            address=address,
            cooperation_start_date=cooperation_start_date,
            status=status,
            invite_status=0,
            linked_tenant_code=None,
            rating_score=round(rng.uniform(3.0, 5.0), 1),
            rating_level=rng.choice((1, 2, 2, 3)),
            last_evaluated_at=datetime.now() - timedelta(days=rng.randint(1, 90)),
            capacity_summary={"mock": True, "vehicles": rng.randint(1, 50), "drivers": rng.randint(1, 80)},
            remark=remark[:2000] if len(remark) > 2000 else remark,
        )
        session.add(carrier)
        session.flush()

        settlements = _mock_settlements(rng, int(carrier.id), accounts_per_carrier)
        for s in settlements:
            session.add(s)
        session.flush()

        carriers_done += 1
        settlements_done += len(settlements)

    if not dry_run:
        session.commit()
    return carriers_done, settlements_done


def main() -> None:
    parser = argparse.ArgumentParser(
        description="向租户库批量插入承运商及结算账户 Mock（biz_carrier + biz_carrier_settlement）"
    )
    parser.add_argument("--tenant-code", required=True, help="租户编码")
    parser.add_argument("--count", type=int, default=15, help="承运商条数")
    parser.add_argument(
        "--accounts",
        type=int,
        default=2,
        help="每位承运商附带的结算账户条数（1~8，首条 is_default=1）",
    )
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不写库")
    args = parser.parse_args()

    acc_n = max(1, min(8, args.accounts))
    settings = get_settings()
    url = settings.tenant_db_url_sync(args.tenant_code)
    rng = random.Random(args.seed)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        nc, ns = generate_carriers(
            session,
            args.count,
            acc_n,
            rng,
            dry_run=args.dry_run,
        )

    action = "预览" if args.dry_run else "已写入"
    print(
        f"[OK] 租户 {args.tenant_code}：{action} {nc} 条承运商，"
        f"约 {ns} 条结算账户（每位 {acc_n} 条）。"
    )


if __name__ == "__main__":
    main()
