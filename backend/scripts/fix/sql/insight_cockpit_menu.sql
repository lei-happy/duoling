-- =====================================================================
-- 经营驾驶舱（BI 看板）- 平台库增量脚本
--
-- 本脚本包含三部分（顺序不可调换，feature 必须先于版本-功能关联存在）：
--   1) sys_product_feature      新增 bi_cockpit / bi_cockpit_overview 两个功能
--   2) sys_version_feature      把上述两个功能绑定到 pro 版本（与 bi_overview 一致）
--   3) sys_menu                 在「数据洞察」下新增「经营驾驶舱」容器 +「经营总览」叶子
--
-- 设计要点：
--   - 不硬编码主键 ID，按 feature_code / menu_code / version_code 定位
--     （兼容线上库与 seed 库 ID 不一致）
--   - 幂等：所有 INSERT 配 WHERE NOT EXISTS / WHERE @var IS NOT NULL，可重复执行
--   - 多语句执行需在同一会话内（@变量），默认开启
--
-- 执行位置：平台库（sys_menu / sys_product_feature / sys_version_feature 所在库）
--
-- 关联快照：本脚本与下面三个快照同步维护，dev 端执行后应能 export 0 差异
--   backend/scripts/platform_sync/snapshots/product_feature.json
--   backend/scripts/platform_sync/snapshots/version_feature.json
--   backend/scripts/platform_sync/snapshots/client_menu.json
-- =====================================================================

SET NAMES utf8mb4;

-- =====================================================================
-- 1. 新增产品功能清单（sys_product_feature）
--    与既有 bi_overview / bi_report / bi_prediction 同 module='insight'
--    sort_order 接续 92（bi_prediction）之后取 93/94。
-- =====================================================================

-- 1.1 bi_cockpit：经营驾驶舱（容器级功能，覆盖整个 BI 大类）
INSERT INTO sys_product_feature
  (feature_code, feature_name, module, sort_order, required_tables, status, is_deleted)
SELECT 'bi_cockpit', '经营驾驶舱', 'insight', 93, NULL, 1, 0
  FROM dual
 WHERE NOT EXISTS (
   SELECT 1 FROM sys_product_feature
    WHERE feature_code = 'bi_cockpit' AND is_deleted = 0
 );

-- 1.2 bi_cockpit_overview：经营总览（叶子页面）
INSERT INTO sys_product_feature
  (feature_code, feature_name, module, sort_order, required_tables, status, is_deleted)
SELECT 'bi_cockpit_overview', '经营驾驶舱-经营总览', 'insight', 94, NULL, 1, 0
  FROM dual
 WHERE NOT EXISTS (
   SELECT 1 FROM sys_product_feature
    WHERE feature_code = 'bi_cockpit_overview' AND is_deleted = 0
 );

-- =====================================================================
-- 2. 绑定到 pro 版本（与 bi_overview / bi_report / bi_prediction 一致）
-- =====================================================================

SET @pro_version_id := (
  SELECT id FROM sys_product_version
   WHERE version_code = 'pro' AND is_deleted = 0
   LIMIT 1
);

SET @feat_bi_cockpit_id := (
  SELECT id FROM sys_product_feature
   WHERE feature_code = 'bi_cockpit' AND is_deleted = 0
   LIMIT 1
);

SET @feat_bi_cockpit_overview_id := (
  SELECT id FROM sys_product_feature
   WHERE feature_code = 'bi_cockpit_overview' AND is_deleted = 0
   LIMIT 1
);

-- 2.1 pro ↔ bi_cockpit
INSERT INTO sys_version_feature
  (version_id, feature_id, status, is_deleted)
SELECT @pro_version_id, @feat_bi_cockpit_id, 1, 0
  FROM dual
 WHERE @pro_version_id IS NOT NULL
   AND @feat_bi_cockpit_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_version_feature
      WHERE version_id = @pro_version_id
        AND feature_id = @feat_bi_cockpit_id
        AND is_deleted = 0
   );

-- 2.2 pro ↔ bi_cockpit_overview
INSERT INTO sys_version_feature
  (version_id, feature_id, status, is_deleted)
