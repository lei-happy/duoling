--数据库名称：zt_platform
--表名称：sys_tenant_product
CREATE TABLE `sys_tenant_product` (
  `tenant_id` bigint NOT NULL COMMENT '租户ID',
  `tenant_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '租户编码',
  `version_id` bigint NOT NULL COMMENT '产品版本ID',
  `version_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '产品版本编码',
  `start_time` datetime DEFAULT NULL COMMENT '授权开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '授权到期时间',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `ix_sys_tenant_product_tenant_code` (`tenant_code`),
  KEY `ix_sys_tenant_product_tenant_id` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='租户产品版本授权表'

