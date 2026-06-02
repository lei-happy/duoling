--数据库名称：zt_platform
--表名称：region_sync_job
CREATE TABLE `region_sync_job` (
  `job_id` bigint NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `status` varchar(16) NOT NULL DEFAULT 'pending' COMMENT '状态 pending/running/success/failed',
  `progress_pct` int NOT NULL DEFAULT '0' COMMENT '进度0-100',
  `payload_json` text COMMENT '任务参数 JSON',
  `log_text` text COMMENT '执行日志',
  `error_message` varchar(2000) DEFAULT NULL COMMENT '错误信息',
  `total_count` int DEFAULT NULL COMMENT '写入条数',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='行政区域高德同步任务';
