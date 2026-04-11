-- 租户业务库数据库
-- 挂车核心表
CREATE TABLE `biz_trailer` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `plate_number` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '挂车车牌号',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plate_number` (`plate_number`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='挂车核心表';
