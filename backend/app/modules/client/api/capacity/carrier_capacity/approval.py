"""
承运商运力-审批 API（占位 router）

TODO: 后续实现承运商审批流程，当前仅提供分页空响应。
"""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.common.response import success

router = APIRouter()


@router.get("")
async def page_carrier_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    _=Depends(get_current_user),
):
    return success(data={
        "list": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
    })
