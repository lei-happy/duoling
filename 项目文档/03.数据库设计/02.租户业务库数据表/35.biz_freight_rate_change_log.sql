-- 租户业务库数据库
-- 运价规则变更日志（每次 update/disable/delete/recreate 都写一条；保留全量字段快照）
CREATE TABLE `biz_freight_rate_change_log` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `rate_id` bigint NOT NULL COMMENT '运价规则ID',
  `contract_id` bigint NOT NULL COMMENT '合同ID',
  `rule_version_before` int DEFAULT NULL COMMENT '变更前版本号',
  `rule_version_after` int NOT NULL COMMENT '变更后版本号',
  `change_type` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '变更类型 create/update/disable/enable/delete',
  `snapshot_before` json DEFAULT NULL COMMENT '变更前完整字段快照',
  `snapshot_after` json DEFAULT NULL COMMENT '变更后完整字段快照',
  `operator_id` bigint DEFAULT NULL COMMENT '操作人用户ID',
  `affected_waybill_count` int DEFAULT NULL COMMENT '本次变更触发重算的运单数量',
  `remark` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_frcl_rate` (`rate_id`),
  KEY `idx_frcl_contract` (`contract_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运价规则变更日志表';
