"""驾驶员财务接口"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.driver.services.driver_context import get_current_driver
from app.modules.driver.services.driver_finance_service import DriverFinanceService

router = APIRouter()


@router.get("/my", summary="我的费用单分页")
async def list_my_docs(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=15, ge=1, le=100, alias="pageSize"),
    docType: Optional[int] = Query(default=None, description="1-预付 2-补款 3-结算"),
    status: Optional[int] = Query(default=None),
    yearMonth: Optional[str] = Query(
        default=None, description="按年月过滤，格式 YYYY-MM"
    ),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    items, total = await DriverFinanceService.list_my_docs(
        tenant_db, ctx,
        doc_type=docType,
        status=status,
        year_month=yearMonth,
        page=page,
        page_size=pageSize,
    )
    return success(
        data={
            "list": [it.model_dump() for it in items],
            "total": total,
            "page": page,
            "pageSize": pageSize,
        }
    )


@router.get("/summary", summary="收入汇总（按月 + doc_type）")
async def finance_summary(
    yearMonth: Optional[str] = Query(default=None),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    summary = await DriverFinanceService.summary(tenant_db, ctx, yearMonth)
    return success(data=summary.model_dump())


@router.get("/account", summary="我的收款账户")
async def list_my_accounts(
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    items = await DriverFinanceService.list_my_accounts(tenant_db, ctx)
    return success(data=[it.model_dump() for it in items])


@router.get("/fund-account", summary="我的资金账户（往来账）")
async def get_my_fund_account(
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    data = await DriverFinanceService.get_my_fund_account(tenant_db, ctx)
    return success(data=data)


@router.get("/fund-account/transactions", summary="我的资金流水")
async def list_my_fund_transactions(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=15, ge=1, le=100, alias="pageSize"),
    bizType: Optional[int] = Query(default=None),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    items, total = await DriverFinanceService.list_my_fund_transactions(
        tenant_db, ctx, biz_type=bizType, page=page, page_size=pageSize,
    )
    return success(
        data={"list": items, "total": total, "page": page, "pageSize": pageSize}
    )


@router.get("/{doc_id}", summary="费用单详情")
async def get_doc_detail(
    doc_id: int,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    detail = await DriverFinanceService.get_doc(tenant_db, ctx, doc_id)
    return success(data=detail.model_dump())
