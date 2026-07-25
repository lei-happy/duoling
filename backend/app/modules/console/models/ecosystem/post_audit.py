"""服务平台挂牌流转审计（平台库）

挂牌的每一次状态变更都在此留痕，是「从发布到交付全流程可追溯」的落地载体。
包括租户操作、运营审核、系统自动流转三类来源，任何一次状态跃迁都必须写一行，
否则出现纠纷时无法还原过程。
"""

from typing import Optional

from sqlalchemy import BigInteger, Index, JSON, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoPostAudit(PlatformModelBase):
    """服务平台挂牌流转审计"""

    __tablename__ = "sys_eco_post_audit"
    __table_args__ = (
        Index("idx_eco_post_audit_post", "post_id", "created_at"),
        Index("idx_eco_post_audit_op", "operator_type", "created_at"),
        {"comment": "服务平台挂牌流转审计"},
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )
    action: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="动作 1-提交 2-通过 3-驳回 4-重新提交 5-主动下架 6-到期下架 "
                "7-强制下架 8-源单失效下架 9-成交下架 10-重新上架 "
                "11-免审直通 12-抽检通过 13-抽检不通过 14-编辑 15-延长展示",
    )
    from_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="变更前状态"
    )
    to_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="变更后状态"
    )
    operator_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="操作人类型 1-租户用户 2-平台运营 3-系统",
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人ID（系统操作时为空）"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名"
    )
    operator_tenant_code: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="操作人所属租户（运营操作时为空）"
    )
    reason_code: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="原因编码（驳回/强制下架原因，见 constants.PostRejectReason）",
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="原因说明"
    )
    changed_fields: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="编辑动作时记录变更字段名与新旧值"
    )
