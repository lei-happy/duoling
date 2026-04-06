--租户业务库
-- 汽车经销商信息表（开户时从平台 basicdata_dealer_info 同步，列定义与平台一致）
CREATE TABLE `biz_dealer` (
  `dealer_id` bigint NOT NULL AUTO_INCREMENT COMMENT '经销商ID，主键，自增',
  `dealer_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '经销商名称',
  `dealer_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '经销商类型（例如4S店、二级经销商等）',
  `main_brand` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '主营品牌',
  `province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '所在省',
  `city` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '所在市',
  `address_detail` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '地址详情',
  `longitude` decimal(10,6) DEFAULT NULL COMMENT '经度坐标',
  `latitude` decimal(10,6) DEFAULT NULL COMMENT '纬度坐标',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`dealer_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='汽车经销商信息表';
