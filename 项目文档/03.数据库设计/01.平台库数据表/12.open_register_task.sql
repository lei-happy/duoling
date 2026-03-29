--数据库名称：zt_platform
--表名称：open_register_task
CREATE TABLE `open_register_task` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '任务 UUID',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'pending running success failed',
  `current_step` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '当前步骤机器可读 key',
  `message` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '当前步骤中文说明',
  `percent` smallint NOT NULL DEFAULT '0' COMMENT '进度 0-100',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用于并发注册防抖查询',
  `payload_json` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'RegisterRequest JSON',
  `result_json` text COLLATE utf8mb4_unicode_ci COMMENT '成功时 RegisterResponse JSON',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '失败原因',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `ix_open_register_task_status` (`status`),
  KEY `ix_open_register_task_contact_phone` (`contact_phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='官网企业注册异步任务';
