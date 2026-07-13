--数据库名称：zt_platform
--表名称：sys_changelog
CREATE TABLE `sys_changelog` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `version` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '版本号（如 v1.2.0）',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新标题',
  `content` text COLLATE utf8mb4_unicode_ci COMMENT '更新内容（Markdown 格式）',
  `release_date` date NOT NULL COMMENT '发布日期',
  `sort_order` smallint NOT NULL DEFAULT '0' COMMENT '排序号（越大越靠前）',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-已发布',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_release_date` (`release_date`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品更新日志表'