SELECT @pro_version_id, @feat_bi_cockpit_overview_id, 1, 0
  FROM dual
 WHERE @pro_version_id IS NOT NULL
   AND @feat_bi_cockpit_overview_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_version_feature
      WHERE version_id = @pro_version_id
        AND feature_id = @feat_bi_cockpit_overview_id
        AND is_deleted = 0
   );

-- =====================================================================
-- 3. 新增客户端菜单（sys_menu）
-- =====================================================================

-- ---------------------------------------------------------------------
-- 3.1 定位「数据洞察」一级菜单 ID
-- ---------------------------------------------------------------------
SET @insight_root_id := (
  SELECT id FROM sys_menu
   WHERE app_type  = 'client'
     AND parent_id = 0
     AND path      = '/insight'
     AND is_deleted = 0
   LIMIT 1
);

-- ---------------------------------------------------------------------
-- 3.2 新增二级容器：经营驾驶舱
-- ---------------------------------------------------------------------
INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @insight_root_id, '经营驾驶舱', 'insight:cockpit', 0,
       '/insight/cockpit', NULL,
       'yybi', 5, 1, 1, 'client', 'bi_cockpit', 0
  FROM dual
 WHERE @insight_root_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_menu
      WHERE menu_code = 'insight:cockpit'
        AND app_type  = 'client'
        AND is_deleted = 0
   );

-- 取「经营驾驶舱」主键，作为叶子的 parent_id
SET @cockpit_id := (
  SELECT id FROM sys_menu
   WHERE menu_code = 'insight:cockpit'
     AND app_type  = 'client'
     AND is_deleted = 0
   LIMIT 1
);

-- ---------------------------------------------------------------------
-- 3.3 新增三级叶子：经营总览
-- ---------------------------------------------------------------------
INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @cockpit_id, '经营总览', 'insight:cockpit:overview', 0,
       '/insight/cockpit/overview', '/dashboard/business-cockpit/overview/index',
       'yybi', 0, 1, 1, 'client', 'bi_cockpit_overview', 0
  FROM dual
 WHERE @cockpit_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_menu
      WHERE menu_code = 'insight:cockpit:overview'
        AND app_type  = 'client'
        AND is_deleted = 0
   );

-- =====================================================================
-- 4. 校验（执行完后建议手动跑一次，确认 4 个结果集均非空）
-- =====================================================================
-- -- 4.1 新增功能（应有 2 行）
-- SELECT id, feature_code, feature_name, module, sort_order, status
--   FROM sys_product_feature
--  WHERE feature_code IN ('bi_cockpit', 'bi_cockpit_overview')
--    AND is_deleted = 0;
--
-- -- 4.2 pro 版本-功能关联（应有 2 行）
-- SELECT vf.id, pv.version_code, pf.feature_code
--   FROM sys_version_feature vf
--   JOIN sys_product_version pv ON pv.id = vf.version_id
--   JOIN sys_product_feature pf ON pf.id = vf.feature_id
--  WHERE pv.version_code = 'pro'
--    AND pf.feature_code IN ('bi_cockpit', 'bi_cockpit_overview')
--    AND vf.is_deleted = 0;
--
-- -- 4.3 新增菜单（应有 2 行）
-- SELECT id, parent_id, menu_name, menu_code, path, component, feature_code, visible
--   FROM sys_menu
--  WHERE menu_code IN ('insight:cockpit', 'insight:cockpit:overview')
--    AND app_type = 'client'
--    AND is_deleted = 0;
--
-- -- 4.4 全局校验：确保所有客户端菜单引用的 feature_code 都已存在（应返回 0 行）
-- SELECT m.menu_code, m.feature_code
--   FROM sys_menu m
--   LEFT JOIN sys_product_feature f
--     ON f.feature_code = m.feature_code AND f.is_deleted = 0
--  WHERE m.app_type = 'client'
--    AND m.is_deleted = 0
--    AND m.feature_code IS NOT NULL
--    AND m.feature_code <> ''
--    AND f.id IS NULL;
