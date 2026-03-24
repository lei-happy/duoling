"""
企业端组织架构/部门管理 API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
)
from app.modules.client.services.department_service import DepartmentService

router = APIRouter()


@router.get("")
async def list_departments(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取部门列表（平铺）"""
    items = await DepartmentService.list_departments(db)
    return success(data=[item.model_dump() for item in items])


@router.get("/tree")
async def get_department_tree(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取部门树形结构"""
    tree = await DepartmentService.get_department_tree(db)
    return success(data=tree)


@router.post("")
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建部门"""
    dept = await DepartmentService.create_department(db, data)
    return success(data=DepartmentOut.from_model(dept).model_dump())


@router.put("/{dept_id}")
async def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新部门"""
    dept = await DepartmentService.update_department(db, dept_id, data)
    return success(data=DepartmentOut.from_model(dept).model_dump())


@router.delete("/{dept_id}")
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除部门"""
    await DepartmentService.delete_department(db, dept_id)
    return success()
