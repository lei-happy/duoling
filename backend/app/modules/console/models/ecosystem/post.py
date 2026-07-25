"""服务平台挂牌主表（平台库）

撮合内核的根对象，货源大厅与运力大厅共用，由 ``post_type`` 区分。

之所以放平台库：租户库物理隔离，跨租户的大厅列表无法在租户库分页排序。
本表是租户数据的**快照**，与源单通过 ``source_type + source_id`` 关联，
一致性由「实时钩子 + 重试队列 + 巡检 Worker」三层机制保证。
详见 doc/02.需求文档/02.企业端/13.服务平台/01.架构与撮合内核设计.md §2.2。

线路、时间窗、数量、价格四组字段放在主表而非扩展表：这些维度在两个大厅
是同构的（货源起点↔运力所在地、货源终点↔运力期望流向、装车窗↔可用窗），
且是大厅列表的筛选与排序依据，放主表才能命中单表联合索引。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoPost(PlatformModelBase):
    """服务平台挂牌主表"""

    __tablename__ = "sys_eco_post"
    __table_args__ = (
        # 大厅按出发地筛选（最高频）
        Index("idx_eco_post_hall_from", "post_type", "status",
              "from_province", "from_city", "window_start"),
        # 大厅默认排序「最新发布」
        Index("idx_eco_post_hall_new", "post_type", "status", "listed_at"),
        # 「我发布的」列表
        Index("idx_eco_post_owner", "owner_tenant_code", "status", "created_at"),
        # 运营待审队列（按进队时间正序）
        Index("idx_eco_post_audit", "audit_status", "submitted_at"),
        # 发布前的重复校验、源单联动反查
        Index("idx_eco_post_source", "owner_tenant_code", "source_type", "source_id"),
        # 过期下架 Worker 扫描
        Index("idx_eco_post_expire", "status", "valid_until"),
        # 信息变更催更 Worker 扫描
        Index("idx_eco_post_changed", "source_changed", "source_changed_at"),
        {"comment": "服务平台挂牌主表"},
    )

    # ===== 身份 =====
    post_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="挂牌编号（对外展示）"
    )
    post_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="挂牌类型 1-货源 2-运力 3-服务(预留)",
    )
    owner_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="归属租户编码"
    )
    owner_tenant_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="归属企业全称（快照）"
    )
    owner_masked_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="归属企业脱敏名（快照）"
    )
    publisher_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="发布人 user_id"
    )
    publisher_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="发布人姓名（快照）"
    )

    # ===== 展示与状态 =====
    title: Mapped[str] = mapped_column(
        String(120), nullable=False, comment="标题"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 1-待审核 2-审核未通过 3-展示中 4-已锁定 "
                "5-履约中 6-已完成 7-已下架 9-已取消",
    )
    delist_reason: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="下架原因 1-主动 2-到期 3-平台强制 4-源单失效 5-成交自动",
    )
    delist_remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="下架说明"
    )
    is_top: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否运营置顶 0-否 1-是",
    )
    top_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="置顶截止时间"
    )

    # ===== 来源与源单联动 =====
    source_type: Mapped[int] = mapped_column(
        SmallInteger, default=3, server_default="3",
        comment="来源 1-系统单据 2-批量来源 3-手工",
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="源单在租户库的主键ID"
    )
    source_snapshot_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="源单快照时间"
    )
    source_changed: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="源单是否已变更待更新 0-否 1-是",
    )
    source_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="源单变更标记时间"
    )

    # ===== 有效期 =====
    valid_from: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="生效时间"
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="失效时间"
    )

    # ===== 线路（货源=起讫地；运力=当前所在地与主要期望流向）=====
    from_province: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="出发地省"
    )
    from_city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="出发地市"
    )
    from_district: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="出发地区县"
    )
    from_region_code: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="出发地行政区划代码（sys_regions.code）"
    )
    from_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="出发地展示串"
    )
    to_province: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="主目的地省（任意流向时为空）"
    )
    to_city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="主目的地市"
    )
    to_district: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="主目的地区县"
    )
    to_region_code: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="主目的地行政区划代码（sys_regions.code）"
    )
    to_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="主目的地展示串"
    )
    any_direction: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否接受任意流向 0-否 1-是（仅运力）",
    )

    # ===== 时间窗（货源=期望装车起止；运力=可用起止）=====
    window_start: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="时间窗开始（装车起/可用起）"
    )
    window_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="时间窗结束（装车止/可用止），长期可用为空"
    )

    # ===== 数量 =====
    total_quantity: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="数量（货源总台数/运力可载台数）"
    )
    quantity_unit: Mapped[str] = mapped_column(
        String(10), default="台", server_default="台", comment="计量单位"
    )
    remaining_quantity: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="剩余可承接量，分批时递减；为空表示不分批",
    )

    # ===== 价格 =====
    price_type: Mapped[int] = mapped_column(
        SmallInteger, default=4, server_default="4",
        comment="计价方式 1-包车 2-按台 3-按公里 4-面议",
    )
    price_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="价格，面议时为空"
    )
    price_include_tax: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="是否含税 0-否 1-是"
    )
    price_negotiable: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="价格是否可议 0-否 1-是"
    )

    # ===== 合作方式 =====
    cooperation_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="合作类型 1-单次 2-长期"
    )
    keep_listed_after_deal: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="成交后是否继续展示 0-否 1-是（长期运力挂牌）",
    )

    # ===== 联系方式（按 contact_visibility 分层暴露，不直接返回）=====
    contact_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="联系人姓名"
    )
    contact_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="联系人手机"
    )
    contact_backup: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="备用联系方式"
    )

    # ===== 可见性配置 =====
    visibility_level: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="企业全称可见起始层级 1-匿名层 2-认证层",
    )
    contact_visibility: Mapped[int] = mapped_column(
        SmallInteger, default=3, server_default="3",
        comment="联系方式可见起始层级 2-认证层 3-洽谈层",
    )
    apply_block_rule: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="是否应用租户级屏蔽名单 0-否 1-是",
    )
    extra_block_tenants: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="本条挂牌额外屏蔽的租户编码数组"
    )

    # ===== 统计冗余 =====
    view_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="详情浏览次数（冗余）"
    )
    viewer_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="浏览企业数（去重冗余）"
    )
    intent_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="有效意向数（冗余）"
    )
    deal_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="成交数（冗余，分批时可大于1）"
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后活跃时间（用于热度排序）"
    )

    # ===== 审核 =====
    audit_status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="审核状态 0-未提交 1-待审 2-通过 3-驳回 4-免审直通待抽检 5-抽检通过",
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="进入审核队列的时间（队列排序与 SLA 基准，不能用 created_at 替代）",
    )
    audit_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="审核时间"
    )
    audit_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="审核人（平台 user_id）"
    )
    audit_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="驳回原因（原样展示给租户）"
    )
    precheck_flags: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="自动预检命中的可疑标记数组"
    )
    listed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="首次上架时间"
    )
