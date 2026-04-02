"""
企业端客户管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerOut,
)
from app.modules.client.services.customer_service import CustomerService

router = APIRouter()


@router.get("")
async def page_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerType: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await CustomerService.page_customers(
        db, page=page, page_size=page_size,
        keyword=keyword, customer_type=customerType, status=status,
    )
    return success(data=data)


@router.post("")
@operation_log(module="客户管理", action="新增", description="新增客户")
async def create_customer(
    request: Request,
    data: CustomerCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    customer = await CustomerService.create_customer(db, data)
    return success(data=CustomerOut.from_model(customer).model_dump())


@router.put("/{customer_id}")
@operation_log(module="客户管理", action="编辑", description="编辑客户")
async def update_customer(
    request: Request,
    customer_id: int,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    customer = await CustomerService.update_customer(db, customer_id, data)
    return success(data=CustomerOut.from_model(customer).model_dump())


@router.delete("/{customer_id}")
@operation_log(module="客户管理", action="删除", description="删除客户")
async def delete_customer(
    request: Request,
    customer_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await CustomerService.delete_customer(db, customer_id)
    return success()
