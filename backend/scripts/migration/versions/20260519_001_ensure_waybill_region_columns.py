"""确保 biz_waybill 存在 origin/destination_region_id（修复漏跑 DDL）

若 20260518_001 已写入 biz_migration_log 但实际未执行 ALTER（曾用错误镜像、
手工改库等），后续 runner 不会再跑 20260518。本迁移用 information_schema
+ DATABASE() 检测当前库，缺列则补列，避免 Inspector 与连接状态边界问题。

幂等：仅当 information_schema 中无对应列时 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260519_001"
MIGRATION_NAME = "biz_waybill: ensure origin/destination_region_id (repair)"

REQUIRES_TABLES = ["biz_waybill"]

_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND column_name = :column_name
    LIMIT 1
    """
)


def upgrade(conn, tenant_code: str) -> None:
    def col_exists(table: str, column: str) -> bool:
        row = conn.execute(
            _EXISTS_SQL,
            {"table_name": table, "column_name": column},
        ).fetchone()
        return row is not None

    if not col_exists("biz_waybill", "origin_region_id"):
        conn.execute(text(
            "ALTER TABLE biz_waybill "
            "ADD COLUMN origin_region_id BIGINT NULL "
            "COMMENT '出发地行政区ID（biz_region.id）' AFTER origin_code"
        ))
    if not col_exists("biz_waybill", "destination_region_id"):
        conn.execute(text(
            "ALTER TABLE biz_waybill "
            "ADD COLUMN destination_region_id BIGINT NULL "
            "COMMENT '目的地行政区ID（biz_region.id）' AFTER destination_code"
        ))
