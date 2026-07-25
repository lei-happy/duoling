"""服务平台发布关联（租户库）

租户库侧唯一的新表。记录「本租户的哪张源单发布成了平台库的哪条挂牌」，
用途有三个：

  1. 任务单/运力列表的角标——不跨库就能显示「已发布到大厅」
  2. 发布前的重复校验——同一源单不能有两条非终态挂牌
  3. 同步失败的重试队列——``sync_pending`` 标记待补偿的记录

镜像字段（``post_status`` / ``intent_count`` / ``deal_count`` /
``partner_tenant_name``）是刻意的冗余：让租户端列表页零跨库查询即可渲染。
一致性由「实时钩子 + 本表重试队列 + 巡检 Worker」三层机制保证，允许短时不一致。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, SmallInteger, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BizEcoPostRef(TenantModelBase):
    """服务平台发布关联"""

    __tablename__ = "biz_eco_post_ref"
    __table_args__ = (
        UniqueConstraint("post_id", name="uk_eco_ref_post"),
        # 任务单列表角标 + 发布前重复校验
        Index("idx_eco_ref_source", "source_type", "source_id", "post_status"),
        # 同步补偿扫描
        Index("idx_eco_ref_sync", "sync_pending", "sync_retry_count"),
        {"comment": "服务平台发布关联"},
    )
    __table_tier__ = "business"

    source_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="来源 1-任务单 2-运输计划 3-运力档案 4-手工",
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="源单主键ID（手工发布时为空）"
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="平台库挂牌ID（sys_eco_post.id）"
    )
    post_no: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="挂牌编号（镜像，便于展示免跨库）"
    )
    post_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="挂牌类型 1-货源 2-运力"
    )
    post_status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="挂牌状态镜像"
    )
    intent_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="意向数镜像"
    )
    deal_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="成交数镜像"
    )
    partner_tenant_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="成交对方企业名镜像（任务单角标展示用）",
    )

    # ===== 同步状态 =====
    sync_pending: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否有待同步到平台库的变更 0-否 1-是",
    )
    sync_retry_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="同步重试次数"
    )
    sync_error: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="最后一次同步失败原因"
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后同步成功时间"
    )
