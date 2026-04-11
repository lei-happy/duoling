-- 租户业务库数据库
-- 运价合同表
CREATE TABLE `biz_freight_contract` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contract_no` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '合同编号',
  `contract_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '合同名称',
  `customer_id` bigint NOT NULL COMMENT '客户ID',
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '客户名称（冗余）',
  `effective_date` date NOT NULL COMMENT '生效日期',
  `expiry_date` date NOT NULL COMMENT '失效日期',
  `status` smallint NOT NULL DEFAULT '0' COMMENT '状态 0-草稿 1-生效 2-已过期 3-已终止',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_contract_no` (`contract_no`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运价合同表';
