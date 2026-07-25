"""敏感词库

平台级内容审核资产，由运营后台维护。首个消费方是服务平台的挂牌发布预检
（见 doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.3），
但内容审核天然跨域——企业名片、意见反馈等后续都可能复用，因此这里不加
``sys_eco_`` 前缀，而是作为平台通用能力，用 ``scope`` 区分适用范围。

**为什么词库要进库而不是写在代码里**：词库需要频繁增删、且属于运营资产，
硬编码在源码里意味着每调整一个词都要发版。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SensitiveWordCategory:
    """敏感词分类（``sys_sensitive_word.category``）

    分类只用于运营侧归类与筛选，不影响命中后的处置——处置看 ``action``。
    """

    POLITICS = 1      # 政治
    PORN = 2          # 色情低俗
    CONTRABAND = 3    # 违禁品
    DIVERSION = 4     # 竞品导流
    FRAUD = 5         # 诈骗
    OTHER = 9         # 其他

    ALL = (POLITICS, PORN, CONTRABAND, DIVERSION, FRAUD, OTHER)


class SensitiveWordAction:
    """命中处置（``sys_sensitive_word.action``）

    不是所有敏感词都该硬拦截：运营对某个词没把握时，设为「转人工」既能
    兜住风险，又不会误伤正常发布——硬拦截误伤一条真实货源的代价，
    远大于多审一条。
    """

    BLOCK = 1     # 硬拦截：提交当场失败
    REVIEW = 2    # 转人工：不阻断提交，标红进审核队列

    ALL = (BLOCK, REVIEW)


class SensitiveWordScope:
    """适用范围（``sys_sensitive_word.scope``）"""

    ALL = "all"                # 全平台通用
    ECOSYSTEM = "ecosystem"    # 仅服务平台（货源/运力大厅）

    VALUES = (ALL, ECOSYSTEM)


@dataclass(frozen=True)
class SensitiveWordRule:
    """一条运行时敏感词规则（由 ``sys_sensitive_word`` 加载而来）

    放在模型模块而不是判定模块（``client.services.ecosystem.content_guard``），
    是为了断开一条真实存在过的循环导入：加载 Service 在运营侧、判定逻辑在租户侧，
    两边都要引用这个类型，谁定义它、另一边就得反向依赖。规则的形状本来就属于
    数据侧，判定侧只是消费者。
    """

    word: str
    category: int = SensitiveWordCategory.OTHER
    action: int = SensitiveWordAction.BLOCK


class SensitiveWord(PlatformModelBase):
    """敏感词"""

    __tablename__ = "sys_sensitive_word"
    __table_args__ = (
        # 词库加载查询：按范围取全部启用词，一次性灌进缓存
        Index("idx_sw_load", "status", "scope", "is_deleted"),
        # 运营新增时的重复校验与关键字搜索
        Index("idx_sw_word", "word"),
        {"comment": "敏感词库"},
    )

    # 刻意不加 (word, scope) 唯一约束：本表是软删除，加唯一约束后
    # 「停用/删除某词 → 过一阵又想加回来」这个高频运营动作会直接报「已存在」。
    # 重复校验放在 Service（命中软删记录则复活），重复词对匹配结果无害。
    word: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="敏感词"
    )
    category: Mapped[int] = mapped_column(
        SmallInteger,
        default=SensitiveWordCategory.OTHER,
        server_default="9",
        nullable=False,
        comment="分类 1-政治 2-色情低俗 3-违禁品 4-竞品导流 5-诈骗 9-其他",
    )
    action: Mapped[int] = mapped_column(
        SmallInteger,
        default=SensitiveWordAction.BLOCK,
        server_default="1",
        nullable=False,
        comment="命中处置 1-硬拦截 2-转人工审核",
    )
    scope: Mapped[str] = mapped_column(
        String(32),
        default=SensitiveWordScope.ALL,
        server_default="all",
        nullable=False,
        comment="适用范围 all-全平台 ecosystem-服务平台",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        server_default="1",
        nullable=False,
        comment="状态 0-停用 1-启用",
    )
    # 命中统计用于让运营看出哪些词是"死词"、哪些词在频繁误伤，
    # 否则词库只会越加越长、没人敢删。
    hit_count: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False, comment="累计命中次数"
    )
    last_hit_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近命中时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
