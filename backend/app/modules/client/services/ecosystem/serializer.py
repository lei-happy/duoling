"""服务平台挂牌序列化器（纯逻辑，零 DB）

把挂牌 ORM 对象按查看方层级裁剪成对外 JSON（camelCase）。
配合 visibility.py，构成可见性的唯一实现点。

设计上不接触数据库、不做查询：所有关联数据（扩展表、目的地、信誉、热度）
由 Service 层批量取好后作为参数传入。好处是这一层可以被穷举单测，
而可见性正是最不能出错的部分。

字段矩阵见 08.接口契约.md §2.2 / §2.3。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.modules.client.services.ecosystem.visibility import (
    EcoViewerContext,
    ViewerLevel,
    brands_only,
    can_see_audit,
    can_see_certified_detail,
    can_see_contact,
    can_see_full_plate,
    can_see_owner_full_name,
    can_see_owner_private,
    coarse_day,
    fmt_datetime,
    mask_plate,
    price_range,
    resolve_level,
)
from app.modules.console.models.ecosystem.constants import (
    MIN_SAMPLES_FOR_AVG_SCORE,
    MIN_SAMPLES_FOR_COMPLETE_RATE,
    PostType,
)


class EcoPostSerializer:
    """挂牌序列化器：唯一允许决定字段可见性的地方"""

    @staticmethod
    def serialize(
        post: Any,
        viewer: EcoViewerContext,
        *,
        cargo: Any = None,
        capacity: Any = None,
        destinations: Optional[List[Any]] = None,
        credit: Any = None,
        viewer_stats: Optional[Dict[str, Any]] = None,
        detail: bool = False,
    ) -> Dict[str, Any]:
        """裁剪并序列化一条挂牌

        Args:
            post: ``SysEcoPost``
            viewer: 查看方上下文，层级由此计算
            cargo: ``SysEcoCargoPost``，货源挂牌时传入
            capacity: ``SysEcoCapacityPost``，运力挂牌时传入
            destinations: ``SysEcoPostDest`` 列表
            credit: ``SysEcoTenantCredit``，发布方信誉
            viewer_stats: 热度反馈，仅发布方可见
            detail: True 输出详情视图，False 输出列表卡片视图
        """
        level = resolve_level(post, viewer)
        data = EcoPostSerializer._base(post, level)

        # 区划代码只给发布方自己：编辑弹层要靠它把「期望流向」翻回租户库的
        # region_id 并回填选中项，其他人只需要省市名
        with_code = can_see_owner_private(level)
        data["destinations"] = [
            {
                "province": d.province,
                "city": d.city,
                **({"regionCode": d.region_code} if with_code else {}),
            }
            for d in (destinations or [])
        ]

        if int(getattr(post, "post_type", 0) or 0) == PostType.CARGO:
            data.update(EcoPostSerializer._cargo(cargo, level))
        else:
            data.update(EcoPostSerializer._capacity(capacity, level))

        data["credit"] = EcoPostSerializer._credit(credit)
        data["viewerLevel"] = int(level)
        data["isMine"] = level == ViewerLevel.OWNER

        if detail:
            data.update(EcoPostSerializer._contact(post, level))
            data.update(EcoPostSerializer._owner_private(post, level, viewer_stats))
            data.update(EcoPostSerializer._audit(post, level, viewer))

        return data

    # ------------------------------------------------------------------
    # 主表：两个大厅同构的字段
    # ------------------------------------------------------------------

    @staticmethod
    def _base(post: Any, level: ViewerLevel) -> Dict[str, Any]:
        certified = can_see_certified_detail(level)

        data: Dict[str, Any] = {
            "id": post.id,
            "postNo": post.post_no,
            "postType": post.post_type,
            "title": post.title,
            "status": post.status,
            "isTop": post.is_top,
            # 脱敏名对所有层级可见；全称按挂牌配置
            "ownerMaskedName": post.owner_masked_name,
            "ownerTenantName": (
                post.owner_tenant_name
                if can_see_owner_full_name(post, level) else None
            ),
            "fromProvince": post.from_province,
            "fromCity": post.from_city,
            "toProvince": post.to_province,
            "toCity": post.to_city,
            "anyDirection": post.any_direction,
            "totalQuantity": post.total_quantity,
            "quantityUnit": post.quantity_unit,
            "remainingQuantity": post.remaining_quantity,
            "priceType": post.price_type,
            "priceNegotiable": post.price_negotiable,
            "priceIncludeTax": post.price_include_tax,
            "cooperationType": post.cooperation_type,
            "listedAt": fmt_datetime(post.listed_at),
            "validUntil": fmt_datetime(post.valid_until),
            "lastActiveAt": fmt_datetime(post.last_active_at),
        }

        # 区县与详细地名属于「认证层可见」：未认证只能看到省市，
        # 足以判断线路是否顺路，但拿不到可直接上门的精确地址。
        if certified:
            data["fromDistrict"] = post.from_district
            data["toDistrict"] = post.to_district
            data["fromName"] = post.from_name
            data["toName"] = post.to_name
            data["windowStart"] = fmt_datetime(post.window_start)
            data["windowEnd"] = fmt_datetime(post.window_end)
            data["priceAmount"] = (
                str(post.price_amount) if post.price_amount is not None else None
            )
            data["priceRange"] = None
            data["viewCount"] = post.view_count
            data["intentCount"] = post.intent_count
        else:
            data["fromDistrict"] = None
            data["toDistrict"] = None
            data["fromName"] = None
            data["toName"] = None
            # 匿名层时间降精度到日、价格降级为区间
            data["windowStart"] = coarse_day(post.window_start)
            data["windowEnd"] = coarse_day(post.window_end)
            data["priceAmount"] = None
            data["priceRange"] = price_range(post.price_amount)
            data["viewCount"] = None
            data["intentCount"] = None

        return data

    # ------------------------------------------------------------------
    # 货源扩展
    # ------------------------------------------------------------------

    @staticmethod
    def _cargo(cargo: Any, level: ViewerLevel) -> Dict[str, Any]:
        if cargo is None:
            return {}
        certified = can_see_certified_detail(level)

        data: Dict[str, Any] = {
            "cargoCategory": cargo.cargo_category,
            "vehicleCondition": cargo.vehicle_condition,
            "cargoName": cargo.cargo_name,
            "cargoWeight": _num(cargo.cargo_weight),
            "cargoVolume": _num(cargo.cargo_volume),
            "packageType": cargo.package_type,
            "requireTruckTypes": cargo.require_truck_types,
            "requireSlotMin": cargo.require_slot_min,
            "requireSlotMax": cargo.require_slot_max,
            "allowSplit": cargo.allow_split,
            "requireInsurance": cargo.require_insurance,
            "referenceMileage": _num(cargo.reference_mileage),
            "segmentCount": cargo.segment_count,
            "timeNegotiable": cargo.time_negotiable,
            "freqDesc": cargo.freq_desc,
        }

        if certified:
            data["cargoItems"] = cargo.cargo_items
            data["viaPoints"] = cargo.via_points
            data["otherRequirements"] = cargo.other_requirements
            data["settleType"] = cargo.settle_type
            data["prepayRatio"] = cargo.prepay_ratio
            data["arriveTime"] = fmt_datetime(cargo.arrive_time)
        else:
            # 车系 + 分车型台数足以反推具体订单，匿名层只给品牌
            data["cargoItems"] = brands_only(cargo.cargo_items)
            data["viaPoints"] = None
            data["otherRequirements"] = None
            data["settleType"] = None
            data["prepayRatio"] = None
            data["arriveTime"] = None

        return data

    # ------------------------------------------------------------------
    # 运力扩展
    # ------------------------------------------------------------------

    @staticmethod
    def _capacity(capacity: Any, level: ViewerLevel) -> Dict[str, Any]:
        if capacity is None:
            return {}
        certified = can_see_certified_detail(level)

        # 司机真实姓名（capacity.driver_name）在此**刻意不被读取**，
        # 任何层级都不返回。见 08.接口契约.md §2.4。
        data: Dict[str, Any] = {
            "postGranularity": capacity.post_granularity,
            "truckType": capacity.truck_type,
            "slotCount": capacity.slot_count,
            "truckLength": _num(capacity.truck_length),
            "ratedLoad": _num(capacity.rated_load),
            "truckQuantity": capacity.truck_quantity,
            "hasTrailer": capacity.has_trailer,
            "goodAtCategories": capacity.good_at_categories,
            "canInvoice": capacity.can_invoice,
            "invoiceType": capacity.invoice_type,
            "hasInsurance": capacity.has_insurance,
            "servicePromise": capacity.service_promise,
        }

        if level == ViewerLevel.OWNER:
            # 发布方总能看到完整车牌，所以「是否公开车牌」这个勾选状态必须单独回：
            # 编辑弹层只看 plateNumber 有没有值，会把它一律回填成「已公开」
            data["platePublic"] = capacity.plate_public

        if can_see_full_plate(capacity, level):
            data["plateNumber"] = capacity.plate_number
            data["plateMasked"] = capacity.plate_masked or mask_plate(
                capacity.plate_number
            )
            data["trailerPlateNumber"] = capacity.trailer_plate_number
        elif certified:
            data["plateNumber"] = None
            data["plateMasked"] = capacity.plate_masked or mask_plate(
                capacity.plate_number
            )
            data["trailerPlateNumber"] = mask_plate(capacity.trailer_plate_number)
        else:
            data["plateNumber"] = None
            data["plateMasked"] = None
            data["trailerPlateNumber"] = None

        if certified:
            data["driverDisplay"] = capacity.driver_display
            data["driverYears"] = capacity.driver_years
            data["driverOrderCount"] = capacity.driver_order_count
            data["departureReadyAt"] = fmt_datetime(capacity.departure_ready_at)
            data["pickupRadius"] = capacity.pickup_radius
            data["settleRequire"] = capacity.settle_require
        else:
            data["driverDisplay"] = None
            data["driverYears"] = None
            data["driverOrderCount"] = None
            data["departureReadyAt"] = None
            data["pickupRadius"] = None
            data["settleRequire"] = None

        return data

    # ------------------------------------------------------------------
    # 联系方式
    # ------------------------------------------------------------------

    @staticmethod
    def _contact(post: Any, level: ViewerLevel) -> Dict[str, Any]:
        if can_see_contact(post, level):
            return {
                "contactName": post.contact_name,
                "contactPhone": post.contact_phone,
                "contactBackup": post.contact_backup,
                "contactLocked": False,
            }
        return {
            "contactName": None,
            "contactPhone": None,
            "contactBackup": None,
            "contactLocked": True,
        }

    # ------------------------------------------------------------------
    # 仅发布方可见
    # ------------------------------------------------------------------

    @staticmethod
    def _owner_private(
        post: Any,
        level: ViewerLevel,
        viewer_stats: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not can_see_owner_private(level):
            return {}
        return {
            "sourceType": post.source_type,
            "sourceId": post.source_id,
            # 编辑弹层要靠它回填「当前所在地」（运力档案里没有位置，是发布时选的）
            "fromRegionCode": post.from_region_code,
            "sourceChanged": post.source_changed,
            "sourceChangedAt": fmt_datetime(post.source_changed_at),
            "applyBlockRule": post.apply_block_rule,
            "extraBlockTenants": post.extra_block_tenants,
            "visibilityLevel": post.visibility_level,
            "contactVisibility": post.contact_visibility,
            "keepListedAfterDeal": post.keep_listed_after_deal,
            "delistReason": post.delist_reason,
            "delistRemark": post.delist_remark,
            # 热度反馈：让发布方知道信息确实被看到了，只是还没人下决心。
            # 对 standard 租户尤其重要——它们不能主动发起意向。
            "viewerStats": viewer_stats,
        }

    @staticmethod
    def _audit(
        post: Any, level: ViewerLevel, viewer: EcoViewerContext
    ) -> Dict[str, Any]:
        if not can_see_audit(level, viewer):
            return {}
        return {
            "auditStatus": post.audit_status,
            "auditReason": post.audit_reason,
            "auditAt": fmt_datetime(post.audit_at),
            "precheckFlags": post.precheck_flags,
        }

    # ------------------------------------------------------------------
    # 信誉块（对所有层级可见，但受最小样本量约束）
    # ------------------------------------------------------------------

    @staticmethod
    def _credit(credit: Any) -> Dict[str, Any]:
        """信誉展示

        样本不足时不给数字，改打「新加入」标签：
        样本不足的百分比比没有数字更有害——2 单成交 1 单失败会显示 50% 完成率，
        读起来像劣质承运商，实际只是新用户。见 04.运营审核与风控设计.md §4.2。
        """
        if credit is None:
            return {
                "isNewcomer": True,
                "dealCompletedCount": 0,
                "completeRate": None,
                "avgScore": None,
                "topTags": None,
                "avgRespondMinutes": None,
            }

        deal_completed = int(credit.deal_completed_count or 0)
        eval_count = int(credit.eval_count or 0)
        enough_deals = int(credit.deal_count or 0) >= MIN_SAMPLES_FOR_COMPLETE_RATE
        enough_evals = eval_count >= MIN_SAMPLES_FOR_AVG_SCORE

        return {
            "isNewcomer": not enough_deals and not enough_evals,
            "dealCompletedCount": deal_completed,
            "completeRate": (
                _num(credit.complete_rate) if enough_deals else None
            ),
            "avgScore": _num(credit.avg_score) if enough_evals else None,
            "topTags": credit.top_tags if enough_evals else None,
            "avgRespondMinutes": credit.avg_respond_minutes,
        }


def _num(value: Any) -> Any:
    """Decimal → float，便于 JSON 序列化；None 原样透传。"""
    if value is None:
        return None
    return float(value)
