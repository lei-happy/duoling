"""
组织架构/部门表（租户库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizDepartment(TenantModelBase):
    """部门/组织架构"""
    __tablename__ = "biz_department"
    __table_args__ = {"comment": "组织架构/部门表"}

    parent_id: Mapped[int] = mapped_column(
        BigInteger, default=0, comment="上级部门ID（0为顶级）"
    )
    dept_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="部门名称"
    )
    dept_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="部门编码"
    )
    dept_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="部门类型（字典 org_type）"
    )
    leader: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="部门负责人"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联系电话"
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
