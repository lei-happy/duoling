-- 租户业务库数据库
-- 驾驶员常跑线路表（与 biz_driver 1:N 关联，一个司机可关联多条常跑线路）
CREATE TABLE `biz_driver_route` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_id` bigint NOT NULL COMMENT '关联驾驶员ID',
  `origin_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出发地区域编码',
  `origin_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出发地名称',
  `dest_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目的地区域编码',
  `dest_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目的地名称',
  `status` smallint NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_driver_id` (`driver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员常跑线路表';
