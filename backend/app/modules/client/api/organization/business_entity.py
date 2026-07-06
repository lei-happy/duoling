"""
企业端经营主体管理 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.schemas.organization.business_entity import (
    BusinessEntityCreate,
    BusinessEntityStatusUpdate,
    BusinessEntityUpdate,
)
from app.modules.client.services.organization.business_entity_service import (
    BusinessEntityService,
)

router = APIRouter()


@router.get("/page")
async def page_entities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """分页查询经营主体"""
    result = await BusinessEntityService.page(
        db, page=page, limit=limit, keyword=keyword, status=status,
    )
    return success(data=result)


@router.get("/options")
async def list_entity_options(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """经营主体下拉选项（仅正常状态，供各业务表单选择器）"""
    return success(data=await BusinessEntityService.options(db))


@router.get("/{entity_id}")
async def get_entity(
    entity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """经营主体详情"""
    data = await BusinessEntityService.get(db, entity_id)
    return success(data=data.model_dump())


@router.post("")
@operation_log(module="经营主体", action="新增", description="新增经营主体")
async def create_entity(
    request: Request,
    data: BusinessEntityCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """新增经营主体"""
    out = await BusinessEntityService.create(db, data)
    return success(data=out.model_dump())


@router.put("/{entity_id}")
@operation_log(module="经营主体", action="编辑", description="编辑经营主体")
async def update_entity(
    request: Request,
    entity_id: int,
    data: BusinessEntityUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """编辑经营主体"""
    out = await BusinessEntityService.update(db, entity_id, data)
    return success(data=out.model_dump())


@router.patch("/{entity_id}/default")
@operation_log(module="经营主体", action="设为默认", description="设为默认经营主体")
async def set_default_entity(
    request: Request,
    entity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """设为默认主体"""
    out = await BusinessEntityService.set_default(db, entity_id)
    return success(data=out.model_dump())


@router.patch("/{entity_id}/status")
@operation_log(module="经营主体", action="启停", description="启用/停用经营主体")
async def toggle_entity_status(
    request: Request,
    entity_id: int,
    data: BusinessEntityStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """启用 / 停用主体"""
    out = await BusinessEntityService.toggle_status(db, entity_id, data.status)
    return success(data=out.model_dump())


@router.delete("/{entity_id}")
@operation_log(module="经营主体", action="删除", description="删除经营主体")
async def delete_entity(
    request: Request,
    entity_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """删除经营主体（关联校验 + 默认主体保护）"""
    await BusinessEntityService.delete(db, entity_id)
    return success()
