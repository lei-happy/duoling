--数据库名称：zt_platform
--表名称：sys_feedback
CREATE TABLE `sys_feedback` (
  `tenant_code` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '租户编码',
  `user_id` bigint NOT NULL COMMENT '反馈用户ID',
  `user_name` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '提交时昵称快照',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '反馈标题',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '反馈内容',
  `feedback_type` smallint NOT NULL COMMENT '反馈类型 0-建议 1-缺陷 2-投诉 3-其他',
  `status` smallint NOT NULL COMMENT '处理状态 0-待处理 1-处理中 2-已解决 3-已关闭',
  `reply` text COLLATE utf8mb4_unicode_ci COMMENT '回复内容',
  `images` text COLLATE utf8mb4_unicode_ci COMMENT '截图URL列表（JSON数组）',
  `handler_id` bigint DEFAULT NULL COMMENT '处理人平台用户ID',
  `handler_name` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '处理人姓名快照',
  `replied_at` datetime DEFAULT NULL COMMENT '最近回复时间',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `ix_sys_feedback_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='意见反馈表'
