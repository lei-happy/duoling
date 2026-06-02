--数据库名称：zt_platform
--表名称：sys_regions
CREATE TABLE `sys_regions` (
  `code` bigint unsigned NOT NULL COMMENT '区划代码',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '名称',
  `short_name` varchar(255) DEFAULT NULL COMMENT '简称',
  `level` tinyint(1) NOT NULL COMMENT '1级：省、直辖市、自治区\r\n2级：地级市\r\n3级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区\r\n4级：镇、乡、民族乡、县辖区、街道',
  `pcode` bigint DEFAULT NULL COMMENT '父级区划代码',
  `citycode` varchar(20) DEFAULT NULL COMMENT '高德 citycode',
  `longitude` decimal(10,6) DEFAULT NULL COMMENT '经度（东经为正，来自高德 center）',
  `latitude` decimal(10,6) DEFAULT NULL COMMENT '纬度（北纬为正，来自高德 center）',
  `category` int DEFAULT NULL COMMENT '城乡分类 (1开头是城镇，2开头是乡村)\r\n111表示主城区；\r\n112表示城乡接合区；\r\n121表示镇中心区；\r\n122表示镇乡接合区；\r\n123表示特殊区域；\r\n210表示乡中心区；\r\n220表示村庄',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序号',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态（0停用，1正常）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除(0未删除，1已删除)',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`code`),
  KEY `name` (`name`),
  KEY `level` (`level`),
  KEY `pcode` (`pcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='全国行政区域表';

-- 增量变更（已有表执行）
-- ALTER TABLE `sys_regions` ADD COLUMN `citycode` varchar(20) DEFAULT NULL COMMENT '高德 citycode' AFTER `pcode`;
-- ALTER TABLE `sys_regions` ADD COLUMN `longitude` decimal(10,6) DEFAULT NULL COMMENT '经度（东经为正）' AFTER `citycode`;
-- ALTER TABLE `sys_regions` ADD COLUMN `latitude` decimal(10,6) DEFAULT NULL COMMENT '纬度（北纬为正）' AFTER `longitude`;
-- ALTER TABLE `sys_regions` ADD COLUMN `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序号' AFTER `category`;
-- ALTER TABLE `sys_regions` ADD COLUMN `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态（0停用，1正常）' AFTER `sort_order`;
