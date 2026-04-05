"""
企业管理接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.client.schemas.enterprise import UpdateSystemNameRequest
from app.modules.client.services.enterprise_service import EnterpriseService

router = APIRouter()


@router.get("/info")
async def get_enterprise_info(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """获取企业信息及版本详情"""
    info = await EnterpriseService.get_enterprise_info(
        db, current_user.tenant_code
    )
    return success(data=info.model_dump())


@router.put("/system-name")
async def update_system_name(
    request: UpdateSystemNameRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """更新系统自定义名称（仅企业管理员可操作）"""
    await EnterpriseService.update_system_name(
        db, current_user.tenant_code, current_user.user_id, request
    )
    return success(message="系统名称更新成功")
