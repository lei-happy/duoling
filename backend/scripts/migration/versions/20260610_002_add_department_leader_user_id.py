"""biz_department: 部门负责人结构化字段 leader_user_id

支撑审批中心「部门负责人」动态审批人解析（见 08.审批中心/04.组织模型扩展依赖）。
保留原 leader 文本字段不动；新增列可空，无回填阻塞。

幂等：information_schema 检测后再 ALTER。
"""

from sqlalchemy import text

MIGRATION_ID = "20260610_002"
MIGRATION_NAME = "biz_department: add leader_user_id"
REQUIRES_TABLES = ["biz_department"]

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
            {"table_name": "biz_department", "column_name": "leader_user_id"},
        ).fetchone()
        is not None
    )
    if not exists:
        conn.execute(
            text(
                "ALTER TABLE biz_department "
                "ADD COLUMN leader_user_id BIGINT NULL "
                "COMMENT '部门负责人 biz_user.id（审批中心动态审批人依赖）' "
                "AFTER leader"
            )
        )
