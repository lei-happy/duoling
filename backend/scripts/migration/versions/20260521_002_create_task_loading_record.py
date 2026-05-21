"""新建装卸记录表 biz_task_loading_record 与桥接表 biz_task_loading_record_item

背景：
  调度工作台 v3「多批次装卸」改造引入了显式装卸事件记录，每次装/卸车都
  会落库一条 biz_task_loading_record 主行 + N 条 biz_task_loading_record_item 桥接行；
  item.status 由记录创建/撤销驱动，task.status 1↔2 / 3↔4 由 item 聚合。

  新表已登记到 sys_product_feature.required_tables（feature_code = biz_task），
  runner Phase 1 会通过 metadata.create_all 自动建表；但仍提供一个**显式**的
  versioned migration，原因：
    1. 给运维一个可追踪的 biz_migration_log 记录（执行时间、执行人）；
    2. 当 Phase 1 被 --skip-ensure 跳过时，仍能保证表存在；
    3. 与 20260521_001 调令重命名同批次配套，便于回溯本次发布。

幂等：CREATE TABLE IF NOT EXISTS（INDEX 在 CREATE TABLE 内联，无需独立判存）。
"""

from sqlalchemy import text

MIGRATION_ID = "20260521_002"
MIGRATION_NAME = "create biz_task_loading_record(_item)"

# 仅对已启用任务单模块（含 biz_task）的租户生效；其它租户由 runner 自动跳过。
REQUIRES_TABLES = ["biz_task"]


_LOADING_RECORD_DDL = """
CREATE TABLE IF NOT EXISTS biz_task_loading_record (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
    task_id BIGINT NOT NULL COMMENT '关联 biz_task.id',
    dispatch_order_id BIGINT NULL
        COMMENT '关联 biz_task_dispatch_order.id（多调令任务必填）',
    event_type SMALLINT NOT NULL COMMENT '事件类型 1-装车 2-卸车',
    happened_at DATETIME NOT NULL COMMENT '实际装/卸时间',
    location VARCHAR(255) NULL COMMENT '装/卸地点名称',
    location_code VARCHAR(20) NULL COMMENT '地点行政区编码',
    location_region_id BIGINT NULL COMMENT '地点行政区 ID',
    quantity INT NOT NULL DEFAULT 0
        COMMENT '本次装/卸总台数（冗余 = SUM(record_item.quantity)）',
    photo_urls JSON NULL COMMENT '照片 URL 数组（OSS 路径，最多 9 张）',
    operator_id BIGINT NULL COMMENT '操作人 user_id',
    operator_name VARCHAR(50) NULL COMMENT '操作人姓名（冗余）',
    remark VARCHAR(255) NULL COMMENT '备注',
    PRIMARY KEY (id),
    INDEX idx_loading_record_task_id (task_id),
    INDEX idx_loading_record_dispatch_order_id (dispatch_order_id),
    INDEX idx_loading_record_event_type (event_type),
    INDEX idx_loading_record_happened_at (happened_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='任务单装卸事件记录表（多批次装/卸车主表）'
"""


_LOADING_RECORD_ITEM_DDL = """
CREATE TABLE IF NOT EXISTS biz_task_loading_record_item (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
    record_id BIGINT NOT NULL COMMENT '关联 biz_task_loading_record.id',
    item_id BIGINT NOT NULL COMMENT '关联 biz_task_waybill_item.id',
    quantity INT NOT NULL
        COMMENT '本次该 item 装/卸的台数（>0，允许 < item.quantity 远期支持 item 内拆批）',
    PRIMARY KEY (id),
    INDEX idx_loading_record_item_record_id (record_id),
    INDEX idx_loading_record_item_item_id (item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='装卸记录与挂接货物的桥接表'
"""


def upgrade(conn, tenant_code: str) -> None:
    conn.execute(text(_LOADING_RECORD_DDL))
    conn.execute(text(_LOADING_RECORD_ITEM_DDL))
