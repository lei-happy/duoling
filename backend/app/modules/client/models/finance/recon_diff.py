"""
对账差异记录表（租户库）

``biz_recon_diff`` 记录「财务单上写的数」与「业务侧当前事实」的每一处不一致，
供对账工作台跟踪未决差异。客户侧与承运商侧共用一张表。

设计要点（文档 09 §5.1）：
- **不是单据**：不继承 ``FinanceDocBaseMixin``——差异没有金额审批与支付流程，
  只是一条待办事项，因此不占 ``doc_kind`` / ``doc_no``。
- **弱关联业务单**：``biz_doc_type + biz_doc_id`` 一张表覆盖运单与任务两侧。
  与文档 01 §4.4「不用多态外键」不冲突：那条禁令针对财务单据与业务单据的
  **主关联**（需强外键做报表 join），差异表是审计辅助表，不参与金额计算。
- **同一差异不重复生成**：靠 ``dedup_key`` 唯一索引实现「``status=0`` 部分唯一」。
  MySQL 不支持 partial index，故待处置时写 key、处置后置 NULL；NULL 在唯一
  索引中不参与冲突判定，天然满足需求。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Numeric, SmallInteger, String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class ReconDiff(TenantModelBase):
    """对账差异记录（对账单与业务事实的不一致项）"""

    __tablename__ = "biz_recon_diff"
    __table_args__ = (
        Index("idx_rdiff_recon", "recon_kind", "recon_id"),
        Index("idx_rdiff_status_severity", "status", "severity"),
        Index("idx_rdiff_biz_doc", "biz_doc_type", "biz_doc_id"),
        Index("uk_rdiff_dedup", "dedup_key", unique=True),
        {"comment": "对账差异记录表"},
    )
    __table_tier__ = "business"

    # ===== 归属 =====
    recon_kind: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="对账单大类 customer_recon-客户对账 carrier_recon-承运商对账",
    )
    recon_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="对账单 ID（漏挂类为空，此时尚无对账单）",
    )
    link_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="对账行 ID（桥接表主键；漏挂/重挂类为空）",
    )

    # ===== 关联业务单据（弱关联） =====
    biz_doc_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="业务单据类型 1-运单 2-任务单"
    )
    biz_doc_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="业务单据 ID"
    )
    biz_doc_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        comment="业务单号（冗余，便于列表展示与业务单软删后追溯）",
    )

    # ===== 差异内容 =====
    diff_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="差异类型 1-漏挂 2-重挂 3-资格不符 4-台数不符 "
                "5-里程不符 6-金额不符 7-扣减不符 8-状态回退",
    )
    severity: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="严重度 1-提示（不阻塞确认） 2-阻塞（拒绝确认，除非强制确认）",
    )
    expected_value: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="财务侧快照值（对账行上写的）"
    )
    actual_value: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="业务侧当前值"
    )
    diff_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2), nullable=True,
        comment="金额类差异的差额（当前 - 快照，可负）",
    )

    # ===== 检出 =====
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="检出时间"
    )
    detected_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="检出人 user_id（定时任务为空）"
    )
    is_manual: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否人工登记 0-核对器检出 1-对账岗手工登记；"
                "人工登记的差异不会被下一轮核对自动置失效",
    )

    # ===== 处置 =====
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="处置状态 0-待处置 1-已回灌 2-已协商确认 3-已强制放行 4-已失效",
    )
    resolution: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="处置说明"
    )
    resolved_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="处置人 user_id"
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处置时间"
    )

    # ===== 去重键 =====
    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(120), nullable=True,
        comment="去重键 recon_kind:recon_id:biz_doc_id:diff_type，"
                "仅待处置(status=0)时有值，处置后置 NULL 释放占用",
    )

    @staticmethod
    def build_dedup_key(
        recon_kind: str,
        recon_id: Optional[int],
        biz_doc_id: int,
        diff_type: int,
    ) -> str:
        """构造去重键（``recon_id`` 为空时用 0 占位，覆盖漏挂类差异）。"""
        return f"{recon_kind}:{recon_id or 0}:{biz_doc_id}:{diff_type}"
