"""
企业端客户管理 API
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import TenantException
from app.common.mask_display import mask_organization_name
from app.common.operation_log import operation_log
from app.core.dependencies import (
    ensure_biz_company_activity_table,
    get_current_user,
    get_tenant_db,
)
from app.common.response import success
from app.core.security import TokenData
from app.modules.client.schemas.partner.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
)
from app.modules.client.services.company_activity_service import CompanyActivityService
from app.modules.client.services.partner.customer_service import CustomerService

router = APIRouter()


def _require_tenant_for_activity(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


@router.get("")
async def page_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerType: Optional[int] = None,
    settlementType: Optional[int] = None,
    status: Optional[int] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CustomerService.page_customers(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        customer_type=customerType,
        settlement_type=settlementType,
        status=status,
        sort=sort,
        order=order,
    )
    return success(data=data)


@router.get("/select")
async def select_customers(
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CustomerService.select_customers(db, keyword=keyword)
    return success(data=data)


@router.get("/{customer_id}")
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    customer = await CustomerService.get_customer(db, customer_id)
    return success(data=CustomerOut.from_model(customer).model_dump())


@router.post("")
@operation_log(module="客户管理", action="新增", description="新增客户")
async def create_customer(
    request: Request,
    data: CustomerCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    customer = await CustomerService.create_customer(db, data)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    masked = mask_organization_name(customer.customer_name)
    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="partner.customer_created",
        summary=f"{label} 新建了客户「{masked}」",
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload={"customer_id": customer.id},
    )
    return success(data=CustomerOut.from_model(customer).model_dump())


@router.put("/{customer_id}")
@operation_log(module="客户管理", action="编辑", description="编辑客户")
async def update_customer(
    request: Request,
    customer_id: int,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    customer = await CustomerService.update_customer(db, customer_id, data)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    masked = mask_organization_name(customer.customer_name)
    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="partner.customer_updated",
        summary=f"{label} 编辑了客户「{masked}」",
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload={"customer_id": customer.id},
    )
    return success(data=CustomerOut.from_model(customer).model_dump())


@router.delete("/{customer_id}")
@operation_log(module="客户管理", action="删除", description="删除客户")
async def delete_customer(
    request: Request,
    customer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    customer = await CustomerService.get_customer(db, customer_id)
    masked = mask_organization_name(customer.customer_name)
    await CustomerService.delete_customer(db, customer_id)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="partner.customer_deleted",
        summary=f"{label} 删除了客户「{masked}」",
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload={"customer_id": customer_id},
    )
    return success()
