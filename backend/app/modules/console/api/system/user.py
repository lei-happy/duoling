"""
用户管理接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.system.user import (
    UserCreate, UserUpdate, UserStatusUpdate,
)
from app.modules.console.services.system.user_service import UserService

router = APIRouter()


@router.get("/page")
async def page_users(
    page: int = Query(1),
    limit: int = Query(20),
    phone: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    sex: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询用户"""
    result = await UserService.page_users(
        db, page, limit, phone, nickname, status, sex
    )
    return success(data=result)


@router.get("/existence")
async def check_existence(
    field: str = Query("phone"),
    value: str = Query(...),
    userId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """检查用户名是否已存在"""
    exists = await UserService.check_existence(db, field, value, userId)
    return success(data=exists)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """根据 ID 查询用户"""
    result = await UserService.get_user(db, user_id)
    return success(data=result.model_dump())


@router.get("")
async def list_users(
    phone: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询用户列表"""
    items = await UserService.list_users(db, phone)
    return success(data=[item.model_dump() for item in items])


@router.post("")
async def add_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """新增用户"""
    await UserService.create_user(db, data)
    await db.commit()
    return success(message="添加成功")


@router.put("")
async def update_user(
    data: UserUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改用户"""
    await UserService.update_user(db, data)
    await db.commit()
    return success(message="修改成功")


@router.delete("/batch")
async def batch_delete_users(
    ids: List[int] = Body(..., embed=False),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量删除用户"""
    await UserService.batch_delete(db, ids)
    await db.commit()
    return success(message="删除成功")


@router.put("/status")
async def update_user_status(
    data: UserStatusUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """修改用户状态"""
    await UserService.update_status(db, data.userId, data.status)
    await db.commit()
    return success(message="修改成功")


