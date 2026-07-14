"""
客户端工作台 - 推广位 Banner
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.client.schemas.workbench.banner import (
    BannerEventIn,
    BannerItem,
    BannerListOut,
)
from app.modules.client.services.banner_service import ClientBannerService

router = APIRouter()


def _require_tenant(current_user: TokenData) -> str:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")
    return current_user.tenant_code


@router.get("")
async def list_banners(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """当前用户可见的推广位 Banner 列表"""
    tenant_code = _require_tenant(current_user)
    raw = await ClientBannerService.list_visible(db, tenant_code)
    items = [BannerItem.model_validate(x) for x in raw]
    return success(data=BannerListOut(items=items).model_dump(mode="json"))


@router.post("/event")
async def report_event(
    data: BannerEventIn,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """上报曝光/点击埋点"""
    tenant_code = _require_tenant(current_user)
    await ClientBannerService.record_event(
        db,
        banner_id=data.banner_id,
        event_type=data.event_type,
        tenant_code=tenant_code,
        user_id=current_user.user_id,
        user_phone=current_user.phone,
        user_agent=request.headers.get("user-agent"),
    )
    return success(message="ok")
