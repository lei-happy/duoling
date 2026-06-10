"""biz_social_capacity: 接入审批中心，挂 approval_instance_id

profile_change 审核走审批引擎后，主表记录对应审批实例 id；
为空表示该档案仍走旧单级审核（平滑过渡）。

幂等：information_schema 检测后再 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260610_001"
MIGRATION_NAME = "biz_social_capacity: add approval_instance_id"
REQUIRES_TABLES = ["biz_social_capacity"]

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
    exists = (
        conn.execute(
            _EXISTS_SQL,
            {"table_name": "biz_social_capacity", "column_name": "approval_instance_id"},
        ).fetchone()
        is not None
    )
    if not exists:
        conn.execute(
            text(
                "ALTER TABLE biz_social_capacity "
                "ADD COLUMN approval_instance_id BIGINT NULL "
                "COMMENT '审批中心实例 id（接入审批引擎后写回）' "
                "AFTER approval_remark"
            )
        )
