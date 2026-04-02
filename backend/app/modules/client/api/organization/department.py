"""
企业端组织架构/部门管理 API
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.organization.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
)
from app.modules.client.services.organization.department_service import DepartmentService

router = APIRouter()


@router.get("/page")
async def page_departments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    organizationName: Optional[str] = Query(None),
    organizationType: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询部门"""
    result = await DepartmentService.page_departments(
        db, page=page, limit=limit,
        organization_name=organizationName,
        organization_type=organizationType,
    )
    return success(data=result)


@router.get("")
async def list_departments(
    organizationName: Optional[str] = Query(None),
    organizationType: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取部门列表（平铺）"""
    items = await DepartmentService.list_departments(
        db, organization_name=organizationName,
        organization_type=organizationType,
        sort=sort, order=order,
    )
    return success(data=[item.model_dump() for item in items])


@router.get("/tree")
async def get_department_tree(
    organizationName: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取部门树形结构"""
    tree = await DepartmentService.get_department_tree(
        db, organization_name=organizationName,
    )
    return success(data=tree)


@router.post("")
@operation_log(module="组织架构", action="新增", description="新增部门")
async def create_department(
    request: Request,
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建部门"""
    dept = await DepartmentService.create_department(db, data)
    return success(data=DepartmentOut.from_model(dept).model_dump())


@router.put("")
@operation_log(module="组织架构", action="编辑", description="编辑部门")
async def update_department(
    request: Request,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新部门"""
    dept = await DepartmentService.update_department(db, data.organizationId, data)
    return success(data=DepartmentOut.from_model(dept).model_dump())


@router.delete("/{dept_id}")
@operation_log(module="组织架构", action="删除", description="删除部门")
async def delete_department(
    request: Request,
    dept_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除部门"""
    await DepartmentService.delete_department(db, dept_id)
    return success()
