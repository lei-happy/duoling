"""
经营主体表（租户库，core tier）

经营主体（法人/独立核算单元）是运力资源与财务账务的归属维度：车辆、司机、
运力、任务、费用单、资金账户均可归属到某个经营主体，用于多主体独立经营与
分主体对账。与组织架构 ``biz_department`` 是不同概念（后者是人员/权限层级）。
"""

from typing import Optional

from sqlalchemy import String, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BusinessEntity(TenantModelBase):
    """经营主体（法人经营主体）"""

    __tablename__ = "biz_business_entity"
    __table_args__ = {"comment": "经营主体表（法人/独立核算单元）"}
    # core tier：注册租户即建表并内置默认主体

    entity_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="主体编码（业务唯一标识）"
    )
    entity_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="主体名称（法人全称）"
    )
    short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="简称（列表/选择器展示）"
    )
    unified_credit_code: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="统一社会信用代码"
    )
    legal_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="法定代表人"
    )
    registered_address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="注册地址"
    )
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="联系电话"
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="对公开户行"
    )
    bank_account: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="对公账号"
    )
    invoice_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开票抬头（默认取 entity_name）"
    )
    invoice_tax_no: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="开票税号（默认取 unified_credit_code）"
    )
    is_default: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", nullable=False,
        comment="是否默认主体 1-是 0-否（租户内至多 1 条为 1）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", nullable=False,
        comment="状态 1-正常 0-停用（停用后不可被新业务选择）",
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", nullable=False,
        comment="排序号",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
