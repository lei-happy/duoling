"""biz_user: 直属上级结构化字段 supervisor_user_id

支撑审批中心「逐级上级主管」动态审批人解析（见 08.审批中心/04.组织模型扩展依赖）。
形成汇报线：员工 → 直属上级 → 上级的上级……新增列可空，无回填阻塞。

幂等：information_schema 检测后再 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260610_003"
MIGRATION_NAME = "biz_user: add supervisor_user_id"
REQUIRES_TABLES = ["biz_user"]

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
            {"table_name": "biz_user", "column_name": "supervisor_user_id"},
        ).fetchone()
        is not None
    )
    if not exists:
        conn.execute(
            text(
                "ALTER TABLE biz_user "
                "ADD COLUMN supervisor_user_id BIGINT NULL "
                "COMMENT '直属上级 biz_user.id（审批中心逐级上级依赖）' "
                "AFTER department_id"
            )
        )
