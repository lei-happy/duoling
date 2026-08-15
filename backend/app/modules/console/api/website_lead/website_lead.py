"""
官网线索管理接口（Console）
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.console.schemas.website_lead.website_lead import WebsiteLeadFollowIn
from app.modules.console.services.website_lead.website_lead_service import (
    WebsiteLeadService,
)

router = APIRouter()


@router.get("")
async def list_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    status: Optional[int] = Query(None, description="跟进状态"),
    stage_band: Optional[str] = Query(None, description="测评档位 L1-L8"),
    fleet_size: Optional[str] = Query(None, description="车队规模"),
    keyword: Optional[str] = Query(None, description="企业/联系人/手机号关键词"),
    created_from: Optional[datetime] = Query(None, description="留资开始时间"),
    created_to: Optional[datetime] = Query(None, description="留资结束时间"),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """分页查询官网留资线索"""
    items, total = await WebsiteLeadService.list_leads(
        db,
        page=page,
        limit=limit,
        status=status,
        stage_band=stage_band,
        fleet_size=fleet_size,
        keyword=keyword,
        created_from=created_from,
        created_to=created_to,
    )
    return success(
        data={
            "list": [item.model_dump(mode="json") for item in items],
            "total": total,
            "page": page,
            "limit": limit,
        }
    )


@router.get("/{lead_id}")
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取线索详情"""
    item = await WebsiteLeadService.get_detail(db, lead_id)
    return success(data=item.model_dump(mode="json"))


@router.put("/{lead_id}/follow")
async def follow_lead(
    lead_id: int,
    data: WebsiteLeadFollowIn,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新跟进状态与备注"""
    handler_name = await WebsiteLeadService.resolve_handler_name(
        db, current_user.user_id
    )
    item = await WebsiteLeadService.follow_lead(
        db,
        lead_id,
        data,
        handler_id=current_user.user_id,
        handler_name=handler_name,
    )
    return success(data=item.model_dump(mode="json"), message="已更新跟进记录")
