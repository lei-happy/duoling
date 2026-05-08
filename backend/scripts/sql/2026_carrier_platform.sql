-- =====================================================================
-- 承运商管理模块 · 平台库 SQL（zt_platform）
--
-- 执行对象：平台主库（默认 zt_platform）
-- 执行频率：一次性执行
-- 关联文档：
--   项目文档/02.需求文档/02.企业端/05.合作伙伴模块/02.承运商管理.md
--   项目文档/02.需求文档/02.企业端/05.合作伙伴模块/03.平台互联体系-账号互通设计.md
--
-- 内容概览：
--   1. sys_user_tenant 加列 invite_source_tenant
--   2. sys_carrier_link / sys_carrier_invitation_inbox 中转表
--   3. 新增 lite 产品版本
--   4. 新增 / 调整 sys_product_feature（partner_carrier / partner_inbound）
--   5. 新增 sys_menu 记录（partner:carrier + partner:inbound + 6 个按钮）
--   6. capacity:external-carrier 改名「承运商运力」，partner:supplier 隐藏
--      （新增/更新均按 menu_code 定位，不依赖具体主键 ID，自增分配）
--
-- 注意：
--   sys_version_feature 表的关联关系（lite/basic/standard/pro/enterprise <-> 各
--   feature_code）由 backend/scripts/seed/seed_product_features.py 脚本统一维护，
--   本 SQL 仅负责创建 lite 版本与新增 partner_carrier/partner_inbound 两个 feature
--   定义；执行完本 SQL 后，请手工再跑一遍：
--       cd backend && python scripts/seed/seed_product_features.py
--   以同步版本-功能关联。
-- =====================================================================

SET NAMES utf8mb4;
START TRANSACTION;

-- ---------------------------------------------------------------------
-- 1. sys_user_tenant 加列：邀请来源租户编码
-- ---------------------------------------------------------------------
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE()
     AND TABLE_NAME = 'sys_user_tenant'
     AND COLUMN_NAME = 'invite_source_tenant'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE sys_user_tenant ADD COLUMN invite_source_tenant VARCHAR(32) NULL COMMENT ''邀请来源租户编码（carrier_invite 场景）'' AFTER status',
  'SELECT ''sys_user_tenant.invite_source_tenant 已存在，跳过'' AS msg'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------
