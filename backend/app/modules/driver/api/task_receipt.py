"""
驾驶员回单接口（一期最小：上传 URL + 列表）

注意：一期仅在 ``task_loading_record.photo_urls`` 中已有装/卸车照片字段；
回单（签收凭证）独立维度暂不落表，先以"按任务 / item 维度的占位接口"提供，
后续可在 ``biz_task_receipt`` 落表后无感升级。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.driver.services.driver_context import get_current_driver
from app.modules.driver.services.driver_task_service import DriverTaskService

router = APIRouter()


class ReceiptUploadRequest(BaseModel):
    taskId: int = Field(ge=1)
    itemId: Optional[int] = None
    fileUrls: List[str] = Field(min_length=1, max_length=9)
    remark: Optional[str] = Field(default=None, max_length=255)


@router.post("/upload", summary="上传回单图片（占位）")
async def upload_receipt(
    payload: ReceiptUploadRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    占位实现：仅校验任务可见性，落表能力待 ``biz_task_receipt`` 落地。
    上传 URL 由前端通过 ``/api/open/files/upload`` 取得后再回写。
    """
    ctx = await get_current_driver(tenant_db, current_user)
    await DriverTaskService._get_visible_task_or_404(
        tenant_db, ctx, payload.taskId
    )
    if not payload.fileUrls:
        raise BizException("请至少上传 1 张图片")
    return success(
        data={
            "taskId": payload.taskId,
            "itemId": payload.itemId,
            "fileUrls": payload.fileUrls,
            "remark": payload.remark,
            "stored": False,
            "tip": "回单落表能力 v0.2 上线后将自动持久化",
        },
        message="上传成功",
    )


@router.get("/my", summary="我的回单列表（占位）")
async def list_my_receipts(
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    # 一期未落表，返回空列表
    await get_current_driver(tenant_db, current_user)
    return success(data={"list": [], "total": 0, "page": 1, "pageSize": 0})
