"""
运单回单凭证表（租户库）

业务语义：运单全量签收（waybill.status=5 已签收）后，把签收底单返还货主即"回单"。
每次确认回单产出一条 ``biz_waybill_receipt``（含底单图片、回收时间、操作人）。

设计要点：
- 回单是 **运单维度** 的人工动作，与任务/任务挂接行状态机彼此独立；
- 一张运单可多次上传/补传底单凭证（多条记录），撤销回单时软删；
- ``file_urls`` 用 JSON 列存储 OSS URL 数组（前端最多 9 张）。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON, BigInteger, DateTime, Index, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class WaybillReceipt(TenantModelBase):
    """运单回单凭证（签收底单返还记录）"""

    __tablename__ = "biz_waybill_receipt"
    __table_args__ = (
        Index("idx_waybill_receipt_waybill_id", "waybill_id"),
        Index("idx_waybill_receipt_received_at", "received_at"),
        {"comment": "运单回单凭证表（签收底单返还货主）"},
    )
    __table_tier__ = "business"

    waybill_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_waybill.id"
    )
    file_urls: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True,
        comment="回单底单文件 URL 数组（OSS 路径，最多 9 张）",
    )
    file_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="文件类型 1-图片 2-PDF",
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="回单回收时间"
    )
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
