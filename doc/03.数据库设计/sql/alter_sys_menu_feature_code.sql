-- ============================================================
-- 为 sys_menu 表添加 feature_code 字段
-- 用于产品版本控制菜单可见性
-- ============================================================

ALTER TABLE `sys_menu`
  ADD COLUMN `feature_code` VARCHAR(50) DEFAULT NULL
  COMMENT '关联功能编码，用于产品版本控制菜单可见性'
  AFTER `app_type`;

CREATE INDEX `idx_feature_code` ON `sys_menu` (`feature_code`);
