-- 租户业务库数据库
-- 运单运费计算结果主表（每次正式计算 = 一条快照）
CREATE TABLE `biz_waybill_freight_result` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `waybill_id` bigint NOT NULL COMMENT '运单ID',
  `waybill_version` int NOT NULL COMMENT '计算时锚定的运单版本',
  `is_active` smallint NOT NULL DEFAULT '1' COMMENT '是否当前有效快照 0-否 1-是',
  `total_amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '计算总金额',
  `calc_status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '计算状态 success/partial/exception',
  `calc_engine_version` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '计算引擎版本',
  `calc_time` datetime NOT NULL COMMENT '计算时间',
  `error_message` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '异常摘要',
  `triggered_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '触发来源 waybill_changed/contract_changed/rule_changed/manual_recalc/batch_import',
  `triggered_user_id` bigint DEFAULT NULL COMMENT '触发用户ID（手动重算时记录）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_wfr_waybill` (`waybill_id`),
  KEY `idx_wfr_active` (`waybill_id`, `is_active`),
  KEY `idx_wfr_calc_status` (`calc_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运单运费计算结果主表';
