"""
操作日志表（租户库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizOperationLog(TenantModelBase):
    """租户级操作日志"""
    __tablename__ = "biz_operation_log"
    __table_args__ = {"comment": "操作日志表"}

    user_id: Mapped[Optional[int]] = mapped_column(
        nullable=True, comment="操作用户ID"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作用户名"
    )
    module: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作模块"
    )
    action: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作类型"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="操作描述"
    )
    request_method: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, comment="请求方法"
    )
    request_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="请求URL"
    )
    request_body: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="请求参数"
    )
    response_body: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="响应结果"
    )
    ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="IP地址"
    )
    elapsed_time: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="耗时（毫秒）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-失败 1-成功"
    )
