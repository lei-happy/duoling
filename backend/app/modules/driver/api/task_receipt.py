"""
驾驶员回单接口（落表版）

- ``POST /task-receipt/upload``   上传回单（落 biz_task_receipt）
- ``GET  /task-receipt/my``       我的回单分页
- ``DELETE /task-receipt/{id}``   删除自己的回单

上传前置：图片 URL 由前端通过 ``/api/driver/file/upload``（scene=task_receipt）
取得后再回写。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.driver.services.driver_context import get_current_driver
from app.modules.driver.services.driver_receipt_service import DriverReceiptService
from app.modules.driver.services.driver_task_service import DriverTaskService

router = APIRouter()


class ReceiptUploadRequest(BaseModel):
    taskId: int = Field(ge=1)
    itemId: Optional[int] = None
    dispatchOrderId: Optional[int] = None
    receiptType: int = Field(default=1, description="1-签收回单 2-其他凭证")
    fileUrls: List[str] = Field(min_length=1, max_length=9)
    remark: Optional[str] = Field(default=None, max_length=255)


@router.post("/upload", summary="上传回单图片（落表）")
async def upload_receipt(
    payload: ReceiptUploadRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    # 校验任务可见性（防止越权给他人任务传回单）
    await DriverTaskService._get_visible_task_or_404(
        tenant_db, ctx, payload.taskId
    )
    data = await DriverReceiptService.create_receipt(
        tenant_db,
        ctx,
        task_id=payload.taskId,
        file_urls=payload.fileUrls,
        item_id=payload.itemId,
        dispatch_order_id=payload.dispatchOrderId,
        receipt_type=payload.receiptType,
        remark=payload.remark,
    )
    return success(data=data, message="上传成功")


@router.get("/my", summary="我的回单列表")
async def list_my_receipts(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=15, ge=1, le=100, alias="pageSize"),
    taskId: Optional[int] = Query(default=None),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    items, total = await DriverReceiptService.list_my_receipts(
        tenant_db, ctx, task_id=taskId, page=page, page_size=pageSize
    )
    return success(
        data={"list": items, "total": total, "page": page, "pageSize": pageSize}
    )


@router.delete("/{receipt_id}", summary="删除回单")
async def delete_receipt(
    receipt_id: int,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    await DriverReceiptService.delete_receipt(tenant_db, ctx, receipt_id)
    return success(message="已删除")
