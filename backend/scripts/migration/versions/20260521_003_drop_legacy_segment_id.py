"""清理 biz_task_waybill_item 多余的旧列 segment_id

背景（drift 复盘）：
  20260521_001 的设计意图是把 ``segment_id`` 重命名为 ``dispatch_order_id``，
  但 runner 三阶段顺序如下：
    Phase 1     ensure_tables
    Phase 1.5   reconcile_columns —— 对已存在表自动 ADD COLUMN 补齐 ORM 缺列
    Phase 2     versioned migrations
  Phase 1.5 比 Phase 2 先跑：reconcile 看到 ORM 模型里 `dispatch_order_id`
  存在、库里没有，就先 ADD COLUMN 加了一个 NULL 空列。
  随后 Phase 2 执行 20260521_001 的 Phase 5：
    if col_exists(segment_id) and not col_exists(dispatch_order_id): RENAME ...
  此时第二个条件已经不成立 → CHANGE COLUMN 被跳过。
  最终库里同时存在 ``segment_id``（旧、含数据）和 ``dispatch_order_id``
  （新、reconcile 加的空列），这就是 --check-drift 报的 [多列]。

修复策略：
  1. 同步数据：UPDATE ... SET dispatch_order_id = segment_id
     WHERE dispatch_order_id IS NULL AND segment_id IS NOT NULL
  2. DROP 旧列 segment_id

边界处理：
  - 极少数租户库 20260521_001 在 reconcile 之前就跑过了（例如 --skip-reconcile
    场景），此时 segment_id 已经被 RENAME 掉、dispatch_order_id 已存在，
    无需再做任何事；幂等返回。
  - 部分租户库 20260521_001 完全没跑过且 reconcile 也没生效（例如先 --skip-ensure
    --skip-reconcile 再跑 versioned），落到「只有 segment_id」分支，按 001
    的原始 RENAME 逻辑兜底执行 CHANGE COLUMN。

幂等：information_schema 判断列存在性，整个脚本可重复执行。
"""

from sqlalchemy import text

MIGRATION_ID = "20260521_003"
MIGRATION_NAME = "biz_task_waybill_item: drop legacy segment_id column"

REQUIRES_TABLES = ["biz_task_waybill_item"]


_COLUMN_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = :table_name
      AND column_name = :column_name
    LIMIT 1
    """
)


def upgrade(conn, tenant_code: str) -> None:
    def col_exists(table: str, column: str) -> bool:
        return conn.execute(
            _COLUMN_EXISTS_SQL,
            {"table_name": table, "column_name": column},
        ).fetchone() is not None

    has_legacy = col_exists("biz_task_waybill_item", "segment_id")
    has_new = col_exists("biz_task_waybill_item", "dispatch_order_id")

    if not has_legacy:
        # 已经是干净状态（20260521_001 RENAME 成功，或本脚本之前已执行过）
        return

    if not has_new:
        # 兜底：001 的 RENAME 没跑成功且 reconcile 也没补列，按 001 原逻辑
        # 直接 RENAME 即可，避免再 ADD + DROP 多一次 IO
        conn.execute(text(
            "ALTER TABLE biz_task_waybill_item "
            "CHANGE COLUMN segment_id dispatch_order_id BIGINT NULL "
            "COMMENT '可选指定走某条调令（NULL=跟随主任务首条重驶调令）'"
        ))
        return

    # 两列共存：把老列数据合并到新列（仅回填 dispatch_order_id 为空的行）
    conn.execute(text(
        "UPDATE biz_task_waybill_item "
        "SET dispatch_order_id = segment_id "
        "WHERE dispatch_order_id IS NULL AND segment_id IS NOT NULL"
    ))

    # DROP 旧列前先删掉可能残留的旧索引（idx_item_segment_id 在 ORM 里已不存在）
    # 用 information_schema.statistics 判存，避免索引名变种
    leftover_idx = conn.execute(text(
        """
        SELECT DISTINCT index_name FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'biz_task_waybill_item'
          AND column_name = 'segment_id'
        """
    )).fetchall()
    for (idx_name,) in leftover_idx:
        if idx_name == "PRIMARY":
            continue
        conn.execute(text(
            f"ALTER TABLE biz_task_waybill_item DROP INDEX `{idx_name}`"
        ))

    conn.execute(text(
        "ALTER TABLE biz_task_waybill_item DROP COLUMN segment_id"
    ))
