-- ============================================================
-- 智途(ZhiTu) 租户业务库建表 SQL 模板
-- 数据库名称：zt_biz_{tenant_code}（生产）/ zt_biz_{tenant_code}_ci（开发）
-- 新租户注册时，系统自动使用此模板创建表结构
-- ============================================================

-- 注意：实际部署时由后端 SQLAlchemy ORM 自动创建表结构
-- 此文件仅用于文档记录和手动初始化场景

-- 创建数据库（以示例租户 1001 为例）
-- CREATE DATABASE IF NOT EXISTS `zt_biz_1001`
--   CHARACTER SET utf8mb4
--   COLLATE utf8mb4_unicode_ci;
-- USE `zt_biz_1001`;

-- ============================================================
-- 1. 业务用户表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码（bcrypt哈希）',
  `real_name` VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  `gender` SMALLINT NOT NULL DEFAULT 0 COMMENT '性别 0-未知 1-男 2-女',
  `user_type` SMALLINT NOT NULL DEFAULT 1 COMMENT '用户类型 1-管理员 2-操作员 3-驾驶员',
  `department_id` BIGINT DEFAULT NULL COMMENT '所属部门ID',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='业务用户表';

-- ============================================================
-- 2. 角色表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_code` VARCHAR(50) NOT NULL COMMENT '角色编码',
  `role_name` VARCHAR(50) NOT NULL COMMENT '角色名称',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='业务角色表';

-- ============================================================
-- 3. 菜单表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_menu` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `parent_id` BIGINT NOT NULL DEFAULT 0 COMMENT '父级菜单ID（0为顶级）',
  `menu_name` VARCHAR(50) NOT NULL COMMENT '菜单名称',
  `menu_code` VARCHAR(100) DEFAULT NULL COMMENT '权限标识',
  `menu_type` SMALLINT NOT NULL DEFAULT 0 COMMENT '类型 0-目录 1-菜单 2-按钮',
  `path` VARCHAR(255) DEFAULT NULL COMMENT '路由路径',
  `component` VARCHAR(255) DEFAULT NULL COMMENT '组件路径',
  `icon` VARCHAR(100) DEFAULT NULL COMMENT '图标',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `visible` SMALLINT NOT NULL DEFAULT 1 COMMENT '是否可见 0-隐藏 1-显示',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='业务菜单表';

