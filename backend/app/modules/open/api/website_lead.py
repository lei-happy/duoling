"""
官网留资接口（公开，无需认证）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_platform_db
from app.modules.open.schemas.website_lead import LeadSubmitRequest
from app.modules.open.services.website_lead_service import WebsiteLeadService

router = APIRouter()


def _client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return request.client.host if request.client else None


@router.post("")
async def submit_lead(
    data: LeadSubmitRequest,
    request: Request,
    db: AsyncSession = Depends(get_platform_db),
):
    """
    官网留资：记录访客的联系方式与自测结果，由运营端跟进。

    被限流或判定为脚本时同样返回成功文案，避免对方据此探测规则。
    """
    await WebsiteLeadService.submit(
        db,
        data,
        client_ip=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )
    return success(
        data={"accepted": True},
        message="已收到你的信息，顾问会在 1 个工作日内联系你",
    )
