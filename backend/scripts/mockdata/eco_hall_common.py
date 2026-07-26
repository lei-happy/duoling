"""货源/运力大厅 Mock 脚本的共用工具（勿单独执行）。

大厅挂牌落在**平台库** ``sys_eco_*``，与本目录其它 ``mock_tenant_*``（租户库）不同。
大厅列表会排除当前登录租户自己的挂牌，因此脚本会：
  - 用 ``--tenant-code`` 写一部分「我发布的」
  - 再写一批其它发布方（真实其它租户或合成 mock 企业）供大厅浏览
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
import random

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.client.services.ecosystem.visibility import mask_company_name
from app.modules.console.models.ecosystem.constants import (
    AuditStatus,
    PostNoPrefix,
    PostStatus,
    PostType,
    SourceType,
)
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile
from app.modules.console.models.tenant.tenant import Tenant

# 商品车运输常见线路（省, 市）
CITY_POOL: tuple[tuple[str, str], ...] = (
    ("浙江省", "杭州市"),
    ("浙江省", "宁波市"),
    ("上海市", "上海市"),
    ("江苏省", "南京市"),
    ("江苏省", "苏州市"),
    ("广东省", "广州市"),
    ("广东省", "深圳市"),
    ("广东省", "东莞市"),
    ("四川省", "成都市"),
    ("重庆市", "重庆市"),
    ("湖北省", "武汉市"),
    ("湖南省", "长沙市"),
    ("河南省", "郑州市"),
    ("山东省", "济南市"),
    ("山东省", "青岛市"),
    ("北京市", "北京市"),
    ("天津市", "天津市"),
    ("陕西省", "西安市"),
    ("福建省", "厦门市"),
    ("安徽省", "合肥市"),
    ("江西省", "南昌市"),
    ("云南省", "昆明市"),
    ("贵州省", "贵阳市"),
    ("广西壮族自治区", "南宁市"),
    ("辽宁省", "沈阳市"),
)

BRANDS: tuple[tuple[str, str], ...] = (
    ("比亚迪", "汉"),
    ("比亚迪", "唐"),
    ("特斯拉", "Model 3"),
    ("特斯拉", "Model Y"),
    ("理想", "L7"),
    ("理想", "L9"),
    ("问界", "M7"),
    ("小鹏", "P7"),
    ("蔚来", "ET5"),
    ("吉利", "星越 L"),
    ("长安", "UNI-V"),
    ("丰田", "凯美瑞"),
    ("本田", "雅阁"),
    ("大众", "帕萨特"),
    ("宝马", "3系"),
)

TRUCK_TYPES = ("板车", "轿运车", "中置轴", "厢式货车", "高栏车")
SLOT_COUNTS = (6, 7, 8, 9, 10, 12)

SURNAMES = (
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
)

# 合成发布方（库内其它租户不足时使用，仅作大厅展示身份）
SYNTHETIC_OWNERS: tuple[tuple[str, str], ...] = (
    ("mock_eco_hz", "杭州速达物流有限公司"),
    ("mock_eco_cd", "成都畅通汽车运输有限公司"),
    ("mock_eco_gz", "广州华南轿运服务有限公司"),
    ("mock_eco_wh", "武汉楚天运力有限公司"),
    ("mock_eco_xa", "西安丝路物流有限公司"),
    ("mock_eco_nj", "南京江宁运输有限公司"),
    ("mock_eco_sz", "深圳湾区供应链有限公司"),
    ("mock_eco_qd", "青岛港联物流有限公司"),
)


@dataclass(frozen=True)
class OwnerIdentity:
    tenant_code: str
    tenant_name: str
    masked_name: str
    contact_name: str
    contact_phone: str


def open_platform_session() -> tuple[object, Session]:
    """返回 (engine, session)，调用方负责关闭 engine。"""
    settings = get_settings()
    engine = create_engine(settings.platform_db_url_sync, echo=False)
    return engine, Session(engine)


def load_tenant(session: Session, tenant_code: str) -> Tenant:
    row = session.execute(
        select(Tenant).where(
            Tenant.tenant_code == tenant_code,
            Tenant.is_deleted == 0,
        )
    ).scalar_one_or_none()
    if row is None:
        raise RuntimeError(
            f"平台库未找到租户编码 {tenant_code!r}（sys_tenant），请确认编码与环境"
        )
    return row


def next_post_no(
    session: Session,
    post_type: int,
    *,
    today: Optional[date] = None,
    offset: int = 0,
) -> str:
    """同步取号：前缀 + yyyyMMdd + 4 位日流水（与 EcoNumberService 规则一致，仅走库内水位）。

    ``offset`` 用于 dry-run 连续预览（未落库时库内水位不变，靠偏移区分多条）。
    """
    prefix = (
        PostNoPrefix.CARGO_POST
        if int(post_type) == PostType.CARGO
        else PostNoPrefix.CAPACITY_POST
    )
    day = (today or date.today()).strftime("%Y%m%d")
    head = f"{prefix}{day}"
    rows = session.execute(
        select(SysEcoPost.post_no).where(SysEcoPost.post_no.like(f"{head}%"))
    ).scalars().all()
    max_seq = 0
    head_len = len(head)
    for no in rows:
        if not no or len(no) <= head_len:
            continue
        tail = no[head_len:]
        if tail.isdigit():
            max_seq = max(max_seq, int(tail))
    seq = max_seq + 1 + max(0, offset)
    if seq > 9999:
        raise RuntimeError(f"{prefix} 当日编号已达上限 9999")
    return f"{head}{seq:04d}"


def ensure_owner_profile(
    session: Session,
    owner: OwnerIdentity,
    rng: random.Random,
    *,
    dry_run: bool,
) -> None:
    """确保发布方有名片（hall_enabled=1）与信誉样本，便于大厅筛选「认证/优质」。"""
    if dry_run:
        return

    profile = session.execute(
        select(SysEcoTenantProfile).where(
            SysEcoTenantProfile.tenant_code == owner.tenant_code,
            SysEcoTenantProfile.is_deleted == 0,
        )
    ).scalar_one_or_none()
    if profile is None:
        session.add(
            SysEcoTenantProfile(
                tenant_code=owner.tenant_code,
                display_name=owner.tenant_name,
                masked_name=owner.masked_name,
                contact_name=owner.contact_name,
                contact_phone=owner.contact_phone,
                license_verified=1,
                license_verified_at=datetime.now(),
                realname_verified=1,
                hall_enabled=1,
                fleet_size=rng.randint(8, 80),
                intro="[mockdata] 服务平台大厅模拟企业名片",
            )
        )
    else:
        profile.hall_enabled = 1
        if not profile.masked_name:
            profile.masked_name = owner.masked_name
        if int(profile.license_verified or 0) != 1:
            profile.license_verified = 1
            profile.license_verified_at = datetime.now()

    credit = session.execute(
        select(SysEcoTenantCredit).where(
            SysEcoTenantCredit.tenant_code == owner.tenant_code,
            SysEcoTenantCredit.is_deleted == 0,
        )
    ).scalar_one_or_none()
    if credit is None:
        deal_completed = rng.randint(5, 40)
        eval_count = rng.randint(3, 30)
        avg = Decimal(str(round(rng.uniform(4.3, 5.0), 2)))
        session.add(
            SysEcoTenantCredit(
                tenant_code=owner.tenant_code,
                publish_count=rng.randint(deal_completed, deal_completed + 20),
                listed_count=rng.randint(deal_completed, deal_completed + 15),
                deal_count=deal_completed + rng.randint(0, 5),
                deal_completed_count=deal_completed,
                complete_rate=Decimal(str(round(rng.uniform(90.0, 99.5), 2))),
                eval_count=eval_count,
                eval_score_sum=int(avg * eval_count * 100) // 100,
                avg_score=avg,
                avg_respond_minutes=rng.choice((30, 60, 90, 120)),
                last_calc_at=datetime.now(),
            )
        )


def resolve_owners(
    session: Session,
    primary: Tenant,
    rng: random.Random,
    *,
    dry_run: bool,
    extra_owner_limit: int = 8,
) -> list[OwnerIdentity]:
    """主租户 + 其它发布方。其它优先取真实租户，不足则用合成 mock 企业。"""
    owners: list[OwnerIdentity] = []
    primary_owner = _identity_from_tenant(primary, rng)
    owners.append(primary_owner)
    ensure_owner_profile(session, primary_owner, rng, dry_run=dry_run)

    others = session.execute(
        select(Tenant).where(
            Tenant.is_deleted == 0,
            Tenant.status == 1,
            Tenant.tenant_code != primary.tenant_code,
        ).limit(extra_owner_limit)
    ).scalars().all()

    for t in others:
        ident = _identity_from_tenant(t, rng)
        owners.append(ident)
        ensure_owner_profile(session, ident, rng, dry_run=dry_run)

    if len(owners) < 3:
        for code, name in SYNTHETIC_OWNERS:
            if any(o.tenant_code == code for o in owners):
                continue
            ident = OwnerIdentity(
                tenant_code=code,
                tenant_name=name,
                masked_name=mask_company_name(name),
                contact_name=_random_person(rng),
                contact_phone=_random_phone(rng),
            )
            owners.append(ident)
            ensure_owner_profile(session, ident, rng, dry_run=dry_run)
            if len(owners) >= 3 + min(4, extra_owner_limit):
                break

    if not dry_run:
        session.flush()
    return owners


def pick_route(rng: random.Random) -> tuple[tuple[str, str], tuple[str, str]]:
    """随机起讫地，保证不同城。"""
    a, b = rng.sample(CITY_POOL, 2)
    return a, b


def pick_owner_for_index(
    owners: list[OwnerIdentity],
    index: int,
    total: int,
    rng: random.Random,
) -> OwnerIdentity:
    """约 30% 归主租户（我发布的），其余归其它方（大厅可见）。"""
    primary = owners[0]
    others = owners[1:] or owners
    mine_quota = max(1, total // 3)
    if index < mine_quota:
        return primary
    return rng.choice(others)


def build_listed_times(
    rng: random.Random, *, valid_days: int = 7
) -> dict:
    """生成展示中挂牌所需时间字段。"""
    now = datetime.now().replace(microsecond=0)
    listed_at = now - timedelta(hours=rng.randint(1, 72))
    window_start = now + timedelta(hours=rng.randint(6, 96))
    window_end = window_start + timedelta(hours=rng.choice((0, 12, 24, 48)))
    if rng.random() < 0.25:
        window_end = None  # 长期可用/时间可协商场景
    valid_until = now + timedelta(days=valid_days)
    return {
        "now": now,
        "listed_at": listed_at,
        "last_active_at": listed_at + timedelta(hours=rng.randint(0, 12)),
        "window_start": window_start,
        "window_end": window_end,
        "valid_from": listed_at,
        "valid_until": valid_until,
    }


def base_post_kwargs(
    *,
    post_no: str,
    post_type: int,
    owner: OwnerIdentity,
    title: str,
    from_prov: str,
    from_city: str,
    to_prov: Optional[str],
    to_city: Optional[str],
    any_direction: int,
    times: dict,
    total_quantity: int,
    price_type: int,
    price_amount: Optional[Decimal],
    cooperation_type: int,
    rng: random.Random,
) -> dict:
    from_name = f"{from_prov}{from_city}"
    to_name = None
    if to_prov and to_city:
        to_name = f"{to_prov}{to_city}"
    return dict(
        post_no=post_no,
        post_type=post_type,
        owner_tenant_code=owner.tenant_code,
        owner_tenant_name=owner.tenant_name,
        owner_masked_name=owner.masked_name,
        publisher_name=owner.contact_name,
        title=title,
        status=PostStatus.LISTED,
        is_top=1 if rng.random() < 0.08 else 0,
        source_type=SourceType.MANUAL,
        source_id=None,
        valid_from=times["valid_from"],
        valid_until=times["valid_until"],
        from_province=from_prov,
        from_city=from_city,
        from_name=from_name,
        to_province=to_prov,
        to_city=to_city,
        to_name=to_name,
        any_direction=any_direction,
        window_start=times["window_start"],
        window_end=times["window_end"],
        total_quantity=total_quantity,
        quantity_unit="台",
        remaining_quantity=total_quantity if rng.random() < 0.4 else None,
        price_type=price_type,
        price_amount=price_amount,
        price_include_tax=rng.choice((0, 1)),
        price_negotiable=1 if price_type == 4 or rng.random() < 0.5 else 0,
        cooperation_type=cooperation_type,
        contact_name=owner.contact_name,
        contact_phone=owner.contact_phone,
        visibility_level=2,
        contact_visibility=3,
        apply_block_rule=1,
        view_count=rng.randint(0, 120),
        viewer_count=rng.randint(0, 40),
        intent_count=rng.randint(0, 8),
        audit_status=AuditStatus.WHITELIST_PASS,
        submitted_at=times["listed_at"],
        audit_at=times["listed_at"],
        listed_at=times["listed_at"],
        last_active_at=times["last_active_at"],
    )


def _identity_from_tenant(tenant: Tenant, rng: random.Random) -> OwnerIdentity:
    name = tenant.tenant_name or tenant.short_name or f"租户{tenant.tenant_code}"
    contact = tenant.contact_person or _random_person(rng)
    phone = tenant.contact_phone or _random_phone(rng)
    return OwnerIdentity(
        tenant_code=tenant.tenant_code,
        tenant_name=name,
        masked_name=mask_company_name(name),
        contact_name=contact,
        contact_phone=phone,
    )


def _random_person(rng: random.Random) -> str:
    return f"{rng.choice(SURNAMES)}{rng.choice(('伟', '强', '军', '涛', '明', '超', '杰', '芳', '敏', '静'))}"


def _random_phone(rng: random.Random) -> str:
    # 假号段，仅 mock；避免与真实号段大量撞车
    return f"138{rng.randint(1000, 9999):04d}{rng.randint(1000, 9999):04d}"[:11]
