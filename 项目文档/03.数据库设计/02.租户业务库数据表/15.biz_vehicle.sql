--租户业务库数据库
-- 车辆信息表
CREATE TABLE `biz_vehicle` (
  `plate_number` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '车牌号',
  `vehicle_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车辆类型（如重型货车、轻型货车等）',
  `brand` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '品牌',
  `model` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '型号',
  `color` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '颜色',
  `vin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车架号(VIN)',
  `engine_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '发动机号',
  `load_capacity` decimal(10,2) DEFAULT NULL COMMENT '核定载重（吨）',
  `volume_capacity` decimal(10,2) DEFAULT NULL COMMENT '核定容积（立方米）',
  `purchase_date` date DEFAULT NULL COMMENT '购买日期',
  `insurance_expire` date DEFAULT NULL COMMENT '保险到期日',
  `inspection_expire` date DEFAULT NULL COMMENT '年检到期日',
  `gps_device_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'GPS设备ID',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常 2-维修中 3-已报废',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `plate_number` (`plate_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车辆信息表';