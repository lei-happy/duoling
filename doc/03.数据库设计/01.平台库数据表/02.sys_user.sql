--数据库名称：zt_platform
--表名称：sys_user
--说明：全平台用户唯一标识为本表主键 id，无需也不应再增加 user_id 列；
--      关联表（如 sys_user_tenant、sys_user_role）中的 user_id 外键均指向本表 id。
--      登录标识为手机号（phone），全平台唯一。
CREATE TABLE `sys_user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID，即平台用户唯一标识（接口与 JWT 载荷中的 user_id / userId）',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号（登录标识，全平台唯一）',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码（bcrypt哈希）',
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '真实姓名',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `gender` smallint NOT NULL COMMENT '性别 0-未知 1-男 2-女',
  `user_type` smallint NOT NULL COMMENT '用户类型 0-平台管理员 1-租户管理员 2-租户用户 3-驾驶员',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `force_change_pwd` smallint NOT NULL DEFAULT '0' COMMENT '是否强制修改密码 0-否 1-是',
  `theme_config` json DEFAULT NULL COMMENT '用户主题配置（JSON格式）',
  `workplace_config` json DEFAULT NULL COMMENT '工作台个性化配置（JSON格式）',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='平台用户表';

