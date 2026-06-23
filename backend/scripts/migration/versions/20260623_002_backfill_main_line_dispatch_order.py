"""为"零调令"的存量任务回填一条主线路调令

背景：
  任务单创建时调令（路线）是可选的。早期未手动规划路线的任务不会生成任何
  调令记录，仅把起终点冗余写到 ``biz_task``。这导致企业端"确认装车/到达"
  弹窗的「关联调令」下拉为空，流程卡死。

  应用层已通过两条路径修复：
    1. 新建/编辑任务时，无手动路线则自动生成"主线路"调令（重驶）；
    2. 调令列表接口对零调令任务做幂等懒修复。
  本迁移是面向**存量数据**的一次性批量回填，避免依赖"逐个打开任务"才触发
  懒修复，确保部署后所有历史任务立即可用。

回填规则（与 ``TaskService.ensure_main_line_dispatch_order`` 完全一致）：
  对每个未删除、且不存在任何未删除调令的任务，按其起终点插入一条
    order_no=1, dispatch_type=1(重驶), status=0(待装车)
  的主线路调令，并把任务 ``segment_count`` 修正为 1。

幂等：
  - 仅对"当前无任何未删除调令"的任务插入（NOT EXISTS 守卫），可重复执行；
  - segment_count 仅修正"仍为 0 且已存在主线路调令"的任务。

REQUIRES_TABLES 缺失（未开通任务特性的租户）→ runner 自动跳过。
"""

from sqlalchemy import text

MIGRATION_ID = "20260623_002"
MIGRATION_NAME = "backfill main line dispatch order for zero-order tasks"

REQUIRES_TABLES = ["biz_task", "biz_task_dispatch_order"]


_TABLE_EXISTS_SQL = text(
    """
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = DATABASE() AND table_name = :name
    LIMIT 1
    """
)


_INSERT_MAIN_LINE_SQL = text(
    """
    INSERT INTO biz_task_dispatch_order
        (task_id, order_no, dispatch_type,
         from_location, from_code, from_region_id,
         to_location, to_code, to_region_id,
         planned_load_time, planned_arrive_time, status)
    SELECT
        t.id, 1, 1,
        t.origin, t.origin_code, t.origin_region_id,
        t.destination, t.destination_code, t.destination_region_id,
        t.planned_load_time, t.planned_arrive_time, 0
    FROM biz_task t
    WHERE t.is_deleted = 0
      AND NOT EXISTS (
          SELECT 1 FROM biz_task_dispatch_order d
          WHERE d.task_id = t.id AND d.is_deleted = 0
      )
    """
)


_FIX_SEGMENT_COUNT_SQL = text(
    """
    UPDATE biz_task t
    SET t.segment_count = 1
    WHERE t.is_deleted = 0
      AND (t.segment_count IS NULL OR t.segment_count = 0)
      AND EXISTS (
          SELECT 1 FROM biz_task_dispatch_order d
          WHERE d.task_id = t.id AND d.is_deleted = 0 AND d.order_no = 1
      )
    """
)


def upgrade(conn, tenant_code: str) -> None:
    def table_exists(name: str) -> bool:
        return conn.execute(_TABLE_EXISTS_SQL, {"name": name}).fetchone() is not None

    # 前置表缺失（未开通任务特性）→ 跳过
    if not table_exists("biz_task") or not table_exists("biz_task_dispatch_order"):
        return

    # 1. 为零调令任务插入主线路调令（幂等：NOT EXISTS 守卫）
    conn.execute(_INSERT_MAIN_LINE_SQL)

    # 2. 修正这些任务的调令计数冗余
    conn.execute(_FIX_SEGMENT_COUNT_SQL)
