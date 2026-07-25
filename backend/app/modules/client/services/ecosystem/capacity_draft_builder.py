"""运力档案 → 运力挂牌草稿

空闲运力是运力大厅的主发布路径。运力信息分散在多张表里，发布时要一次拼齐：

``biz_capacity``（绑定关系、司机、车牌）+ ``biz_vehicle_ext``（车型、载重、证照效期）
+ ``biz_trailer_ext``（板位、车长）+ ``biz_driver_license``（驾驶证、从业资格证）

## 证照校验是本模块存在的主要理由（03.运力大厅设计.md §2.1）

把一台证照过期的车推给同行，一旦路上出事，平台的责任说不清。所以证照过期是
**硬拦截**，不是标红提醒。

## 隐私处理（03 §4.2、08 §2.4）

- 车牌默认打码（``plate_masked``），原值留库供成交后与运营核查
- 司机姓名对外只给「王师傅」（``driver_display``），原值永不出现在响应里
- **司机手机号不落平台库**，需要时回租户库读
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.biz_dict import BizDictItem
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.driver.driver_license import (
    DriverLicense,
)
from app.modules.client.models.capacity.self_capacity.trailer_ext import TrailerExt
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.services.ecosystem.post_draft import DestDraft, PostDraft
from app.modules.client.services.ecosystem.region_resolver import (
    RegionResolver,
    ResolvedRegion,
)
from app.modules.client.services.ecosystem.title_builder import build_capacity_title
from app.modules.client.services.ecosystem.visibility import mask_plate
from app.modules.console.models.ecosystem.constants import (
    CooperationType,
    PostGranularity,
    PostType,
    PriceType,
    SourceType,
)

# biz_capacity.status
CAPACITY_BOUND = 1
# biz_capacity.operation_status
OPERATION_AVAILABLE = 1

_OPERATION_STATUS_NAMES = {
    2: "运输中",
    3: "休假",
    4: "停运",
    5: "维修保养",
}

# 期望流向条数上限：勾满全国不如直接勾「任意流向」，
# 留个上限避免 dest 表被一条挂牌写进几十行拖慢筛选
MAX_DESTINATIONS = 10

# 证照效期校验项：(CapacitySource 上的属性名, 效期字段, 对用户的称呼)
# 硬拦截 = 跑这一趟必须合法有效的证照
_HARD_LICENSE_CHECKS = (
    ("vehicle_ext", "inspection_expire", "车辆年检"),
    ("vehicle_ext", "transport_license_expire", "道路运输证"),
    ("driver_license", "license_expire", "司机驾驶证"),
    ("driver_license", "qualification_expire", "司机从业资格证"),
)
# 软标记 = 不影响上路合法性，但影响出事后的追偿
_SOFT_LICENSE_CHECKS = (("vehicle_ext", "insurance_expire", "车辆保险"),)


@dataclass
class CapacityPublishForm:
    """用户在发布弹层里填的内容

    当前所在地与期望流向**必须由用户填**：运力档案里没有实时位置，
    而位置与流向恰恰是找车方的第一决策依据（03 §3.1）。
    """

    # 当前所在地（租户库 biz_region.id）
    from_region_id: Optional[int] = None
    # 期望流向（租户库 biz_region.id 列表）
    to_region_ids: List[int] = field(default_factory=list)
    any_direction: int = 0

    # 可用起止；长期可用时 window_end 留空
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    departure_ready_at: Optional[datetime] = None
    pickup_radius: Optional[int] = None

    contact_name: str = ""
    contact_phone: str = ""
    contact_backup: Optional[str] = None

    valid_days: int = 7
    cooperation_type: int = CooperationType.ONCE
    keep_listed_after_deal: int = 0

    price_type: int = PriceType.NEGOTIABLE
    price_amount: Optional[Decimal] = None
    price_include_tax: int = 0
    price_negotiable: int = 1
    settle_require: Optional[int] = None

    # 板位数取不到时允许手填（03 §2.2）
    slot_count: Optional[int] = None
    plate_public: int = 0
    good_at_categories: Optional[List[str]] = None
    can_invoice: int = 0
    invoice_type: Optional[str] = None
    has_insurance: int = 0
    service_promise: Optional[str] = None

    visibility_level: int = 2
    contact_visibility: int = 3
    apply_block_rule: int = 1
    extra_block_tenants: Optional[List[str]] = None

    title: Optional[str] = None


@dataclass
class CapacitySource:
    """运力侧读出来的事实"""

    capacity: Capacity
    vehicle: Optional[Vehicle] = None
    vehicle_ext: Optional[VehicleExt] = None
    trailer_ext: Optional[TrailerExt] = None
    driver_license: Optional[DriverLicense] = None
    origin: ResolvedRegion = field(default_factory=ResolvedRegion)
    destinations: List[ResolvedRegion] = field(default_factory=list)
    # 车型编码对应的中文名，发布时从租户字典解析（见 truck_type）
    truck_type_label: Optional[str] = None

    @property
    def slot_count(self) -> Optional[int]:
        """板位数：挂车上的才是真实值，牵引车本身没有板位"""
        if self.trailer_ext and self.trailer_ext.parking_spots:
            return int(self.trailer_ext.parking_spots)
        return None

    @property
    def truck_length(self) -> Optional[Decimal]:
        if self.trailer_ext and self.trailer_ext.length:
            return Decimal(str(self.trailer_ext.length))
        return None

    @property
    def rated_load(self) -> Optional[Decimal]:
        """核定载重：带挂时以挂车为准，否则取车辆本身"""
        if self.trailer_ext and self.trailer_ext.load_capacity:
            return Decimal(str(self.trailer_ext.load_capacity))
        if self.vehicle_ext and self.vehicle_ext.load_capacity:
            return Decimal(str(self.vehicle_ext.load_capacity))
        return None

    @property
    def truck_type_code(self) -> str:
        """车型在租户字典里的编码，如 ``heavy_truck``"""
        if self.vehicle_ext and (self.vehicle_ext.vehicle_type or "").strip():
            return self.vehicle_ext.vehicle_type.strip()
        if self.trailer_ext and (self.trailer_ext.trailer_type or "").strip():
            return self.trailer_ext.trailer_type.strip()
        return ""

    @property
    def truck_type(self) -> str:
        """对外展示的车型名

        平台库存的是给别家看的快照，所以这里必须是中文名而不是 ``heavy_truck``
        这种编码：字典项在各租户自己的库里（``biz_dict_item``），看的人查不到它
        对应的中文名，卡片上就会直接显示一串英文。与省市存名称而不是区划码同理。

        解析不到时退回编码而不是「其他」：编码至少还能看出个大概，
        统一写成「其他」等于把信息抹掉。
        """
        return self.truck_type_label or self.truck_type_code or "其他"


def driver_display(name: Optional[str]) -> Optional[str]:
    """司机对外展示串：``王大锤`` → ``王师傅``

    只露姓氏。既能让对方在电话里称呼得上，又不构成可被批量收集的个人信息。
    """
    name = (name or "").strip()
    if not name:
        return None
    # 复姓两字连着取，避免「欧阳」被削成「欧师傅」
    surname = name[:2] if name[:2] in _COMPOUND_SURNAMES else name[:1]
    return f"{surname}师傅"


_COMPOUND_SURNAMES = {
    "欧阳", "上官", "司马", "诸葛", "东方", "独孤", "南宫", "西门",
    "夏侯", "皇甫", "宇文", "长孙", "慕容", "司徒", "端木", "百里",
}


class CapacityDraftBuilder:
    """运力档案 → 运力草稿"""

    @staticmethod
    async def build(
        tenant_db: AsyncSession,
        *,
        capacity_id: int,
        form: CapacityPublishForm,
        now: Optional[datetime] = None,
    ) -> PostDraft:
        now = now or datetime.now()
        source = await CapacityDraftBuilder.load_source(
            tenant_db, capacity_id, form=form, now=now
        )
        return CapacityDraftBuilder.to_draft(source, form)

    # ------------------------------------------------------------------

    @staticmethod
    async def load_source(
        tenant_db: AsyncSession,
        capacity_id: int,
        *,
        form: CapacityPublishForm,
        now: Optional[datetime] = None,
    ) -> CapacitySource:
        now = now or datetime.now()

        capacity = (
            await tenant_db.execute(
                select(Capacity).where(
                    Capacity.id == capacity_id, Capacity.is_deleted == 0
                )
            )
        ).scalars().first()
        if capacity is None:
            raise BizException("这条运力记录已经不在了，请刷新后重试")

        CapacityDraftBuilder.assert_bindable(capacity)

        vehicle, vehicle_ext, trailer_ext = await CapacityDraftBuilder._load_vehicle(
            tenant_db, capacity.vehicle_id
        )
        driver_license = await CapacityDraftBuilder._load_driver_license(
            tenant_db, capacity.driver_id
        )

        origin, destinations = await CapacityDraftBuilder._resolve_places(
            tenant_db, form
        )

        source = CapacitySource(
            capacity=capacity,
            vehicle=vehicle,
            vehicle_ext=vehicle_ext,
            trailer_ext=trailer_ext,
            driver_license=driver_license,
            origin=origin,
            destinations=destinations,
        )
        source.truck_type_label = await CapacityDraftBuilder._resolve_truck_type(
            tenant_db, source
        )
        CapacityDraftBuilder.assert_publishable(source, form, now=now)
        return source

    @staticmethod
    def assert_bindable(capacity: Capacity) -> None:
        """绑定与运营状态校验（03 §2.1）"""
        if int(capacity.status or 0) != CAPACITY_BOUND:
            raise BizException("这台车还没有绑定司机，请先完成绑定")
        operation_status = int(capacity.operation_status or 0)
        if operation_status != OPERATION_AVAILABLE:
            state = _OPERATION_STATUS_NAMES.get(operation_status, "不可接单")
            raise BizException(f"这台车正在{state}，暂时不能对外发布")

    @staticmethod
    def assert_publishable(
        source: CapacitySource,
        form: CapacityPublishForm,
        *,
        now: Optional[datetime] = None,
    ) -> None:
        """线路、档期、证照校验"""
        now = now or datetime.now()

        if not source.origin.is_usable:
            raise BizException("请先选择车辆当前所在地，同行才知道你能不能顺路")
        if not form.any_direction and not source.destinations:
            raise BizException("请选择期望流向，或勾选「接受任意流向」")
        if not form.window_start:
            raise BizException("请填写可用开始时间")
        if form.window_end and form.window_start > form.window_end:
            raise BizException("可用时间的开始时间不能晚于结束时间")

        expired = CapacityDraftBuilder.expired_licenses(source, today=now.date())
        if expired:
            raise BizException(f"{'、'.join(expired)}已过期，请先更新后再对外发布")

    @staticmethod
    def expired_licenses(
        source: CapacitySource, *, today: Optional[date] = None
    ) -> List[str]:
        """列出已过期、且足以拦截发布的证照

        只拦「跑这一趟必须合法有效」的证照。车辆保险不在其中，
        走 ``soft_expired_licenses`` 交人工审核，理由见该方法注释。
        """
        return CapacityDraftBuilder._expired(source, _HARD_LICENSE_CHECKS, today)

    @staticmethod
    def soft_expired_licenses(
        source: CapacitySource, *, today: Optional[date] = None
    ) -> List[str]:
        """列出已过期但不拦截的证照

        目前只有车辆保险：它影响的是理赔而不是上路合法性，且各家投保节奏差异大，
        硬拦会误伤大量正常运力。但出事时它最影响追偿，所以必须标红让审核员看见，
        而不是当作不存在。
        """
        return CapacityDraftBuilder._expired(source, _SOFT_LICENSE_CHECKS, today)

    @staticmethod
    def _expired(source: CapacitySource, checks, today: Optional[date]) -> List[str]:
        today = today or date.today()
        expired = []
        for holder_attr, attr, label in checks:
            holder = getattr(source, holder_attr, None)
            if holder is None:
                continue
            expire_at = getattr(holder, attr, None)
            # 未填效期不视为过期：大量存量档案没录全，拦掉等于劝退用户
            if expire_at and expire_at < today:
                expired.append(label)
        return expired

    # ------------------------------------------------------------------

    @staticmethod
    async def _load_vehicle(tenant_db: AsyncSession, vehicle_id: Optional[int]):
        if not vehicle_id:
            return None, None, None

        vehicle = (
            await tenant_db.execute(
                select(Vehicle).where(
                    Vehicle.id == vehicle_id, Vehicle.is_deleted == 0
                )
            )
        ).scalars().first()
        vehicle_ext = (
            await tenant_db.execute(
                select(VehicleExt).where(
                    VehicleExt.vehicle_id == vehicle_id, VehicleExt.is_deleted == 0
                )
            )
        ).scalars().first()

        trailer_ext = None
        if vehicle is not None and vehicle.trailer_id:
            trailer_ext = (
                await tenant_db.execute(
                    select(TrailerExt).where(
                        TrailerExt.trailer_id == vehicle.trailer_id,
                        TrailerExt.is_deleted == 0,
                    )
                )
            ).scalars().first()
        return vehicle, vehicle_ext, trailer_ext

    @staticmethod
    async def _resolve_truck_type(
        tenant_db: AsyncSession, source: CapacitySource
    ) -> Optional[str]:
        """车型编码 → 中文名（``biz_dict_item``）

        车辆档案上存的是字典编码，挂到大厅要给别家看，必须换成中文名。
        """
        code = source.truck_type_code
        if not code:
            return None
        dict_code = (
            "vehicle_type"
            if source.vehicle_ext and (source.vehicle_ext.vehicle_type or "").strip()
            else "trailer_type"
        )
        return (
            await tenant_db.execute(
                select(BizDictItem.item_name).where(
                    BizDictItem.dict_code == dict_code,
                    BizDictItem.item_value == code,
                    BizDictItem.status == 1,
                    BizDictItem.is_deleted == 0,
                )
            )
        ).scalars().first()

    @staticmethod
    async def _load_driver_license(tenant_db: AsyncSession, driver_id: Optional[int]):
        if not driver_id:
            return None
        return (
            await tenant_db.execute(
                select(DriverLicense).where(
                    DriverLicense.driver_id == driver_id,
                    DriverLicense.is_deleted == 0,
                )
            )
        ).scalars().first()

    @staticmethod
    async def _resolve_places(tenant_db: AsyncSession, form: CapacityPublishForm):
        """一次查询解析所在地与全部期望流向"""
        wanted = [form.from_region_id, *(form.to_region_ids or [])]
        resolved = await RegionResolver.resolve_many(tenant_db, wanted)

        origin = resolved.get(int(form.from_region_id)) if form.from_region_id else None
        destinations = []
        if not form.any_direction:
            seen = set()
            for region_id in (form.to_region_ids or [])[:MAX_DESTINATIONS]:
                item = resolved.get(int(region_id))
                if item is None or not item.is_usable:
                    continue
                # 同省同市只留一条：dest 表上有 (post_id, province, city) 唯一约束
                key = (item.province, item.city)
                if key in seen:
                    continue
                seen.add(key)
                destinations.append(item)
        return origin or ResolvedRegion(), destinations

    # ------------------------------------------------------------------

    @staticmethod
    def to_draft(source: CapacitySource, form: CapacityPublishForm) -> PostDraft:
        capacity = source.capacity
        slot_count = source.slot_count or form.slot_count
        any_direction = int(form.any_direction)
        primary = source.destinations[0] if source.destinations else ResolvedRegion()

        auto_title = build_capacity_title(
            from_province=source.origin.province,
            from_city=source.origin.city,
            from_district=source.origin.district,
            to_province=primary.province,
            to_city=primary.city,
            to_district=primary.district,
            any_direction=bool(any_direction),
            truck_type_name=source.truck_type,
            slot_count=slot_count,
            total_quantity=slot_count,
        )
        title = (form.title or "").strip() or auto_title

        draft = PostDraft(
            post_type=PostType.CAPACITY,
            source_type=SourceType.REF_CAPACITY,
            source_id=int(capacity.id),
            source_snapshot_at=datetime.now(),
            title=title,
            from_province=source.origin.province,
            from_city=source.origin.city,
            from_district=source.origin.district,
            from_region_code=source.origin.region_code,
            from_name=source.origin.display,
            to_name=primary.display or None,
            any_direction=any_direction,
            destinations=[
                DestDraft(
                    province=item.province,
                    city=item.city,
                    region_code=item.region_code,
                    sort_order=index,
                )
                for index, item in enumerate(source.destinations)
            ],
            window_start=form.window_start,
            window_end=form.window_end,
            valid_days=int(form.valid_days or 7),
            total_quantity=slot_count,
            quantity_unit="台",
            price_type=int(form.price_type),
            price_amount=form.price_amount,
            price_include_tax=int(form.price_include_tax),
            price_negotiable=int(form.price_negotiable),
            cooperation_type=int(form.cooperation_type),
            keep_listed_after_deal=int(form.keep_listed_after_deal),
            contact_name=(form.contact_name or "").strip(),
            contact_phone=(form.contact_phone or "").strip(),
            contact_backup=form.contact_backup,
            visibility_level=int(form.visibility_level),
            contact_visibility=int(form.contact_visibility),
            apply_block_rule=int(form.apply_block_rule),
            extra_block_tenants=form.extra_block_tenants,
            ext=CapacityDraftBuilder._build_ext(source, form, slot_count),
            guard_texts=CapacityDraftBuilder._guard_texts(title, form),
            soft_expired_licenses=CapacityDraftBuilder.soft_expired_licenses(source),
        )
        draft.sync_primary_dest()
        return draft

    @staticmethod
    def _build_ext(
        source: CapacitySource, form: CapacityPublishForm, slot_count: Optional[int]
    ) -> Dict[str, Any]:
        capacity = source.capacity
        plate = (capacity.plate_number or "").strip() or None
        trailer_id = source.vehicle.trailer_id if source.vehicle else None
        return {
            "post_granularity": PostGranularity.SPECIFIC,
            "truck_type": source.truck_type,
            "slot_count": slot_count,
            "truck_length": source.truck_length,
            "rated_load": source.rated_load,
            "truck_quantity": 1,
            "plate_number": plate,
            "plate_masked": mask_plate(plate),
            "plate_public": int(form.plate_public),
            "has_trailer": 1 if trailer_id else 0,
            # 司机姓名存原值但永不对外返回，对外只给 driver_display
            "driver_name": (capacity.driver_name or "").strip() or None,
            "driver_display": driver_display(capacity.driver_name),
            "departure_ready_at": form.departure_ready_at,
            "pickup_radius": form.pickup_radius,
            "good_at_categories": form.good_at_categories or None,
            "can_invoice": int(form.can_invoice),
            "invoice_type": (form.invoice_type or "").strip() or None,
            "has_insurance": int(form.has_insurance),
            "service_promise": (form.service_promise or "").strip() or None,
            "settle_require": form.settle_require,
        }

    @staticmethod
    def _guard_texts(title: str, form: CapacityPublishForm) -> Dict[str, str]:
        texts = {"标题": title}
        if (form.service_promise or "").strip():
            texts["服务承诺"] = form.service_promise.strip()
        return texts
