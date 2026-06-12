"""approval_flow_version_log

审批流程模板版本快照表，记录每次发布/停用/启用的配置快照。
"""

from sqlalchemy import text

MIGRATION_ID = "20260612_002"
MIGRATION_NAME = "approval_flow_version_log"

REQUIRES_TABLES = ["biz_approval_flow"]


_TABLE_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = DATABASE()
      AND table_name = :tn
    LIMIT 1
    """
)


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(_TABLE_EXISTS_SQL, {"tn": table_name}).fetchone() is not None


def upgrade(conn, tenant_code: str) -> None:
    if _table_exists(conn, "biz_approval_flow_version_log"):
        return

    conn.execute(text(
        """
        CREATE TABLE `biz_approval_flow_version_log` (
          `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
          `flow_id` bigint NOT NULL COMMENT '流程模板ID',
          `version` int NOT NULL COMMENT '发布版本号',
          `change_type` varchar(32) NOT NULL COMMENT '变更类型 publish/disable/enable',
          `snapshot` json DEFAULT NULL COMMENT '该版本流程配置快照',
          `operator_id` bigint DEFAULT NULL COMMENT '操作人用户ID',
          `remark` varchar(255) DEFAULT NULL COMMENT '备注',
          `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
          `is_deleted` tinyint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
          PRIMARY KEY (`id`),
          KEY `idx_afl_flow` (`flow_id`),
          KEY `idx_afl_flow_version` (`flow_id`,`version`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批流程模板版本日志表'
        """
    ))
