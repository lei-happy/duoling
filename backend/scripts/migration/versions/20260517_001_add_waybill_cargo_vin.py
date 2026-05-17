"""为 biz_waybill_cargo 添加 vin 字段（车架号/VIN）

幂等：内部用 information_schema 自检后再 ALTER。
"""

from sqlalchemy import text, inspect as sa_inspect

MIGRATION_ID = "20260517_001"
MIGRATION_NAME = "biz_waybill_cargo: add vin"

REQUIRES_TABLES = ["biz_waybill_cargo"]


def upgrade(conn, tenant_code: str) -> None:
    insp = sa_inspect(conn)
    cols = {c["name"] for c in insp.get_columns("biz_waybill_cargo")}

    if "vin" not in cols:
        conn.execute(text(
            "ALTER TABLE biz_waybill_cargo "
            "ADD COLUMN vin VARCHAR(50) NULL "
            "COMMENT '车架号(VIN)'"
        ))
