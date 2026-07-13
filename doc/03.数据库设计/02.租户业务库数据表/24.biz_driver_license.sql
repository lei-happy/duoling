-- 租户业务库数据库
-- 驾驶员资质信息表（与 biz_driver 1:1 关联，存储驾驶证和从业资格证信息）
CREATE TABLE `biz_driver_license` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_id` bigint NOT NULL COMMENT '关联驾驶员ID',
  `license_type` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '驾驶证类型（A1/A2/B1/B2/C1等）',
  `license_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '驾驶证号',
  `license_expire` date DEFAULT NULL COMMENT '驾驶证有效期',
  `qualification_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '从业资格证号',
  `qualification_expire` date DEFAULT NULL COMMENT '从业资格证有效期',
  `license_photo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '驾驶证照片URL',
  `qualification_photo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '从业资格证照片URL',
  `id_card_front_photo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证正面照片URL',
  `id_card_back_photo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证反面照片URL',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_driver_id` (`driver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员资质信息表';
