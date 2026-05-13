-- 租户业务库数据库
-- 运单批量导入：批次表 + 行明细表

CREATE TABLE `biz_waybill_import_batch` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '原始文件名',
  `total_count` int NOT NULL DEFAULT '0' COMMENT '总行数',
  `success_count` int NOT NULL DEFAULT '0' COMMENT '导入成功行数',
  `fail_count` int NOT NULL DEFAULT '0' COMMENT '校验失败行数',
  `calc_success_count` int NOT NULL DEFAULT '0' COMMENT '计算成功数',
  `calc_exception_count` int NOT NULL DEFAULT '0' COMMENT '计算异常数',
  `status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending'
    COMMENT '状态 pending/importing/imported/calculating/done/failed',
  `error_message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '批次级错误',
  `created_by` bigint DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_wib_status` (`status`),
  KEY `idx_wib_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运单导入批次表';

CREATE TABLE `biz_waybill_import_row` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `batch_id` bigint NOT NULL COMMENT '批次ID',
  `row_no` int NOT NULL COMMENT '原 Excel 行号',
  `raw_data_json` json DEFAULT NULL COMMENT '原始行数据 JSON',
  `validate_status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT '校验状态 pending/success/failed',
  `validate_message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '校验信息',
  `waybill_id` bigint DEFAULT NULL COMMENT '生成的运单ID',
  `calc_status` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '该行运单的最新计算状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_wir_batch` (`batch_id`),
  KEY `idx_wir_validate` (`validate_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运单导入行明细表';
