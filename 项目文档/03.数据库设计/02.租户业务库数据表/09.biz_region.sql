--租户业务库数据库
-- 行政区域表（含系统标准地区 + 企业自定义地区）
CREATE TABLE `biz_region` (
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '行政区划代码',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
  `parent_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '上级行政区划代码',
  `level` smallint NOT NULL COMMENT '层级 1-省 2-市 3-区/县 4-自定义子级',
  `sort_order` int NOT NULL COMMENT '排序号',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `source` smallint NOT NULL DEFAULT '0' COMMENT '数据来源 0-系统初始化 1-企业自定义',
  `created_by` bigint DEFAULT NULL COMMENT '创建人用户ID',
  `longitude` decimal(10,6) DEFAULT NULL COMMENT '经度（东经为正）',
  `latitude` decimal(10,6) DEFAULT NULL COMMENT '纬度（北纬为正）',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_biz_region_level` (`level`),
  KEY `idx_biz_region_parent_code` (`parent_code`),
  KEY `idx_biz_region_source` (`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行政区域表';
