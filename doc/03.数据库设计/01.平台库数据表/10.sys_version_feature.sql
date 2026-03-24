--数据库名称：zt_platform
--表名称：sys_version_feature
CREATE TABLE `sys_version_feature` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `version_id` bigint NOT NULL,
  `feature_id` bigint NOT NULL,
  `status` smallint DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` smallint DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_vf_version_id` (`version_id`),
  KEY `idx_vf_feature_id` (`feature_id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='版本功能关联表'

