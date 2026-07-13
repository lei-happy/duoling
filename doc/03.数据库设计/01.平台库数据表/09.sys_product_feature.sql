--数据库名称：zt_platform
--表名称：sys_product_feature
CREATE TABLE `sys_product_feature` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `feature_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `feature_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `module` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `required_tables` json DEFAULT NULL,
  `sort_order` smallint DEFAULT '0',
  `status` smallint DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` smallint DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_feature_code` (`feature_code`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品功能清单表'

