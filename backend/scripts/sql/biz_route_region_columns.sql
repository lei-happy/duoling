-- =====================================================================
-- 路线表 biz_route：增加行政区匹配字段（租户业务库 zt_biz_*）
-- 执行：每个已存在租户库执行一次；新建租户由 SQLAlchemy 模型同步建表
-- =====================================================================

SET NAMES utf8mb4;

ALTER TABLE biz_route
  ADD COLUMN origin_region_id BIGINT NULL COMMENT '出发地行政区ID（biz_region.id）' AFTER destination,
  ADD COLUMN destination_region_id BIGINT NULL COMMENT '目的地行政区ID（biz_region.id）' AFTER origin_region_id,
  ADD COLUMN origin_code VARCHAR(20) NULL COMMENT '出发地国标区划码' AFTER destination_region_id,
  ADD COLUMN destination_code VARCHAR(20) NULL COMMENT '目的地国标区划码' AFTER origin_code;

CREATE INDEX idx_biz_route_region_pair
  ON biz_route (is_deleted, origin_region_id, destination_region_id);
