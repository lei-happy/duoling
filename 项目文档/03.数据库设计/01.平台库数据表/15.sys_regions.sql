--数据库名称：zt_platform
--表名称：sys_regions
CREATE TABLE `sys_regions` (
  `code` bigint unsigned NOT NULL COMMENT '区划代码',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '名称',
  `short_name` varchar(255) DEFAULT NULL COMMENT '简称',
  `level` tinyint(1) NOT NULL COMMENT '1级：省、直辖市、自治区\r\n2级：地级市\r\n3级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区\r\n4级：镇、乡、民族乡、县辖区、街道\r\n5级：村、居委会',
  `pcode` bigint DEFAULT NULL COMMENT '父级区划代码',
  `category` int DEFAULT NULL COMMENT '城乡分类 (1开头是城镇，2开头是乡村)\r\n111表示主城区；\r\n112表示城乡接合区；\r\n121表示镇中心区；\r\n122表示镇乡接合区；\r\n123表示特殊区域；\r\n210表示乡中心区；\r\n220表示村庄',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除(0未删除，1已删除)',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`code`),
  KEY `name` (`name`),
  KEY `level` (`level`),
  KEY `pcode` (`pcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='全国行政区域表';
