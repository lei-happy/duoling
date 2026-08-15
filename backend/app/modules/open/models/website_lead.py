"""
官网留资线索（平台库）

来自官网匿名访客，没有租户上下文，因此和 open_register_task 一样放平台库，
由运营端统一查看与跟进。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import PlatformBase


class WebsiteLead(PlatformBase):
    """官网留资线索"""

    __tablename__ = "open_website_lead"
    __table_args__ = {"comment": "官网留资线索"}

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键"
    )

    # ---------------------------------------------------------------- 联系信息
    company_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="企业名称"
    )
    contact_person: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="联系人称呼"
    )
    contact_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, comment="联系手机号"
    )

    # ---------------------------------------------------------------- 业务画像
    fleet_size: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="自有板车规模 lt10/10-30/30-100/gt100"
    )
    pain_point: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="当前最头疼的一件事"
    )
    profile_answers: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="自测画像题 P1-P3 作答 JSON"
    )

    # ---------------------------------------------------------------- 自测结果
    stage_band: Mapped[Optional[str]] = mapped_column(
        String(8), nullable=True, index=True, comment="测评档位 L1-L8"
    )
    stage_name: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="档位名称，如 数字化推进期"
    )
    total_score: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="自测总分 0-80"
    )
    dim_a: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="业务在线 0-20"
    )
    dim_b: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="数据贯通 0-20"
    )
    dim_c: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="智能应用 0-20"
    )
    dim_d: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="经营闭环 0-20"
    )

    # ---------------------------------------------------------------- 来源
    source_page: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="提交所在页面路径"
    )
    referrer: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="来源页 referrer"
    )
    client_ip: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True, comment="提交方 IP，用于频控"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="浏览器 UA"
    )

    # ---------------------------------------------------------------- 跟进
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default="0",
        index=True,
        comment="跟进状态 0-待联系 1-已联系 2-已转化 3-无效",
    )
    follow_remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="跟进备注"
    )
    handler_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="跟进人平台用户ID"
    )
    handler_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="跟进人姓名快照"
    )
    contacted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="首次联系时间"
    )
    converted_tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="转化后的租户编码"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否删除 0-否 1-是"
    )
