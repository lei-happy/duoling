-- 租户业务库数据库
-- 车型/品牌别名表（将非标准的"品牌+车型"映射到标准 brand_id / series_id）
CREATE TABLE `biz_vehicle_alias` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `alias_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL
    COMMENT '别名（品牌别名=品牌串；车系别名="品牌\\x1f车型"组合串）',
  `alias_kind` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'series' COMMENT '别名类型 brand/series',
  `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID',
  `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-启用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_vehicle_alias_name` (`alias_name`),
  KEY `idx_vehicle_alias_brand` (`brand_id`),
  KEY `idx_vehicle_alias_series` (`series_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车型/品牌别名表';
