"""
企业内部用户表（租户库）
"""

from datetime import date
from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Text, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizUser(TenantModelBase):
    """企业用户"""
    __tablename__ = "biz_user"
    __table_args__ = {"comment": "企业用户表"}

    phone: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="手机号（登录标识，租户内唯一）"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码（bcrypt哈希）"
    )
    real_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="真实姓名"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="昵称"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="邮箱"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="头像URL"
    )
    gender: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="性别 0-未知 1-男 2-女"
    )
    birthday: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="出生日期"
    )
    user_type: Mapped[int] = mapped_column(
        SmallInteger, default=2, comment="用户类型 1-管理员 2-普通员工 3-驾驶员"
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="所属部门ID"
    )
    supervisor_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="直属上级 biz_user.id（汇报线，审批中心动态审批人「逐级上级」依赖）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="状态 0-正常 1-停用"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