-- ============================================================
-- 4. 角色菜单关联表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_role_menu` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_id` BIGINT NOT NULL COMMENT '角色ID',
  `menu_id` BIGINT NOT NULL COMMENT '菜单ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_role_id` (`role_id`),
  KEY `idx_menu_id` (`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表';

-- ============================================================
-- 5. 用户角色关联表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_user_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `role_id` BIGINT NOT NULL COMMENT '角色ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- ============================================================
-- 6. 组织架构/部门表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_department` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `parent_id` BIGINT NOT NULL DEFAULT 0 COMMENT '上级部门ID（0为顶级）',
  `dept_name` VARCHAR(100) NOT NULL COMMENT '部门名称',
  `dept_code` VARCHAR(50) DEFAULT NULL COMMENT '部门编码',
  `leader` VARCHAR(50) DEFAULT NULL COMMENT '部门负责人',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='组织架构/部门表';

-- ============================================================
-- 7. 车辆信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_vehicle` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `plate_number` VARCHAR(20) NOT NULL COMMENT '车牌号',
  `vehicle_type` VARCHAR(50) DEFAULT NULL COMMENT '车辆类型',
  `brand` VARCHAR(50) DEFAULT NULL COMMENT '品牌',
  `model` VARCHAR(50) DEFAULT NULL COMMENT '车型',
  `color` VARCHAR(20) DEFAULT NULL COMMENT '颜色',
  `vin` VARCHAR(50) DEFAULT NULL COMMENT '车架号',
  `engine_number` VARCHAR(50) DEFAULT NULL COMMENT '发动机号',
  `buy_date` DATE DEFAULT NULL COMMENT '购买日期',
  `load_capacity` DECIMAL(10,2) DEFAULT NULL COMMENT '载重量（吨）',
  `volume_capacity` DECIMAL(10,2) DEFAULT NULL COMMENT '容积（立方米）',
  `insurance_expire` DATE DEFAULT NULL COMMENT '保险到期日',
  `annual_review_expire` DATE DEFAULT NULL COMMENT '年检到期日',
  `gps_device_id` VARCHAR(50) DEFAULT NULL COMMENT 'GPS设备ID',
  `department_id` BIGINT DEFAULT NULL COMMENT '所属部门ID',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-空闲 2-运输中 3-维修中',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plate_number` (`plate_number`),
  KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车辆信息表';

-- ============================================================
-- 8. 驾驶员信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_driver` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT DEFAULT NULL COMMENT '关联用户ID',
  `driver_name` VARCHAR(50) NOT NULL COMMENT '驾驶员姓名',
  `phone` VARCHAR(20) NOT NULL COMMENT '手机号',
  `id_card` VARCHAR(30) DEFAULT NULL COMMENT '身份证号',
  `license_type` VARCHAR(10) DEFAULT NULL COMMENT '驾照类型',
  `license_number` VARCHAR(50) DEFAULT NULL COMMENT '驾照号',
  `license_expire` DATE DEFAULT NULL COMMENT '驾照有效期',
  `qualification_cert` VARCHAR(50) DEFAULT NULL COMMENT '从业资格证号',
  `qualification_expire` DATE DEFAULT NULL COMMENT '从业资格证有效期',
  `emergency_contact` VARCHAR(50) DEFAULT NULL COMMENT '紧急联系人',
  `emergency_phone` VARCHAR(20) DEFAULT NULL COMMENT '紧急联系电话',
  `department_id` BIGINT DEFAULT NULL COMMENT '所属部门ID',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-空闲 2-任务中 3-休假',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='驾驶员信息表';

-- ============================================================
-- 9. 客户信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_customer` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `customer_name` VARCHAR(100) NOT NULL COMMENT '客户名称',
  `short_name` VARCHAR(50) DEFAULT NULL COMMENT '客户简称',
  `customer_type` SMALLINT NOT NULL DEFAULT 0 COMMENT '客户类型 0-发货方 1-收货方 2-两者兼有',
  `contact_person` VARCHAR(50) DEFAULT NULL COMMENT '联系人',
  `contact_phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '地址',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户信息表';

-- ============================================================
-- 10. 路线表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_route` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `route_name` VARCHAR(100) NOT NULL COMMENT '路线名称',
  `origin` VARCHAR(100) NOT NULL COMMENT '起点',
  `origin_address` VARCHAR(255) DEFAULT NULL COMMENT '起点详细地址',
  `destination` VARCHAR(100) NOT NULL COMMENT '终点',
  `destination_address` VARCHAR(255) DEFAULT NULL COMMENT '终点详细地址',
  `distance` DECIMAL(10,2) DEFAULT NULL COMMENT '距离（公里）',
  `estimated_hours` DECIMAL(6,2) DEFAULT NULL COMMENT '预计耗时（小时）',
  `waypoints` JSON DEFAULT NULL COMMENT '途经点（JSON数组）',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='路线表';

-- ============================================================
-- 11. 运单表
-- ============================================================
CREATE TABLE IF NOT EXISTS `biz_order` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `order_no` VARCHAR(50) NOT NULL COMMENT '运单编号',
  `route_id` BIGINT DEFAULT NULL COMMENT '路线ID',
  `vehicle_id` BIGINT DEFAULT NULL COMMENT '车辆ID',
  `driver_id` BIGINT DEFAULT NULL COMMENT '驾驶员ID',
  `customer_id` BIGINT DEFAULT NULL COMMENT '客户（发货方）ID',
  `receiver_id` BIGINT DEFAULT NULL COMMENT '收货方ID',

  `origin` VARCHAR(100) DEFAULT NULL COMMENT '起点',
  `origin_address` VARCHAR(255) DEFAULT NULL COMMENT '起点详细地址',
  `destination` VARCHAR(100) DEFAULT NULL COMMENT '终点',
  `destination_address` VARCHAR(255) DEFAULT NULL COMMENT '终点详细地址',

  `cargo_name` VARCHAR(100) DEFAULT NULL COMMENT '货物名称',
  `cargo_type` VARCHAR(50) DEFAULT NULL COMMENT '货物类型',
  `cargo_weight` DECIMAL(10,2) DEFAULT NULL COMMENT '货物重量（吨）',
  `cargo_volume` DECIMAL(10,2) DEFAULT NULL COMMENT '货物体积（立方米）',
  `cargo_quantity` INT DEFAULT NULL COMMENT '货物件数',

  `freight_amount` DECIMAL(12,2) DEFAULT NULL COMMENT '运费金额',
  `payment_method` SMALLINT NOT NULL DEFAULT 0 COMMENT '付款方式 0-月结 1-到付 2-现付',

  `status` SMALLINT NOT NULL DEFAULT 0 COMMENT '运单状态 0-待派车 1-已派车 2-运输中 3-已到达 4-已签收 5-已完成 6-已取消',
  `dispatch_time` DATETIME DEFAULT NULL COMMENT '派车时间',
  `depart_time` DATETIME DEFAULT NULL COMMENT '发车时间',
  `arrive_time` DATETIME DEFAULT NULL COMMENT '到达时间',
  `sign_time` DATETIME DEFAULT NULL COMMENT '签收时间',
  `complete_time` DATETIME DEFAULT NULL COMMENT '完成时间',

  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_by` BIGINT DEFAULT NULL COMMENT '创建人ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_vehicle_id` (`vehicle_id`),
  KEY `idx_driver_id` (`driver_id`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运单表';

-- ============================================================
-- 初始种子数据（新租户默认数据）
-- ============================================================

-- 默认管理员角色
INSERT INTO `biz_role` (`role_code`, `role_name`, `sort_order`, `status`) VALUES
('admin', '管理员', 0, 1),
('operator', '操作员', 10, 1),
('driver', '驾驶员', 20, 1);

-- 默认部门
INSERT INTO `biz_department` (`parent_id`, `dept_name`, `dept_code`, `sort_order`, `status`) VALUES
(0, '总公司', 'HQ', 0, 1),
(1, '运营部', 'OP', 0, 1),
(1, '车队部', 'FL', 10, 1),
(1, '财务部', 'FI', 20, 1);
