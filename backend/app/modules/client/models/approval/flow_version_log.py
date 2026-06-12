"""审批流程模板版本快照"""

from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class ApprovalFlowVersionLog(TenantModelBase):
    """审批流程发布/状态变更版本日志"""

    __tablename__ = "biz_approval_flow_version_log"
    __table_args__ = (
        Index("idx_afl_flow", "flow_id"),
        Index("idx_afl_flow_version", "flow_id", "version"),
        {"comment": "审批流程模板版本日志表"},
    )
    __table_tier__ = "business"

    flow_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="流程模板ID"
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="发布版本号"
    )
    change_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="变更类型 publish/disable/enable",
    )
    snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="该版本流程配置快照"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人用户ID"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
