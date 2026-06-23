"""运单回单：新增 biz_waybill_receipt 凭证表 + biz_waybill.receipt_at；
并把运单状态机「已关闭」从 6 整体后移为 7（腾出 6 = 已回单）。

背景：
  2026-06 客户端业务闭环改造引入运单「回单」环节（签收底单返还货主），
  这是运单维度的人工动作，与任务/挂接行状态机彼此独立。新状态空间：
    0 待确认 / 1 待调度 / 2 调度中 / 3 运输中 / 4 待签收 / 5 已签收
    / 6 已回单（新） / 7 已关闭（原 6，整体后移）

本迁移做三件事（均幂等）：
  1. CREATE TABLE IF NOT EXISTS biz_waybill_receipt（与 ORM 对齐，供 runner
     Phase 1 之外的显式追踪；--skip-ensure 时也能建表）。
  2. ALTER biz_waybill ADD COLUMN receipt_at（information_schema 判存后再加）。
  3. 数据迁移：存量「已关闭」运单 status=6 → 7。
     说明：新语义 6=已回单为全新状态，存量数据不可能已是新 6，故
     UPDATE ... WHERE status = 6 仅命中旧「已关闭」记录，安全。
     依赖 biz_migration_log 保证本迁移每租户仅执行一次，不会重复改写。
"""

from sqlalchemy import text

MIGRATION_ID = "20260623_001"
MIGRATION_NAME = "waybill receipt table + receipt_at + renumber closed 6->7"

REQUIRES_TABLES = ["biz_waybill"]


_RECEIPT_DDL = """
CREATE TABLE IF NOT EXISTS biz_waybill_receipt (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
    waybill_id BIGINT NOT NULL COMMENT '关联 biz_waybill.id',
    file_urls JSON NULL COMMENT '回单底单文件 URL 数组（OSS 路径，最多 9 张）',
    file_type SMALLINT NOT NULL DEFAULT 1 COMMENT '文件类型 1-图片 2-PDF',
    received_at DATETIME NOT NULL COMMENT '回单回收时间',
    uploaded_by BIGINT NULL COMMENT '操作人 user_id',
    operator_name VARCHAR(50) NULL COMMENT '操作人姓名（冗余）',
    remark VARCHAR(255) NULL COMMENT '备注',
    PRIMARY KEY (id),
    INDEX idx_waybill_receipt_waybill_id (waybill_id),
    INDEX idx_waybill_receipt_received_at (received_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='运单回单凭证表（签收底单返还货主）'
"""


_COL_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND column_name = :column_name
    LIMIT 1
    """
)


def upgrade(conn, tenant_code: str) -> None:
    # 1. 回单凭证表
    conn.execute(text(_RECEIPT_DDL))

    # 2. biz_waybill.receipt_at（幂等）
    has_receipt_at = conn.execute(
        _COL_EXISTS_SQL,
        {"table_name": "biz_waybill", "column_name": "receipt_at"},
    ).fetchone() is not None
    if not has_receipt_at:
        conn.execute(text(
            "ALTER TABLE biz_waybill "
            "ADD COLUMN receipt_at DATETIME NULL "
            "COMMENT '回单确认时间（签收底单返还货主）' AFTER status"
        ))

    # 3. 存量「已关闭」运单 status 6 -> 7（腾出 6 = 已回单）
    conn.execute(text(
        "UPDATE biz_waybill SET status = 7 WHERE status = 6 AND is_deleted = 0"
    ))

    # 4. 同步 biz_waybill.status 列注释到新状态空间（仅注释，元数据级变更）
    conn.execute(text(
        "ALTER TABLE biz_waybill MODIFY COLUMN status SMALLINT NOT NULL DEFAULT 0 "
        "COMMENT '状态 0-待确认 1-待调度 2-调度中 3-运输中 4-待签收 "
        "5-已签收 6-已回单 7-已关闭'"
    ))
