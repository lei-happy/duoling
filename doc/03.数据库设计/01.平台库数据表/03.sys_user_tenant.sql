--数据库名称：zt_platform
--表名称：sys_user_tenant
CREATE TABLE `sys_user_tenant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `tenant_code` varchar(32) NOT NULL COMMENT '企业编码',
  `user_type` smallint NOT NULL DEFAULT '2' COMMENT '角色类型 1-租户管理员 2-租户用户 3-驾驶员',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-正常',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_tenant` (`user_id`,`tenant_code`),
  KEY `idx_tenant_code` (`tenant_code`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户企业关联表'

