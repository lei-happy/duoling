"""
企业端员工管理 API
"""

from typing import Optional, List
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from loguru import logger

from app.core.dependencies import get_tenant_db, get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.operation_log import operation_log
from app.common.exceptions import TenantException
from app.modules.client.schemas.user.user import (
    BizUserCreate, BizUserUpdate, BizUserOut,
    BizUserStatusUpdate,
)
from app.modules.client.services.user.user_service import BizUserService
from app.modules.client.services.user.platform_user_sync import BizPlatformUserSync
from app.modules.client.services.quota_service import QuotaService

router = APIRouter()


@router.get("/page")
async def page_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    phone: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    sex: Optional[str] = Query(None),
    organizationId: Optional[int] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询员工列表"""
    result = await BizUserService.page_users(
        db, page=page, limit=limit,
        phone=phone, nickname=nickname,
        status=status,
        sex=sex,
        organization_id=organizationId,
        sort=sort,
        order=order,
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
    phone: Optional[str] = Query(None),
    nickname: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    sex: Optional[str] = Query(None),
    organizationId: Optional[int] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """查询员工列表（不分页）"""
    items = await BizUserService.list_users(
        db,
        phone=phone,
        nickname=nickname,
        status=status,
        sex=sex,
        organization_id=organizationId,
        sort=sort,
        order=order,
    )
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
@operation_log(module="员工管理", action="新增", description="新增员工")
async def create_user(
    request: Request,
    data: BizUserCreate,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """创建员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await QuotaService.ensure_user_quota(db, current.tenant_code)
    user = await BizUserService.create_user(db, data)
    try:
        await BizPlatformUserSync.sync_employee_create(
            pdb, db, current.tenant_code, user.id, data.roleIds
        )
    except Exception as e:
        logger.error(
            f"同步员工到平台库失败 | tenant={current.tenant_code} "
            f"biz_user_id={user.id} phone={data.phone} error={e}",
            exc_info=True,
        )
        raise
    roles = await BizUserService._get_user_roles(db, user.id)
    dept_name = await BizUserService._get_dept_name(db, user.department_id)
    return success(data=BizUserOut.from_model(user, roles=roles, dept_name=dept_name).model_dump())


@router.put("")
@operation_log(module="员工管理", action="编辑", description="编辑员工")
async def update_user(
    request: Request,
    data: BizUserUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """更新员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    user = await BizUserService.update_user(db, data.userId, data)
    try:
        await BizPlatformUserSync.sync_employee_update(
            pdb, db, current.tenant_code, user.id, data.roleIds
        )
    except Exception as e:
        logger.error(
            f"同步员工更新到平台库失败 | tenant={current.tenant_code} "
            f"biz_user_id={user.id} error={e}",
            exc_info=True,
        )
        raise
    roles = await BizUserService._get_user_roles(db, user.id)
    dept_name = await BizUserService._get_dept_name(db, user.department_id)
    return success(data=BizUserOut.from_model(user, roles=roles, dept_name=dept_name).model_dump())


@router.put("/status")
@operation_log(module="员工管理", action="状态变更", description="变更员工状态")
async def update_user_status(
    request: Request,
    data: BizUserStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """修改员工状态"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await BizUserService.update_status(db, data.userId, data.status)
    try:
        await BizPlatformUserSync.sync_employee_status(
            pdb, db, current.tenant_code, data.userId, data.status
        )
    except Exception as e:
        logger.error(
            f"同步员工状态到平台库失败 | tenant={current.tenant_code} "
            f"biz_user_id={data.userId} error={e}",
            exc_info=True,
        )
        raise
    return success()


@router.delete("/batch")
@operation_log(module="员工管理", action="批量删除", description="批量删除员工")
async def batch_delete_users(
    request: Request,
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
        try:
            await BizPlatformUserSync.sync_employee_remove(
                pdb, db, current.tenant_code, uid
            )
        except Exception as e:
            logger.error(
                f"同步删除员工到平台库失败 | tenant={current.tenant_code} "
                f"biz_user_id={uid} error={e}",
                exc_info=True,
            )
            raise
    return success()


@router.delete("/{user_id}")
@operation_log(module="员工管理", action="删除", description="删除员工")
async def delete_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    pdb: AsyncSession = Depends(get_platform_db),
    current: TokenData = Depends(get_current_user),
):
    """删除员工"""
    if not current.tenant_code:
        raise TenantException("缺少租户信息，无法同步登录账号")
    await BizUserService.delete_user(db, user_id)
    try:
        await BizPlatformUserSync.sync_employee_remove(
            pdb, db, current.tenant_code, user_id
        )
    except Exception as e:
        logger.error(
            f"同步删除员工到平台库失败 | tenant={current.tenant_code} "
            f"biz_user_id={user_id} error={e}",
            exc_info=True,
        )
        raise
    return success()
