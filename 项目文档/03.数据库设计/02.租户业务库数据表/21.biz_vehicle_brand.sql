--租户业务库
-- 品牌信息表（开户时从平台 basicdata_brand 同步，列定义与平台一致）
CREATE TABLE `biz_vehicle_brand` (
  `brand_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '品牌ID（主键）',
  `brand_logo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '品牌Logo路径或链接',
  `brand_name_cn` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '品牌中文名称',
  `brand_country` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '品牌国别',
  `brand_introduce` text COLLATE utf8mb4_unicode_ci COMMENT '品牌介绍',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`brand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='品牌信息表';
