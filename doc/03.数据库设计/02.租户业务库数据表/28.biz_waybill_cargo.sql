-- 租户业务库数据库
-- 运单货物明细表（一单多品牌/车型）
CREATE TABLE `biz_waybill_cargo` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `waybill_id` bigint NOT NULL COMMENT '运单ID',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序序号',
  `vehicle_brand` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品车品牌',
  `vehicle_model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '商品车车型',
  `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID（biz_vehicle_brand.brand_id）',
  `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID（biz_vehicle_series.series_id）',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '台数',
  `cargo_version` int NOT NULL DEFAULT '1' COMMENT '明细版本号',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_waybill_id` (`waybill_id`),
  KEY `idx_cargo_brand` (`brand_id`),
  KEY `idx_cargo_series` (`series_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运单货物明细表';

-- 升级脚本 v2（已有租户库 - 增加车型标准化与版本号字段）
ALTER TABLE `biz_waybill_cargo`
  ADD COLUMN `brand_id` int unsigned DEFAULT NULL COMMENT '标准品牌ID' AFTER `vehicle_model`,
  ADD COLUMN `series_id` int unsigned DEFAULT NULL COMMENT '标准车系ID' AFTER `brand_id`,
  ADD COLUMN `cargo_version` int NOT NULL DEFAULT 1 COMMENT '明细版本号' AFTER `quantity`,
  ADD INDEX `idx_cargo_brand` (`brand_id`),
  ADD INDEX `idx_cargo_series` (`series_id`);

-- 历史数据回填：每条运单生成一行明细（与主表品牌/车型/台数对齐）
INSERT INTO `biz_waybill_cargo` (`waybill_id`, `sort_order`, `vehicle_brand`, `vehicle_model`, `quantity`, `created_at`, `updated_at`, `is_deleted`)
SELECT `id`, 0, `vehicle_brand`, `vehicle_model`, `quantity`, NOW(), NOW(), 0
FROM `biz_waybill` AS `w`
WHERE `w`.`is_deleted` = 0
  AND NOT EXISTS (
    SELECT 1 FROM `biz_waybill_cargo` AS `c`
    WHERE `c`.`waybill_id` = `w`.`id` AND `c`.`is_deleted` = 0
  );
