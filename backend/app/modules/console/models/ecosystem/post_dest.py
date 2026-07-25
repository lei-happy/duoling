"""服务平台挂牌目的地/期望流向（平台库）

单独成表而非在主表存 JSON 数组，原因是目的地是核心筛选维度而运力的期望流向
是多值的（「我想往华东或华中走」）：

  - 主表存 JSON + ``JSON_CONTAINS``：无法有效使用索引；多值索引对 MySQL
    版本有硬要求（8.0.17+），风险不必要
  - 主表存逗号分隔 + ``LIKE``：全表扫描，且会匹配到脏数据
  - 独立子表 + ``EXISTS``：可索引、版本无关，采用

货源挂牌**也写入一行**（终点），使筛选逻辑对两个大厅完全统一，Service 层
不需要 ``if post_type`` 分支。「接受任意流向」的运力挂牌不写本表，靠主表
``any_direction=1`` 标记，筛选时用 ``OR any_direction = 1`` 兜住。
"""

from typing import Optional

from sqlalchemy import BigInteger, Index, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoPostDest(PlatformModelBase):
    """服务平台挂牌目的地/期望流向"""

    __tablename__ = "sys_eco_post_dest"
    __table_args__ = (
        # city 允许为 NULL，MySQL 唯一索引允许多行 NULL，因此「整省」行不会互斥。
        # 同一挂牌不会同时存在「四川省」与「四川-成都」两行，由应用层保证。
        UniqueConstraint("post_id", "province", "city", name="uk_eco_dest"),
        # 大厅按目的地筛选时的驱动索引
        Index("idx_eco_dest_lookup", "province", "city", "post_id"),
        {"comment": "服务平台挂牌目的地/期望流向"},
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="挂牌ID（sys_eco_post.id）"
    )
    post_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="挂牌类型（冗余，便于按大厅统计）"
    )
    province: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="目的地省"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="目的地市，为空表示整省"
    )
    region_code: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="行政区划代码（sys_regions.code）"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="顺序，0 为主目的地"
    )
