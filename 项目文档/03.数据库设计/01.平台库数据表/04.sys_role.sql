--数据库名称：zt_platform
--表名称：sys_role
CREATE TABLE `sys_role` (
  `role_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色编码',
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色名称',
  `role_type` smallint NOT NULL COMMENT '角色类型 0-平台角色 1-租户角色',
  `tenant_code` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属租户编码（平台角色为空）',
  `sort_order` smallint NOT NULL COMMENT '排序号',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_code` (`role_code`),
  KEY `ix_sys_role_tenant_code` (`tenant_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表'

