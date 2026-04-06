--数据库名称：zt_platform
--表名称：basicdata_car_series
--说明：车系信息表
CREATE TABLE `basicdata_car_series` (
  `series_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '车系ID（主键）',
  `brand_id` int unsigned NOT NULL COMMENT '关联品牌ID（外键）',
  `price` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '价格范围',
  `series_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '车系图片（路径或链接）',
  `series_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '车系名称',
  `energy_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '能源类型（如汽油、柴油、纯电动、混合动力等）',
  `length_mm` int unsigned DEFAULT NULL COMMENT '车长(mm)',
  `width_mm` int unsigned DEFAULT NULL COMMENT '车宽(mm)',
  `height_mm` int unsigned DEFAULT NULL COMMENT '车高(mm)',
  `wheelbase_mm` int unsigned DEFAULT NULL COMMENT '轴距(mm)',
  `front_track_mm` int unsigned DEFAULT NULL COMMENT '前轮距(mm)',
  `rear_track_mm` int unsigned DEFAULT NULL COMMENT '后轮距(mm)',
  `approach_angle` decimal(5,2) DEFAULT NULL COMMENT '接近角(°)',
  `departure_angle` decimal(5,2) DEFAULT NULL COMMENT '离去角(°)',
  `curb_weight_kg` int unsigned DEFAULT NULL COMMENT '整备质量(kg)',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`series_id`),
  KEY `idx_brand_id` (`brand_id`),
  CONSTRAINT `basicdata_car_series_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `basicdata_brand` (`brand_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3391 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='车系信息表';