"""
企业端系统配置 API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.schemas.system_config import SystemConfigUpdate, SystemConfigOut
from app.modules.client.services.system_config_service import SystemConfigService

router = APIRouter()


@router.get("")
async def list_configs(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await SystemConfigService.get_all(db)
    return success(data=data)


@router.get("/group/{group}")
async def list_configs_by_group(
    group: str,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await SystemConfigService.get_by_group(db, group)
    return success(data=data)


@router.put("/{key}")
@operation_log(module="系统配置", action="编辑", description="修改系统配置")
async def update_config(
    request: Request,
    key: str,
    data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    config = await SystemConfigService.update_value(db, key, data.configValue)
    return success(data=SystemConfigOut.from_model(config).model_dump())
