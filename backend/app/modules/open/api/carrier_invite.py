"""
承运商邀请着陆页/激活 - 开放接口（无需登录）
路径 B：未注册手机号点击邀请短信链接 → 输入企业名 + 真实姓名 + 短信验证码 → 创建 lite 租户
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_platform_db
from app.modules.client.services.partner.carrier_invite_service import (
    CarrierInviteService,
)
from app.modules.open.schemas.carrier_invite import (
    CarrierInviteActivateRequest,
)

router = APIRouter()


@router.get("/{invite_code}")
async def get_invite_info(
    invite_code: str,
    db: AsyncSession = Depends(get_platform_db),
):
    """着陆页加载邀请信息（仅返回脱敏字段）"""
    info = await CarrierInviteService.get_info_by_code(db, invite_code)
    return success(data=info.model_dump())


@router.post("/activate")
async def activate_invite(
    data: CarrierInviteActivateRequest,
    db: AsyncSession = Depends(get_platform_db),
):
    """着陆页提交激活：路径 B 创建 lite 租户并下发登录 token"""
    res = await CarrierInviteService.activate(db, data)
    return success(data=res.model_dump(), message="激活成功")
