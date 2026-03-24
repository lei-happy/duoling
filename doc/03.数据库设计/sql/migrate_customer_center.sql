-- ============================================================
-- 客户运营中心迁移脚本
-- 功能：将"租户管理"重构为"客户运营中心"
-- ============================================================

-- 1. sys_tenant 表新增字段
ALTER TABLE sys_tenant ADD COLUMN in_follow_pool SMALLINT NOT NULL DEFAULT 0 COMMENT '是否在跟进池 0-否 1-是';
ALTER TABLE sys_tenant ADD COLUMN follow_remark TEXT NULL COMMENT '跟进备注';

-- 2. 更新原"租户管理"一级菜单
UPDATE sys_menu
SET menu_name = '客户运营中心',
    menu_code = 'customer',
    path = '/customer',
    icon = 'DataAnalysis'
WHERE menu_code = 'tenant' AND app_type = 'platform';

-- 3. 删除原子菜单
DELETE FROM sys_role_menu
WHERE menu_id IN (
    SELECT id FROM sys_menu
    WHERE menu_code IN ('tenant:list', 'tenant:feedback') AND app_type = 'platform'
);

DELETE FROM sys_menu
WHERE menu_code IN ('tenant:list', 'tenant:feedback') AND app_type = 'platform';

-- 4. 插入新子菜单
SET @pid = (SELECT id FROM sys_menu WHERE menu_code = 'customer' AND app_type = 'platform');

INSERT INTO sys_menu (parent_id, menu_name, menu_code, menu_type, path, component, sort_order, app_type, visible, status, is_deleted) VALUES
(@pid, '新注册客户',   'customer:new',       0, '/customer/new',       '/customer/new/index',       0,  'platform', 1, 1, 0),
(@pid, '免费体验客户', 'customer:trial',     0, '/customer/trial',     '/customer/trial/index',     10, 'platform', 1, 1, 0),
(@pid, '跟进池',       'customer:follow-up', 0, '/customer/follow-up', '/customer/follow-up/index', 20, 'platform', 1, 1, 0),
(@pid, '付费客户',     'customer:paid',      0, '/customer/paid',      '/customer/paid/index',      30, 'platform', 1, 1, 0),
(@pid, '流失客户',     'customer:churned',   0, '/customer/churned',   '/customer/churned/index',   40, 'platform', 1, 1, 0),
(@pid, '全量客户',     'customer:all',       0, '/customer/all',       '/customer/all/index',       50, 'platform', 1, 1, 0);

-- 5. 为 super_admin 角色关联新菜单
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT r.id, m.id
FROM sys_role r, sys_menu m
WHERE r.role_code = 'super_admin'
  AND m.menu_code LIKE 'customer:%'
  AND m.app_type = 'platform'
  AND NOT EXISTS (
    SELECT 1 FROM sys_role_menu rm WHERE rm.role_id = r.id AND rm.menu_id = m.id
  );
