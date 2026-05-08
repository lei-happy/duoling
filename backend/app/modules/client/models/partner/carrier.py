"""
承运商主体档案表（租户库）
合作伙伴 - 承运商（下游运输合作伙伴）
"""

from datetime import datetime, date
from typing import Optional, Any
from sqlalchemy import String, SmallInteger, Text, BigInteger, Date, DateTime, Numeric, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Carrier(TenantModelBase):
    """承运商档案"""
    __tablename__ = "biz_carrier"
    __table_args__ = (
        Index("idx_carrier_name", "carrier_name"),
        Index("idx_contact_phone", "contact_phone"),
        Index("idx_linked_tenant_code", "linked_tenant_code"),
        Index("idx_status_invite", "status", "invite_status"),
        {"comment": "承运商档案表"},
    )
    __table_tier__ = "business"

    carrier_code: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, comment="承运商编码（租户内唯一）"
    )
    carrier_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="承运商全称"
    )
    short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="简称"
    )
    carrier_type: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="承运商类型 0-公司车队 1-个体司机/小车队 2-其他",
    )
    credit_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="统一社会信用代码（公司必填，个体可空）"
    )
    id_card_no: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="身份证号（个体场景）"
    )
    legal_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="法人代表/负责人"
    )
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="主要联系人"
    )
    contact_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="联系电话（互联激活关键字段）"
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="联系邮箱"
    )
    province: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="省"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="市"
    )
    district: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="区/县"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="详细地址"
    )
    cooperation_start_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="合作起始日"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="状态 0-停用 1-正常 2-黑名单",
    )

    # ===== 互联字段 =====
    linked_tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True,
        comment="互联：B 在本系统的 tenant_code，NULL 表示纯档案",
    )
    invite_status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="0-未邀请 1-邀请中 2-已激活 3-邀请失败 4-A 端预审待确认 "
                "5-A 已撤回 6-B 已拒绝 7-代转交中 8-A 端预审拒绝 9-B 端解绑",
    )
    invite_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="触发邀请的操作员 user_id"
    )
    invited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近邀请时间"
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="B 首次登录或确认接受时间"
    )

    # ===== 考核评价（远期预留）=====
    rating_score: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1), nullable=True, comment="考核综合评分 0.0~5.0"
    )
    rating_level: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="考核等级 1-A 2-B 3-C 4-D"
    )
    last_evaluated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近一次考核时间"
    )
    capacity_summary: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="运力概要快照"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
