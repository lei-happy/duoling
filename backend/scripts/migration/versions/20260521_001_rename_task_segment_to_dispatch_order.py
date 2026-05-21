"""把 biz_task_segment 重命名扩展为 biz_task_dispatch_order，并新增装卸记录关联字段

变更内容：
1. RENAME TABLE biz_task_segment → biz_task_dispatch_order
2. 列重命名：segment_no → order_no
3. 新增列：dispatch_type / accepted_at / started_at / completed_at
4. 索引/唯一约束重命名：
   - idx_segment_task_id → idx_dispatch_order_task_id
   - uk_task_segment → uk_task_dispatch_order
5. 新增索引 idx_dispatch_order_dispatch_type
6. biz_task_waybill_item 列重命名：segment_id → dispatch_order_id

幂等：通过 information_schema 检测当前表 / 列 / 索引 是否已是新名后再执行。
"""

from sqlalchemy import text

MIGRATION_ID = "20260521_001"
MIGRATION_NAME = "rename biz_task_segment to biz_task_dispatch_order"

REQUIRES_TABLES = ["biz_task_segment", "biz_task_waybill_item"]


_TABLE_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = :name
    LIMIT 1
    """
)

_COLUMN_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND column_name = :column_name
    LIMIT 1
    """
)

_INDEX_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND index_name = :index_name
    LIMIT 1
    """
)


def upgrade(conn, tenant_code: str) -> None:
    def table_exists(name: str) -> bool:
        return conn.execute(_TABLE_EXISTS_SQL, {"name": name}).fetchone() is not None

    def col_exists(table: str, column: str) -> bool:
        return conn.execute(
            _COLUMN_EXISTS_SQL,
            {"table_name": table, "column_name": column},
        ).fetchone() is not None

    def idx_exists(table: str, index: str) -> bool:
        return conn.execute(
            _INDEX_EXISTS_SQL,
            {"table_name": table, "index_name": index},
        ).fetchone() is not None

    # ---------------------------------------------------------------
    # Phase 1: 重命名表 biz_task_segment → biz_task_dispatch_order
    # ---------------------------------------------------------------
    if table_exists("biz_task_segment") and not table_exists("biz_task_dispatch_order"):
        conn.execute(text(
            "RENAME TABLE biz_task_segment TO biz_task_dispatch_order"
        ))

    if not table_exists("biz_task_dispatch_order"):
        # 全新租户首次开通本特性时由 runner Phase 1 + required_tables 创建，
        # 这里直接返回，后续 ALTER 步骤都不需要执行。
        return

    # ---------------------------------------------------------------
    # Phase 2: 列重命名 segment_no → order_no
    # ---------------------------------------------------------------
    if col_exists("biz_task_dispatch_order", "segment_no") and not col_exists(
        "biz_task_dispatch_order", "order_no"
    ):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "CHANGE COLUMN segment_no order_no SMALLINT NOT NULL "
            "COMMENT '调令序号 1,2,3...'"
        ))

    # ---------------------------------------------------------------
    # Phase 3: 新增列 dispatch_type / accepted_at / started_at / completed_at
    # ---------------------------------------------------------------
    if not col_exists("biz_task_dispatch_order", "dispatch_type"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD COLUMN dispatch_type SMALLINT NOT NULL DEFAULT 1 "
            "COMMENT '调令类型 1-重驶 2-空驶 3-年检 4-应急 5-其他' "
            "AFTER order_no"
        ))
    if not col_exists("biz_task_dispatch_order", "accepted_at"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD COLUMN accepted_at DATETIME NULL "
            "COMMENT '调令接收时间（司机端确认）' "
            "AFTER actual_arrive_time"
        ))
    if not col_exists("biz_task_dispatch_order", "started_at"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD COLUMN started_at DATETIME NULL "
            "COMMENT '调令开始时间（司机点击出发）' "
            "AFTER accepted_at"
        ))
    if not col_exists("biz_task_dispatch_order", "completed_at"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD COLUMN completed_at DATETIME NULL "
            "COMMENT '调令完成时间' "
            "AFTER started_at"
        ))

    # ---------------------------------------------------------------
    # Phase 4: 索引/唯一约束重命名 + 新增 dispatch_type 索引
    # ---------------------------------------------------------------
    if idx_exists("biz_task_dispatch_order", "idx_segment_task_id"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "RENAME INDEX idx_segment_task_id TO idx_dispatch_order_task_id"
        ))
    elif not idx_exists("biz_task_dispatch_order", "idx_dispatch_order_task_id"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD INDEX idx_dispatch_order_task_id (task_id)"
        ))

    if idx_exists("biz_task_dispatch_order", "uk_task_segment"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "RENAME INDEX uk_task_segment TO uk_task_dispatch_order"
        ))
    elif not idx_exists("biz_task_dispatch_order", "uk_task_dispatch_order"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD UNIQUE KEY uk_task_dispatch_order (task_id, order_no)"
        ))

    if not idx_exists("biz_task_dispatch_order", "idx_dispatch_order_dispatch_type"):
        conn.execute(text(
            "ALTER TABLE biz_task_dispatch_order "
            "ADD INDEX idx_dispatch_order_dispatch_type (dispatch_type)"
        ))

    # ---------------------------------------------------------------
    # Phase 5: biz_task_waybill_item 列重命名 segment_id → dispatch_order_id
    #
    # 注意：runner Phase 1.5 (reconcile_columns) 在本 Phase 之前执行，
    # 它会因 ORM 模型已声明 dispatch_order_id 而提前 ADD COLUMN 一个空列，
    # 使两列并存。本步分两种情况处理：
    #   - 仅有 segment_id：原始 CHANGE COLUMN（v1 行为）
    #   - 两列并存：把老列数据回填到新列，再 DROP 老列
    # 二者都已在 20260521_003 中再次兜底；这里收紧本迁移自身的幂等性，
    # 避免新租户首次执行依旧落入 drift 状态。
    # ---------------------------------------------------------------
    has_legacy_col = col_exists("biz_task_waybill_item", "segment_id")
    has_new_col = col_exists("biz_task_waybill_item", "dispatch_order_id")
    if has_legacy_col and not has_new_col:
        conn.execute(text(
            "ALTER TABLE biz_task_waybill_item "
            "CHANGE COLUMN segment_id dispatch_order_id BIGINT NULL "
            "COMMENT '可选指定走某条调令（NULL=跟随主任务首条重驶调令）'"
        ))
    elif has_legacy_col and has_new_col:
        conn.execute(text(
            "UPDATE biz_task_waybill_item "
            "SET dispatch_order_id = segment_id "
            "WHERE dispatch_order_id IS NULL AND segment_id IS NOT NULL"
        ))
        conn.execute(text(
            "ALTER TABLE biz_task_waybill_item DROP COLUMN segment_id"
        ))
