"""
企业端员工管理 API
"""

from typing import Optional, List
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.exceptions import TenantException
from app.modules.client.schemas.user.user import (
    BizUserCreate, BizUserUpdate, BizUserOut,
    BizUserStatusUpdate, BizUserResetPassword,
)
from app.modules.client.services.user.user_service import BizUserService
from app.modules.client.services.user.platform_user_sync import BizPlatformUserSync

router = APIRouter()


@router.get("/page")
async def page_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    organizationId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询员工列表"""
    result = await BizUserService.page_users(
        db, page=page, limit=limit,
        username=username, nickname=nickname,
        phone=phone, status=status,
        organization_id=organizationId,
    )
    return success(data=result)


@router.get("/existence")
async def check_existence(
    field: str = Query(...),
    value: str = Query(...),
    id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """检查用户名/手机号是否存在"""
    exists = await BizUserService.check_existence(db, field, value, exclude_id=id)
    if exists:
        return success(message="已存在", data=True)
    return success(message="可使用", data=False)


@router.get("")
async def list_users(
    organizationId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """查询员工列表（不分页）"""
    items = await BizUserService.list_users(db, organization_id=organizationId)
    return success(data=items)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """根据ID查询员工详情"""
    data = await BizUserService.get_user(db, user_id)
    return success(data=data)


@router.post("")
async def create_user(
    data: BizUserCreate,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """创建员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    user = await BizUserService.create_user(db, data)
    await BizPlatformUserSync.sync_employee_create(
        pdb, db, current.tenant_code, user.id, data.roleIds
    )
    roles = await BizUserService._get_user_roles(db, user.id)
    dept_name = await BizUserService._get_dept_name(db, user.department_id)
    return success(data=BizUserOut.from_model(user, roles=roles, dept_name=dept_name).model_dump())


@router.put("")
async def update_user(
    data: BizUserUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """更新员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    user = await BizUserService.update_user(db, data.userId, data)
    await BizPlatformUserSync.sync_employee_update(
        pdb, db, current.tenant_code, user.id, data.roleIds
    )
    roles = await BizUserService._get_user_roles(db, user.id)
    dept_name = await BizUserService._get_dept_name(db, user.department_id)
    return success(data=BizUserOut.from_model(user, roles=roles, dept_name=dept_name).model_dump())


@router.put("/status")
async def update_user_status(
    data: BizUserStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """修改员工状态"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await BizUserService.update_status(db, data.userId, data.status)
    await BizPlatformUserSync.sync_employee_status(
        pdb, db, current.tenant_code, data.userId, data.status
    )
    return success()


@router.put("/password")
async def reset_password(
    data: BizUserResetPassword,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """重置员工密码"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await BizUserService.reset_password(db, data.userId, data.password)
    await BizPlatformUserSync.sync_employee_password(
        pdb, db, current.tenant_code, data.userId, data.password
    )
    return success(message="密码重置成功")


@router.delete("/batch")
async def batch_delete_users(
    data: List[int] = Body(..., embed=False),
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """批量删除员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await BizUserService.batch_delete_users(db, data)
    for uid in data:
        await BizPlatformUserSync.sync_employee_remove(
            pdb, db, current.tenant_code, uid
        )
    return success()


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """删除员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await BizUserService.delete_user(db, user_id)
    await BizPlatformUserSync.sync_employee_remove(
        pdb, db, current.tenant_code, user_id
    )
    return success()
