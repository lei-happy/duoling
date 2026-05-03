"""Console 端：数字员工管理"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.ai.schemas.console.employee import EmployeeCreate, EmployeeUpdate
from app.modules.ai.services.employee_service import EmployeeService

router = APIRouter()


@router.get("")
async def page_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = Query(None),
    employee_type: Optional[str] = Query(None, alias="employeeType"),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await EmployeeService.page(
        db, page=page, page_size=page_size,
        keyword=keyword, status=status, employee_type=employee_type,
    )
    return success(data=data)


@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await EmployeeService.get(db, employee_id)
    return success(data=data)


@router.post("")
async def create_employee(
    body: EmployeeCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await EmployeeService.create(db, body)
    return success(data={"id": row.id}, message="创建成功")


@router.put("/{employee_id}")
async def update_employee(
    employee_id: int,
    body: EmployeeUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await EmployeeService.update(db, employee_id, body)
    return success(message="更新成功")


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await EmployeeService.delete(db, employee_id)
    return success(message="删除成功")
