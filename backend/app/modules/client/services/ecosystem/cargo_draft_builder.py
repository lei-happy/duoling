"""任务单 → 货源挂牌草稿

配载完成的任务单是货源大厅的主发布路径：货已经配好了、就差车。

## 绝不出库的字段（02.货源大厅设计.md §2.2）

客户名称、客户 ID、内部单号（``task_no`` / ``waybill_no``）、内部运费与成本
（``carrier_cost_amount``）、VIN 码、收发货联系人与详细地址。

这些在**本模块**就必须过滤掉，不能指望序列化层兜底：一旦写进平台库，它就是
跨租户可见的数据，事后删也补不回泄露。所以：

- 货物明细只聚合「品牌 + 车系 + 台数」，逐项白名单，不做整行拷贝
- 报价由用户在发布表单里另填，**不取** ``carrier_cost_amount``——内部成本
  等于利润空间，带出去等于把底价交给同行
- ``from_name`` / ``to_name`` 用**行政区划名拼出来**，不用 ``task.origin``：
  后者是 varchar(255) 的自由文本，很可能写着「xx路123号仓库」，
  直接搬过去就违反了「只带到区县级」
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.services.ecosystem.post_draft import DestDraft, PostDraft
from app.modules.client.services.ecosystem.region_resolver import (
    ResolvedRegion,
    resolve_pair,
)
from app.modules.client.services.ecosystem.title_builder import build_cargo_title
from app.modules.console.models.ecosystem.constants import (
    CargoCategory,
    CooperationType,
    PostType,
    PriceType,
    SourceType,
)

# 只有「待派车」的任务可以发布：更早的状态配载还在调整，信息不稳定
TASK_STATUS_PENDING_DISPATCH = 0

# 货物明细条数上限。品牌车系组合过多时截断，避免把一张 JSON 撑到几百条——
# 卡片上根本展示不完，反而拖慢列表查询。
MAX_CARGO_ITEMS = 20


@dataclass
class CargoPublishForm:
    """用户在发布弹层里填的内容

    只包含用户真正需要决策的项：线路、货物、台数、时间全部来自任务单，
    不接受前端传（08.接口契约.md §4.2）。
    """

    contact_name: str = ""
    contact_phone: str = ""
    contact_backup: Optional[str] = None

    valid_days: int = 7
    cooperation_type: int = CooperationType.ONCE

    price_type: int = PriceType.NEGOTIABLE
    price_amount: Optional[Decimal] = None
    price_include_tax: int = 0
    price_negotiable: int = 1
    settle_type: Optional[int] = None
    prepay_ratio: Optional[int] = None

    require_truck_types: Optional[List[str]] = None
    require_slot_min: Optional[int] = None
    require_slot_max: Optional[int] = None
    allow_split: int = 0
    require_insurance: int = 0
    other_requirements: Optional[str] = None
    time_negotiable: int = 1
    freq_desc: Optional[str] = None

    visibility_level: int = 2
    contact_visibility: int = 3
    apply_block_rule: int = 1
    extra_block_tenants: Optional[List[str]] = None

    # 用户改写过的标题；留空则用自动生成的
    title: Optional[str] = None


@dataclass
class CargoItem:
    """货物明细行（已剥离客户与 VIN）"""

    brand: Optional[str]
    series: Optional[str]
    quantity: int

    def to_dict(self) -> Dict[str, Any]:
        return {"brand": self.brand, "series": self.series, "quantity": self.quantity}


@dataclass
class CargoSource:
    """任务单侧读出来的事实"""

    task: Task
    origin: ResolvedRegion
    destination: ResolvedRegion
    items: List[CargoItem] = field(default_factory=list)

    @property
    def brands(self) -> List[str]:
        return [i.brand for i in self.items if i.brand]


class CargoDraftBuilder:
    """任务单 → 货源草稿"""

    @staticmethod
    async def build(
        tenant_db: AsyncSession,
        *,
        task_id: int,
        form: CargoPublishForm,
        now: Optional[datetime] = None,
    ) -> PostDraft:
        """读任务单、校验、拼草稿

        Raises:
            BizException: 任务单不满足发布条件，文案直接展示给用户
        """
        now = now or datetime.now()
        source = await CargoDraftBuilder.load_source(tenant_db, task_id, now=now)
        return CargoDraftBuilder.to_draft(source, form)

    # ------------------------------------------------------------------

    @staticmethod
    async def load_source(
        tenant_db: AsyncSession, task_id: int, *, now: Optional[datetime] = None
    ) -> CargoSource:
        """读源单并做前置校验（02.货源大厅设计.md §2.1）"""
        now = now or datetime.now()
        task = (
            await tenant_db.execute(
                select(Task).where(Task.id == task_id, Task.is_deleted == 0)
            )
        ).scalars().first()
        if task is None:
            raise BizException("这条任务单已经不在了，请刷新后重试")

        CargoDraftBuilder.assert_publishable(task, now=now)

        origin, destination = await resolve_pair(
            tenant_db, task.origin_region_id, task.destination_region_id
        )
        if not origin.is_usable:
            raise BizException("起点地址不完整，请先补全省市信息，同行才能找到你")
        if not destination.is_usable:
            raise BizException("终点地址不完整，请先补全省市信息，同行才能找到你")

        items = await CargoDraftBuilder._load_items(tenant_db, task.id)
        return CargoSource(
            task=task, origin=origin, destination=destination, items=items
        )

    @staticmethod
    def assert_publishable(task: Task, *, now: Optional[datetime] = None) -> None:
        """前置校验

        文案与前端按钮置灰时的提示保持一致：用户可能绕过置灰直接调接口，
        两处说法不一致会让人以为是系统出错。
        """
        now = now or datetime.now()

        if int(task.status or 0) != TASK_STATUS_PENDING_DISPATCH:
            raise BizException("只有还没派车的任务可以发布到货源大厅")
        if task.capacity_id or task.carrier_id:
            raise BizException("这单已经安排了承运方，不需要再找车了")
        if int(task.is_locked or 0) == 1:
            raise BizException("这单已进入结算流程，不能对外发布")
        if not (task.origin or "").strip() or not (task.destination or "").strip():
            raise BizException("请先补全起点和终点，同行才能找到你")
        if not task.planned_load_time:
            raise BizException("请先填写计划装车时间再发布")
        if task.planned_load_time <= now:
            raise BizException("计划装车时间已过，请先调整时间再发布")

    @staticmethod
    async def _load_items(tenant_db: AsyncSession, task_id: int) -> List[CargoItem]:
        """聚合货物明细：只取品牌、车系、台数

        逐字段白名单，不整行拷贝——``biz_task_waybill_item`` 上还冗余着
        ``customer_name`` / ``dealer_name`` / ``waybill_no``，那些是商业机密。
        """
        rows = (
            await tenant_db.execute(
                select(
                    TaskWaybillItem.vehicle_brand,
                    TaskWaybillItem.vehicle_model,
                    TaskWaybillItem.quantity,
                ).where(
                    TaskWaybillItem.task_id == task_id,
                    TaskWaybillItem.is_deleted == 0,
                )
            )
        ).all()
        return CargoDraftBuilder._aggregate(rows)

    @staticmethod
    def _aggregate(rows: Any) -> List[CargoItem]:
        """按「品牌 + 车系」合并台数"""
        grouped: Dict[tuple, int] = {}
        for brand, model, quantity in rows:
            key = ((brand or "").strip() or None, (model or "").strip() or None)
            grouped[key] = grouped.get(key, 0) + int(quantity or 0)

        items = [
            CargoItem(brand=brand, series=series, quantity=qty)
            for (brand, series), qty in grouped.items()
            if qty > 0
        ]
        # 台数多的排前面：卡片上只展示前几条，应该先给最有代表性的
        items.sort(key=lambda i: (-i.quantity, i.brand or ""))
        return items[:MAX_CARGO_ITEMS]

    # ------------------------------------------------------------------

    @staticmethod
    def to_draft(source: CargoSource, form: CargoPublishForm) -> PostDraft:
        """把源单事实与用户填写合并成草稿"""
        task = source.task
        total_quantity = int(task.total_quantity or 0) or sum(
            i.quantity for i in source.items
        )

        auto_title = build_cargo_title(
            from_province=source.origin.province,
            from_city=source.origin.city,
            from_district=source.origin.district,
            to_province=source.destination.province,
            to_city=source.destination.city,
            to_district=source.destination.district,
            total_quantity=total_quantity,
            brands=source.brands,
        )
        title = (form.title or "").strip() or auto_title

        draft = PostDraft(
            post_type=PostType.CARGO,
            source_type=SourceType.REF_TASK,
            source_id=int(task.id),
            source_snapshot_at=datetime.now(),
            title=title,
            # 地名只到区县级，且由行政区划名拼出，不用源单的自由文本地址
            from_province=source.origin.province,
            from_city=source.origin.city,
            from_district=source.origin.district,
            from_region_code=source.origin.region_code,
            from_name=source.origin.display,
            to_name=source.destination.display,
            destinations=[
                DestDraft(
                    province=source.destination.province,
                    city=source.destination.city,
                    region_code=source.destination.region_code,
                    sort_order=0,
                )
            ],
            window_start=task.planned_load_time,
            window_end=task.planned_arrive_time,
            valid_days=int(form.valid_days or 7),
            total_quantity=total_quantity or None,
            quantity_unit="台",
            # 接受分批时才需要跟踪剩余量，否则留空表示整单承接
            remaining_quantity=total_quantity if form.allow_split else None,
            price_type=int(form.price_type),
            price_amount=form.price_amount,
            price_include_tax=int(form.price_include_tax),
            price_negotiable=int(form.price_negotiable),
            cooperation_type=int(form.cooperation_type),
            contact_name=(form.contact_name or "").strip(),
            contact_phone=(form.contact_phone or "").strip(),
            contact_backup=form.contact_backup,
            visibility_level=int(form.visibility_level),
            contact_visibility=int(form.contact_visibility),
            apply_block_rule=int(form.apply_block_rule),
            extra_block_tenants=form.extra_block_tenants,
            ext=CargoDraftBuilder._build_ext(source, form),
            guard_texts=CargoDraftBuilder._guard_texts(title, form),
        )
        draft.sync_primary_dest()
        return draft

    @staticmethod
    def _build_ext(source: CargoSource, form: CargoPublishForm) -> Dict[str, Any]:
        """货源扩展表字段"""
        return {
            "segment_count": int(source.task.segment_count or 1),
            "cargo_category": CargoCategory.VEHICLE,
            "cargo_items": [i.to_dict() for i in source.items] or None,
            "require_truck_types": form.require_truck_types or None,
            "require_slot_min": form.require_slot_min,
            "require_slot_max": form.require_slot_max,
            "allow_split": int(form.allow_split),
            "require_insurance": int(form.require_insurance),
            "other_requirements": (form.other_requirements or "").strip() or None,
            "arrive_time": source.task.planned_arrive_time,
            "time_negotiable": int(form.time_negotiable),
            "settle_type": form.settle_type,
            "prepay_ratio": form.prepay_ratio,
            "freq_desc": (form.freq_desc or "").strip() or None,
        }

    @staticmethod
    def _guard_texts(title: str, form: CargoPublishForm) -> Dict[str, str]:
        """交给预检扫描的自由文本

        只收用户可写的字段——系统生成的内容没有夹带联系方式的可能，
        扫它只会白白增加误拦风险。
        """
        texts = {"标题": title}
        if (form.other_requirements or "").strip():
            texts["其他要求"] = form.other_requirements.strip()
        if (form.freq_desc or "").strip():
            texts["货量频次"] = form.freq_desc.strip()
        return texts
