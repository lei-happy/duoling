"""
合作客户（反向视角）API
B 视角：从 sys_carrier_link 反查所有把本企业纳入承运商互联的 A 公司。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import (
    get_platform_db, get_current_user, get_tenant_code,
)
from app.core.security import TokenData
from app.modules.client.services.partner.carrier_inbound_service import (
    CarrierInboundService,
)

router = APIRouter()


@router.get("")
async def page_inbound(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    linkStatus: Optional[int] = Query(
        None, description="1-激活 2-A端已删除 3-B端已退出；不传=全部"
    ),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    _: TokenData = Depends(get_current_user),
):
    """合作客户分页列表（B 视角）。

    数据来自 sys_carrier_link（linked_tenant_code = 当前租户），
    并联 sys_tenant 拿对方公司的实时基础信息（名称/联系人/地址等）。
    """
    items, total = await CarrierInboundService.list_page(
        platform_db,
        linked_tenant_code=tenant_code,
        keyword=keyword,
        link_status=linkStatus,
        page=page,
        page_size=page_size,
    )
    return success(data={
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })
