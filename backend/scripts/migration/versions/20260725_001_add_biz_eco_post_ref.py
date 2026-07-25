"""add biz_eco_post_ref

服务平台（生态）在租户库的唯一新表。

**本迁移刻意为空操作，不是未完成的 stub。**

`biz_eco_post_ref` 是纯新增表，由 runner Phase 1 依据
`sys_product_feature.required_tables` 在版本开通时自动建出（与
`biz_open_call_log` 的处理方式一致，见 20260724_001）。在此重复建表既无必要，
也会与自动建表逻辑产生两个事实源。

存量租户不会自动拥有本表，需要一次性脚本遍历所有 `db_initialized = 1` 的租户
执行 `ensure_tenant_tables(["biz_eco_post_ref"])`。因为发布权开放到了 standard，
覆盖范围是全部 standard 与 pro 租户——建议直接对所有已初始化租户执行，
多建一张空表的成本远低于漏建导致的运行时报错。
"""

from sqlalchemy import text

MIGRATION_ID = "20260725_001"
MIGRATION_NAME = "add biz_eco_post_ref"

REQUIRES_TABLES = []


_COL_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :tn
      AND column_name = :cn
    LIMIT 1
    """
)

_INDEX_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = :tn
      AND index_name = :ix
    LIMIT 1
    """
)


def _col_exists(conn, table_name: str, column_name: str) -> bool:
    return conn.execute(
        _COL_EXISTS_SQL, {"tn": table_name, "cn": column_name}
    ).fetchone() is not None


def _index_exists(conn, table_name: str, index_name: str) -> bool:
    return conn.execute(
        _INDEX_EXISTS_SQL, {"tn": table_name, "ix": index_name}
    ).fetchone() is not None


def upgrade(conn, tenant_code: str) -> None:
    # NOTE: 新表 `biz_eco_post_ref` —— 推荐直接由 runner Phase 1 (feature.required_tables) 自动建表。
    # 如本迁移确实需要在租户库强建该表，请改用 metadata.create_all 风格。
    # 此处空操作。

    return None

