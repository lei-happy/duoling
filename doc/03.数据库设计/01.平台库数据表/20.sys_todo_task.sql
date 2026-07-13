-- 数据库名称：zt_platform
-- 表名称：sys_todo_task（待办；creator_id/assignee_id 为对应租户库 biz_user.id，须与 tenant_code 联用）
CREATE TABLE `sys_todo_task` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `tenant_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '租户编码',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '标题',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '描述',
  `creator_id` bigint NOT NULL COMMENT '创建人，租户内 biz_user.id',
  `assignee_id` bigint DEFAULT NULL COMMENT '主责任人，租户内 biz_user.id',
  `creator_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '创建人姓名快照',
  `assignee_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '责任人姓名快照',
  `due_time` datetime DEFAULT NULL COMMENT '截止时间',
  `priority` smallint NOT NULL DEFAULT '1' COMMENT '优先级 0低/1中/2高',
  `status` smallint NOT NULL DEFAULT '0' COMMENT '状态 0待处理/1进行中/2已完成/3已关闭',
  `completed_time` datetime DEFAULT NULL COMMENT '完成时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_sys_todo_tenant_assignee_status` (`tenant_code`,`assignee_id`,`status`),
  KEY `idx_sys_todo_tenant_status` (`tenant_code`,`status`),
  KEY `idx_sys_todo_due_time` (`due_time`),
  KEY `ix_sys_todo_task_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='待办任务表（平台库）';
