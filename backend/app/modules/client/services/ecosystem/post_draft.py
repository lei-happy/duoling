"""挂牌草稿：发布流程的类型无关中间表示

两个大厅的发布入口不同（任务单 / 运力档案 / 手工），但落库动作完全一样。
把「读源单、算字段」和「写库」之间切一刀，用本模块的 ``PostDraft`` 衔接：

    任务单  ─┐
    运力档案 ─┼→ XxxDraftBuilder → PostDraft → EcoPublishService._persist → 平台库 + 租户库
    手工表单 ─┘

这样落库内核里就不需要出现 ``if post_type == 1``（01.架构与撮合内核设计.md §4.1
的硬约定），货源与运力的差异全部收敛在各自的 Builder 与 ``ext`` 字段里。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.modules.client.services.ecosystem.content_guard import (
    PrecheckInput,
    PrecheckResult,
    run_precheck,
)
from app.modules.console.models.ecosystem.constants import (
    CooperationType,
    PostType,
    PriceType,
    SourceType,
)


@dataclass
class DestDraft:
    """目的地 / 期望流向

    货源也要写一行（终点），这样大厅筛选对两个大厅完全同构。
    """

    province: str
    city: Optional[str] = None
    region_code: Optional[int] = None
    sort_order: int = 0


@dataclass
class PostDraft:
    """一条待落库的挂牌

    ``ext`` 是扩展表字段字典（货源→``sys_eco_cargo_post``，
    运力→``sys_eco_capacity_post``），由 Builder 按类型填好，内核只负责透传。
    """

    post_type: int
    source_type: int = SourceType.MANUAL
    source_id: Optional[int] = None

    title: str = ""

    # ===== 线路 =====
    from_province: Optional[str] = None
    from_city: Optional[str] = None
    from_district: Optional[str] = None
    from_region_code: Optional[int] = None
    from_name: Optional[str] = None
    to_province: Optional[str] = None
    to_city: Optional[str] = None
    to_district: Optional[str] = None
    to_region_code: Optional[int] = None
    to_name: Optional[str] = None
    any_direction: int = 0
    destinations: List[DestDraft] = field(default_factory=list)

    # ===== 时间窗与有效期 =====
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    valid_days: int = 7

    # ===== 数量 =====
    total_quantity: Optional[int] = None
    quantity_unit: str = "台"
    remaining_quantity: Optional[int] = None

    # ===== 价格 =====
    price_type: int = PriceType.NEGOTIABLE
    price_amount: Optional[Decimal] = None
    price_include_tax: int = 0
    price_negotiable: int = 1

    # ===== 合作 =====
    cooperation_type: int = CooperationType.ONCE
    keep_listed_after_deal: int = 0

    # ===== 联系方式 =====
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_backup: Optional[str] = None

    # ===== 可见性 =====
    visibility_level: int = 2
    contact_visibility: int = 3
    apply_block_rule: int = 1
    extra_block_tenants: Optional[List[str]] = None

    # ===== 扩展表字段 =====
    ext: Dict[str, Any] = field(default_factory=dict)

    # ===== 预检素材（不落库）=====
    # {"标题": "...", "其他要求": "..."}：带字段名才能告诉用户是哪一栏有问题
    guard_texts: Dict[str, str] = field(default_factory=dict)
    guard_cargo_name: Optional[str] = None
    expired_licenses: List[str] = field(default_factory=list)
    # 已过期但不拦截的证照，只交人工审核关注
    soft_expired_licenses: List[str] = field(default_factory=list)
    # 源单快照时间，为空则取发布时刻
    source_snapshot_at: Optional[datetime] = None

    @property
    def is_cargo(self) -> bool:
        return int(self.post_type) == PostType.CARGO

    def primary_dest(self) -> Optional[DestDraft]:
        """主目的地：sort_order 最小的那个"""
        if not self.destinations:
            return None
        return sorted(self.destinations, key=lambda d: d.sort_order)[0]

    def sync_primary_dest(self) -> None:
        """把主目的地回填到主表的 ``to_*`` 字段

        主表冗余主目的地是为了列表页展示时不用连 ``sys_eco_post_dest``。
        Builder 只需要维护 ``destinations`` 一处，避免两处各填一遍写歪。
        """
        if self.any_direction:
            # 接受任意流向时主表不写目的地，筛选靠 any_direction 兜住
            self.to_province = None
            self.to_city = None
            self.to_district = None
            self.to_region_code = None
            return
        dest = self.primary_dest()
        if dest is None:
            return
        self.to_province = dest.province
        self.to_city = dest.city
        if dest.region_code is not None:
            self.to_region_code = dest.region_code


def run_draft_precheck(
    draft: PostDraft, precheck: Optional[PrecheckInput], now: datetime
) -> PrecheckResult:
    """用草稿里的素材跑预检

    发布与编辑两条链路都要跑同一套预检，判定素材的来源分工也必须一致：
    **线路、时间、文本、证照以草稿为准，调用方只负责提供需要查库的事实**
    （敏感词库、近 24 小时发布数、租户注册天数等）。两边各自拼一遍输入，
    迟早会出现「发布时拦、编辑时不拦」的口子。

    ``precheck`` 传 ``None`` 表示跳过预检，返回空结论——只有运营侧补录场景
    才允许这么做。
    """
    if precheck is None:
        return PrecheckResult()
    precheck.texts = {**(precheck.texts or {}), **(draft.guard_texts or {})}
    precheck.from_province = draft.from_province
    precheck.from_city = draft.from_city
    precheck.from_district = draft.from_district
    precheck.to_province = draft.to_province
    precheck.to_city = draft.to_city
    precheck.to_district = draft.to_district
    precheck.window_start = draft.window_start
    precheck.now = precheck.now or now
    precheck.cargo_name = precheck.cargo_name or draft.guard_cargo_name
    if draft.expired_licenses:
        precheck.expired_licenses = list(draft.expired_licenses)
    if draft.soft_expired_licenses:
        precheck.soft_expired_licenses = list(draft.soft_expired_licenses)
    return run_precheck(precheck)
