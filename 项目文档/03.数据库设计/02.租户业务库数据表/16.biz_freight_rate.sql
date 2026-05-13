-- 租户业务库数据库
-- 运价明细表
CREATE TABLE `biz_freight_rate` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_id` bigint NOT NULL COMMENT '所属合同ID',
  `customer_id` bigint NOT NULL COMMENT '客户ID（冗余，加速计费查询）',
  `origin` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出发地',
  `origin_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出发地编码',
  `origin_region_id` bigint DEFAULT NULL COMMENT '出发地行政区ID（biz_region.id）',
  `destination` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目的地',
  `destination_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目的地编码',
  `destination_region_id` bigint DEFAULT NULL COMMENT '目的地行政区ID（biz_region.id）',
  `vehicle_brand` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品车品牌（可选，精细化定价）',
  `vehicle_model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品车车型（可选）',
  `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID',
  `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID',
  `match_type` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'series' COMMENT '车型匹配类型 series/brand/general',
  `billing_mode` smallint NOT NULL DEFAULT '0' COMMENT '计费模式 0-台单价 1-单公里单价 2-整单价格',
  `distance_km` decimal(10,2) DEFAULT NULL COMMENT '线路公里数（单公里计费时必填，客户标准）',
  `unit_price` decimal(12,2) NOT NULL COMMENT '单价（台单价:元/台 单公里:元/台/公里 整单:元/单）',
  `min_amount` decimal(12,2) DEFAULT NULL COMMENT '最低运费',
  `price_type` smallint NOT NULL DEFAULT '0' COMMENT '运价类型 0-明确运价 1-预估运价',
  `is_bidirectional` smallint NOT NULL DEFAULT '0' COMMENT '是否双向 0-否 1-是',
  `priority` int NOT NULL DEFAULT '0' COMMENT '人工优先级（数值越大越优先）',
  `effective_date` date DEFAULT NULL COMMENT '明细生效日期',
  `expiry_date` date DEFAULT NULL COMMENT '明细失效日期',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-正常',
  `rule_version` int NOT NULL DEFAULT '1' COMMENT '规则版本号',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_contract_id` (`contract_id`),
  KEY `idx_rate_match` (`customer_id`, `origin_code`, `destination_code`, `status`, `is_deleted`),
  KEY `idx_rate_match_region` (`customer_id`, `origin_region_id`, `destination_region_id`, `status`, `is_deleted`)
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

-- 升级脚本 v3（已有租户库 - 计费引擎升级所需的标准化与扩展字段）
ALTER TABLE `biz_freight_rate`
  ADD COLUMN `origin_region_id` bigint DEFAULT NULL COMMENT '出发地行政区ID' AFTER `origin_code`,
  ADD COLUMN `destination_region_id` bigint DEFAULT NULL COMMENT '目的地行政区ID' AFTER `destination_code`,
  ADD COLUMN `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID' AFTER `vehicle_model`,
  ADD COLUMN `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID' AFTER `brand_id`,
  ADD COLUMN `match_type` varchar(16) NOT NULL DEFAULT 'series' COMMENT '车型匹配类型 series/brand/general' AFTER `series_id`,
  ADD COLUMN `min_amount` decimal(12,2) DEFAULT NULL COMMENT '最低运费' AFTER `unit_price`,
  ADD COLUMN `is_bidirectional` smallint NOT NULL DEFAULT 0 COMMENT '是否双向 0-否 1-是' AFTER `price_type`,
  ADD COLUMN `priority` int NOT NULL DEFAULT 0 COMMENT '人工优先级' AFTER `is_bidirectional`,
  ADD COLUMN `rule_version` int NOT NULL DEFAULT 1 COMMENT '规则版本号' AFTER `status`,
  ADD INDEX `idx_rate_match_region` (`customer_id`, `origin_region_id`, `destination_region_id`, `status`, `is_deleted`);
