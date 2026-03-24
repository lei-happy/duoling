-- ============================================================
-- 智途(ZhiTu) 平台主库建表 SQL
-- 数据库名称：zt_platform（生产）/ zt_platform_ci（开发）
-- ============================================================

-- 创建数据库（根据环境修改名称）
CREATE DATABASE IF NOT EXISTS `zt_platform`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `zt_platform`;

-- ============================================================
-- 1. 租户/企业信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_tenant` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `tenant_code` VARCHAR(32) NOT NULL COMMENT '租户编码（唯一标识）',
  `tenant_name` VARCHAR(100) NOT NULL COMMENT '企业名称',
  `short_name` VARCHAR(50) DEFAULT NULL COMMENT '企业简称',
  `contact_person` VARCHAR(50) DEFAULT NULL COMMENT '联系人',
  `contact_phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `contact_email` VARCHAR(100) DEFAULT NULL COMMENT '联系邮箱',
  `province` VARCHAR(50) DEFAULT NULL COMMENT '省份',
  `city` VARCHAR(50) DEFAULT NULL COMMENT '城市',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
  `logo` VARCHAR(255) DEFAULT NULL COMMENT '企业Logo URL',
  `license_no` VARCHAR(100) DEFAULT NULL COMMENT '营业执照号',
  `status` SMALLINT NOT NULL DEFAULT 2 COMMENT '状态 0-停用 1-正常 2-待审核 3-已过期',
  `db_name` VARCHAR(100) DEFAULT NULL COMMENT '租户数据库名称',
  `db_initialized` SMALLINT NOT NULL DEFAULT 0 COMMENT '数据库是否已初始化 0-否 1-是',
  `expire_time` DATETIME DEFAULT NULL COMMENT '授权到期时间',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `source_channel` VARCHAR(50) DEFAULT NULL COMMENT '来源渠道: website-官网注册 console-后台录入 referral-企业推荐',
  `referrer_code` VARCHAR(50) DEFAULT NULL COMMENT '推荐人企业编码（来源为referral时记录）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='租户/企业信息表';

-- ============================================================
-- 2. 平台用户表
-- 说明：用户唯一性由 phone 保证，用户与企业的关联通过 sys_user_tenant 表实现
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码（bcrypt哈希）',
  `real_name` VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号（唯一）',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  `gender` SMALLINT NOT NULL DEFAULT 0 COMMENT '性别 0-未知 1-男 2-女',
  `user_type` SMALLINT NOT NULL DEFAULT 2 COMMENT '用户类型 0-平台管理员（其余值仅做默认标记，实际角色由 sys_user_tenant 决定）',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `force_change_pwd` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否强制修改密码 0-否 1-是',
  `theme_config` JSON DEFAULT NULL COMMENT '用户主题配置（JSON格式）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='平台用户表';

