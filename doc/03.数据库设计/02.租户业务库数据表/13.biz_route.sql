--租户业务库数据库
-- 路线表
CREATE TABLE `biz_route` (
  `route_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '路线名称',
  `route_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '路线编码',
  `origin` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '起点',
  `destination` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '终点',
  `distance` decimal(10,2) DEFAULT NULL COMMENT '距离（公里）',
  `estimated_hours` decimal(5,1) DEFAULT NULL COMMENT '预计耗时（小时）',
  `waypoints` text COLLATE utf8mb4_unicode_ci COMMENT '途经点（JSON数组）',
  `route_polyline` text COLLATE utf8mb4_unicode_ci COMMENT '驾车路线折线 JSON：[[lng,lat],...]，供地图预览',
  `status` smallint NOT NULL COMMENT '状态 0-停用 1-正常',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT '0' COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `route_code` (`route_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='路线表';