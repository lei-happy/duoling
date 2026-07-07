"""
驾驶员回单服务（落表版）

将司机上传的回单图片持久化到 ``biz_task_receipt``，并提供按当前 driver 过滤的
列表 / 删除能力。文件本身通过 ``/api/driver/file/upload``（scene=task_receipt）
先上传取 URL，再调用本服务落表。
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task_receipt import TaskReceipt
from app.modules.driver.services.driver_context import DriverContext


class DriverReceiptService:
    """驾驶员回单落表服务（按 driver_id 过滤）"""

    @staticmethod
    def _to_dict(r: TaskReceipt) -> dict:
        try:
            urls = json.loads(r.file_urls) if r.file_urls else []
        except (ValueError, TypeError):
            urls = []
        return {
            "id": int(r.id),
            "taskId": int(r.task_id),
            "dispatchOrderId": r.dispatch_order_id,
            "itemId": r.item_id,
            "driverId": r.driver_id,
            "receiptType": int(r.receipt_type or 1),
            "fileUrls": urls,
            "remark": r.remark,
            "uploaderName": r.uploader_name,
            "createdAt": (
                r.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if r.created_at
                else None
            ),
        }

    @staticmethod
    async def create_receipt(
        db: AsyncSession,
        ctx: DriverContext,
        *,
        task_id: int,
        file_urls: List[str],
        item_id: Optional[int] = None,
        dispatch_order_id: Optional[int] = None,
        receipt_type: int = 1,
        remark: Optional[str] = None,
    ) -> dict:
        if not file_urls:
            raise BizException("请至少上传 1 张回单图片")
        if len(file_urls) > 9:
            raise BizException("回单图片最多 9 张")

        receipt = TaskReceipt(
            task_id=task_id,
            dispatch_order_id=dispatch_order_id,
            item_id=item_id,
            driver_id=ctx.driver_id,
            receipt_type=receipt_type,
            file_urls=json.dumps(file_urls, ensure_ascii=False),
            remark=remark,
            uploaded_by=ctx.user_id,
            uploader_name=ctx.driver.name,
        )
        db.add(receipt)
        await db.flush()
        await db.refresh(receipt)
        return DriverReceiptService._to_dict(receipt)

    @staticmethod
    async def list_my_receipts(
        db: AsyncSession,
        ctx: DriverContext,
        *,
        task_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 15,
    ) -> Tuple[List[dict], int]:
        conds = [
            TaskReceipt.driver_id == ctx.driver_id,
            TaskReceipt.is_deleted == 0,
        ]
        if task_id is not None:
            conds.append(TaskReceipt.task_id == task_id)

        total = int(
            (await db.execute(select(func.count(TaskReceipt.id)).where(*conds)))
            .scalar_one()
        )

        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        rows = (
            await db.execute(
                select(TaskReceipt)
                .where(*conds)
                .order_by(TaskReceipt.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return [DriverReceiptService._to_dict(r) for r in rows], total

    @staticmethod
    async def delete_receipt(
        db: AsyncSession, ctx: DriverContext, receipt_id: int
    ) -> None:
        row = (
            await db.execute(
                select(TaskReceipt).where(
                    TaskReceipt.id == receipt_id,
                    TaskReceipt.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("回单不存在")
        if int(row.driver_id or 0) != ctx.driver_id:
            raise BizException("无权删除该回单")
        row.is_deleted = 1
        row.updated_at = datetime.now()
        await db.flush()
