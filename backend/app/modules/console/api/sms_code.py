"""
短信验证码记录接口（管理后台查看）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.services.sms_code_service import SmsCodeService

router = APIRouter()


@router.get("/page")
async def page_sms_codes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    phone: Optional[str] = Query(None),
    purpose: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询短信验证码记录"""
    result = await SmsCodeService.page_sms_codes(
        db,
        page=page,
        limit=limit,
        phone=phone,
        purpose=purpose,
        status=status,
        createTimeStart=createTimeStart,
        createTimeEnd=createTimeEnd,
    )
    return success(data=result)


@router.get("")
async def list_sms_codes(
    phone: Optional[str] = Query(None),
    purpose: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    createTimeStart: Optional[str] = Query(None),
    createTimeEnd: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询列表（导出等），最多 10000 条"""
    items = await SmsCodeService.list_sms_codes(
        db,
        phone=phone,
        purpose=purpose,
        status=status,
        createTimeStart=createTimeStart,
        createTimeEnd=createTimeEnd,
    )
    return success(data=[i.model_dump() for i in items])
