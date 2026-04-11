--租户业务库数据库
-- 企业用户表
CREATE TABLE `biz_user` (
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号（登录标识，租户内唯一）',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码（bcrypt哈希）',
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '真实姓名',
  `nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '昵称',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `gender` smallint NOT NULL COMMENT '性别 0-未知 1-男 2-女',
  `birthday` date DEFAULT NULL COMMENT '出生日期',
  `user_type` smallint NOT NULL COMMENT '用户类型 1-管理员 2-操作员 3-驾驶员',
  `department_id` bigint DEFAULT NULL COMMENT '所属部门ID',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='企业用户表';