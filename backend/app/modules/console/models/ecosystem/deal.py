"""服务平台成交单与履约节点（平台库）

成交单是本模块唯一有商业价值的数据资产：它记录了两家物流公司通过平台达成的
真实合作。信誉体系、生态看板、二期的运单直通都建立在这张表上。

关于线上登记的动机设计：一期不做强技术管控（无法阻止双方拿到联系方式后私下
成交），而是靠信誉积累与纠纷仲裁让线上登记成为双方的理性选择。
详见 04.运营审核与风控设计.md。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoDeal(PlatformModelBase):
    """服务平台成交单"""

    __tablename__ = "sys_eco_deal"
    __table_args__ = (
        Index("idx_eco_deal_owner", "owner_tenant_code", "status", "created_at"),
        Index("idx_eco_deal_partner", "partner_tenant_code", "status", "created_at"),
        Index("idx_eco_deal_post", "post_id"),
        # 确认超时 Worker 扫描
        Index("idx_eco_deal_deadline", "status", "confirm_deadline"),
        # 生态看板的线路成交分布 + 审核预检的「同线路均价」基线
        Index("idx_eco_deal_route", "from_province", "to_province", "status"),
        {"comment": "服务平台成交单"},
    )

    # ===== 身份 =====
    deal_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="成交编号"
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )
    post_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="挂牌类型（冗余）"
    )
    intent_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="被选定的意向ID（sys_eco_intent.id）"
    )

    # ===== 双方 =====
    owner_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="挂牌方租户"
    )
    owner_tenant_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="挂牌方企业名（快照）"
    )
    owner_contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="挂牌方联系人"
    )
    owner_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="挂牌方联系电话"
    )
    partner_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="合作方租户"
    )
    partner_tenant_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="合作方企业名（快照）"
    )
    partner_contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="合作方联系人"
    )
    partner_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="合作方联系电话"
    )
    carrier_side: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="承运角色 1-挂牌方承运(运力大厅) 2-合作方承运(货源大厅)",
    )

    # ===== 状态 =====
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-待确认 1-已成交 2-履约中 3-已完成 4-已终止",
    )

    # ===== 标的（快照，成交后不随挂牌变化）=====
    deal_quantity: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="本次成交量"
    )
    quantity_unit: Mapped[str] = mapped_column(
        String(10), default="台", server_default="台", comment="计量单位"
    )
    from_province: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="起点省（快照）"
    )
    from_city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="起点市（快照）"
    )
    from_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="起点展示串"
    )
    to_province: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="终点省（快照）"
    )
    to_city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="终点市（快照）"
    )
    to_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="终点展示串"
    )
    load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="约定装车时间"
    )

    # ===== 价格 =====
    deal_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="成交价"
    )
    price_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="计价方式 1-包车 2-按台 3-按公里 4-面议"
    )
    price_include_tax: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否含税 0-否 1-是"
    )
    settle_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="结算方式 1-现结 2-月结 3-预付"
    )
    prepay_ratio: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="预付比例（%）"
    )

    # ===== 履约（车牌与司机在首次节点上报时写入）=====
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="承运车牌"
    )
    trailer_plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="承运挂车车牌"
    )
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="承运司机姓名（仅成交双方可见）"
    )
    driver_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True,
        comment="承运司机电话（司机手机号进入平台库的唯一入口，仅成交双方可见）",
    )
    current_milestone: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="当前履约节点 0-未开始 1-已安排车辆 2-已装车 3-运输中 "
                "4-已送达 5-已完成",
    )

    # ===== 流转时间 =====
    confirm_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="承接方确认截止时间（选定 +24h）"
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="确认成交时间"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="开始履约时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="完成时间"
    )
    auto_completed: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否系统自动完成（送达 +7 天）0-否 1-是",
    )
    terminated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="终止时间"
    )
    terminate_by: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="终止发起方租户编码"
    )
    terminate_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="终止原因"
    )

    # ===== 评价 =====
    owner_evaluated: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="挂牌方是否已评价 0-否 1-是",
    )
    partner_evaluated: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="合作方是否已评价 0-否 1-是",
    )

    # ===== 与既有体系的衔接 =====
    carrier_linked: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否已建立承运商关系 0-否 1-是",
    )
    carrier_link_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="关联 sys_carrier_link.id"
    )
    owner_task_backfilled: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="发布方是否已把承运方回填到自己的任务单 0-否 1-是",
    )
    partner_task_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="承接方任务单ID（二期运单直通预留，一期留空）",
    )


class SysEcoDealMilestone(PlatformModelBase):
    """服务平台履约节点上报

    同一节点允许多次上报（比如「运输中」会更新位置多次），因此不建唯一索引。
    时间线展示时按 ``milestone_type`` 分组取最新一条，同时保留历史供展开查看。
    """

    __tablename__ = "sys_eco_deal_milestone"
    __table_args__ = (
        Index("idx_eco_milestone_deal", "deal_id", "occurred_at"),
        {"comment": "服务平台履约节点上报"},
    )

    deal_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="成交单ID（sys_eco_deal.id）"
    )
    milestone_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="节点 1-已安排车辆 2-已装车 3-运输中 4-已送达 5-确认完成",
    )
    reporter_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="上报方租户"
    )
    reporter_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="上报人 user_id"
    )
    reporter_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="上报人姓名"
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="节点发生时间"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="当前位置"
    )
    eta: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="预计到达时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
    attachments: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="附件URL数组（装车照/回单）"
    )
