-- 租户业务库数据库
-- 驾驶员运营属性表（与 biz_driver 1:1 关联，存储车队归属、司机类型、运营状态等）
CREATE TABLE `biz_driver_operation` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `driver_id` bigint NOT NULL COMMENT '关联驾驶员ID',
  `department_id` bigint DEFAULT NULL COMMENT '所属车队/部门ID，关联biz_department.id',
  `driver_type` smallint DEFAULT NULL COMMENT '司机类型 1-自有 2-外协 3-临时',
  `resident_areas` json DEFAULT NULL COMMENT '常驻区域，存储省市代码数组',
  `common_routes` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '常跑线路（文本描述）',
  `operation_status` smallint NOT NULL DEFAULT 1 COMMENT '运营状态 1-可接单 2-忙碌 3-休假 4-停运',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` smallint NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_driver_id` (`driver_id`),
  KEY `idx_department_id` (`department_id`),
  KEY `idx_operation_status` (`operation_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员运营属性表';
