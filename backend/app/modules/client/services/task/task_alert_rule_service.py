"""
任务预警阈值规则 Service

规则的运行时匹配在 ``alert.matcher``，这里只管配置侧：增删改查、生效校验、
保存前的冲突预检。

冲突预检的定位要说清楚：它是**提示**而不是**拦截**。引擎在同分冲突时会按版本号
兜底继续出警，所以配重了不会漏报；但两条规则互相盖来盖去，运营自己也会算不清
到底哪条生效，所以保存时提前把话讲明白。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.task.task_alert_rule import TaskAlertRule
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import (
    BizVehicleBrand,
)
from app.modules.client.models.vehicle_basic.biz_vehicle_series import (
    BizVehicleSeries,
)
from app.modules.client.schemas.task.task_alert import (
    TaskAlertRuleCreate,
    TaskAlertRuleUpdate,
)
from app.modules.client.services.task.alert.catalog import (
    CATALOG_BY_CODE,
    STAGE_LABELS,
)

_SCOPE_FIELDS = (
    "customer_id",
    "customer_type",
    "origin_region_id",
    "destination_region_id",
    "distance_min",
    "distance_max",
    "brand_id",
    "series_id",
    "carrier_type",
)

_CUSTOMER_TYPE_LABELS = {
    0: "主机厂", 1: "贸易商", 2: "经销商", 3: "个人", 4: "其他",
}
_CARRIER_TYPE_LABELS = {1: "自有车", 2: "承运商", 3: "社会运力"}


class TaskAlertRuleService:
    """预警阈值规则配置"""

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    @staticmethod
    async def get_or_404(db: AsyncSession, rule_id: int) -> TaskAlertRule:
        r = await db.execute(
            select(TaskAlertRule).where(
                TaskAlertRule.id == rule_id, TaskAlertRule.is_deleted == 0
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这条预警规则不存在，可能已被删除")
        return row

    @staticmethod
    async def page_rules(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        rule_code: Optional[str] = None,
        only_default: Optional[bool] = None,
        status: Optional[int] = None,
    ) -> tuple[list[TaskAlertRule], int]:
        base = select(TaskAlertRule).where(TaskAlertRule.is_deleted == 0)
        cnt = select(func.count(TaskAlertRule.id)).where(
            TaskAlertRule.is_deleted == 0
        )
        if rule_code:
            base = base.where(TaskAlertRule.rule_code == rule_code)
            cnt = cnt.where(TaskAlertRule.rule_code == rule_code)
        if status is not None:
            base = base.where(TaskAlertRule.status == status)
            cnt = cnt.where(TaskAlertRule.status == status)
        if only_default is not None:
            # 必须在 SQL 里筛，否则分页取完再过滤会出现「有 20 条却只显示 3 条」
            cond = _has_scope_condition()
            cond = ~cond if only_default else cond
            base = base.where(cond)
            cnt = cnt.where(cond)

        total = int((await db.execute(cnt)).scalar() or 0)
        offset = max(0, (page - 1) * page_size)
        r = await db.execute(
            base.order_by(
                TaskAlertRule.rule_code.asc(),
                TaskAlertRule.priority.desc(),
                TaskAlertRule.id.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @staticmethod
    async def list_defaults(db: AsyncSession) -> list[TaskAlertRule]:
        """租户默认阈值（未限定任何维度的规则行）。"""
        r = await db.execute(
            select(TaskAlertRule)
            .where(TaskAlertRule.is_deleted == 0)
            .order_by(TaskAlertRule.rule_code.asc(), TaskAlertRule.stage.asc())
        )
        return [x for x in r.scalars().all() if not x.has_scope()]

    @staticmethod
    async def resolve_scope_names(
        db: AsyncSession, rows: list[TaskAlertRule]
    ) -> "ScopeNames":
        """批量把维度上的 ID 换成名称。

        列表里给运营看「指定客户#128」等于没说，必须落到「上汽大众」。
        一次性按 ID 集合批量查，避免逐行 N+1。
        """
        names = ScopeNames()
        customer_ids = {r.customer_id for r in rows if r.customer_id is not None}
        region_ids = {
            rid
            for r in rows
            for rid in (r.origin_region_id, r.destination_region_id)
            if rid is not None
        }
        brand_ids = {r.brand_id for r in rows if r.brand_id is not None}
        series_ids = {r.series_id for r in rows if r.series_id is not None}

        if customer_ids:
            q = await db.execute(
                select(Customer.id, Customer.customer_name).where(
                    Customer.id.in_(customer_ids), Customer.is_deleted == 0
                )
            )
            names.customers = {int(i): n for i, n in q.all()}
        if region_ids:
            q = await db.execute(
                select(BizRegion.id, BizRegion.name).where(
                    BizRegion.id.in_(region_ids)
                )
            )
            names.regions = {int(i): n for i, n in q.all()}
        if brand_ids:
            q = await db.execute(
                select(BizVehicleBrand.id, BizVehicleBrand.brand_name_cn).where(
                    BizVehicleBrand.id.in_(brand_ids)
                )
            )
            names.brands = {int(i): n for i, n in q.all()}
        if series_ids:
            q = await db.execute(
                select(BizVehicleSeries.id, BizVehicleSeries.series_name).where(
                    BizVehicleSeries.id.in_(series_ids)
                )
            )
            names.series = {int(i): n for i, n in q.all()}
        return names

    # ------------------------------------------------------------------
    # 增删改
    # ------------------------------------------------------------------

    @staticmethod
    async def create(
        db: AsyncSession, data: TaskAlertRuleCreate
    ) -> TaskAlertRule:
        TaskAlertRuleService._validate(data)
        row = TaskAlertRule(rule_code=data.ruleCode, rule_version=1)
        TaskAlertRuleService._assign(row, data)
        await TaskAlertRuleService._assert_default_unique(db, row)
        db.add(row)
        await db.flush()
        # created_at / updated_at 是 server_default，flush 后仍是过期态；
        # 异步 Session 里同步读会触发 MissingGreenlet
        await db.refresh(row)
        return row

    @staticmethod
    async def update(
        db: AsyncSession, rule_id: int, data: TaskAlertRuleUpdate
    ) -> TaskAlertRule:
        TaskAlertRuleService._validate(data)
        row = await TaskAlertRuleService.get_or_404(db, rule_id)
        TaskAlertRuleService._assign(row, data)
        await TaskAlertRuleService._assert_default_unique(db, row, exclude_id=rule_id)
        # 版本号是同分冲突时的 tie-break 依据，每次编辑都要推进
        row.rule_version = int(row.rule_version or 1) + 1
        await db.flush()
        return row

    @staticmethod
    async def remove(db: AsyncSession, rule_id: int) -> None:
        row = await TaskAlertRuleService.get_or_404(db, rule_id)
        row.is_deleted = 1
        await db.flush()

    # ------------------------------------------------------------------
    # 冲突预检
    # ------------------------------------------------------------------

    @staticmethod
    async def find_conflicts(
        db: AsyncSession,
        data: TaskAlertRuleCreate,
        *,
        exclude_id: Optional[int] = None,
    ) -> list[TaskAlertRule]:
        """找出「同规则码 + 同维度组合 + 同优先级 + 生效期重叠」的既有规则。"""
        r = await db.execute(
            select(TaskAlertRule).where(
                TaskAlertRule.rule_code == data.ruleCode,
                TaskAlertRule.is_deleted == 0,
            )
        )
        probe = TaskAlertRule(rule_code=data.ruleCode)
        TaskAlertRuleService._assign(probe, data)

        out: list[TaskAlertRule] = []
        for other in r.scalars().all():
            if exclude_id is not None and int(other.id) == int(exclude_id):
                continue
            if int(other.status or 0) != 1 or int(probe.status or 0) != 1:
                continue
            if (other.stage or None) != (probe.stage or None):
                continue
            if int(other.priority or 0) != int(probe.priority or 0):
                continue
            if any(
                getattr(other, f) != getattr(probe, f) for f in _SCOPE_FIELDS
            ):
                continue
            if not _date_ranges_overlap(
                other.effective_date, other.expiry_date,
                probe.effective_date, probe.expiry_date,
            ):
                continue
            out.append(other)
        return out

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(data: TaskAlertRuleCreate) -> None:
        rule_def = CATALOG_BY_CODE.get(data.ruleCode)
        if rule_def is None:
            raise BizException("预警类型不存在，请从列表中选择")
        if data.stage is not None and data.stage not in rule_def.stages:
            raise BizException(
                f"「{rule_def.name}」不适用于该阶段，请重新选择"
            )
        if rule_def.stage_scoped and data.stage is None and not _has_scope(data):
            raise BizException("阶段滞留的默认阈值需要指定具体阶段")
        if (
            data.distanceMin is not None
            and data.distanceMax is not None
            and data.distanceMin >= data.distanceMax
        ):
            raise BizException("里程下限要小于上限，请检查后重新填写")
        if (
            data.effectiveDate
            and data.expiryDate
            and data.effectiveDate > data.expiryDate
        ):
            raise BizException("生效日期不能晚于失效日期")
        if (
            rule_def.supports_time_basis
            and data.status == 1
            and not data.planEnabled
            and not data.requiredEnabled
        ):
            raise BizException(
                "内部计划和客户要求至少要开一路，否则这条预警不会生效"
            )

    @staticmethod
    def _assign(row: TaskAlertRule, data: TaskAlertRuleCreate) -> None:
        row.rule_code = data.ruleCode
        row.rule_name = data.ruleName
        row.stage = data.stage
        row.customer_id = data.customerId
        row.customer_type = data.customerType
        row.origin_region_id = data.originRegionId
        row.destination_region_id = data.destinationRegionId
        row.distance_min = data.distanceMin
        row.distance_max = data.distanceMax
        row.brand_id = data.brandId
        row.series_id = data.seriesId
        row.carrier_type = data.carrierType
        row.time_basis = data.timeBasis
        row.plan_enabled = 1 if data.planEnabled else 0
        row.required_enabled = 1 if data.requiredEnabled else 0
        row.anchor_offset_minutes = data.anchorOffsetMinutes
        row.warn_ahead_minutes = data.warnAheadMinutes
        row.critical_after_minutes = data.criticalAfterMinutes
        row.warn_ahead_required_minutes = data.warnAheadRequiredMinutes
        row.critical_after_required_minutes = data.criticalAfterRequiredMinutes
        row.stagnant_hours = data.stagnantHours
        row.priority = data.priority
        row.status = data.status
        row.effective_date = data.effectiveDate
        row.expiry_date = data.expiryDate
        row.remark = data.remark

    @staticmethod
    async def _assert_default_unique(
        db: AsyncSession,
        row: TaskAlertRule,
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        """默认阈值一个规则码（+阶段）只能有一条，否则「默认」就没有意义了。"""
        if row.has_scope():
            return
        r = await db.execute(
            select(TaskAlertRule).where(
                TaskAlertRule.rule_code == row.rule_code,
                TaskAlertRule.is_deleted == 0,
            )
        )
        for other in r.scalars().all():
            if exclude_id is not None and int(other.id) == int(exclude_id):
                continue
            if other.has_scope():
                continue
            if (other.stage or None) != (row.stage or None):
                continue
            stage_hint = (
                f"（{STAGE_LABELS.get(int(row.stage), '')}）"
                if row.stage is not None else ""
            )
            raise BizException(
                f"该预警类型{stage_hint}的默认阈值已存在，请直接修改，不要重复新增"
            )


@dataclass
class ScopeNames:
    """维度 ID → 名称的批量映射，供 ``scope_summary`` 拼人话用。"""

    customers: dict[int, str] = field(default_factory=dict)
    regions: dict[int, str] = field(default_factory=dict)
    brands: dict[int, str] = field(default_factory=dict)
    series: dict[int, str] = field(default_factory=dict)


_EMPTY_NAMES = ScopeNames()


def scope_summary(
    row: TaskAlertRule, names: Optional[ScopeNames] = None
) -> str:
    """把维度列拼成一句人话，列表里一眼看清这条规则管谁。"""
    n = names or _EMPTY_NAMES
    parts: list[str] = []
    if row.stage is not None:
        parts.append(STAGE_LABELS.get(int(row.stage), f"阶段{row.stage}"))
    if row.customer_id is not None:
        parts.append(n.customers.get(int(row.customer_id)) or "指定客户")
    if row.customer_type is not None:
        parts.append(
            _CUSTOMER_TYPE_LABELS.get(int(row.customer_type), "其他客户类型")
        )
    if row.origin_region_id or row.destination_region_id:
        origin = (
            n.regions.get(int(row.origin_region_id))
            if row.origin_region_id else None
        ) or "不限"
        dest = (
            n.regions.get(int(row.destination_region_id))
            if row.destination_region_id else None
        ) or "不限"
        parts.append(f"{origin} → {dest}")
    if row.distance_min is not None or row.distance_max is not None:
        lo = f"{float(row.distance_min):g}" if row.distance_min is not None else "0"
        hi = (
            f"{float(row.distance_max):g}" if row.distance_max is not None else "不限"
        )
        parts.append(f"里程 {lo}~{hi} 公里")
    if row.series_id is not None:
        parts.append(n.series.get(int(row.series_id)) or "指定车系")
    elif row.brand_id is not None:
        parts.append(n.brands.get(int(row.brand_id)) or "指定品牌")
    if row.carrier_type is not None:
        parts.append(_CARRIER_TYPE_LABELS.get(int(row.carrier_type), "指定承运方式"))
    return " / ".join(parts) if parts else "全部任务（默认阈值）"


def _has_scope_condition():
    """SQL 版的 ``TaskAlertRule.has_scope()``：任一维度列非空即为覆盖规则。"""
    return or_(*(getattr(TaskAlertRule, f).isnot(None) for f in _SCOPE_FIELDS))


def _has_scope(data: TaskAlertRuleCreate) -> bool:
    return any(
        v is not None
        for v in (
            data.customerId, data.customerType, data.originRegionId,
            data.destinationRegionId, data.distanceMin, data.distanceMax,
            data.brandId, data.seriesId, data.carrierType,
        )
    )


def _date_ranges_overlap(
    a_start: Optional[date], a_end: Optional[date],
    b_start: Optional[date], b_end: Optional[date],
) -> bool:
    if a_end and b_start and a_end < b_start:
        return False
    if b_end and a_start and b_end < a_start:
        return False
    return True
