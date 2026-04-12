-- 租户业务库数据库
-- 驾驶员账户结算表（与 biz_driver 1:N 关联，一个驾驶员可有多个结算账户）
CREATE TABLE `biz_driver_account` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_id` bigint NOT NULL COMMENT '关联驾驶员ID',
  `enterprise_id` bigint DEFAULT NULL COMMENT '所属企业ID（经营主体）',
  `account_type` smallint NOT NULL COMMENT '账户类型 1-银行卡 2-油气款 3-积分',
  `account_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '账户名称',
  `account_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '账户号',
  `balance` decimal(12,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_driver_id` (`driver_id`),
  KEY `idx_enterprise_id` (`enterprise_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员账户结算表';
