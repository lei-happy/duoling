--数据库名称：zt_platform
--表名称：sys_product_version
CREATE TABLE `sys_product_version` (
  `version_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '版本编码（如 basic/standard/pro/enterprise）',
  `version_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '版本名称',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '版本说明',
  `features` json DEFAULT NULL COMMENT '功能清单（JSON格式，菜单编码列表等）',
  `max_users` int NOT NULL COMMENT '最大用户数',
  `max_vehicles` int NOT NULL COMMENT '最大车辆数',
  `price` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '价格',
  `sort_order` smallint NOT NULL COMMENT '排序号',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `version_code` (`version_code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品版本表'

