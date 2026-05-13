-- 租户业务库数据库
-- 运单运费计算结果明细（按 biz_waybill_cargo 一行一条）
CREATE TABLE `biz_waybill_freight_result_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `result_id` bigint NOT NULL COMMENT '计算结果主表ID',
  `waybill_id` bigint NOT NULL COMMENT '运单ID',
  `waybill_cargo_id` bigint NOT NULL COMMENT '运单货物明细ID',

  `brand_id` int unsigned DEFAULT NULL COMMENT '品牌ID',
  `series_id` int unsigned DEFAULT NULL COMMENT '车系ID',
  `vehicle_brand` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '品牌名称（冗余）',
  `vehicle_model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车型名称（冗余）',
  `quantity` int NOT NULL DEFAULT '0' COMMENT '台数',

  `matched_contract_id` bigint DEFAULT NULL COMMENT '匹配的合同ID',
  `matched_rule_id` bigint DEFAULT NULL COMMENT '匹配的运价规则ID',
  `matched_rule_version` int DEFAULT NULL COMMENT '匹配规则版本号',

  `origin_match_region_id` bigint DEFAULT NULL COMMENT '实际命中的出发地行政区ID',
  `origin_match_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '出发地命中层级 province/city/district/custom',
  `destination_match_region_id` bigint DEFAULT NULL COMMENT '实际命中的目的地行政区ID',
  `destination_match_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '目的地命中层级',
  `direction` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '方向 forward/backward',
  `model_match_type` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车型命中层级 series/brand/general',

  `unit_price` decimal(12,2) DEFAULT NULL COMMENT '单价',
  `billing_mode` smallint DEFAULT NULL COMMENT '计费模式快照',
  `distance_km` decimal(10,2) DEFAULT NULL COMMENT '公里数快照',
  `amount` decimal(12,2) NOT NULL DEFAULT '0.00' COMMENT '本明细计算金额',

  `match_score` int DEFAULT NULL COMMENT '匹配综合评分',
  `match_trace_json` json DEFAULT NULL COMMENT '匹配过程留痕',

  `calc_status` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '计算状态 success/exception',
  `error_type` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '异常类型',
  `error_message` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '异常描述',

  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_wfrd_result` (`result_id`),
  KEY `idx_wfrd_waybill` (`waybill_id`),
  KEY `idx_wfrd_cargo` (`waybill_cargo_id`),
  KEY `idx_wfrd_rule` (`matched_rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运单运费计算结果明细表';
