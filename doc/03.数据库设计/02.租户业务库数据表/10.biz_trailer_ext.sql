-- 租户业务库数据库
-- 挂车扩展信息表（与 biz_trailer 1:1 关联，存储可扩展的详细属性）
CREATE TABLE `biz_trailer_ext` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `trailer_id` bigint NOT NULL COMMENT '关联挂车ID',
  `trailer_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '挂车类型（数据字典 trailer_type）',
  `axle_count` smallint DEFAULT NULL COMMENT '轴数',
  `load_capacity` decimal(10,2) DEFAULT NULL COMMENT '核定载重（吨）',
  `volume_capacity` decimal(10,2) DEFAULT NULL COMMENT '核定容积（立方米）',
  `length` decimal(6,2) DEFAULT NULL COMMENT '车厢长度（米）',
  `width` decimal(6,2) DEFAULT NULL COMMENT '车厢宽度（米）',
  `height` decimal(6,2) DEFAULT NULL COMMENT '车厢高度（米）',
  `parking_spots` smallint DEFAULT NULL COMMENT '车位数',
  `purchase_date` date DEFAULT NULL COMMENT '购买日期',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_trailer_id` (`trailer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='挂车扩展信息表';
