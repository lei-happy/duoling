"""
自有运力-运力分组 API

分组 CRUD + 成员管理：
  - GET    /                分组分页列表（含 memberCount）
  - GET    /options         启用分组精简列表（供成本规则条件下拉）
  - POST   /                新建分组
  - PUT    /{id}            编辑分组
  - PUT    /{id}/status     启用/停用
  - DELETE /{id}            删除分组（连带软删成员）
  - GET    /{id}/members    分组成员分页（联查当前运力）
  - POST   /{id}/members    批量添加成员（传运力ID，落库 driver_id）
  - DELETE /{id}/members    批量移出成员
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_tenant_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.common.operation_log import operation_log
from app.modules.client.schemas.capacity.self_capacity.capacity_group import (
    CapacityGroupCreate,
    CapacityGroupUpdate,
    CapacityGroupStatusUpdate,
    CapacityGroupMemberAdd,
    CapacityGroupMemberRemove,
)
from app.modules.client.services.capacity.self_capacity.capacity_group_service import (
    CapacityGroupService,
)

router = APIRouter()


@router.get("/options")
async def group_options(
    enterpriseId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """启用状态分组精简列表"""
    data = await CapacityGroupService.list_options(db, enterprise_id=enterpriseId)
    return success(data=data)


@router.get("")
async def page_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    status: Optional[int] = Query(None),
    enterpriseId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """运力分组分页列表"""
    data = await CapacityGroupService.page_groups(
        db, page=page, page_size=page_size, keyword=keyword,
        status=status, enterprise_id=enterpriseId,
    )
    return success(data=data)


@router.post("")
@operation_log(module="运力分组", action="新建分组", description="创建运力分组")
async def create_group(
    request: Request,
    data: CapacityGroupCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """新建分组"""
    result = await CapacityGroupService.create_group(
        db, data, operator_user_id=current_user.user_id,
    )
    return success(data=result.model_dump(), message="分组已创建")


@router.put("/{group_id}")
@operation_log(module="运力分组", action="编辑分组", description="修改运力分组")
async def update_group(
    request: Request,
    group_id: int,
    data: CapacityGroupUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """编辑分组"""
    result = await CapacityGroupService.update_group(
        db, group_id, data, operator_user_id=current_user.user_id,
    )
    return success(data=result.model_dump(), message="分组已更新")


@router.put("/{group_id}/status")
@operation_log(module="运力分组", action="启停分组", description="启用/停用运力分组")
async def update_group_status(
    request: Request,
    group_id: int,
    data: CapacityGroupStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """启用/停用"""
    await CapacityGroupService.update_status(db, group_id, data.status)
    return success(message="已启用" if data.status == 1 else "已停用")


@router.delete("/{group_id}")
@operation_log(module="运力分组", action="删除分组", description="删除运力分组")
async def delete_group(
    request: Request,
    group_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """删除分组"""
    await CapacityGroupService.delete_group(db, group_id)
    return success(message="分组已删除")


@router.get("/{group_id}/members")
async def page_members(
    group_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """分组成员分页列表"""
    data = await CapacityGroupService.page_members(
        db, group_id, page=page, page_size=page_size, keyword=keyword,
    )
    return success(data=data)


@router.post("/{group_id}/members")
@operation_log(module="运力分组", action="添加成员", description="向运力分组添加成员")
async def add_members(
    request: Request,
    group_id: int,
    data: CapacityGroupMemberAdd,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """批量添加成员（传运力ID列表）"""
    result = await CapacityGroupService.add_members(
        db, group_id, data.capacityIds, operator_user_id=current_user.user_id,
    )
    msg = f"已添加 {result['added']} 条运力"
    if result["skipped"]:
        msg += f"，跳过 {result['skipped']} 条（已在组内或无效）"
    return success(data=result, message=msg)


@router.delete("/{group_id}/members")
@operation_log(module="运力分组", action="移出成员", description="从运力分组移出成员")
async def remove_members(
    request: Request,
    group_id: int,
    data: CapacityGroupMemberRemove,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """批量移出成员"""
    result = await CapacityGroupService.remove_members(
        db, group_id, member_ids=data.memberIds, driver_ids=data.driverIds,
    )
    return success(data=result, message=f"已移出 {result['removed']} 条运力")
