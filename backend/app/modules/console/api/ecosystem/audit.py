"""运营后台：服务平台挂牌审核

对应 08.接口契约.md §4.1。

  - GET  /options                 下拉元数据（驳回原因、状态、类型）
  - GET  /backlog                 积压统计（顶部数字卡）
  - GET  /pending                 待审队列（按进队时间正序）
  - GET  /spot-check              抽检队列（免审直通已上架）
  - GET  /                        全量检索（按进队时间倒序）
  - GET  /{id}                    审核详情（判断依据一次给全）
  - POST /{id}/approve            通过
  - POST /{id}/reject             驳回
  - POST /batch-approve           批量通过
  - POST /{id}/force-delist       强制下架
  - POST /{id}/spot-check-pass    抽检通过
  - POST /{id}/spot-check-fail    抽检不通过

## 三个队列为什么是三个接口

排序口径不同：待审按提交时间正序（等最久的先处理），抽检按上架时间正序
（挂得最久的最该复核），全量检索按提交时间倒序（运营是来查最近发生了什么）。
合成一个接口靠参数切换，迟早有人改了默认排序把「先来先服务」变成「后来先审」，
而这件事在界面上完全看不出来，只会体现为高峰期 SLA 从尾部开始崩。

## 筛选条件三套队列共用

运营在待审队列里筛了「只看货源、只看有可疑标记的」，切到全量检索时希望条件
还在。所以查询参数收敛成同一个 ``AuditPostFilter``。
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.console.models.ecosystem.constants import (
    MAX_BATCH_APPROVE,
    REJECT_REASON_LABELS,
    SPOT_CHECK_HOURS,
)
from app.modules.console.models.system.user import User
from app.modules.console.schemas.ecosystem import (
    AuditApproveRequest,
    AuditRejectRequest,
    BatchApproveRequest,
    ForceDelistRequest,
    SpotCheckFailRequest,
    SpotCheckPassRequest,
)
from app.modules.console.services.ecosystem.audit_facade import EcoAuditFacade
from app.modules.console.services.ecosystem.audit_query_service import (
    AuditPostFilter,
    OpsContext,
)
from app.modules.console.services.ecosystem.audit_serializer import (
    AUDIT_STATUS_LABELS,
    POST_TYPE_LABELS,
    PRECHECK_FLAG_LABELS,
    EcoAuditSerializer,
)
from app.modules.console.services.ecosystem.audit_service import (
    REJECT_TEMPLATES,
    EcoAuditService,
)
from app.modules.client.services.ecosystem.post_state_machine import STATUS_LABELS

MODULE = "服务平台审核"

router = APIRouter()


async def _ops(db: AsyncSession, current_user: TokenData) -> OpsContext:
    """审核动作的操作人

    姓名要落进 ``sys_eco_post_audit.operator_name``：出现审核纠纷时，
    「谁在什么时候通过了这条」必须能查到人，只存 user_id 等于每次都要再查一次库，
    而那时用户可能已经被停用甚至删除了。
    """
    name = (
        await db.execute(select(User.real_name).where(User.id == current_user.user_id))
    ).scalar()
    return OpsContext(
        user_id=current_user.user_id,
        user_name=name or current_user.phone,
    )


def _filter(
    *,
    page: int,
    size: int,
    postType: Optional[int],
    tenantCode: Optional[str],
    keyword: Optional[str],
    flaggedOnly: bool,
    overdueOnly: bool,
    statuses: Optional[List[int]] = None,
    auditStatuses: Optional[List[int]] = None,
    submittedFrom: Optional[datetime] = None,
    submittedTo: Optional[datetime] = None,
) -> AuditPostFilter:
    return AuditPostFilter(
        post_type=postType,
        tenant_code=tenantCode,
        keyword=keyword,
        flagged_only=flaggedOnly,
        overdue_only=overdueOnly,
        statuses=statuses or None,
        audit_statuses=auditStatuses or None,
        submitted_from=submittedFrom,
        submitted_to=submittedTo,
        page=page,
        size=size,
    )


# ======================================================================
# 元数据与统计
# ======================================================================


@router.get("/options")
async def audit_options(_: TokenData = Depends(get_current_user)):
    """下拉元数据

    驳回原因由后端下发并附带模板文案：运营在界面上选原因时就能看到
    「不补充说明时租户会收到哪句话」，避免套用了一句不合适的模板还不知道。
    """
    return success(
        data={
            "rejectReasons": [
                {
                    "value": code,
                    "label": label,
                    "template": REJECT_TEMPLATES.get(code),
                    # 没有模板的原因（其他）必须自己写说明
                    "reasonRequired": code not in REJECT_TEMPLATES,
                }
                for code, label in REJECT_REASON_LABELS.items()
            ],
            "postStatuses": [
                {"value": k, "label": v} for k, v in STATUS_LABELS.items()
            ],
            "auditStatuses": [
                {"value": k, "label": v} for k, v in AUDIT_STATUS_LABELS.items()
            ],
            "postTypes": [
                {"value": k, "label": v} for k, v in POST_TYPE_LABELS.items()
            ],
            # 队列行里的 precheckFlags 是编码，界面要显示人话
            "precheckFlags": [
                {"value": k, "label": v} for k, v in PRECHECK_FLAG_LABELS.items()
            ],
            "batchApproveLimit": MAX_BATCH_APPROVE,
            "spotCheckHours": SPOT_CHECK_HOURS,
        }
    )


@router.get("/backlog")
async def audit_backlog(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """积压统计"""
    return success(data=await EcoAuditFacade.backlog(db))


# ======================================================================
# 队列
# ======================================================================


@router.get("/pending")
async def page_pending(
    page: int = Query(1, ge=1),
    size: int = Query(20, alias="limit", ge=1, le=100),
    postType: Optional[int] = Query(None),
    tenantCode: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    flaggedOnly: bool = Query(False),
    overdueOnly: bool = Query(False),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """待人工审核队列"""
    flt = _filter(
        page=page, size=size, postType=postType, tenantCode=tenantCode,
        keyword=keyword, flaggedOnly=flaggedOnly, overdueOnly=overdueOnly,
    )
    return success(data=await EcoAuditFacade.page_pending(db, flt))


@router.get("/spot-check")
async def page_spot_check(
    page: int = Query(1, ge=1),
    size: int = Query(20, alias="limit", ge=1, le=100),
    postType: Optional[int] = Query(None),
    tenantCode: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    flaggedOnly: bool = Query(False),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """免审直通待抽检队列

    没有 ``overdueOnly``：抽检的时限口径是「上架后 N 小时内复核」
    （``SPOT_CHECK_HOURS``），与人工审核的工作时段 SLA 不是一回事，
    共用一个参数名只会让两边都算错。
    """
    flt = _filter(
        page=page, size=size, postType=postType, tenantCode=tenantCode,
        keyword=keyword, flaggedOnly=flaggedOnly, overdueOnly=False,
    )
    return success(data=await EcoAuditFacade.page_spot_check(db, flt))


@router.get("")
async def page_all(
    page: int = Query(1, ge=1),
    size: int = Query(20, alias="limit", ge=1, le=100),
    postType: Optional[int] = Query(None),
    tenantCode: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    flaggedOnly: bool = Query(False),
    overdueOnly: bool = Query(False),
    statuses: Optional[List[int]] = Query(None),
    auditStatuses: Optional[List[int]] = Query(None),
    submittedFrom: Optional[datetime] = Query(None),
    submittedTo: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """全量检索"""
    flt = _filter(
        page=page, size=size, postType=postType, tenantCode=tenantCode,
        keyword=keyword, flaggedOnly=flaggedOnly, overdueOnly=overdueOnly,
        statuses=statuses, auditStatuses=auditStatuses,
        submittedFrom=submittedFrom, submittedTo=submittedTo,
    )
    return success(data=await EcoAuditFacade.page_all(db, flt))


# ======================================================================
# 动作
# ======================================================================


@router.post("/batch-approve")
@operation_log(module=MODULE, action="批量通过", description="批量通过挂牌审核")
async def batch_approve(
    request: Request,
    data: BatchApproveRequest,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """批量通过

    **部分失败仍返回成功响应**，前端按 ``failed`` 是否为空决定用成功提示还是
    带明细的警告弹层。当成整体失败处理会让运营以为通过的那些也没生效，
    然后重复点击。
    """
    result = await EcoAuditService.batch_approve(
        db, data.postIds, operator=await _ops(db, current_user)
    )
    return success(
        data=EcoAuditSerializer.batch_result(result), message=result.message
    )


@router.get("/{post_id}")
async def audit_detail(
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """审核详情"""
    return success(data=await EcoAuditFacade.detail(db, post_id))


@router.post("/{post_id}/approve")
@operation_log(module=MODULE, action="审核通过", description="通过挂牌审核")
async def approve(
    request: Request,
    data: AuditApproveRequest,
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """审核通过，挂牌进入大厅"""
    result = await EcoAuditService.approve(
        db, post_id, operator=await _ops(db, current_user), remark=data.remark
    )
    return success(
        data=EcoAuditSerializer.action_result(result), message=result.message
    )


@router.post("/{post_id}/reject")
@operation_log(module=MODULE, action="审核驳回", description="驳回挂牌审核")
async def reject(
    request: Request,
    data: AuditRejectRequest,
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """驳回。``reason`` 原样展示给租户，留空时套用原因模板"""
    result = await EcoAuditService.reject(
        db,
        post_id,
        reason_code=data.reasonCode,
        reason=data.reason,
        operator=await _ops(db, current_user),
    )
    return success(
        data=EcoAuditSerializer.action_result(result), message=result.message
    )


@router.post("/{post_id}/force-delist")
@operation_log(module=MODULE, action="强制下架", description="强制下架违规挂牌")
async def force_delist(
    request: Request,
    data: ForceDelistRequest,
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """强制下架

    正在洽谈的意向会一并失效并通知对方；已进入成交的挂牌拦下，
    提示到成交单里走终止流程。
    """
    result = await EcoAuditService.force_delist(
        db,
        post_id,
        reason=data.reason,
        reason_code=data.reasonCode,
        operator=await _ops(db, current_user),
        revoke_whitelist=data.revokeWhitelist,
    )
    return success(
        data=EcoAuditSerializer.action_result(result), message=result.message
    )


@router.post("/{post_id}/spot-check-pass")
@operation_log(module=MODULE, action="抽检通过", description="免审挂牌抽检通过")
async def spot_check_pass(
    request: Request,
    data: SpotCheckPassRequest,
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """抽检通过：只改审核状态，挂牌本来就在大厅里挂着"""
    result = await EcoAuditService.spot_check_pass(
        db, post_id, operator=await _ops(db, current_user), remark=data.remark
    )
    return success(
        data=EcoAuditSerializer.action_result(result), message=result.message
    )


@router.post("/{post_id}/spot-check-fail")
@operation_log(module=MODULE, action="抽检不通过", description="免审挂牌抽检不通过")
async def spot_check_fail(
    request: Request,
    data: SpotCheckFailRequest,
    post_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """抽检不通过：下架 + 移出免审白名单"""
    result = await EcoAuditService.spot_check_fail(
        db,
        post_id,
        reason=data.reason,
        reason_code=data.reasonCode,
        operator=await _ops(db, current_user),
    )
    return success(
        data=EcoAuditSerializer.action_result(result), message=result.message
    )
