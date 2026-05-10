"""
客户端工作台 - 最新动态
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException, TenantException
from app.common.response import success
from app.core.config import get_settings
from app.core.dependencies import (
    get_current_user,
    get_tenant_db,
    ensure_biz_company_activity_table,
)
from app.core.security import TokenData
from app.modules.client.schemas.workbench.company_activity import (
    CompanyActivityItem,
    CompanyActivityListOut,
    CompanyActivityDemoSeedOut,
)
from app.modules.client.services.company_activity_service import CompanyActivityService

router = APIRouter()


def _require_tenant(current_user: TokenData) -> str:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")
    return current_user.tenant_code


@router.get("")
async def list_activities(
    limit: int = Query(50, ge=1, le=100),
    current_user: TokenData = Depends(get_current_user),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """当日企业动态列表（最新在上）"""
    _require_tenant(current_user)
    raw = await CompanyActivityService.list_today(tenant_db, limit=limit)
    items = [CompanyActivityItem.model_validate(x) for x in raw]
    return success(data=CompanyActivityListOut(items=items).model_dump(mode="json"))


@router.post("/demo-seed")
async def demo_seed(
    current_user: TokenData = Depends(get_current_user),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """开发环境写入演示数据；生产环境不可用。"""
    _require_tenant(current_user)
    settings = get_settings()
    if not settings.is_dev:
        raise BizException("当前环境不支持演示种子接口")

    inserted = await CompanyActivityService.seed_demo_if_dev(tenant_db)
    return success(
        data=CompanyActivityDemoSeedOut(inserted=inserted).model_dump(mode="json"),
        message="ok",
    )
