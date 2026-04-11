-- 租户业务库数据库
-- 客户表
CREATE TABLE `biz_customer` (
  `customer_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '客户编码',
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '客户名称',
  `short_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '客户简称',
  `customer_type` smallint NOT NULL DEFAULT '0' COMMENT '客户类型 0-主机厂 1-贸易商 2-经销商 3-个人 4-其他',
  `contact_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系人',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '地址',
  `settlement_type` smallint DEFAULT NULL COMMENT '结算方式 0-月结 1-票结 2-预付',
  `credit_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '统一社会信用代码',
  `status` smallint NOT NULL DEFAULT '1' COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customer_code` (`customer_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户表';

-- 升级脚本（已有租户库执行）
ALTER TABLE `biz_customer`
  ADD COLUMN `customer_code` varchar(50) DEFAULT NULL COMMENT '客户编码' AFTER `id`,
  ADD COLUMN `settlement_type` smallint DEFAULT NULL COMMENT '结算方式 0-月结 1-票结 2-预付' AFTER `address`,
  ADD COLUMN `credit_code` varchar(50) DEFAULT NULL COMMENT '统一社会信用代码' AFTER `settlement_type`,
  ADD UNIQUE KEY `uk_customer_code` (`customer_code`),
  MODIFY COLUMN `customer_type` smallint NOT NULL DEFAULT '0' COMMENT '客户类型 0-主机厂 1-贸易商 2-经销商 3-个人 4-其他';