-- 租户业务库数据库
-- 运费计算异常表（业务结果维度，区别于 task 的工作流维度）
CREATE TABLE `biz_freight_calc_exception` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `waybill_id` bigint DEFAULT NULL COMMENT '运单ID（导入校验异常可能为空）',
  `waybill_cargo_id` bigint DEFAULT NULL COMMENT '运单货物明细ID',
  `batch_id` bigint DEFAULT NULL COMMENT '批量导入批次ID',
  `import_row_id` bigint DEFAULT NULL COMMENT '批量导入行ID',

  `exception_type` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL
    COMMENT '异常类型 AREA_NOT_RECOGNIZED/SERIES_NOT_RECOGNIZED/CONTRACT_NOT_FOUND/RULE_NOT_FOUND/RULE_CONFLICT/INVALID_QTY/WAYBILL_LOCKED/IMPORT_VALIDATE_FAILED',
  `exception_message` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '异常描述',
  `context_json` json DEFAULT NULL COMMENT '异常上下文',

  `status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT '处理状态 pending/processed/ignored',
  `processed_by` bigint DEFAULT NULL COMMENT '处理人',
  `processed_at` datetime DEFAULT NULL COMMENT '处理时间',
  `process_remark` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '处理备注',

  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_fce_status` (`status`),
  KEY `idx_fce_waybill` (`waybill_id`),
  KEY `idx_fce_type` (`exception_type`),
  KEY `idx_fce_batch` (`batch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运费计算异常表';
