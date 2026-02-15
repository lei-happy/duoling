"""
企业自助注册接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.modules.open.schemas.register import RegisterRequest
from app.modules.open.services.register_service import RegisterService

router = APIRouter()


@router.post("")
async def register_tenant(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """企业自助注册开户"""
    result = await RegisterService.register(db, data)
    return success(data=result.model_dump(), message="注册成功")
