--数据库名称：zt_platform
--表名称：basicdata_brand
--说明：品牌信息表
CREATE TABLE `basicdata_brand` (
  `brand_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '品牌ID（主键）',
  `brand_logo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '品牌Logo路径或链接',
  `brand_name_cn` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '品牌中文名称',
  `brand_country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '品牌国别',
  `brand_introduce` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '品牌介绍',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`brand_id`)
) ENGINE=InnoDB AUTO_INCREMENT=624 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='品牌信息表';