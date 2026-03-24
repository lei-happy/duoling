--数据库名称：zt_platform
--表名称：sys_menu
CREATE TABLE `sys_menu` (
  `parent_id` bigint NOT NULL COMMENT '父级菜单ID（0为顶级）',
  `menu_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜单名称',
  `menu_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '权限标识',
  `menu_type` smallint NOT NULL COMMENT '类型 0-目录 1-菜单 2-按钮',
  `path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '路由路径',
  `component` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '组件路径',
  `icon` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '图标',
  `sort_order` smallint NOT NULL COMMENT '排序号',
  `visible` smallint NOT NULL COMMENT '是否可见 0-隐藏 1-显示',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `app_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '归属应用 platform/console/client',
  `feature_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联功能编码',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_feature_code` (`feature_code`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表'