-- ============================================================
-- 2.1 用户企业关联表
-- 说明：同一用户可关联多个企业，每个企业中有独立的角色类型和状态
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_user_tenant` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `tenant_code` VARCHAR(32) NOT NULL COMMENT '企业编码',
  `user_type` SMALLINT NOT NULL DEFAULT 2 COMMENT '角色类型 1-租户管理员 2-租户用户 3-驾驶员',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_tenant` (`user_id`, `tenant_code`),
  KEY `idx_tenant_code` (`tenant_code`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户企业关联表';

-- ============================================================
-- 3. 角色表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_code` VARCHAR(50) NOT NULL COMMENT '角色编码',
  `role_name` VARCHAR(50) NOT NULL COMMENT '角色名称',
  `role_type` SMALLINT NOT NULL DEFAULT 0 COMMENT '角色类型 0-平台角色 1-租户角色',
  `tenant_code` VARCHAR(32) DEFAULT NULL COMMENT '所属租户编码（平台角色为空）',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`),
  KEY `idx_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- ============================================================
-- 4. 菜单表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_menu` (
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
  `app_type` VARCHAR(20) NOT NULL DEFAULT 'platform' COMMENT '归属应用 platform/console/client',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';

-- ============================================================
-- 5. 角色菜单关联表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_role_menu` (
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
-- 6. 用户角色关联表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_user_role` (
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
-- 7. 产品版本表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_product_version` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `version_code` VARCHAR(50) NOT NULL COMMENT '版本编码',
  `version_name` VARCHAR(100) NOT NULL COMMENT '版本名称',
  `description` TEXT DEFAULT NULL COMMENT '版本说明',
  `features` JSON DEFAULT NULL COMMENT '功能清单（JSON格式）',
  `max_users` INT NOT NULL DEFAULT 10 COMMENT '最大用户数',
  `max_vehicles` INT NOT NULL DEFAULT 50 COMMENT '最大车辆数',
  `price` VARCHAR(50) DEFAULT NULL COMMENT '价格',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_version_code` (`version_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品版本表';

-- ============================================================
-- 8. 租户产品版本授权表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_tenant_product` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `tenant_id` BIGINT NOT NULL COMMENT '租户ID',
  `tenant_code` VARCHAR(32) NOT NULL COMMENT '租户编码',
  `version_id` BIGINT NOT NULL COMMENT '产品版本ID',
  `version_code` VARCHAR(50) NOT NULL COMMENT '产品版本编码',
  `start_time` DATETIME DEFAULT NULL COMMENT '授权开始时间',
  `end_time` DATETIME DEFAULT NULL COMMENT '授权到期时间',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_id` (`tenant_id`),
  KEY `idx_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='租户产品版本授权表';

-- ============================================================
-- 9. 数据字典表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_dict` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `dict_code` VARCHAR(100) NOT NULL COMMENT '字典编码',
  `dict_name` VARCHAR(100) NOT NULL COMMENT '字典名称',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dict_code` (`dict_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据字典表';

-- ============================================================
-- 10. 数据字典项表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_dict_item` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `dict_id` BIGINT NOT NULL COMMENT '字典ID',
  `dict_code` VARCHAR(100) NOT NULL COMMENT '字典编码',
  `item_name` VARCHAR(100) NOT NULL COMMENT '字典项名称',
  `item_value` VARCHAR(255) NOT NULL COMMENT '字典项值',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-正常',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_dict_id` (`dict_id`),
  KEY `idx_dict_code` (`dict_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据字典项表';

-- ============================================================
-- 11. 意见反馈表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_feedback` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `tenant_code` VARCHAR(32) DEFAULT NULL COMMENT '租户编码',
  `user_id` BIGINT NOT NULL COMMENT '反馈用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '反馈标题',
  `content` TEXT NOT NULL COMMENT '反馈内容',
  `feedback_type` SMALLINT NOT NULL DEFAULT 0 COMMENT '反馈类型 0-建议 1-bug 2-投诉 3-其他',
  `status` SMALLINT NOT NULL DEFAULT 0 COMMENT '处理状态 0-待处理 1-处理中 2-已解决 3-已关闭',
  `reply` TEXT DEFAULT NULL COMMENT '回复内容',
  `images` TEXT DEFAULT NULL COMMENT '截图URL列表（JSON数组）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='意见反馈表';

-- ============================================================
-- 12. 产品更新日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_changelog` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `version` VARCHAR(50) NOT NULL COMMENT '版本号（如 v1.2.0）',
  `title` VARCHAR(200) NOT NULL COMMENT '更新标题',
  `content` TEXT DEFAULT NULL COMMENT '更新内容（Markdown 格式）',
  `release_date` DATE NOT NULL COMMENT '发布日期',
  `sort_order` SMALLINT NOT NULL DEFAULT 0 COMMENT '排序号（越大越靠前）',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-停用 1-已发布',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_release_date` (`release_date`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品更新日志表';

-- ============================================================
-- 13. 操作日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS `sys_operation_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT DEFAULT NULL COMMENT '操作用户ID',
  `username` VARCHAR(50) DEFAULT NULL COMMENT '操作用户名',
  `tenant_code` VARCHAR(32) DEFAULT NULL COMMENT '租户编码',
  `module` VARCHAR(50) DEFAULT NULL COMMENT '操作模块',
  `action` VARCHAR(50) DEFAULT NULL COMMENT '操作类型',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '操作描述',
  `request_method` VARCHAR(10) DEFAULT NULL COMMENT '请求方法',
  `request_url` VARCHAR(255) DEFAULT NULL COMMENT '请求URL',
  `request_body` TEXT DEFAULT NULL COMMENT '请求参数',
  `response_body` TEXT DEFAULT NULL COMMENT '响应结果',
  `ip` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
  `elapsed_time` INT DEFAULT NULL COMMENT '耗时（毫秒）',
  `status` SMALLINT NOT NULL DEFAULT 1 COMMENT '状态 0-失败 1-成功',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` SMALLINT NOT NULL DEFAULT 0 COMMENT '是否删除 0-否 1-是',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_code` (`tenant_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ============================================================
-- 初始种子数据
-- ============================================================

-- 超级管理员（密码: admin123，bcrypt哈希）
INSERT INTO `sys_user` (`username`, `password`, `real_name`, `phone`, `user_type`, `status`)
VALUES ('admin', '$2b$12$LJ3m4ys3uz2V7S4Iy.EBQuYBbkRbKzGM2D2FOdHfJU7KGEOYdDxYy', '超级管理员', '13800000000', 0, 1);

-- 默认角色
INSERT INTO `sys_role` (`role_code`, `role_name`, `role_type`, `sort_order`, `status`)
VALUES ('super_admin', '超级管理员', 0, 0, 1);

-- 用户角色关联
INSERT INTO `sys_user_role` (`user_id`, `role_id`) VALUES (1, 1);

-- 产品版本
INSERT INTO `sys_product_version` (`version_code`, `version_name`, `description`, `max_users`, `max_vehicles`, `price`, `sort_order`, `status`) VALUES
('basic', '基础版', '适合小型车队，包含基础车辆和驾驶员管理功能', 5, 20, '免费', 0, 1),
('standard', '标准版', '适合中型车队，包含运单管理、路线管理等功能', 20, 100, '2999/年', 10, 1),
('pro', '专业版', '适合大型车队，包含数据分析、结算管理等高级功能', 100, 500, '9999/年', 20, 1),
('enterprise', '企业版', '定制化解决方案，不限用户和车辆数，专属技术支持', 9999, 9999, '面议', 30, 1);

-- 数据字典：车辆类型
INSERT INTO `sys_dict` (`dict_code`, `dict_name`, `sort_order`, `status`) VALUES ('vehicle_type', '车辆类型', 0, 1);
INSERT INTO `sys_dict_item` (`dict_id`, `dict_code`, `item_name`, `item_value`, `sort_order`) VALUES
(1, 'vehicle_type', '重型货车', 'heavy_truck', 0),
(1, 'vehicle_type', '中型货车', 'medium_truck', 10),
(1, 'vehicle_type', '轻型货车', 'light_truck', 20),
(1, 'vehicle_type', '微型货车', 'mini_truck', 30),
(1, 'vehicle_type', '挂车', 'trailer', 40);

-- 数据字典：驾照类型
INSERT INTO `sys_dict` (`dict_code`, `dict_name`, `sort_order`, `status`) VALUES ('license_type', '驾照类型', 10, 1);
INSERT INTO `sys_dict_item` (`dict_id`, `dict_code`, `item_name`, `item_value`, `sort_order`) VALUES
(2, 'license_type', 'A1', 'A1', 0),
(2, 'license_type', 'A2', 'A2', 10),
(2, 'license_type', 'B1', 'B1', 20),
(2, 'license_type', 'B2', 'B2', 30),
(2, 'license_type', 'C1', 'C1', 40);

-- 数据字典：运单状态
INSERT INTO `sys_dict` (`dict_code`, `dict_name`, `sort_order`, `status`) VALUES ('order_status', '运单状态', 20, 1);
INSERT INTO `sys_dict_item` (`dict_id`, `dict_code`, `item_name`, `item_value`, `sort_order`) VALUES
(3, 'order_status', '待派车', '0', 0),
(3, 'order_status', '已派车', '1', 10),
(3, 'order_status', '运输中', '2', 20),
(3, 'order_status', '已到达', '3', 30),
(3, 'order_status', '已签收', '4', 40),
(3, 'order_status', '已完成', '5', 50),
(3, 'order_status', '已取消', '6', 60);
