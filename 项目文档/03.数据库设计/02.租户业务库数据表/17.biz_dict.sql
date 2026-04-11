--租户业务库数据库
-- 数据字典表
CREATE TABLE `biz_dict` (
  `dict_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字典编码',
  `dict_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字典名称',
  `sort_order` smallint NOT NULL COMMENT '排序号',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `dict_code` (`dict_code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据字典表';