"""服务平台企业名片（平台库）

租户在大厅的对外形象，1:1 于 ``sys_tenant``。之所以不直接扩展 ``sys_tenant``：
名片是服务平台的领域数据（认证状态、主营线路、默认可见性偏好），与租户的
基础身份信息生命周期不同，混在一张表里会让 ``sys_tenant`` 持续膨胀。

采用**懒加载**创建：租户首次访问大厅时按 ``sys_tenant`` 自动建一条，不预生成。
理由是平台上多数租户短期内不会碰服务平台，预生成几千条空记录没有意义，
还会让「有多少租户真的在用」这个运营指标失真。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, JSON, SmallInteger, String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoTenantProfile(PlatformModelBase):
    """服务平台企业名片"""

    __tablename__ = "sys_eco_tenant_profile"
    __table_args__ = (
        UniqueConstraint("tenant_code", name="uk_eco_profile_tenant"),
        Index("idx_eco_profile_verified", "license_verified", "hall_enabled"),
        {"comment": "服务平台企业名片"},
    )

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="租户编码（1:1 于 sys_tenant）"
    )

    # ===== 对外形象 =====
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="对外展示企业名，默认取 tenant_name"
    )
    masked_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="脱敏企业名（固化存储；出现在每张大厅卡片上，实时计算太贵）",
    )
    intro: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="企业简介"
    )
    main_routes: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True,
        comment="主营线路 [{fromProvince,fromCity,toProvince,toCity}]",
    )
    fleet_size: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="车队规模（台）"
    )
    fleet_desc: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="车队描述"
    )
    good_at_categories: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="擅长货物类别数组"
    )
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="默认联系人"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="默认联系电话"
    )
    contact_wechat: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="默认微信"
    )

    # ===== 认证 =====
    license_verified: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="营业执照是否已核验 0-否 1-是（决定可见层级 L1/L2）",
    )
    license_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="执照核验时间"
    )
    license_verified_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="执照核验人（平台 user_id）"
    )
    transport_license_no: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="道路运输经营许可证号"
    )
    transport_license_file: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="许可证附件URL"
    )
    transport_license_verified: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="许可证是否已核验 0-否 1-是",
    )
    transport_license_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="许可证核验时间"
    )
    realname_verified: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否实名（注册手机号已验证）0-否 1-是",
    )

    # ===== 新建挂牌的默认偏好 =====
    default_visibility_level: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2", comment="默认企业名可见层级"
    )
    default_contact_visibility: Mapped[int] = mapped_column(
        SmallInteger, default=3, server_default="3", comment="默认联系方式可见层级"
    )
    default_valid_days: Mapped[int] = mapped_column(
        SmallInteger, default=7, server_default="7", comment="默认展示天数"
    )

    # ===== 运营管控 =====
    hall_enabled: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="大厅能力是否开启 0-关闭 1-开启（运营可关停违规租户）",
    )
    disabled_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="关闭原因"
    )
    disabled_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="关闭截止时间"
    )
