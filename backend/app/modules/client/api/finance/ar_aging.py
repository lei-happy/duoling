"""应收账龄与信用预警 API（文档 12 §六）

接口前缀：``/api/client/finance/ar-aging``

全部只读：账龄是结算单与收款核销的实时聚合视图，没有落表，也没有写操作。唯一的
写动作是高危预警留痕（见 ``customer-brief`` 的 ``scene``）。
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.ar_aging import (
    AgingCustomerRow,
    AgingSettleDetail,
    CustomerCreditBrief,
)
from app.modules.client.services.finance.customer.aging_service import AgingService
from app.modules.client.services.finance.customer.credit_alert_service import (
    CreditAlertService,
)

router = APIRouter()


@router.get("")
async def page_aging(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    customerId: Optional[int] = None,
    enterpriseId: Optional[int] = None,
    creditStatus: Optional[int] = Query(default=None, ge=0, le=2),
    keyword: Optional[str] = None,
    bucket: Optional[int] = Query(default=None, ge=0, le=7),
    onlyOverdue: bool = False,
    onlyExceeded: bool = False,
    baseDate: Optional[date] = Query(
        default=None, description="统计基准日，默认今天；传历史日期可回溯账龄",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """客户维度账龄汇总（按未收余额倒序）。"""
    data = await AgingService.customer_page(
        db,
        page=page, page_size=page_size, base_date=baseDate,
        customer_id=customerId, enterprise_id=enterpriseId,
        credit_status=creditStatus, keyword=keyword, bucket=bucket,
        only_overdue=onlyOverdue, only_exceeded=onlyExceeded,
    )
    data["list"] = [
        AgingCustomerRow.model_validate(x).model_dump() for x in data["list"]
    ]
    return success(data=data)


@router.get("/summary")
async def aging_summary(
    enterpriseId: Optional[int] = None,
    creditStatus: Optional[int] = Query(default=None, ge=0, le=2),
    keyword: Optional[str] = None,
    baseDate: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """顶部 KPI + 分桶分布 + 按经营主体分列。"""
    return success(data=await AgingService.summary(
        db,
        base_date=baseDate, enterprise_id=enterpriseId,
        credit_status=creditStatus, keyword=keyword,
    ))


@router.get("/detail")
async def aging_detail(
    customerId: int = Query(..., description="客户ID"),
    bucket: Optional[int] = Query(default=None, ge=0, le=7),
    baseDate: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """某客户的结算单明细（客户汇总行展开用，按到期日先后排）。"""
    data = await AgingService.customer_detail(
        db, customerId, base_date=baseDate, bucket=bucket,
    )
    data["list"] = [
        AgingSettleDetail.model_validate(x).model_dump() for x in data["list"]
    ]
    if data.get("customer"):
        data["customer"] = AgingCustomerRow.model_validate(
            data["customer"]
        ).model_dump()
    return success(data=data)


@router.get("/customer-brief")
async def customer_brief(
    customerId: int = Query(..., description="客户ID"),
    scene: Optional[str] = Query(
        default=None,
        description="展示场景：waybill_create / task_dispatch / recon_confirm / "
                    "settle_submit。传了场景表示提示真的展示给人看了，高危级会留痕",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """单客户预警摘要：未收余额、逾期、额度、超额、预警文案。

    供运单录入、派车确认、对账确认、结算提交等业务页面同步调用，**只提示不拦截**。
    """
    brief = await CreditAlertService.brief_with_alert(
        db, customerId, scene=scene, operator_id=current_user.user_id,
    )
    return success(data=CustomerCreditBrief.model_validate(brief).model_dump())


@router.get("/export")
async def export_aging(
    enterpriseId: Optional[int] = None,
    creditStatus: Optional[int] = Query(default=None, ge=0, le=2),
    keyword: Optional[str] = None,
    bucket: Optional[int] = Query(default=None, ge=0, le=7),
    baseDate: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """导出客户汇总 + 结算单明细两张表页。"""
    data = await AgingService.build_export_workbook(
        db,
        base_date=baseDate, enterprise_id=enterpriseId,
        credit_status=creditStatus, keyword=keyword, bucket=bucket,
    )
    stamp = (baseDate or date.today()).isoformat()
    return StreamingResponse(
        BytesIO(data),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="ar-aging-{stamp}.xlsx"'
            )
        },
    )
