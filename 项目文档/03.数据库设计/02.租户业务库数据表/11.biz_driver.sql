-- 租户业务库数据库
-- 驾驶员核心身份表（重构：原单表拆分为核心表+资质表+运营表+账户表）
CREATE TABLE `biz_driver` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_code` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '司机编号（业务唯一标识，如D20260001）',
  `user_id` bigint DEFAULT NULL COMMENT '关联的用户ID',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `gender` smallint NOT NULL DEFAULT 0 COMMENT '性别 0-未知 1-男 2-女',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号',
  `id_card` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证号',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `emergency_contact` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '紧急联系人姓名',
  `emergency_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '紧急联系人电话',
  `home_address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '家庭住址',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '人事状态 0-冻结 1-在职 2-离职',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_driver_code` (`driver_code`),
  KEY `idx_phone` (`phone`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员核心身份表';
