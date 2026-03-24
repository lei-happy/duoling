--数据库名称：zt_platform
--表名称：sys_operation_log
CREATE TABLE `sys_operation_log` (
  `user_id` int DEFAULT NULL COMMENT '操作用户ID',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作用户名',
  `tenant_code` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '租户编码',
  `module` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作模块',
  `action` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作类型',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作描述',
  `request_method` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '请求方法',
  `request_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '请求URL',
  `request_body` text COLLATE utf8mb4_unicode_ci COMMENT '请求参数',
  `response_body` text COLLATE utf8mb4_unicode_ci COMMENT '响应结果',
  `ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  `elapsed_time` int DEFAULT NULL COMMENT '耗时（毫秒）',
  `status` smallint NOT NULL COMMENT '状态 0-失败 1-成功',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `ix_sys_operation_log_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表'