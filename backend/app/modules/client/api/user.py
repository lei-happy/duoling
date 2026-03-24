"""
企业端员工管理 API
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.user import (
    BizUserCreate, BizUserUpdate, BizUserOut, BizUserResetPassword,
)
from app.modules.client.services.user_service import BizUserService

router = APIRouter()


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询员工列表"""
    result = await BizUserService.page_users(
        db, page=page, page_size=pageSize,
        keyword=keyword, department=department, status=status,
    )
    return success(data=result)


@router.post("")
async def create_user(
    data: BizUserCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """创建员工"""
    user = await BizUserService.create_user(db, data)
    roles = await BizUserService._get_user_roles(db, user.id)
    return success(data=BizUserOut.from_model(user, roles=roles).model_dump())


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: BizUserUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """更新员工"""
    user = await BizUserService.update_user(db, user_id, data)
    roles = await BizUserService._get_user_roles(db, user.id)
    return success(data=BizUserOut.from_model(user, roles=roles).model_dump())


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除员工"""
    await BizUserService.delete_user(db, user_id)
    return success()


@router.put("/password/reset")
async def reset_password(
    data: BizUserResetPassword,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """重置员工密码"""
    await BizUserService.reset_password(db, data.userId, data.newPassword)
    return success(message="密码重置成功")
