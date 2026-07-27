"""
设计对接模块（平台库）

产品经理 / UI / 开发在文档中心「设计对接」中协作的轻量工单。
"""

from typing import Optional

from sqlalchemy import BigInteger, Index, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysDesignModule(PlatformModelBase):
    """设计对接模块表"""

    __tablename__ = "sys_design_module"
    __table_args__ = (
        Index("idx_sys_design_module_status", "status"),
        Index("idx_sys_design_module_priority", "priority"),
        Index("idx_sys_design_module_product_line", "product_line"),
        {"comment": "设计对接模块（原型/Figma/优先级/进度）"},
    )

    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="模块/页面名称"
    )
    product_line: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="other",
        server_default="other",
        comment="端：console/client/mobile/lite/other",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="需求说明"
    )
    priority: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="优先级 0低/1中/2高/3紧急",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="状态 0待原型/1原型已出/2设计中/3设计完成/4开发中/5已完成/6已搁置",
    )
    prototype_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="原型 HTML 相对路径（相对仓库 prototype/ 目录）",
    )
    figma_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Figma 分享链接"
    )
    pm_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="产品负责人 sys_user.id"
    )
    pm_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="产品负责人姓名快照"
    )
    designer_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="设计师 sys_user.id"
    )
    designer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="设计师姓名快照"
    )
    developer_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="开发负责人 sys_user.id"
    )
    developer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开发负责人姓名快照"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="同列内排序（越小越靠前）",
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 sys_user.id"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="最后更新人 sys_user.id"
    )
