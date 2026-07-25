"""服务平台挂牌入参

## 为什么出参不在这里

挂牌的出参由 ``EcoPostSerializer`` 生成（已是 camelCase 的 dict），**不再套一层
Pydantic 出参模型**。字段可见性是这个模块最不能出错的地方，序列化器是它唯一的
实现点；再定义一份 ``PostOut``，就等于把「哪个字段对谁可见」复制到了第二处，
两处迟早不一致，而不一致的方向恰好是多返回一个字段——不会报错，只会泄露。

## 校验放在哪一层

这里只做**与业务无关的形状校验**：枚举取值、字符串长度、数值区间。
「任务单是否可发布」「证照是否过期」「联系方式是否夹带在文本里」这类判断留在
Builder 与预检里，因为它们要读库、要给出可行动的文案，塞进 Pydantic
只会得到一句用户看不懂的 422。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.modules.client.services.ecosystem.capacity_draft_builder import (
    CapacityPublishForm,
)
from app.modules.client.services.ecosystem.cargo_draft_builder import CargoPublishForm
from app.modules.console.models.ecosystem.constants import (
    DEFAULT_VALID_DAYS,
    VALID_DAYS_OPTIONS,
    CooperationType,
    PriceType,
    SettleType,
    VisibilityLevel,
)

_VALID_DAYS_TEXT = "、".join(str(d) for d in VALID_DAYS_OPTIONS)


class _PostFormBase(BaseModel):
    """两个大厅发布弹层的公共项：联系方式、展示时长、报价、可见范围"""

    contactName: str = Field(..., min_length=1, max_length=50)
    contactPhone: str = Field(..., min_length=5, max_length=20)
    contactBackup: Optional[str] = Field(None, max_length=20)

    validDays: int = DEFAULT_VALID_DAYS
    cooperationType: int = CooperationType.ONCE

    priceType: int = PriceType.NEGOTIABLE
    priceAmount: Optional[Decimal] = None
    priceIncludeTax: int = 0
    priceNegotiable: int = 1

    visibilityLevel: int = VisibilityLevel.CERTIFIED
    contactVisibility: int = VisibilityLevel.NEGOTIATING
    applyBlockRule: int = 1
    extraBlockTenants: Optional[List[str]] = None

    title: Optional[str] = Field(None, max_length=100)

    @field_validator("validDays")
    @classmethod
    def _check_valid_days(cls, v: int) -> int:
        if int(v) not in VALID_DAYS_OPTIONS:
            raise ValueError(f"展示天数请选择 {_VALID_DAYS_TEXT} 天")
        return int(v)

    @field_validator("cooperationType")
    @classmethod
    def _check_cooperation(cls, v: int) -> int:
        if int(v) not in (CooperationType.ONCE, CooperationType.LONG_TERM):
            raise ValueError("请选择合作方式：单次或长期")
        return int(v)

    @field_validator("priceType")
    @classmethod
    def _check_price_type(cls, v: int) -> int:
        if int(v) not in PriceType.ALL:
            raise ValueError("请选择计价方式")
        return int(v)

    @field_validator("priceAmount")
    @classmethod
    def _check_price_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("报价要大于 0，不报价请选择「面议」")
        return v

    @field_validator("visibilityLevel")
    @classmethod
    def _check_visibility(cls, v: int) -> int:
        # 企业名只能选「所有人可见」或「认证企业可见」：洽谈层才露出企业名
        # 意味着卡片上连脱敏名都没有，同行无从判断要不要谈
        if int(v) not in (VisibilityLevel.ANONYMOUS, VisibilityLevel.CERTIFIED):
            raise ValueError("企业名可见范围请选择「所有人」或「认证企业」")
        return int(v)

    @field_validator("contactVisibility")
    @classmethod
    def _check_contact_visibility(cls, v: int) -> int:
        # 联系方式下限是认证层：对匿名层公开等于把手机号挂在公网上
        if int(v) not in (VisibilityLevel.CERTIFIED, VisibilityLevel.NEGOTIATING):
            raise ValueError("联系方式可见范围请选择「认证企业」或「洽谈后」")
        return int(v)


class CargoFormRequest(_PostFormBase):
    """货源发布弹层表单（发布与编辑共用）

    线路、时间、台数、货物明细一律来自任务单，**不接受前端传**（08 §3.4）：
    这些字段是运营审核比对源单的依据，让前端传等于让发布方可以挂一条与任务单
    无关的信息，源单一致性校验立刻失去意义。
    """

    settleType: Optional[int] = None
    prepayRatio: Optional[int] = Field(None, ge=0, le=100)

    requireTruckTypes: Optional[List[str]] = None
    requireSlotMin: Optional[int] = Field(None, ge=1, le=30)
    requireSlotMax: Optional[int] = Field(None, ge=1, le=30)
    allowSplit: int = 0
    requireInsurance: int = 0
    otherRequirements: Optional[str] = Field(None, max_length=500)
    timeNegotiable: int = 1
    freqDesc: Optional[str] = Field(None, max_length=100)

    @field_validator("settleType")
    @classmethod
    def _check_settle(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and int(v) not in (
            SettleType.CASH, SettleType.MONTHLY, SettleType.PREPAY
        ):
            raise ValueError("请选择结算方式")
        return v

    def to_form(self) -> CargoPublishForm:
        return CargoPublishForm(
            contact_name=self.contactName.strip(),
            contact_phone=self.contactPhone.strip(),
            contact_backup=(self.contactBackup or "").strip() or None,
            valid_days=self.validDays,
            cooperation_type=self.cooperationType,
            price_type=self.priceType,
            price_amount=self.priceAmount,
            price_include_tax=self.priceIncludeTax,
            price_negotiable=self.priceNegotiable,
            settle_type=self.settleType,
            prepay_ratio=self.prepayRatio,
            require_truck_types=self.requireTruckTypes,
            require_slot_min=self.requireSlotMin,
            require_slot_max=self.requireSlotMax,
            allow_split=self.allowSplit,
            require_insurance=self.requireInsurance,
            other_requirements=(self.otherRequirements or "").strip() or None,
            time_negotiable=self.timeNegotiable,
            freq_desc=(self.freqDesc or "").strip() or None,
            visibility_level=self.visibilityLevel,
            contact_visibility=self.contactVisibility,
            apply_block_rule=self.applyBlockRule,
            extra_block_tenants=self.extraBlockTenants,
            title=(self.title or "").strip() or None,
        )


class CargoPublishRequest(CargoFormRequest):
    """发布货源：表单 + 源任务单"""

    taskId: int = Field(..., gt=0)


class CapacityFormRequest(_PostFormBase):
    """运力发布弹层表单（发布与编辑共用）

    当前所在地与期望流向**必须由用户填**：运力档案里没有实时位置，而位置与流向
    正是找车方的第一决策依据（03 §3.1）。车辆、司机、板位来自运力档案。
    """

    fromRegionId: Optional[int] = Field(None, gt=0)
    toRegionIds: List[int] = Field(default_factory=list)
    anyDirection: int = 0

    windowStart: Optional[datetime] = None
    windowEnd: Optional[datetime] = None
    departureReadyAt: Optional[datetime] = None
    pickupRadius: Optional[int] = Field(None, ge=0, le=500)

    keepListedAfterDeal: int = 0
    settleRequire: Optional[int] = None

    slotCount: Optional[int] = Field(None, ge=1, le=30)
    platePublic: int = 0
    goodAtCategories: Optional[List[str]] = None
    canInvoice: int = 0
    invoiceType: Optional[str] = Field(None, max_length=50)
    hasInsurance: int = 0
    servicePromise: Optional[str] = Field(None, max_length=500)

    @field_validator("toRegionIds")
    @classmethod
    def _dedup_regions(cls, v: List[int]) -> List[int]:
        # 期望流向去重并保序：前端多选组件重复选中同一个市是常见操作，
        # 落库成两行会让目的地唯一索引报冲突
        seen: List[int] = []
        for r in v or []:
            if int(r) > 0 and int(r) not in seen:
                seen.append(int(r))
        return seen

    def to_form(self) -> CapacityPublishForm:
        return CapacityPublishForm(
            from_region_id=self.fromRegionId,
            to_region_ids=self.toRegionIds,
            any_direction=self.anyDirection,
            window_start=self.windowStart,
            window_end=self.windowEnd,
            departure_ready_at=self.departureReadyAt,
            pickup_radius=self.pickupRadius,
            contact_name=self.contactName.strip(),
            contact_phone=self.contactPhone.strip(),
            contact_backup=(self.contactBackup or "").strip() or None,
            valid_days=self.validDays,
            cooperation_type=self.cooperationType,
            keep_listed_after_deal=self.keepListedAfterDeal,
            price_type=self.priceType,
            price_amount=self.priceAmount,
            price_include_tax=self.priceIncludeTax,
            price_negotiable=self.priceNegotiable,
            settle_require=self.settleRequire,
            slot_count=self.slotCount,
            plate_public=self.platePublic,
            good_at_categories=self.goodAtCategories,
            can_invoice=self.canInvoice,
            invoice_type=(self.invoiceType or "").strip() or None,
            has_insurance=self.hasInsurance,
            service_promise=(self.servicePromise or "").strip() or None,
            visibility_level=self.visibilityLevel,
            contact_visibility=self.contactVisibility,
            apply_block_rule=self.applyBlockRule,
            extra_block_tenants=self.extraBlockTenants,
            title=(self.title or "").strip() or None,
        )


class CapacityPublishRequest(CapacityFormRequest):
    """发布运力：表单 + 源运力档案"""

    capacityId: int = Field(..., gt=0)


class CargoPreviewRequest(BaseModel):
    """发布前试算（货源）

    只要源单 ID：用户刚在任务单上点「发布到货源大厅」，弹层还没填任何东西，
    此时要先告诉他「这单能不能发、发出去长什么样」。表单里的自由文本还没输入，
    所以试算覆盖的是源单侧的事实（线路、时间、可发布状态）与自动生成的标题，
    文本类预检留到真正提交时跑。
    """

    taskId: int = Field(..., gt=0)

    def to_form(self) -> CargoPublishForm:
        return CargoPublishForm()


class CapacityPreviewRequest(BaseModel):
    """发布前试算（运力）

    比货源多带位置与流向：运力档案里没有实时位置，不填就算不出线路，
    自动标题也就无从生成。
    """

    capacityId: int = Field(..., gt=0)
    fromRegionId: Optional[int] = Field(None, gt=0)
    toRegionIds: List[int] = Field(default_factory=list)
    anyDirection: int = 0
    windowStart: Optional[datetime] = None
    windowEnd: Optional[datetime] = None
    slotCount: Optional[int] = Field(None, ge=1, le=30)

    def to_form(self) -> CapacityPublishForm:
        return CapacityPublishForm(
            from_region_id=self.fromRegionId,
            to_region_ids=[int(r) for r in (self.toRegionIds or []) if int(r) > 0],
            any_direction=self.anyDirection,
            window_start=self.windowStart,
            window_end=self.windowEnd,
            slot_count=self.slotCount,
        )


class PostDelistRequest(BaseModel):
    """停止展示"""

    remark: Optional[str] = Field(None, max_length=255)


class PostSubmitRequest(BaseModel):
    """提交审核 / 重新上架

    ``validDays`` 可选：草稿躺了几天再提交时，用户往往想顺手改一下展示时长。
    不传则沿用挂牌上原有的天数。
    """

    validDays: Optional[int] = None

    @field_validator("validDays")
    @classmethod
    def _check_valid_days(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return None
        if int(v) not in VALID_DAYS_OPTIONS:
            raise ValueError(f"展示天数请选择 {_VALID_DAYS_TEXT} 天")
        return int(v)


class PostExtendRequest(BaseModel):
    """延长展示"""

    days: int = DEFAULT_VALID_DAYS

    @field_validator("days")
    @classmethod
    def _check_days(cls, v: int) -> int:
        if int(v) not in VALID_DAYS_OPTIONS:
            raise ValueError(f"展示天数请选择 {_VALID_DAYS_TEXT} 天")
        return int(v)
