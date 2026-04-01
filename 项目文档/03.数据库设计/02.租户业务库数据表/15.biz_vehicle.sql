-- 租户业务库数据库
-- 车辆核心表（重构：原单表拆分为核心表+扩展表）
CREATE TABLE `biz_vehicle` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `plate_number` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '车牌号',
  `trailer_id` bigint DEFAULT NULL COMMENT '关联挂车ID，可为空',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常 2-维修/保养 3-保险续期 9-已报废',
  `status_source` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'manual' COMMENT '状态变更来源（manual-手动/maintenance-维修保养/insurance-保险）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plate_number` (`plate_number`),
  KEY `idx_trailer_id` (`trailer_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车辆核心表';
