"""客户对账单 API

接口前缀：``/api/client/finance/customer-recon``

差异相关接口挂在对账单下（``/{recon_id}/diffs``）而不是单独一棵树：差异永远
属于某张对账单，独立成路由只会让前端多传一个 ``reconKind``。
"""

from datetime import date, datetime, time as dtime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.customer_recon import (
    ReconAddWaybillsRequest,
    ReconConfirmRequest,
    ReconCreateRequest,
    ReconCustomerSignRequest,
    ReconLineAdjustRequest,
    ReconLineOut,
    ReconListItem,
    ReconOut,
    ReconReasonRequest,
    ReconRecalcRequest,
    ReconUpdateRequest,
)
from app.modules.client.schemas.finance.recon_diff import (
    ReconCheckReportOut,
    ReconDiffOut,
    ReconDiffRaiseRequest,
    ReconDiffResolveRequest,
)
from app.modules.client.services.finance.customer.customer_recon_service import (
    CustomerReconService,
)
from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
    DiffCandidate,
)

router = APIRouter()

_MODULE = "客户对账"
_RECON_KIND = CustomerReconService.doc_kind


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


def _day_start(d: Optional[date]) -> Optional[datetime]:
    return datetime.combine(d, dtime.min) if d else None


def _day_end(d: Optional[date]) -> Optional[datetime]:
    return datetime.combine(d, dtime.max) if d else None


async def _detail(db: AsyncSession, recon_id: int) -> dict:
    recon = await CustomerReconService.get_or_404(db, recon_id)
    lines = await CustomerReconService.list_lines(db, recon_id)
    return ReconOut.from_model(
        recon, lines=lines, actions=CustomerReconService.action_flags(recon),
    ).model_dump()


# ============================================================
# 候选与漏挂
# ============================================================