-- 2. sys_carrier_link：跨租户承运商互联关系镜像（B 端反查加速）
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sys_carrier_link (
  id                  BIGINT       NOT NULL AUTO_INCREMENT,
  source_tenant_code  VARCHAR(32)  NOT NULL COMMENT 'A 的 tenant_code',
  source_carrier_id   BIGINT       NOT NULL COMMENT 'A.biz_carrier.id',
  source_carrier_name VARCHAR(100) NOT NULL COMMENT 'A 中维护的承运商名（脱敏冗余）',
  source_tenant_name  VARCHAR(100) NULL     COMMENT 'A 的企业名（脱敏冗余）',
  linked_tenant_code  VARCHAR(32)  NOT NULL COMMENT 'B 的 tenant_code',
  link_status         SMALLINT     NOT NULL DEFAULT 1 COMMENT '1-激活 2-A 端已删除 3-B 端已退出',
  cooperation_start   DATE         NULL,
  created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted          SMALLINT     NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_source (source_tenant_code, source_carrier_id),
  KEY idx_linked (linked_tenant_code, link_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='跨租户承运商互联关系（B 端反查加速）';

-- ---------------------------------------------------------------------
-- 3. sys_carrier_invitation_inbox：邀请索引中转表（B 端反查/管理员审核加速）
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sys_carrier_invitation_inbox (
  id                     BIGINT       NOT NULL AUTO_INCREMENT,
  invite_code            VARCHAR(32)  NOT NULL COMMENT '同 biz_carrier_invitation.invite_code',
  source_tenant_code     VARCHAR(32)  NOT NULL COMMENT 'A 的 tenant_code',
  source_carrier_id      BIGINT       NOT NULL COMMENT 'A.biz_carrier.id',
  source_carrier_name    VARCHAR(100) NOT NULL COMMENT 'A 录入的承运商名',
  source_tenant_name     VARCHAR(100) NULL     COMMENT 'A 的企业名',
  invite_phone           VARCHAR(20)  NOT NULL COMMENT '被邀请手机号',
  invitee_user_id        BIGINT       NULL     COMMENT 'invitee sys_user.id（路径 C 写入；路径 B 创建租户后回填）',
  invite_path            VARCHAR(8)   NOT NULL COMMENT 'B / C1 / C2 / C3',
  status                 SMALLINT     NOT NULL DEFAULT 1
                                      COMMENT '镜像 biz_carrier_invitation.status：0-待发送 1-已发送 2-已点击 3-已激活 4-已过期 5-A 已撤回 6-B 已拒绝 7-代转交中 8-A 端预审拒绝',
  forwarder_tenant_code  VARCHAR(32)  NULL     COMMENT 'C2 转交所选租户',
  forwarder_user_id      BIGINT       NULL     COMMENT 'C2 转交者 user_id',
  target_admin_tenants   JSON         NULL     COMMENT 'C2 待管理员审核的目标租户列表（冗余加速 admin 查询）',
  expires_at             DATETIME     NOT NULL,
  created_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_deleted             SMALLINT     NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uk_invite_code (invite_code),
  KEY idx_invite_phone (invite_phone),
  KEY idx_invitee_user_id (invitee_user_id),
  KEY idx_forwarder_tenant_status (forwarder_tenant_code, status),
  KEY idx_status_expires (status, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='承运商邀请索引中转表（被邀请方反查加速）';

-- ---------------------------------------------------------------------
-- 4. 新增 lite 产品版本（轻量版，被邀请承运商默认开通）
-- ---------------------------------------------------------------------
INSERT INTO sys_product_version
  (version_code, version_name, description, max_users, max_vehicles, price, sort_order, status, is_deleted)
SELECT 'lite', '轻量版',
       '承运商邀请激活专用版本，仅含运力管理与合作客户',
       5, 20, '免费', 5, 1, 0
WHERE NOT EXISTS (
  SELECT 1 FROM sys_product_version WHERE version_code = 'lite' AND is_deleted = 0
);

-- ---------------------------------------------------------------------
-- 5. sys_product_feature 新增 / 调整
--    本 SQL 只负责把"必须立即生效的字段"写好（partner_carrier required_tables、
--    partner_inbound 行的存在性）；版本-功能关联（sys_version_feature）由
--    seed_product_features.py 重跑时统一刷新。
-- ---------------------------------------------------------------------

-- 5.1 partner_carrier：required_tables 写入；feature_name 校正
INSERT INTO sys_product_feature
  (feature_code, feature_name, module, sort_order, required_tables, status, is_deleted)
SELECT 'partner_carrier', '承运商管理', 'partner', 16,
       JSON_ARRAY('biz_carrier', 'biz_carrier_settlement', 'biz_carrier_invitation'),
       1, 0
WHERE NOT EXISTS (
  SELECT 1 FROM sys_product_feature WHERE feature_code = 'partner_carrier' AND is_deleted = 0
);

UPDATE sys_product_feature
   SET feature_name    = '承运商管理',
       module          = 'partner',
       sort_order      = 16,
       required_tables = JSON_ARRAY('biz_carrier', 'biz_carrier_settlement', 'biz_carrier_invitation')
 WHERE feature_code = 'partner_carrier' AND is_deleted = 0;

-- 5.2 partner_inbound：合作客户反向视角（lite 必含）
INSERT INTO sys_product_feature
  (feature_code, feature_name, module, sort_order, required_tables, status, is_deleted)
SELECT 'partner_inbound', '合作客户（反向视角）', 'partner', 17,
       NULL, 1, 0
WHERE NOT EXISTS (
  SELECT 1 FROM sys_product_feature WHERE feature_code = 'partner_inbound' AND is_deleted = 0
);

-- 5.3 partner_supplier：远期上游供应商，调整名称与排序，本期不做（visible=0）
UPDATE sys_product_feature
   SET feature_name = '供应商管理（远期·上游）',
       module       = 'partner',
       sort_order   = 18
 WHERE feature_code = 'partner_supplier' AND is_deleted = 0;

-- ---------------------------------------------------------------------
-- 6. sys_menu 调整与新增（app_type='client'）
--    说明：本段不再硬编码菜单主键 ID，全部按 menu_code / path 定位，
--          兼容线上库与 seed 库 ID 不一致的情况。新增菜单的 ID 由
--          AUTO_INCREMENT 自动分配，子菜单通过 @parent_id 变量回填父级。
--    要求：客户端连接需保留多语句执行（默认开启），@变量 在同一会话内有效。
-- ---------------------------------------------------------------------

-- 6.1 「外协供应商」改名为「承运商运力」（按 menu_code 定位）
UPDATE sys_menu
   SET menu_name = '承运商运力'
 WHERE menu_code = 'capacity:external-carrier'
   AND app_type  = 'client'
   AND is_deleted = 0;

-- 6.2 「供应商管理」隐藏（visible=0），保留作为远期上游供应商占位
UPDATE sys_menu
   SET visible = 0
 WHERE menu_code = 'partner:supplier'
   AND app_type  = 'client'
   AND is_deleted = 0;

-- 6.3 取「客商中心」目录的主键，作为后续两组主菜单的 parent_id
--     客商中心是顶层目录（parent_id=0、path='/partner'、menu_code IS NULL）
SET @partner_root_id := (
  SELECT id FROM sys_menu
   WHERE app_type  = 'client'
     AND parent_id = 0
     AND path      = '/partner'
     AND is_deleted = 0
   LIMIT 1
);

-- 6.4 新增 partner:carrier 主菜单（自增 ID）
INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @partner_root_id, '承运商管理', 'partner:carrier', 0,
       '/partner/carrier', '/partner/carrier/index',
       'chengyunshang', 15, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @partner_root_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_menu
      WHERE menu_code = 'partner:carrier'
        AND app_type  = 'client'
        AND is_deleted = 0
   );

-- 取 partner:carrier 主键，作为 5 个按钮的 parent_id
SET @carrier_id := (
  SELECT id FROM sys_menu
   WHERE menu_code = 'partner:carrier'
     AND app_type  = 'client'
     AND is_deleted = 0
   LIMIT 1
);

-- 6.5 partner:carrier 下的 6 个按钮权限（list / add / edit / delete / invite / revoke-invite）
INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @carrier_id, '查询', 'partner:carrier:list', 1,
       NULL, NULL, NULL, 0, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @carrier_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM sys_menu
                    WHERE menu_code='partner:carrier:list' AND app_type='client' AND is_deleted=0);

INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @carrier_id, '新增', 'partner:carrier:add', 1,
       NULL, NULL, NULL, 1, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @carrier_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM sys_menu
                    WHERE menu_code='partner:carrier:add' AND app_type='client' AND is_deleted=0);

INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @carrier_id, '编辑', 'partner:carrier:edit', 1,
       NULL, NULL, NULL, 2, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @carrier_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM sys_menu
                    WHERE menu_code='partner:carrier:edit' AND app_type='client' AND is_deleted=0);

INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @carrier_id, '删除', 'partner:carrier:delete', 1,
       NULL, NULL, NULL, 3, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @carrier_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM sys_menu
                    WHERE menu_code='partner:carrier:delete' AND app_type='client' AND is_deleted=0);

INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @carrier_id, '邀请激活', 'partner:carrier:invite', 1,
       NULL, NULL, NULL, 4, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @carrier_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM sys_menu
                    WHERE menu_code='partner:carrier:invite' AND app_type='client' AND is_deleted=0);

INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @carrier_id, '撤回邀请', 'partner:carrier:revoke-invite', 1,
       NULL, NULL, NULL, 5, 1, 1, 'client', 'partner_carrier', 0
  FROM dual
 WHERE @carrier_id IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM sys_menu
                    WHERE menu_code='partner:carrier:revoke-invite' AND app_type='client' AND is_deleted=0);

-- 6.6 新增 partner:inbound 主菜单（合作客户反向视角，lite 必含）
INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @partner_root_id, '合作客户', 'partner:inbound', 0,
       '/partner/inbound', '/partner/inbound/index',
       'kehuguanli', 25, 1, 1, 'client', 'partner_inbound', 0
  FROM dual
 WHERE @partner_root_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_menu
      WHERE menu_code = 'partner:inbound'
        AND app_type  = 'client'
        AND is_deleted = 0
   );

-- 6.7 校验：执行完后请确认 4 行结果均不为空
--   SELECT id, menu_code, parent_id, menu_name, visible
--     FROM sys_menu
--    WHERE menu_code IN ('capacity:external-carrier','partner:supplier',
--                        'partner:carrier','partner:inbound')
--      AND app_type='client' AND is_deleted=0;

COMMIT;

-- =====================================================================
-- 执行完毕后，请运行下面命令以同步 sys_version_feature 关联：
--   cd backend && python scripts/seed/seed_product_features.py
-- 该脚本会按代码中最新的 _BASIC_FEATURES / _LITE_DELTA / _STANDARD_DELTA / ...
-- 重建 lite/basic/standard/pro/enterprise 五档与功能的关联关系。
-- =====================================================================
