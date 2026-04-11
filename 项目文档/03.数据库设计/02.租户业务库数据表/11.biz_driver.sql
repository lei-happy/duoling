--租户业务库数据库
-- 驾驶员信息表
CREATE TABLE `biz_driver` (
  `user_id` bigint DEFAULT NULL COMMENT '关联的用户ID',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号',
  `id_card` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证号',
  `gender` smallint NOT NULL COMMENT '性别 0-未知 1-男 2-女',
  `license_type` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '驾照类型（A1/A2/B1/B2/C1等）',
  `license_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '驾驶证号',
  `license_expire` date DEFAULT NULL COMMENT '驾驶证到期日',
  `qualification_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '从业资格证号',
  `qualification_expire` date DEFAULT NULL COMMENT '从业资格证到期日',
  `emergency_contact` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '紧急联系人',
  `emergency_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '紧急联系电话',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-在岗 2-休息 3-离职',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员信息表';