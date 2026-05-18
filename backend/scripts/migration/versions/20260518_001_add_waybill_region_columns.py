"""为 biz_waybill 增加起讫点行政区 ID 列（与 ORM / 设计文档对齐）

旧库若只跑过 Phase 1 补表、未执行过 migrate_freight_engine 手工脚本，
则缺本列会导致运单列表 count 查询失败（1054 Unknown column）。

幂等：information_schema 自检后再 ALTER。
"""

from sqlalchemy import text, inspect as sa_inspect

MIGRATION_ID = "20260518_001"
MIGRATION_NAME = "biz_waybill: add origin/destination_region_id"

REQUIRES_TABLES = ["biz_waybill"]


def upgrade(conn, tenant_code: str) -> None:
    insp = sa_inspect(conn)
    cols = {c["name"] for c in insp.get_columns("biz_waybill")}

    if "origin_region_id" not in cols:
        conn.execute(text(
            "ALTER TABLE biz_waybill "
            "ADD COLUMN origin_region_id BIGINT NULL "
            "COMMENT '出发地行政区ID（biz_region.id）' AFTER origin_code"
        ))
    if "destination_region_id" not in cols:
        conn.execute(text(
            "ALTER TABLE biz_waybill "
            "ADD COLUMN destination_region_id BIGINT NULL "
            "COMMENT '目的地行政区ID（biz_region.id）' AFTER destination_code"
        ))
