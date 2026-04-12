-- 平台主库数据库
-- 平台司机表（汇总各租户司机摘要）
CREATE TABLE `sys_driver` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `tenant_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '租户编码',
  `biz_driver_id` bigint NOT NULL COMMENT '租户库 biz_driver.id',
  `driver_code` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '司机编号',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '人事状态 0-冻结 1-在职 2-离职',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tenant_driver` (`tenant_code`, `biz_driver_id`),
  KEY `idx_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='平台司机表（汇总各租户司机摘要）';
