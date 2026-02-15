"""
用户管理接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.user import UserCreate, UserUpdate, UserOut, UpdatePasswordRequest
from app.modules.console.services.user_service import UserService

router = APIRouter()


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = None,
    user_type: Optional[int] = None,
    tenant_code: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取用户列表"""
    items, total = await UserService.get_user_list(
        db, page=page, page_size=page_size,
        keyword=keyword, user_type=user_type,
        tenant_code=tenant_code, status=status,
    )
    return success(data={
        "list": [UserOut.model_validate(u).model_dump() for u in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取用户详情"""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        return fail("用户不存在")
    return success(data=UserOut.model_validate(user).model_dump())


@router.post("")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """创建用户"""
    user = await UserService.create_user(db, data)
    return success(data=UserOut.model_validate(user).model_dump(), message="创建成功")


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新用户"""
    user = await UserService.update_user(db, user_id, data)
    return success(data=UserOut.model_validate(user).model_dump(), message="更新成功")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """删除用户"""
    await UserService.delete_user(db, user_id)
    return success(message="删除成功")


@router.put("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """重置用户密码（管理员操作，重置为 123456）"""
    await UserService.reset_password(db, user_id, "123456")
    return success(message="密码已重置为 123456")


@router.put("/me/password")
async def update_my_password(
    data: UpdatePasswordRequest,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """修改当前用户密码"""
    await UserService.update_password(
        db, current_user.user_id, data.old_password, data.new_password
    )
    return success(message="密码修改成功")
