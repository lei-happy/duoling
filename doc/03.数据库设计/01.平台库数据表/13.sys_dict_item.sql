--数据库名称：zt_platform
--表名称：sys_dict_item
CREATE TABLE `sys_dict_item` (
  `dict_id` bigint NOT NULL COMMENT '字典ID',
  `dict_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字典编码',
  `item_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字典项名称',
  `item_value` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字典项值',
  `sort_order` smallint NOT NULL COMMENT '排序号',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `ix_sys_dict_item_dict_id` (`dict_id`),
  KEY `ix_sys_dict_item_dict_code` (`dict_code`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据字典项表'

