-- 租户业务库数据库
-- 运价明细表
CREATE TABLE `biz_freight_rate` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_id` bigint NOT NULL COMMENT '所属合同ID',
  `customer_id` bigint NOT NULL COMMENT '客户ID（冗余，加速计费查询）',
  `origin` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出发地',
  `origin_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出发地编码',
  `destination` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目的地',
  `destination_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目的地编码',
  `vehicle_brand` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品车品牌（可选，精细化定价）',
  `vehicle_model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品车车型（可选）',
  `billing_mode` smallint NOT NULL DEFAULT '0' COMMENT '计费模式 0-台单价 1-单公里单价 2-整单价格',
  `distance_km` decimal(10,2) DEFAULT NULL COMMENT '线路公里数（单公里计费时必填，客户标准）',
  `unit_price` decimal(12,2) NOT NULL COMMENT '单价（台单价:元/台 单公里:元/台/公里 整单:元/单）',
  `price_type` smallint NOT NULL DEFAULT '0' COMMENT '运价类型 0-明确运价 1-预估运价',
  `effective_date` date DEFAULT NULL COMMENT '明细生效日期',
  `expiry_date` date DEFAULT NULL COMMENT '明细失效日期',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-正常',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_contract_id` (`contract_id`),
  KEY `idx_rate_match` (`customer_id`, `origin_code`, `destination_code`, `status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运价明细表';

-- 升级脚本 v1（已有租户库 - 增加 price_type）
ALTER TABLE `biz_freight_rate`
  ADD COLUMN `price_type` smallint NOT NULL DEFAULT 0
  COMMENT '运价类型 0-明确运价 1-预估运价' AFTER `unit_price`;

-- 升级脚本 v2（已有租户库 - 增加计费模式与公里数）
ALTER TABLE `biz_freight_rate`
  ADD COLUMN `billing_mode` smallint NOT NULL DEFAULT 0
    COMMENT '计费模式 0-台单价 1-单公里单价 2-整单价格' AFTER `vehicle_model`,
  ADD COLUMN `distance_km` decimal(10,2) DEFAULT NULL
    COMMENT '线路公里数（单公里计费时必填，客户标准）' AFTER `billing_mode`;
