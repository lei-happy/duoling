"""biz_task: 分配时间、派车时间（调度工作台按阶段筛选）

幂等：information_schema 检测后再 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260528_001"
MIGRATION_NAME = "biz_task: add assigned_at / dispatched_at"

REQUIRES_TABLES = ["biz_task"]

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
    def col_exists(column: str) -> bool:
        return (
            conn.execute(
                _EXISTS_SQL,
                {"table_name": "biz_task", "column_name": column},
            ).fetchone()
            is not None
        )

    if not col_exists("assigned_at"):
        conn.execute(text(
            "ALTER TABLE biz_task "
            "ADD COLUMN assigned_at DATETIME NULL "
            "COMMENT '承运分配完成时间（-1→0/1）' AFTER actual_load_time"
        ))
    if not col_exists("dispatched_at"):
        conn.execute(text(
            "ALTER TABLE biz_task "
            "ADD COLUMN dispatched_at DATETIME NULL "
            "COMMENT '派车完成时间（0→1 或分配直达已派车）' AFTER assigned_at"
        ))
