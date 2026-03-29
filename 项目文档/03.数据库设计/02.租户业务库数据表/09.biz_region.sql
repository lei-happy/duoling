--租户业务库数据库
-- 全国行政区域表
CREATE TABLE `biz_region` (
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '行政区划代码',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
  `parent_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '上级行政区划代码',
  `level` smallint NOT NULL COMMENT '层级 1-省 2-市 3-区/县',
  `sort_order` int NOT NULL COMMENT '排序号',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_biz_region_level` (`level`),
  KEY `idx_biz_region_parent_code` (`parent_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='全国行政区域表';