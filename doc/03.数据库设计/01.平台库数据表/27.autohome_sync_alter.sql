-- 数据库名称：zt_platform
-- 说明：阶段2-汽车之家同步 — 平台品牌/车系外部 ID + 同步任务表
-- 执行前请备份；若列/表已存在请跳过对应语句

-- 1) 品牌：汽车之家品牌 ID（幂等同步）
ALTER TABLE `basicdata_brand`
  ADD COLUMN `autohome_brand_id` int unsigned DEFAULT NULL COMMENT '汽车之家品牌ID' AFTER `brand_id`,
  ADD UNIQUE KEY `uk_autohome_brand_id` (`autohome_brand_id`);

-- 2) 车系：汽车之家车系 ID
ALTER TABLE `basicdata_car_series`
  ADD COLUMN `autohome_series_id` int unsigned DEFAULT NULL COMMENT '汽车之家车系ID' AFTER `brand_id`,
  ADD UNIQUE KEY `uk_autohome_series_id` (`autohome_series_id`);

-- 3) 同步任务（运营后台「数据同步 → 汽车之家同步」）
CREATE TABLE IF NOT EXISTS `autohome_sync_job` (
  `job_id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `job_type` varchar(32) NOT NULL DEFAULT 'probe' COMMENT '任务类型：probe探测 full全量(预留)',
  `status` varchar(16) NOT NULL DEFAULT 'pending' COMMENT 'pending running success failed',
  `progress_pct` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '进度0-100',
  `payload_json` text COMMENT '任务参数JSON',
  `log_text` mediumtext COMMENT '执行日志',
  `error_message` varchar(2000) DEFAULT NULL COMMENT '失败原因',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`job_id`),
  KEY `idx_status_create` (`status`,`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='汽车之家数据同步任务';