@router.get("/candidates")
async def list_candidates(
    customerId: int = Query(description="客户 ID"),
    periodStart: Optional[date] = None,
    periodEnd: Optional[date] = None,
    keyword: Optional[str] = None,
    reconId: Optional[int] = Query(
        default=None, description="给已存在的对账单补挂运单时传入，本单已挂的不算冲突"
    ),
    limit: int = Query(default=500, ge=1, le=1000),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """可加入对账的运单候选（已交车、未锁定、未挂其他对账单）。"""
    rows = await CustomerReconService.list_candidates(
        db,
        customer_id=customerId,
        period_start=_day_start(periodStart),
        period_end=_day_end(periodEnd),
        keyword=keyword,
        recon_id=reconId,
        limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("/orphans")
async def list_orphans(
    customerId: int = Query(description="客户 ID"),
    periodStart: Optional[date] = None,
    periodEnd: Optional[date] = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """漏挂检测：周期内已交车、未挂任何对账单的运单（对账工作台）。"""
    candidates = await ConsistencyChecker.detect_orphans(
        db,
        recon_kind=_RECON_KIND,
        customer_id=customerId,
        period_start=_day_start(periodStart),
        period_end=_day_end(periodEnd),
        limit=limit,
    )
    rows = [
        {
            "waybillId": c.biz_doc_id,
            "waybillNo": c.biz_doc_no,
            "freightAmount": (
                float(c.diff_amount) if c.diff_amount is not None else None
            ),
        }
        for c in candidates
    ]
    return success(data={"list": rows, "count": len(rows)})


# ============================================================
# 对账单主体
# ============================================================

@router.get("")
async def page_recons(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    enterpriseId: Optional[int] = None,
    status: Optional[int] = None,
    periodStart: Optional[date] = None,
    periodEnd: Optional[date] = None,
    onlyDirty: bool = False,
    onlyDiff: bool = False,
    onlyUnsigned: bool = Query(
        default=False, description="只看已确认但未回签的单（对账工作台「待客户回签」）",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await CustomerReconService.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        customer_id=customerId, enterprise_id=enterpriseId, status=status,
        period_start=periodStart, period_end=periodEnd,
        only_dirty=onlyDirty, only_diff=onlyDiff, only_unsigned=onlyUnsigned,
    )
    return success(data={
        "list": [ReconListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
@operation_log(module=_MODULE, action="新增对账单", description="生成客户对账单")
async def create_recon(
    request: Request,
    data: ReconCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    recon = await CustomerReconService.create_from_candidates(
        db,
        customer_id=data.customerId,
        period_start=_day_start(data.periodStart),
        period_end=_day_end(data.periodEnd),
        waybill_ids=data.waybillIds,
        billing_base=data.billingBase,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, recon.id))


@router.get("/{recon_id}")
async def get_recon(
    recon_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, recon_id))


@router.put("/{recon_id}")
@operation_log(module=_MODULE, action="编辑对账单", description="编辑对账单表头")
async def update_recon(
    request: Request,
    recon_id: int,
    data: ReconUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    recon = await CustomerReconService.get_or_404(db, recon_id)
    CustomerReconService.assert_editable(recon)
    if data.periodStart is not None or data.periodEnd is not None:
        start = _day_start(data.periodStart) or recon.period_start
        end = _day_end(data.periodEnd) or recon.period_end
        if start and end and start > end:
            from app.common.exceptions import BizException
            raise BizException("对账周期的开始日期不能晚于结束日期")
        recon.period_start = start
        recon.period_end = end
        recon.dedup_key = type(recon).build_dedup_key(
            int(recon.customer_id), start, end,
        )
    if data.customerContactName is not None:
        recon.customer_contact_name = data.customerContactName
    if data.customerContactPhone is not None:
        recon.customer_contact_phone = data.customerContactPhone
    if data.remark is not None:
        recon.remark = data.remark
    await db.flush()
    return success(data=await _detail(db, recon_id))


@router.delete("/{recon_id}")
@operation_log(module=_MODULE, action="删除对账单", description="删除对账单")
async def delete_recon(
    request: Request,
    recon_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.soft_delete(db, recon_id)
    return success()


# ============================================================
# 对账行
# ============================================================

@router.get("/{recon_id}/lines")
async def list_lines(
    recon_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await CustomerReconService.get_or_404(db, recon_id)
    lines = await CustomerReconService.list_lines(db, recon_id)
    return success(data=[ReconLineOut.from_model(x).model_dump() for x in lines])


@router.post("/{recon_id}/lines")
@operation_log(module=_MODULE, action="添加对账明细", description="批量添加对账运单")
async def add_lines(
    request: Request,
    recon_id: int,
    data: ReconAddWaybillsRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.add_waybills(
        db, recon_id, data.waybillIds,
        billing_base=data.billingBase,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, recon_id))


@router.put("/{recon_id}/lines/{link_id}")
@operation_log(module=_MODULE, action="调整对账明细", description="调整对账行数量/单价/调整额")
async def adjust_line(
    request: Request,
    recon_id: int,
    link_id: int,
    data: ReconLineAdjustRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.adjust_line(
        db, recon_id, link_id,
        quantity=data.quantity,
        unit_price=data.unitPrice,
        adjust_amount=data.adjustAmount,
        adjust_reason=data.adjustReason,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, recon_id))


@router.delete("/{recon_id}/lines/{link_id}")
@operation_log(module=_MODULE, action="移除对账明细", description="移除对账行")
async def remove_line(
    request: Request,
    recon_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.remove_line(
        db, recon_id, link_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, recon_id))


# ============================================================
# 一致性核对与差异
# ============================================================

@router.post("/{recon_id}/check")
@operation_log(module=_MODULE, action="一致性核对", description="重新核对对账单与业务事实")
async def check_recon(
    request: Request,
    recon_id: int,
    persist: bool = Query(default=True, description="false 表示只试算不落库"),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    report = await ConsistencyChecker.check_recon(
        db,
        recon_kind=_RECON_KIND,
        recon_id=recon_id,
        persist=persist,
        operator_id=current_user.user_id,
    )
    diffs = []
    if persist:
        rows = await ConsistencyChecker.list_diffs(
            db, recon_kind=_RECON_KIND, recon_id=recon_id, only_open=True,
        )
        diffs = [ReconDiffOut.from_model(x) for x in rows]
    return success(data=ReconCheckReportOut(
        reconId=report.recon_id,
        reconKind=report.recon_kind,
        checkedLines=report.checked_lines,
        blockingCount=report.blocking_count,
        warningCount=report.warning_count,
        dirtyLines=report.dirty_lines,
        passed=report.passed,
        checkedAt=report.checked_at,
        diffs=diffs,
    ).model_dump())


@router.get("/{recon_id}/diffs")
async def list_diffs(
    recon_id: int,
    onlyOpen: bool = False,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await CustomerReconService.get_or_404(db, recon_id)
    rows = await ConsistencyChecker.list_diffs(
        db, recon_kind=_RECON_KIND, recon_id=recon_id,
        only_open=onlyOpen, status=status,
    )
    return success(data=[ReconDiffOut.from_model(x).model_dump() for x in rows])


@router.post("/{recon_id}/diffs")
@operation_log(module=_MODULE, action="登记差异", description="手工登记一条对账差异")
async def raise_diff(
    request: Request,
    recon_id: int,
    data: ReconDiffRaiseRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.get_or_404(db, recon_id)
    row = await ConsistencyChecker.raise_manual_diff(
        db,
        recon_kind=_RECON_KIND,
        recon_id=recon_id,
        candidate=DiffCandidate(
            biz_doc_id=data.bizDocId,
            biz_doc_no=data.bizDocNo,
            link_id=data.linkId,
            diff_type=data.diffType,
            expected_value=data.expectedValue,
            actual_value=data.actualValue,
            diff_amount=(
                Decimal(str(data.diffAmount))
                if data.diffAmount is not None else None
            ),
            severity=data.severity,
        ),
        operator_id=current_user.user_id,
    )
    return success(data=ReconDiffOut.from_model(row).model_dump())


@router.post("/diffs/{diff_id}/resolve")
@operation_log(module=_MODULE, action="处置差异", description="处置一条对账差异")
async def resolve_diff(
    request: Request,
    diff_id: int,
    data: ReconDiffResolveRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    row = await ConsistencyChecker.resolve_diff(
        db, diff_id,
        status=data.status,
        resolution=data.resolution,
        operator_id=current_user.user_id,
    )
    return success(data=ReconDiffOut.from_model(row).model_dump())


@router.post("/{recon_id}/recalc")
@operation_log(module=_MODULE, action="回灌重算", description="按业务侧当前数据重算对账行")
async def recalc_recon(
    request: Request,
    recon_id: int,
    data: ReconRecalcRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    refreshed = await CustomerReconService.recalc_from_business(
        db, recon_id, only_dirty=data.onlyDirty,
        operator_id=current_user.user_id,
    )
    detail = await _detail(db, recon_id)
    detail["refreshedLines"] = refreshed
    return success(data=detail, message=f"已重算 {refreshed} 行")


# ============================================================
# 状态流转
# ============================================================

@router.post("/{recon_id}/approve-adjust")
@operation_log(module=_MODULE, action="审批大额调整", description="业务主管审批大额调整")
async def approve_adjust(
    request: Request,
    recon_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.approve_adjust(
        db, recon_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, recon_id), message="大额调整已审批通过")


@router.post("/{recon_id}/confirm")
@operation_log(module=_MODULE, action="确认对账单", description="确认客户对账单")
async def confirm_recon(
    request: Request,
    recon_id: int,
    data: Optional[ReconConfirmRequest] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.confirm(
        db, recon_id,
        operator_id=current_user.user_id,
        force_reason=(data.forceReason if data else None),
    )
    return success(data=await _detail(db, recon_id), message="对账单已确认")


@router.post("/{recon_id}/customer-sign")
@operation_log(module=_MODULE, action="登记客户回签", description="登记客户回签确认")
async def customer_sign(
    request: Request,
    recon_id: int,
    data: ReconCustomerSignRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.record_customer_sign(
        db, recon_id,
        signer_name=data.signerName,
        voucher_url=data.voucherUrl,
        signed_at=data.signedAt,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, recon_id), message="已登记客户回签")


@router.post("/{recon_id}/withdraw")
@operation_log(module=_MODULE, action="退回草稿", description="对账单退回草稿")
async def withdraw_recon(
    request: Request,
    recon_id: int,
    data: ReconReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.withdraw(
        db, recon_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, recon_id), message="已退回草稿，可继续修改")


@router.post("/{recon_id}/cancel")
@operation_log(module=_MODULE, action="撤销对账单", description="撤销客户对账单")
async def cancel_recon(
    request: Request,
    recon_id: int,
    data: ReconReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.cancel_recon(
        db, recon_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, recon_id), message="对账单已撤销")


@router.post("/{recon_id}/unlock-settled")
@operation_log(module=_MODULE, action="解锁已结清", description="已结清对账单解锁回已确认")
async def unlock_settled(
    request: Request,
    recon_id: int,
    data: ReconReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await CustomerReconService.unlock_settled(
        db, recon_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, recon_id), message="已解锁，可继续调整")


@router.get("/{recon_id}/events")
async def list_events(
    recon_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """审计事件流（详情抽屉「操作记录」区块）。"""
    events = await CustomerReconService.list_events(db, recon_id)
    return success(data=[
        {
            "id": e.id,
            "eventType": e.event_type,
            "fromStatus": e.from_status,
            "toStatus": e.to_status,
            "occurredAmount": (
                float(e.occurred_amount) if e.occurred_amount is not None else None
            ),
            "operatorId": e.operator_id,
            "operatorName": e.operator_name,
            "reason": e.reason,
            "eventTime": e.event_time,
        }
        for e in events
    ])
