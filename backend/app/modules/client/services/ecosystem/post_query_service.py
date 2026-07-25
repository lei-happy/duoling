"""服务平台挂牌查询（读平台库）

## 大厅列表

``page_hall`` 是大厅列表的唯一查询入口。安全要点有三条，都在
``_apply_visibility_scope`` 一处收口，禁止在调用方零散补：

1. **屏蔽名单是双向静默的**：被屏蔽方看不到对方的挂牌，也不会收到任何提示。
2. ``viewer_tenant_code`` **是必填参数**，不给默认值。可见性范围绝不能因为
   调用方忘传而退化成「全部可见」——这类漏洞不会报错，只会静默泄露。
3. 只有 ``status = 展示中`` 且未过期的挂牌进入大厅。

## 「我发布的」

``page_mine`` **刻意不走 ``_apply_visibility_scope``**：屏蔽名单、状态与有效期
这三道限制都是「对外」的，看自己的东西不适用——发布方必须能看到草稿、
待审核、被驳回、已过期的挂牌，否则他根本没有入口去处理它们。

它换成另一条同等强度的边界：``owner_tenant_code`` 必填且恒在 WHERE 里。
两个方法放同一个文件，是为了让这处差异摆在一起被看见——分到两个文件，
下一个人只会照着离手最近的那个抄。

设计文档：08.接口契约.md §3.1 与 §3.6、04.运营审核与风控设计.md §3。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import Select, and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.ecosystem.block_rule import SysEcoBlockRule
from app.modules.console.models.ecosystem.capacity_post import SysEcoCapacityPost
from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost
from app.modules.console.models.ecosystem.constants import PostStatus, PostType
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile

# 「只看优质企业」的门槛，与前端筛选项文案「完成率 ≥ 90%、评分 ≥ 4.5」对应
HIGH_CREDIT_MIN_COMPLETE_RATE = 90
HIGH_CREDIT_MIN_SCORE = 4.5

SORT_OPTIONS = ("latest", "windowStart", "active", "priceAsc", "priceDesc")

# 「我发布的」Tab 角标分组（键名对应 08.接口契约.md §3.6 的 statusCounts）。
# 「已锁定」与「履约中」合并成一个「进行中」Tab：用户视角里它们是同一件事
# ——这单已经谈成了、正在往下走，分两个 Tab 只会让人不知道该点哪个。
MY_POST_STATUS_GROUPS: Dict[str, Tuple[int, ...]] = {
    "draft": (PostStatus.DRAFT,),
    "auditing": (PostStatus.AUDITING,),
    "rejected": (PostStatus.REJECTED,),
    "listed": (PostStatus.LISTED,),
    "dealing": (PostStatus.LOCKED, PostStatus.FULFILLING),
    "finished": (PostStatus.FINISHED,),
    "delisted": (PostStatus.DELISTED,),
    "cancelled": (PostStatus.CANCELLED,),
}


def resolve_status_group(key: Optional[str]) -> List[int]:
    """Tab 键名 → 状态值列表。未知键返回空列表，即不按状态过滤"""
    if not key:
        return []
    return list(MY_POST_STATUS_GROUPS.get(key, ()))


@dataclass
class MyPostFilter:
    """「我发布的」筛选条件"""

    page: int = 1
    page_size: int = 20
    post_type: Optional[int] = None
    statuses: List[int] = field(default_factory=list)
    keyword: Optional[str] = None


@dataclass
class HallFilter:
    """大厅筛选条件（两个大厅共用；不适用的字段留空即可）"""

    page: int = 1
    page_size: int = 20
    keyword: Optional[str] = None
    from_province: Optional[str] = None
    from_city: Optional[str] = None
    to_provinces: List[str] = field(default_factory=list)
    to_city: Optional[str] = None
    window_start_from: Optional[datetime] = None
    window_start_to: Optional[datetime] = None
    quantity_min: Optional[int] = None
    quantity_max: Optional[int] = None
    truck_types: List[str] = field(default_factory=list)
    slot_min: Optional[int] = None
    slot_max: Optional[int] = None
    cargo_category: Optional[int] = None
    price_type: Optional[int] = None
    only_verified: bool = False
    only_high_credit: bool = False
    exclude_mine: bool = True
    sort_by: str = "latest"


class EcoPostQueryService:
    """挂牌查询"""

    @staticmethod
    async def page_hall(
        db: AsyncSession,
        *,
        post_type: int,
        viewer_tenant_code: str,
        flt: HallFilter,
    ) -> Tuple[List[SysEcoPost], int]:
        """大厅分页列表

        Args:
            viewer_tenant_code: 查看方租户，**必填**，用于屏蔽名单与排除自己
        """
        if not viewer_tenant_code:
            raise ValueError("viewer_tenant_code 不能为空：大厅查询必须带查看方身份")

        stmt = select(SysEcoPost)
        stmt = EcoPostQueryService._apply_visibility_scope(
            stmt, post_type=post_type, viewer_tenant_code=viewer_tenant_code,
            exclude_mine=flt.exclude_mine,
        )
        stmt = EcoPostQueryService._apply_filters(stmt, post_type, flt)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await db.execute(count_stmt)).scalar() or 0)
        if total == 0:
            return [], 0

        stmt = EcoPostQueryService._apply_sort(stmt, flt.sort_by)
        page = max(1, int(flt.page or 1))
        page_size = min(100, max(1, int(flt.page_size or 20)))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        rows = (await db.execute(stmt)).scalars().all()
        return list(rows), total

    @staticmethod
    async def get_hall_post(
        db: AsyncSession,
        *,
        post_id: int,
        viewer_tenant_code: str,
    ) -> Optional[SysEcoPost]:
        """按 ID 取一条**大厅可见**的挂牌

        详情页与列表页走同一个 ``_apply_visibility_scope``。分开写就会出现
        「列表里搜不到、但把 ID 拼进详情 URL 就能看到」——挂牌 ID 是自增的，
        这等于把整个大厅的私有内容开放成了可遍历接口。

        ``exclude_mine=False``：发布方从自己的分享链接点进来要能看到，
        序列化时会按发布方层级给全字段。
        """
        if not viewer_tenant_code:
            raise ValueError("viewer_tenant_code 不能为空：挂牌详情必须带查看方身份")

        stmt = EcoPostQueryService._apply_visibility_scope(
            select(SysEcoPost),
            post_type=None,
            viewer_tenant_code=viewer_tenant_code,
            exclude_mine=False,
        ).where(SysEcoPost.id == int(post_id))
        return (await db.execute(stmt)).scalars().first()

    # ------------------------------------------------------------------
    # 「我发布的」：看自己的数据，边界是归属而非可见性
    # ------------------------------------------------------------------

    @staticmethod
    async def get_own_post(
        db: AsyncSession, *, post_id: int, owner_tenant_code: str
    ) -> Optional[SysEcoPost]:
        """按 ID 取一条自己发布的挂牌（不限状态）"""
        if not owner_tenant_code:
            raise ValueError("owner_tenant_code 不能为空：只能查看自己发布的挂牌")

        stmt = select(SysEcoPost).where(
            SysEcoPost.id == int(post_id),
            SysEcoPost.owner_tenant_code == owner_tenant_code,
            SysEcoPost.is_deleted == 0,
        )
        return (await db.execute(stmt)).scalars().first()

    @staticmethod
    async def page_mine(
        db: AsyncSession,
        *,
        owner_tenant_code: str,
        flt: MyPostFilter,
    ) -> Tuple[List[SysEcoPost], int]:
        """「我发布的」分页列表

        不过滤有效期：已过期但状态还是「展示中」的挂牌必须出现在列表里，
        用户要靠它去点「延长展示」。前端按 ``validUntil`` 打「已过期」标签。
        """
        stmt = EcoPostQueryService._mine_scope(owner_tenant_code, flt)
        if flt.statuses:
            stmt = stmt.where(SysEcoPost.status.in_([int(s) for s in flt.statuses]))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await db.execute(count_stmt)).scalar() or 0)
        if total == 0:
            return [], 0

        # 按创建时间倒序而不是最后活跃时间：正好命中 idx_eco_post_owner
        # (owner_tenant_code, status, created_at)，且「我发布的」本来就是
        # 按发布批次回看的场景
        stmt = stmt.order_by(SysEcoPost.created_at.desc(), SysEcoPost.id.desc())
        page = max(1, int(flt.page or 1))
        page_size = min(100, max(1, int(flt.page_size or 20)))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        rows = (await db.execute(stmt)).scalars().all()
        return list(rows), total

    @staticmethod
    async def count_mine_by_status(
        db: AsyncSession,
        *,
        owner_tenant_code: str,
        flt: Optional[MyPostFilter] = None,
    ) -> Dict[str, int]:
        """Tab 角标计数

        除状态之外的筛选条件照样生效（角标要反映当前搜索结果里各状态各有几条），
        一次 ``GROUP BY`` 拿全，不为八个 Tab 打八次查询。
        """
        flt = flt or MyPostFilter()
        stmt = (
            select(SysEcoPost.status, func.count())
            .select_from(SysEcoPost)
            .group_by(SysEcoPost.status)
        )
        stmt = EcoPostQueryService._apply_mine_conditions(stmt, owner_tenant_code, flt)

        raw = {int(s): int(c) for s, c in (await db.execute(stmt)).all()}
        return {
            key: sum(raw.get(s, 0) for s in statuses)
            for key, statuses in MY_POST_STATUS_GROUPS.items()
        }

    @staticmethod
    def _mine_scope(owner_tenant_code: str, flt: MyPostFilter) -> Select:
        return EcoPostQueryService._apply_mine_conditions(
            select(SysEcoPost), owner_tenant_code, flt
        )

    @staticmethod
    def _apply_mine_conditions(
        stmt: Select, owner_tenant_code: str, flt: MyPostFilter
    ) -> Select:
        """归属边界 + 非状态类筛选

        ``owner_tenant_code`` 必填且恒在 WHERE 里，这是本查询唯一的安全边界。
        缺了它，「我发布的」就变成「所有人发布的」——而这个错误不会报错。
        """
        if not owner_tenant_code:
            raise ValueError("owner_tenant_code 不能为空：我发布的必须带归属租户身份")

        stmt = stmt.where(
            SysEcoPost.owner_tenant_code == owner_tenant_code,
            SysEcoPost.is_deleted == 0,
        )
        if flt.post_type is not None:
            stmt = stmt.where(SysEcoPost.post_type == int(flt.post_type))
        if flt.keyword:
            like = f"%{flt.keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    SysEcoPost.title.like(like),
                    SysEcoPost.post_no.like(like),
                    SysEcoPost.from_name.like(like),
                    SysEcoPost.to_name.like(like),
                )
            )
        return stmt

    # ------------------------------------------------------------------
    # 可见性范围：安全边界，唯一收口点
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_visibility_scope(
        stmt: Select,
        *,
        post_type: Optional[int],
        viewer_tenant_code: str,
        exclude_mine: bool,
    ) -> Select:
        """施加大厅可见范围

        这里的每一条都不能省，也不能挪到调用方：
          - 只展示「展示中」且未过期
          - 排除发布方已关停大厅能力的租户（运营处置违规租户的手段）
          - 排除对方设置了屏蔽名单、把查看方屏蔽掉的挂牌
          - 排除挂牌级 extra_block_tenants 命中查看方的挂牌

        ``post_type`` 为 None 表示不限大厅（详情页按 ID 取单条时用），
        其余每一条限制照旧生效。
        """
        now = datetime.now()

        stmt = stmt.where(
            SysEcoPost.status == PostStatus.LISTED,
            SysEcoPost.is_deleted == 0,
            SysEcoPost.valid_until > now,
        )
        if post_type is not None:
            stmt = stmt.where(SysEcoPost.post_type == int(post_type))

        if exclude_mine:
            stmt = stmt.where(SysEcoPost.owner_tenant_code != viewer_tenant_code)

        # 发布方被运营关停大厅能力后，其挂牌立即从大厅消失。
        # 名片记录缺失（懒加载还没建）不影响展示，因此用 NOT EXISTS 语义：
        # 只在「明确存在且 hall_enabled = 0」时排除。
        stmt = stmt.where(
            ~exists(
                select(SysEcoTenantProfile.id).where(
                    SysEcoTenantProfile.tenant_code == SysEcoPost.owner_tenant_code,
                    SysEcoTenantProfile.hall_enabled == 0,
                    SysEcoTenantProfile.is_deleted == 0,
                )
            )
        )

        # 租户级屏蔽：对方（挂牌归属方）把查看方加进了自己的屏蔽名单。
        # 注意查询方向——以 blocked_tenant_code = 查看方 为条件，
        # 反过来写 SQL 依然能跑、结果集也非空，但语义完全相反且不报错。
        stmt = stmt.where(
            ~exists(
                select(SysEcoBlockRule.id).where(
                    SysEcoBlockRule.tenant_code == SysEcoPost.owner_tenant_code,
                    SysEcoBlockRule.blocked_tenant_code == viewer_tenant_code,
                    SysEcoBlockRule.is_deleted == 0,
                )
            )
        )

        # 挂牌级临时屏蔽
        stmt = stmt.where(
            or_(
                SysEcoPost.extra_block_tenants.is_(None),
                func.json_contains(
                    SysEcoPost.extra_block_tenants,
                    json.dumps(viewer_tenant_code, ensure_ascii=False),
                )
                == 0,
            )
        )

        return stmt

    # ------------------------------------------------------------------
    # 业务筛选
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_filters(stmt: Select, post_type: int, flt: HallFilter) -> Select:
        if flt.keyword:
            like = f"%{flt.keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    SysEcoPost.title.like(like),
                    SysEcoPost.from_name.like(like),
                    SysEcoPost.to_name.like(like),
                    SysEcoPost.post_no.like(like),
                )
            )

        if flt.from_province:
            stmt = stmt.where(SysEcoPost.from_province == flt.from_province)
        if flt.from_city:
            stmt = stmt.where(SysEcoPost.from_city == flt.from_city)

        # 目的地多选：命中子表，或该挂牌接受任意流向。
        # 走 sys_eco_post_dest 而非主表 JSON，是为了让筛选可索引（见 07 §2.2）。
        if flt.to_provinces:
            dest_cond = exists(
                select(SysEcoPostDest.id).where(
                    SysEcoPostDest.post_id == SysEcoPost.id,
                    SysEcoPostDest.province.in_(flt.to_provinces),
                    SysEcoPostDest.is_deleted == 0,
                )
            )
            stmt = stmt.where(or_(dest_cond, SysEcoPost.any_direction == 1))

        if flt.to_city:
            stmt = stmt.where(
                or_(
                    exists(
                        select(SysEcoPostDest.id).where(
                            SysEcoPostDest.post_id == SysEcoPost.id,
                            SysEcoPostDest.city == flt.to_city,
                            SysEcoPostDest.is_deleted == 0,
                        )
                    ),
                    SysEcoPost.any_direction == 1,
                )
            )

        if flt.window_start_from:
            stmt = stmt.where(SysEcoPost.window_start >= flt.window_start_from)
        if flt.window_start_to:
            stmt = stmt.where(SysEcoPost.window_start <= flt.window_start_to)

        if flt.quantity_min is not None:
            stmt = stmt.where(SysEcoPost.total_quantity >= flt.quantity_min)
        if flt.quantity_max is not None:
            stmt = stmt.where(SysEcoPost.total_quantity <= flt.quantity_max)

        if flt.price_type is not None:
            stmt = stmt.where(SysEcoPost.price_type == flt.price_type)

        if flt.only_verified:
            stmt = stmt.where(
                exists(
                    select(SysEcoTenantProfile.id).where(
                        SysEcoTenantProfile.tenant_code
                        == SysEcoPost.owner_tenant_code,
                        SysEcoTenantProfile.license_verified == 1,
                        SysEcoTenantProfile.is_deleted == 0,
                    )
                )
            )

        if flt.only_high_credit:
            stmt = stmt.where(
                exists(
                    select(SysEcoTenantCredit.id).where(
                        SysEcoTenantCredit.tenant_code
                        == SysEcoPost.owner_tenant_code,
                        SysEcoTenantCredit.complete_rate
                        >= HIGH_CREDIT_MIN_COMPLETE_RATE,
                        SysEcoTenantCredit.avg_score >= HIGH_CREDIT_MIN_SCORE,
                        SysEcoTenantCredit.is_deleted == 0,
                    )
                )
            )

        if post_type == PostType.CARGO:
            stmt = EcoPostQueryService._apply_cargo_filters(stmt, flt)
        else:
            stmt = EcoPostQueryService._apply_capacity_filters(stmt, flt)

        return stmt

    @staticmethod
    def _apply_cargo_filters(stmt: Select, flt: HallFilter) -> Select:
        needs_ext = (
            flt.cargo_category is not None
            or flt.truck_types
            or flt.slot_min is not None
            or flt.slot_max is not None
        )
        if not needs_ext:
            return stmt

        conds: List[Any] = [
            SysEcoCargoPost.post_id == SysEcoPost.id,
            SysEcoCargoPost.is_deleted == 0,
        ]
        if flt.cargo_category is not None:
            conds.append(SysEcoCargoPost.cargo_category == flt.cargo_category)
        if flt.slot_min is not None:
            conds.append(
                or_(
                    SysEcoCargoPost.require_slot_min.is_(None),
                    SysEcoCargoPost.require_slot_min >= flt.slot_min,
                )
            )
        if flt.slot_max is not None:
            conds.append(
                or_(
                    SysEcoCargoPost.require_slot_max.is_(None),
                    SysEcoCargoPost.require_slot_max <= flt.slot_max,
                )
            )
        if flt.truck_types:
            # 用 JSON_CONTAINS 而非 JSON_OVERLAPS：后者要求 MySQL 8.0.17+，
            # 为一个次级筛选项抬高数据库版本门槛不值得。
            # 该条件走不了索引，但主表的线路/时间窗条件已先把结果集收窄。
            stmt = stmt.where(
                exists(
                    select(SysEcoCargoPost.id).where(
                        and_(
                            *conds,
                            or_(
                                SysEcoCargoPost.require_truck_types.is_(None),
                                *[
                                    func.json_contains(
                                        SysEcoCargoPost.require_truck_types,
                                        json.dumps(t, ensure_ascii=False),
                                    )
                                    == 1
                                    for t in flt.truck_types
                                ],
                            ),
                        )
                    )
                )
            )
            return stmt

        return stmt.where(exists(select(SysEcoCargoPost.id).where(and_(*conds))))

    @staticmethod
    def _apply_capacity_filters(stmt: Select, flt: HallFilter) -> Select:
        needs_ext = (
            flt.truck_types or flt.slot_min is not None or flt.slot_max is not None
        )
        if not needs_ext:
            return stmt

        conds: List[Any] = [
            SysEcoCapacityPost.post_id == SysEcoPost.id,
            SysEcoCapacityPost.is_deleted == 0,
        ]
        if flt.truck_types:
            conds.append(SysEcoCapacityPost.truck_type.in_(flt.truck_types))
        if flt.slot_min is not None:
            conds.append(SysEcoCapacityPost.slot_count >= flt.slot_min)
        if flt.slot_max is not None:
            conds.append(SysEcoCapacityPost.slot_count <= flt.slot_max)

        return stmt.where(exists(select(SysEcoCapacityPost.id).where(and_(*conds))))

    # ------------------------------------------------------------------
    # 排序
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_sort(stmt: Select, sort_by: Optional[str]) -> Select:
        """排序：运营置顶恒定优先，其后按用户选择

        面议（price_amount 为空）在按价排序时排在最后，否则一堆 NULL 占住首屏
        会让排序看起来失灵。
        """
        key = sort_by if sort_by in SORT_OPTIONS else "latest"
        top_first = SysEcoPost.is_top.desc()

        if key == "windowStart":
            return stmt.order_by(top_first, SysEcoPost.window_start.asc(),
                                 SysEcoPost.id.desc())
        if key == "active":
            return stmt.order_by(top_first, SysEcoPost.last_active_at.desc(),
                                 SysEcoPost.id.desc())
        if key == "priceAsc":
            return stmt.order_by(
                top_first,
                SysEcoPost.price_amount.is_(None).asc(),
                SysEcoPost.price_amount.asc(),
                SysEcoPost.id.desc(),
            )
        if key == "priceDesc":
            return stmt.order_by(
                top_first,
                SysEcoPost.price_amount.is_(None).asc(),
                SysEcoPost.price_amount.desc(),
                SysEcoPost.id.desc(),
            )
        return stmt.order_by(top_first, SysEcoPost.listed_at.desc(),
                             SysEcoPost.id.desc())

    # ------------------------------------------------------------------
    # 关联数据批量装载（避免列表页 N+1）
    # ------------------------------------------------------------------

    @staticmethod
    async def load_related(
        db: AsyncSession, posts: Sequence[SysEcoPost], post_type: int
    ) -> dict:
        """一次性取出整页挂牌的扩展表、目的地与信誉

        返回 ``{"ext": {post_id: ext}, "dests": {post_id: [dest]},
        "credits": {tenant_code: credit}}``。
        """
        post_ids = [p.id for p in posts]
        tenant_codes = list({p.owner_tenant_code for p in posts})
        if not post_ids:
            return {"ext": {}, "dests": {}, "credits": {}}

        ext_model = (
            SysEcoCargoPost if post_type == PostType.CARGO else SysEcoCapacityPost
        )
        ext_rows = (
            await db.execute(
                select(ext_model).where(
                    ext_model.post_id.in_(post_ids), ext_model.is_deleted == 0
                )
            )
        ).scalars().all()

        dest_rows = (
            await db.execute(
                select(SysEcoPostDest)
                .where(
                    SysEcoPostDest.post_id.in_(post_ids),
                    SysEcoPostDest.is_deleted == 0,
                )
                .order_by(SysEcoPostDest.sort_order.asc())
            )
        ).scalars().all()

        credit_rows = (
            await db.execute(
                select(SysEcoTenantCredit).where(
                    SysEcoTenantCredit.tenant_code.in_(tenant_codes),
                    SysEcoTenantCredit.is_deleted == 0,
                )
            )
        ).scalars().all()

        dests: dict = {}
        for d in dest_rows:
            dests.setdefault(d.post_id, []).append(d)

        return {
            "ext": {e.post_id: e for e in ext_rows},
            "dests": dests,
            "credits": {c.tenant_code: c for c in credit_rows},
        }
