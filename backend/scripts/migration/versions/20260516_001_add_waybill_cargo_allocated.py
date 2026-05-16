"""为 biz_waybill_cargo 添加 allocated_quantity / cargo_version 字段

背景：
  v2 运输任务单模块（biz_task*）按"台数 M:N"挂接到 biz_waybill_cargo，
  需要在 cargo 行上维护「已分配到任务单的台数」与「明细版本号」。
  纯建表场景由 runner Phase 1 自动覆盖，但 ALTER COLUMN 必须显式写迁移。

幂等：内部用 information_schema 自检后再 ALTER。
"""

from sqlalchemy import text, inspect as sa_inspect

MIGRATION_ID = "20260516_001"
MIGRATION_NAME = "biz_waybill_cargo: add allocated_quantity & cargo_version"

# 该迁移只对已启用运单模块的租户有意义；缺 biz_waybill_cargo 则 runner 自动跳过
REQUIRES_TABLES = ["biz_waybill_cargo"]


def upgrade(conn, tenant_code: str) -> None:
    insp = sa_inspect(conn)
    cols = {c["name"] for c in insp.get_columns("biz_waybill_cargo")}

    if "allocated_quantity" not in cols:
        conn.execute(text(
            "ALTER TABLE biz_waybill_cargo "
            "ADD COLUMN allocated_quantity INT NOT NULL DEFAULT 0 "
            "COMMENT '已分配到任务单的台数（应用层维护，约束 allocated<=quantity）'"
        ))

    if "cargo_version" not in cols:
        conn.execute(text(
            "ALTER TABLE biz_waybill_cargo "
            "ADD COLUMN cargo_version INT NOT NULL DEFAULT 1 "
            "COMMENT '明细版本号'"
        ))
