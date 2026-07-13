-- 租户业务库数据库
-- 运费计算任务表（异步重算工作流）
CREATE TABLE `biz_freight_calc_task` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_type` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '任务类型 waybill_changed/contract_changed/rule_changed/manual_recalc/batch_import',
  `target_type` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目标类型 waybill/contract/rule/batch',
  `target_id` bigint NOT NULL COMMENT '目标ID',
  `waybill_id` bigint DEFAULT NULL COMMENT '冗余的运单ID（合同/规则触发由展开阶段写入）',

  `status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT '状态 pending/running/success/failed',
  `priority` int NOT NULL DEFAULT '0' COMMENT '优先级（数值越大越优先）',

  `retry_count` int NOT NULL DEFAULT '0' COMMENT '已重试次数',
  `max_retry_count` int NOT NULL DEFAULT '3' COMMENT '最大重试次数',

  `error_message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最近一次错误信息',
  `triggered_by_user_id` bigint DEFAULT NULL COMMENT '触发用户ID',

  `started_at` datetime DEFAULT NULL COMMENT '开始时间',
  `finished_at` datetime DEFAULT NULL COMMENT '完成时间',

  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_fct_status_priority` (`status`, `priority`, `created_at`),
  KEY `idx_fct_target` (`target_type`, `target_id`),
  KEY `idx_fct_waybill` (`waybill_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运费计算任务表';
