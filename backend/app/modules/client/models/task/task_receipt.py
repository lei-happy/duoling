"""
任务回单/签收凭证表（租户库）

司机在到货/签收环节上传的回单图片（纸质回单拍照、电子签收单等）。与装卸车
凭证（``biz_task_loading_record.photo_urls``）区分：装卸凭证记录"装/卸动作发生"，
回单则是"客户签收确认"的凭证，独立成表便于按任务/运单维度归档与追溯。

一条回单可包含 1~9 张图片（``file_urls`` 存 JSON 数组）。可按任务整票上传，
也可挂到具体挂接行（``item_id``）。
"""

from typing import Optional

from sqlalchemy import BigInteger, Index, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskReceipt(TenantModelBase):
    """任务回单/签收凭证"""

    __tablename__ = "biz_task_receipt"
    __table_args__ = (
        Index("idx_task_receipt_task_id", "task_id"),
        Index("idx_task_receipt_driver_id", "driver_id"),
        {"comment": "任务回单/签收凭证表"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    dispatch_order_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联调令 biz_task_dispatch_order.id（可空）"
    )
    item_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联挂接行 biz_task_waybill_item.id（整票为空）"
    )
    driver_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="上传司机 biz_driver.id"
    )
    receipt_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="回单类型 1-签收回单 2-其他凭证",
    )
    file_urls: Mapped[str] = mapped_column(
        Text, nullable=False, comment="图片 URL 列表（JSON 数组字符串）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="上传人 user_id"
    )
    uploader_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="上传人姓名（冗余）"
    )
