"""
运力分组表（租户库）

biz_capacity_group: 用户自定义的运力分组（供成本政策 / 计费规则按分组指定政策）
biz_capacity_group_member: 分组成员关联表（M:N），以司机为成员锚点、运力为操作入口

设计要点：
  - 一个运力(司机)可属于多个分组；一个分组可含多个运力。
  - 成员锚定 driver_id（稳定实体），司机换车不丢分组，保证成本命中稳定。
  - capacity_id / plate_number 仅为加入时的展示快照，不参与计费命中。
"""

from typing import Optional

from sqlalchemy import String, SmallInteger, Integer, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CapacityGroup(TenantModelBase):
    """运力分组"""
    __tablename__ = "biz_capacity_group"
    __table_args__ = (
        Index("idx_group_enterprise", "enterprise_id"),
        Index("idx_group_status", "status", "is_deleted"),
        {"comment": "运力分组表"},
    )
    __table_tier__ = "business"

    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="所属经营主体ID（空=企业级公共分组）",
    )
    group_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="分组名称（同企业未删除内唯一）"
    )
    group_code: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True,
        comment="分组编码（唯一，留空自动生成）",
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="标签颜色（如 #409EFF）"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
        comment="排序号，越小越靠前",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1",
        comment="状态 0-停用 1-启用",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="更新人"
    )


class CapacityGroupMember(TenantModelBase):
    """运力分组成员关联（M:N，成员锚定司机）"""
    __tablename__ = "biz_capacity_group_member"
    __table_args__ = (
        Index("uk_group_driver", "group_id", "driver_id", "is_deleted", unique=True),
        Index("idx_member_group", "group_id"),
        Index("idx_member_driver", "driver_id"),
        {"comment": "运力分组成员关联表"},
    )
    __table_tier__ = "business"

    group_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联分组ID"
    )
    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="成员锚点：司机ID"
    )
    driver_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="司机姓名（冗余）"
    )
    capacity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="加入时运力ID（展示快照，不参与命中）"
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="加入时车牌（冗余快照）"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="添加人"
    )
