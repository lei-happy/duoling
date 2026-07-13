-- 租户业务库数据库
-- 地名别名表（将运单/导入数据里的非标准地名映射到 biz_region.id）
CREATE TABLE `biz_region_alias` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `alias_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '别名（去空白）',
  `region_id` bigint NOT NULL COMMENT '目标行政区ID（biz_region.id）',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-启用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_region_alias_name` (`alias_name`),
  KEY `idx_region_alias_region` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='地名别名表';
