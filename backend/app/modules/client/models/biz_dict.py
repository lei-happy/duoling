"""
数据字典表（租户库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizDict(TenantModelBase):
    """企业级数据字典"""
    __tablename__ = "biz_dict"
    __table_args__ = {"comment": "数据字典表"}

    dict_code: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="字典编码"
    )
    dict_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="字典名称"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )


class BizDictItem(TenantModelBase):
    """企业级数据字典项"""
    __tablename__ = "biz_dict_item"
    __table_args__ = {"comment": "数据字典项表"}

    dict_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="字典ID"
    )
    dict_code: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="字典编码"
    )
    item_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="字典项名称"
    )
    item_value: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="字典项值"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-正常"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
