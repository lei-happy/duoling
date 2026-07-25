"""审核台序列化器（纯逻辑，零 DB）

把挂牌、租户档案、白名单资格、流水这几类对象转成运营后台可直接渲染的 JSON。

## 为什么不复用租户端的 EcoPostSerializer

那个序列化器的职责是**按查看方层级裁剪字段**，运营审核的职责恰好相反——
判断信息真伪必须看到原文，脱敏过的内容审不出问题（联系方式违规是驳回原因
之一，可它在租户端序列化里根本不会被输出）。

复用它的唯一办法是伪造一个「我是发布方」的查看方上下文骗过可见性内核。
那等于在系统里留一个「构造一下上下文就能看到全部字段」的样板，
下一个人照抄到别处就是一次越权。这里另写一份，两边职责各自清晰：
租户端那份保证「不该看的看不到」，这份保证「该审的都在」。

## 数据的敏感边界

平台库里本来就没有客户名称、内部成本、VIN、司机手机号（发布时就被
Builder 过滤掉了，见 cargo_draft_builder / capacity_draft_builder），
所以这里「全字段输出」的上限也就是那些能对外的字段。唯一的例外是
``driver_name``：它落了库、且**只允许在审核台输出**，审核员核验车辆
与司机的对应关系需要它。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence

from app.modules.client.services.ecosystem.post_state_machine import (
    STATUS_LABELS,
    describe,
)
from app.modules.console.models.ecosystem.constants import (
    REJECT_REASON_LABELS,
    AuditStatus,
    PostType,
    SourceType,
)
from app.modules.console.services.ecosystem import audit_sla

AUDIT_STATUS_LABELS: Dict[int, str] = {
    AuditStatus.NOT_SUBMITTED: "未提交",
    AuditStatus.PENDING: "待审核",
    AuditStatus.APPROVED: "审核通过",
    AuditStatus.REJECTED: "已驳回",
    AuditStatus.WHITELIST_PASS: "免审直通待抽检",
    AuditStatus.SPOT_CHECKED: "抽检通过",
}

POST_TYPE_LABELS: Dict[int, str] = {
    PostType.CARGO: "货源",
    PostType.CAPACITY: "运力",
    PostType.SERVICE: "服务",
}

# 流水动作的中文名。与 constants.PostAuditAction 的取值一一对应，
# 放在这里而不是常量模块，是因为它只服务于展示
AUDIT_ACTION_LABELS: Dict[int, str] = {
    1: "提交审核",
    2: "审核通过",
    3: "审核驳回",
    4: "修改后重新提交",
    5: "发布方主动下架",
    6: "到期自动下架",
    7: "平台强制下架",
    8: "源单失效下架",
    9: "成交自动下架",
    10: "重新上架",
    11: "免审直通上架",
    12: "抽检通过",
    13: "抽检不通过",
    14: "编辑挂牌",
    15: "延长展示",
}

OPERATOR_TYPE_LABELS: Dict[int, str] = {
    1: "企业用户",
    2: "平台运营",
    3: "系统自动",
}

# 预检可疑标记的中文名。落库的 ``precheck_flags`` 是一串编码
# （见 content_guard.SuspiciousFlag），判定时那句人话没有持久化，
# 所以审核台的措辞在这里定义、由 ``/options`` 下发给前端，
# 避免前端各写一套导致同一个标记在队列和详情里叫两个名字
PRECHECK_FLAG_LABELS: Dict[str, str] = {
    "sensitive_word_review": "命中需人工确认的词",
    "price_abnormal": "报价明显偏离同线路均价",
    "too_many_posts": "近 24 小时发布过多，疑似刷屏",
    "duplicate_like": "与近 7 天的挂牌高度相似",
    "new_tenant": "新注册企业首次发布",
    "insurance_expired": "车辆保险已过期",
    "was_force_delisted": "曾被平台强制下架过",
}


class EcoAuditSerializer:
    """审核台序列化"""

    # ------------------------------------------------------------------
    # 队列行
    # ------------------------------------------------------------------

    @staticmethod
    def queue_row(row: Any) -> Dict[str, Any]:
        """一条队列行：挂牌摘要 + 时效

        时效字段由取数层算好（``AuditQueueRow``），这里只做翻译。前端拿到
        ``urgencyLabel`` 直接展示，不要自己按 ``submittedAt`` 减当前时间——
        那个口径是自然时长，凌晨提交的会显示成 7 小时（见 audit_sla 模块注释）。
        """
        return {
            "post": EcoAuditSerializer.post_summary(row.post),
            "waitedMinutes": int(row.waited_minutes or 0),
            "urgency": int(row.urgency or 0),
            "urgencyLabel": audit_sla.describe_urgency(row.urgency),
            "deadline": _dt(row.deadline),
            "isOverdue": bool(row.is_overdue),
        }

    @staticmethod
    def post_summary(post: Any) -> Dict[str, Any]:
        """列表用的挂牌摘要

        比租户端卡片多给三样东西：发布方编码（要能跳到租户档案）、
        预检标记（审核员据此决定先看哪条）、审核状态（队列里混着免审直通的）。
        """
        flags = list(post.precheck_flags or [])
        return {
            "id": post.id,
            "postNo": post.post_no,
            "postType": post.post_type,
            "postTypeLabel": POST_TYPE_LABELS.get(int(post.post_type or 0), "未知"),
            "title": post.title,
            "status": post.status,
            "statusLabel": describe(post.status),
            "auditStatus": post.audit_status,
            "auditStatusLabel": AUDIT_STATUS_LABELS.get(
                int(post.audit_status or 0), "未知"
            ),
            "isTop": post.is_top,
            "ownerTenantCode": post.owner_tenant_code,
            "ownerTenantName": post.owner_tenant_name,
            "publisherName": post.publisher_name,
            "fromProvince": post.from_province,
            "fromCity": post.from_city,
            "fromDistrict": post.from_district,
            "toProvince": post.to_province,
            "toCity": post.to_city,
            "toDistrict": post.to_district,
            "anyDirection": post.any_direction,
            "windowStart": _dt(post.window_start),
            "windowEnd": _dt(post.window_end),
            "totalQuantity": post.total_quantity,
            "quantityUnit": post.quantity_unit,
            "priceType": post.price_type,
            "priceAmount": _num(post.price_amount),
            "cooperationType": post.cooperation_type,
            "sourceType": post.source_type,
            "sourceChanged": post.source_changed,
            "precheckFlagCount": len(flags),
            "precheckFlags": flags,
            "submittedAt": _dt(post.submitted_at),
            "listedAt": _dt(post.listed_at),
            "validUntil": _dt(post.valid_until),
            "auditAt": _dt(post.audit_at),
            "auditReason": post.audit_reason,
            "viewCount": post.view_count,
            "intentCount": post.intent_count,
            "createdAt": _dt(post.created_at),
        }

    # ------------------------------------------------------------------
    # 详情
    # ------------------------------------------------------------------

    @staticmethod
    def post_full(
        post: Any,
        *,
        cargo: Any = None,
        capacity: Any = None,
        destinations: Optional[Sequence[Any]] = None,
    ) -> Dict[str, Any]:
        """审核详情里的挂牌全字段（不脱敏）"""
        data = EcoAuditSerializer.post_summary(post)
        data.update(
            {
                "ownerMaskedName": post.owner_masked_name,
                "publisherUserId": post.publisher_user_id,
                "fromName": post.from_name,
                "toName": post.to_name,
                "fromRegionCode": post.from_region_code,
                "toRegionCode": post.to_region_code,
                "remainingQuantity": post.remaining_quantity,
                "priceIncludeTax": post.price_include_tax,
                "priceNegotiable": post.price_negotiable,
                "keepListedAfterDeal": post.keep_listed_after_deal,
                # 联系方式对运营完整可见：「联系方式违规」是驳回原因之一，
                # 看不到原文就无法判断填的是本人还是中间人
                "contactName": post.contact_name,
                "contactPhone": post.contact_phone,
                "contactBackup": post.contact_backup,
                "visibilityLevel": post.visibility_level,
                "contactVisibility": post.contact_visibility,
                "applyBlockRule": post.apply_block_rule,
                "extraBlockTenants": post.extra_block_tenants,
                "validFrom": _dt(post.valid_from),
                "topUntil": _dt(post.top_until),
                "delistReason": post.delist_reason,
                "delistRemark": post.delist_remark,
                "viewerCount": post.viewer_count,
                "dealCount": post.deal_count,
                "lastActiveAt": _dt(post.last_active_at),
                "auditBy": post.audit_by,
                "destinations": [
                    {
                        "province": d.province,
                        "city": d.city,
                        "regionCode": d.region_code,
                        "sortOrder": d.sort_order,
                    }
                    for d in (destinations or [])
                ],
            }
        )
        if cargo is not None:
            data["cargo"] = EcoAuditSerializer._cargo(cargo)
        if capacity is not None:
            data["capacity"] = EcoAuditSerializer._capacity(capacity)
        return data

    @staticmethod
    def _cargo(cargo: Any) -> Dict[str, Any]:
        return {
            "cargoCategory": cargo.cargo_category,
            "cargoItems": cargo.cargo_items,
            "vehicleCondition": cargo.vehicle_condition,
            "cargoName": cargo.cargo_name,
            "cargoWeight": _num(cargo.cargo_weight),
            "cargoVolume": _num(cargo.cargo_volume),
            "packageType": cargo.package_type,
            "viaPoints": cargo.via_points,
            "referenceMileage": _num(cargo.reference_mileage),
            "segmentCount": cargo.segment_count,
            "requireTruckTypes": cargo.require_truck_types,
            "requireSlotMin": cargo.require_slot_min,
            "requireSlotMax": cargo.require_slot_max,
            "allowSplit": cargo.allow_split,
            "requireInsurance": cargo.require_insurance,
            "otherRequirements": cargo.other_requirements,
            "arriveTime": _dt(cargo.arrive_time),
            "timeNegotiable": cargo.time_negotiable,
            "settleType": cargo.settle_type,
            "prepayRatio": cargo.prepay_ratio,
            "freqDesc": cargo.freq_desc,
        }

    @staticmethod
    def _capacity(capacity: Any) -> Dict[str, Any]:
        """运力扩展

        ``driverName`` 只在这里输出：核验「车牌 — 司机 — 证照」是否对得上是
        运力审核的主要工作，租户端任何接口都拿不到它（见 08 §2.4）。
        """
        return {
            "postGranularity": capacity.post_granularity,
            "truckType": capacity.truck_type,
            "slotCount": capacity.slot_count,
            "truckLength": _num(capacity.truck_length),
            "ratedLoad": _num(capacity.rated_load),
            "truckQuantity": capacity.truck_quantity,
            "plateNumber": capacity.plate_number,
            "plateMasked": capacity.plate_masked,
            "platePublic": capacity.plate_public,
            "hasTrailer": capacity.has_trailer,
            "trailerPlateNumber": capacity.trailer_plate_number,
            "driverName": capacity.driver_name,
            "driverDisplay": capacity.driver_display,
            "driverYears": capacity.driver_years,
            "driverOrderCount": capacity.driver_order_count,
            "departureReadyAt": _dt(capacity.departure_ready_at),
            "pickupRadius": capacity.pickup_radius,
            "goodAtCategories": capacity.good_at_categories,
            "canInvoice": capacity.can_invoice,
            "invoiceType": capacity.invoice_type,
            "hasInsurance": capacity.has_insurance,
            "servicePromise": capacity.service_promise,
            "settleRequire": capacity.settle_require,
        }

    # ------------------------------------------------------------------
    # 判断依据
    # ------------------------------------------------------------------

    @staticmethod
    def precheck(post: Any) -> Dict[str, Any]:
        """预检结论

        ``flags`` 是发布时落库的原始标记（含 code / level / hint），
        直接透传；这里额外给一个「有没有硬拦级标记」的汇总，
        免得前端自己遍历判断该不该把整块标红。
        """
        flags = list(post.precheck_flags or [])
        return {
            "flags": flags,
            "flagCount": len(flags),
            "hasBlocking": any(
                str(f.get("level") or "") == "block"
                for f in flags
                if isinstance(f, dict)
            ),
        }

    @staticmethod
    def source_check(post: Any) -> Dict[str, Any]:
        """源单核验

        ``sourceConsistent`` 的语义严格限定为「快照与源单之间没有待同步的变更」，
        判据是 ``source_changed`` 标记（由源单变更钩子写入）。手工发布的挂牌
        没有源单可比，返回 ``None`` 而不是 ``True``——把「无从核验」说成「一致」
        会让审核员对最需要警惕的一类挂牌放松要求。
        """
        has_source = (
            int(post.source_type or 0) == SourceType.SYSTEM_DOC
            and post.source_id is not None
        )
        changed = int(post.source_changed or 0) == 1
        if not has_source:
            consistent: Optional[bool] = None
            hint = "手工填写的信息，系统里没有对应单据可核对，请重点看内容是否具体、可执行"
        elif changed:
            consistent = False
            hint = "来源单据在发布后被改过，挂牌上展示的还是旧内容，请核对后再决定"
        else:
            consistent = True
            hint = "由系统单据带出，内容与单据一致"
        return {
            "hasSource": has_source,
            "sourceType": post.source_type,
            "sourceId": post.source_id,
            "snapshotAt": _dt(post.source_snapshot_at),
            "sourceChanged": post.source_changed,
            "sourceChangedAt": _dt(post.source_changed_at),
            "sourceConsistent": consistent,
            "hint": hint,
        }

    @staticmethod
    def tenant_context(stats: Any) -> Dict[str, Any]:
        """发布方档案（08 §4.1 ownerContext）"""
        pass_rate = stats.pass_rate
        return {
            "tenantCode": stats.tenant_code,
            "tenantName": stats.tenant_name,
            "maskedName": stats.masked_name,
            "licenseVerified": stats.license_verified,
            "transportLicenseVerified": stats.transport_license_verified,
            "realnameVerified": stats.realname_verified,
            "hallEnabled": stats.hall_enabled,
            "auditWhitelist": stats.audit_whitelist,
            "whitelistSource": stats.whitelist_source,
            "whitelistAt": _dt(stats.whitelist_at),
            "whitelistRevokedAt": _dt(stats.whitelist_revoked_at),
            "whitelistRevokeReason": stats.whitelist_revoke_reason,
            "publishRestrictedUntil": _dt(stats.publish_restricted_until),
            "intentRestrictedUntil": _dt(stats.intent_restricted_until),
            "publishCount": stats.publish_count,
            "listedCount": stats.listed_count,
            "pendingCount": stats.pending_count,
            "passRate": float(pass_rate) if pass_rate is not None else None,
            "rejectCount": stats.reject_count,
            "rejectCountRecent": stats.reject_count_recent,
            "forceDelistCount": stats.force_delist_count,
            "forceDelistCountRecent": stats.force_delist_count_recent,
            "spotCheckFailCount": stats.spot_check_fail_count,
            "dealCount": stats.deal_count,
            "dealCompletedCount": stats.deal_completed_count,
            "reportValidCount": stats.report_valid_count,
            "reportValidCountRecent": stats.report_valid_count_recent,
            "firstPublishAt": _dt(stats.first_publish_at),
            "recentPosts": [
                {
                    "id": p.id,
                    "postNo": p.post_no,
                    "postType": p.post_type,
                    "title": p.title,
                    "status": p.status,
                    "statusLabel": describe(p.status),
                    "auditStatus": p.audit_status,
                    "createdAt": _dt(p.created_at),
                }
                for p in (stats.recent_posts or [])
            ],
        }

    @staticmethod
    def audit_trail(rows: Sequence[Any]) -> List[Dict[str, Any]]:
        """流转流水

        审核详情里带上它，是因为「这条挂牌上一轮为什么被驳回、租户改了哪些字段」
        决定了这一轮该看什么。不给流水，审核员只能凭标题重新审一遍。
        """
        return [
            {
                "id": r.id,
                "action": r.action,
                "actionLabel": AUDIT_ACTION_LABELS.get(int(r.action or 0), "其他操作"),
                "fromStatus": r.from_status,
                "fromStatusLabel": STATUS_LABELS.get(int(r.from_status or -1), None),
                "toStatus": r.to_status,
                "toStatusLabel": STATUS_LABELS.get(int(r.to_status or -1), None),
                "operatorType": r.operator_type,
                "operatorTypeLabel": OPERATOR_TYPE_LABELS.get(
                    int(r.operator_type or 0), "未知"
                ),
                "operatorName": r.operator_name,
                "operatorTenantCode": r.operator_tenant_code,
                "reasonCode": r.reason_code,
                "reasonLabel": REJECT_REASON_LABELS.get(int(r.reason_code or 0), None),
                "reason": r.reason,
                "changedFields": r.changed_fields,
                "createdAt": _dt(r.created_at),
            }
            for r in (rows or [])
        ]

    # ------------------------------------------------------------------
    # 白名单
    # ------------------------------------------------------------------

    @staticmethod
    def eligibility(result: Any) -> Dict[str, Any]:
        """白名单资格判定（08 §4.2）

        ``eligible`` 与 ``manualAllowed`` 分开给：前者是自动准入结论，
        后者决定界面上的「仍然授予」按钮要不要留着。合成一个布尔值，
        运营遇到「不满足自动条件但确实该放行」时就只剩改数据库这条路。
        """
        return {
            "tenantCode": result.tenant_code,
            "eligible": result.eligible,
            "manualAllowed": result.manual_allowed,
            "summary": result.summary,
            "items": [
                {
                    "code": i.code,
                    "label": i.label,
                    "passed": i.passed,
                    "detail": i.detail,
                    "blocking": i.blocking,
                }
                for i in result.items
            ],
        }

    # ------------------------------------------------------------------
    # 统计与动作结果
    # ------------------------------------------------------------------

    @staticmethod
    def backlog(stats: Any) -> Dict[str, Any]:
        return {
            "pending": stats.pending,
            "pendingOverdue": stats.pending_overdue,
            "pendingFlagged": stats.pending_flagged,
            "spotCheckPending": stats.spot_check_pending,
            "spotCheckOverdue": stats.spot_check_overdue,
            "slaMinutes": audit_sla.SLA_MINUTES,
            "warnMinutes": audit_sla.WARN_MINUTES,
        }

    @staticmethod
    def action_result(result: Any) -> Dict[str, Any]:
        """单条审核动作的结果

        ``refSynced`` 为 false 只表示企业端业务列表上那个「已发布到大厅」的角标
        暂时没刷新，审核结论本身已经生效，交巡检补偿。前端不要提示为失败。
        """
        return {
            "postId": result.post_id,
            "postNo": result.post_no,
            "status": result.status,
            "statusLabel": describe(result.status),
            "auditStatus": result.audit_status,
            "auditStatusLabel": AUDIT_STATUS_LABELS.get(
                int(result.audit_status or 0), "未知"
            ),
            "changed": result.changed,
            "refSynced": result.ref_synced,
            "whitelistRevoked": result.whitelist_revoked,
            "invalidatedIntentCount": len(result.invalidated_intents or []),
        }

    @staticmethod
    def batch_result(result: Any) -> Dict[str, Any]:
        return {
            "successCount": result.success_count,
            "succeeded": list(result.succeeded or []),
            "failed": [
                {"postId": f.post_id, "postNo": f.post_no, "message": f.message}
                for f in (result.failed or [])
            ],
        }

    @staticmethod
    def whitelist_member(row: Any) -> Dict[str, Any]:
        """白名单列表的一行

        ``row`` 是 ``(信誉记录, 企业名)``。列表上带发布量与违规数，是为了让运营
        扫一眼就能发现「这家已经被强制下架过 2 次却还在白名单里」这类漏处置。
        """
        credit, tenant_name = row
        return {
            "tenantCode": credit.tenant_code,
            "tenantName": tenant_name,
            "whitelistAt": _dt(credit.whitelist_at),
            "whitelistSource": credit.whitelist_source,
            "whitelistSourceLabel": (
                "人工授予" if int(credit.whitelist_source or 0) == 2 else "自动授予"
            ),
            "whitelistBy": credit.whitelist_by,
            "whitelistRevokedAt": _dt(credit.whitelist_revoked_at),
            "whitelistRevokeReason": credit.whitelist_revoke_reason,
            "publishCount": credit.publish_count,
            "listedCount": credit.listed_count,
            "dealCount": credit.deal_count,
            "dealCompletedCount": credit.deal_completed_count,
            "forceDelistCount": credit.force_delist_count,
            "reportValidCount": credit.report_valid_count,
        }

    @staticmethod
    def whitelist_result(result: Any) -> Dict[str, Any]:
        return {
            "tenantCode": result.tenant_code,
            "auditWhitelist": result.audit_whitelist,
            "source": result.source,
            "changed": result.changed,
        }


def _dt(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _num(value: Any) -> Any:
    """Decimal → float，便于 JSON 序列化；None 原样透传"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value
