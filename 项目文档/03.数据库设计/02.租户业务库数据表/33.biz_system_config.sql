-- 租户业务库数据库
-- 系统配置表（core 层，注册即创建）
CREATE TABLE `biz_system_config` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `config_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置值',
  `config_group` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '分组',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '说明',
  `value_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'string' COMMENT '值类型 string/number/boolean/enum',
  `default_value` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '默认值',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 初始配置数据
INSERT INTO `biz_system_config` (`config_key`, `config_value`, `config_group`, `description`, `value_type`, `default_value`) VALUES
('waybill.freight_calc_mode', 'auto_preferred', 'waybill', '运费计算模式：auto_required-强制自动计费 auto_preferred-优先自动允许手动 manual_only-仅手动', 'enum', 'auto_preferred');
