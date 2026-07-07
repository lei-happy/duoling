-- =====================================================================
-- 经营驾驶舱 - 利润总览（老板视角收入成本 BI）- 平台库增量脚本
--
-- 在既有「经营驾驶舱」容器下新增第二个叶子「利润总览」，与「运单总览」
-- 并列。展示收入 / 成本 / 毛利 / 毛利率（收入取运费引擎结果，成本取任务
-- 成本引擎结果按台数分摊到运单）。
--
-- 本脚本包含三部分（顺序不可调换，feature 必须先于版本-功能关联存在）：
--   1) sys_product_feature   新增 bi_cockpit_profit 功能
--   2) sys_version_feature   版本绑定：
--        - bi_cockpit_profit → standard（标准版）+ pro（专业版，高版本保留）
--        - bi_cockpit（经营驾驶舱容器）→ standard，使标准版下菜单能正常嵌套显示
--          （容器原本仅 pro，标准版缺容器会导致「利润总览」孤儿化）
--   3) sys_menu              在「经营驾驶舱」(insight:cockpit) 下新增叶子「利润总览」
--
-- 设计要点：
--   - 不硬编码主键 ID，按 feature_code / menu_code / version_code 定位
--   - 幂等：所有 INSERT 配 WHERE NOT EXISTS，可重复执行
--   - 多语句执行需在同一会话内（@变量）
--
-- 执行位置：平台库（sys_menu / sys_product_feature / sys_version_feature 所在库）
--
-- 关联快照（本脚本与下面三个快照同步维护，dev 端执行后应能 export 0 差异）：
--   backend/scripts/platform_sync/snapshots/product_feature.json
--   backend/scripts/platform_sync/snapshots/version_feature.json
--   backend/scripts/platform_sync/snapshots/client_menu.json
-- =====================================================================

SET NAMES utf8mb4;

-- =====================================================================
-- 1. 新增产品功能（sys_product_feature）
--    module='insight'，sort_order 接续 bi_cockpit_overview(94) 之后取 95。
-- =====================================================================
INSERT INTO sys_product_feature
  (feature_code, feature_name, module, sort_order, required_tables, status, is_deleted)
SELECT 'bi_cockpit_profit', '经营驾驶舱-利润总览', 'insight', 95, NULL, 1, 0
  FROM dual
 WHERE NOT EXISTS (
   SELECT 1 FROM sys_product_feature
    WHERE feature_code = 'bi_cockpit_profit' AND is_deleted = 0
 );

-- =====================================================================
-- 2. 版本绑定（sys_version_feature）
-- =====================================================================
SET @pro_version_id := (
  SELECT id FROM sys_product_version
   WHERE version_code = 'pro' AND is_deleted = 0
   LIMIT 1
);
SET @standard_version_id := (
  SELECT id FROM sys_product_version
   WHERE version_code = 'standard' AND is_deleted = 0
   LIMIT 1
);
SET @feat_bi_cockpit_id := (
  SELECT id FROM sys_product_feature
   WHERE feature_code = 'bi_cockpit' AND is_deleted = 0
   LIMIT 1
);
SET @feat_bi_cockpit_profit_id := (
  SELECT id FROM sys_product_feature
   WHERE feature_code = 'bi_cockpit_profit' AND is_deleted = 0
   LIMIT 1
);

-- 2.1 bi_cockpit_profit ↔ pro（高版本保留）
INSERT INTO sys_version_feature
  (version_id, feature_id, status, is_deleted)
SELECT @pro_version_id, @feat_bi_cockpit_profit_id, 1, 0
  FROM dual
 WHERE @pro_version_id IS NOT NULL
   AND @feat_bi_cockpit_profit_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_version_feature
      WHERE version_id = @pro_version_id
        AND feature_id = @feat_bi_cockpit_profit_id
        AND is_deleted = 0
   );

-- 2.2 bi_cockpit_profit ↔ standard（标准版）
INSERT INTO sys_version_feature
  (version_id, feature_id, status, is_deleted)
SELECT @standard_version_id, @feat_bi_cockpit_profit_id, 1, 0
  FROM dual
 WHERE @standard_version_id IS NOT NULL
   AND @feat_bi_cockpit_profit_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_version_feature
      WHERE version_id = @standard_version_id
        AND feature_id = @feat_bi_cockpit_profit_id
        AND is_deleted = 0
   );

-- 2.3 bi_cockpit（经营驾驶舱容器）↔ standard（使标准版菜单可正常嵌套）
INSERT INTO sys_version_feature
  (version_id, feature_id, status, is_deleted)
SELECT @standard_version_id, @feat_bi_cockpit_id, 1, 0
  FROM dual
 WHERE @standard_version_id IS NOT NULL
   AND @feat_bi_cockpit_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_version_feature
      WHERE version_id = @standard_version_id
        AND feature_id = @feat_bi_cockpit_id
        AND is_deleted = 0
   );

-- =====================================================================
-- 3. 新增客户端菜单（sys_menu）
-- =====================================================================

-- 3.1 定位「经营驾驶舱」二级容器 ID（叶子的 parent_id）
SET @cockpit_id := (
  SELECT id FROM sys_menu
   WHERE menu_code = 'insight:cockpit'
     AND app_type  = 'client'
     AND is_deleted = 0
   LIMIT 1
);

-- 3.2 新增三级叶子：利润总览（sort_order=1，紧随「运单总览」sort_order=0）
INSERT INTO sys_menu
  (parent_id, menu_name, menu_code, menu_type, path, component, icon,
   sort_order, visible, status, app_type, feature_code, is_deleted)
SELECT @cockpit_id, '利润总览', 'insight:cockpit:profit', 0,
       '/insight/cockpit/profit', '/insight/cockpit/profit/index',
       '', 1, 1, 1, 'client', 'bi_cockpit_profit', 0
  FROM dual
 WHERE @cockpit_id IS NOT NULL
   AND NOT EXISTS (
     SELECT 1 FROM sys_menu
      WHERE menu_code = 'insight:cockpit:profit'
        AND app_type  = 'client'
        AND is_deleted = 0
   );

-- =====================================================================
-- 4. 校验（执行完后建议手动跑一次，确认 3 个结果集均非空）
-- =====================================================================
-- SELECT id, feature_code, feature_name, module, sort_order, status
--   FROM sys_product_feature WHERE feature_code = 'bi_cockpit_profit' AND is_deleted = 0;
--
-- SELECT vf.id, pv.version_code, pf.feature_code
--   FROM sys_version_feature vf
--   JOIN sys_product_version pv ON pv.id = vf.version_id
--   JOIN sys_product_feature pf ON pf.id = vf.feature_id
--  WHERE pv.version_code = 'pro' AND pf.feature_code = 'bi_cockpit_profit'
--    AND vf.is_deleted = 0;
--
-- SELECT id, parent_id, menu_name, menu_code, path, component, feature_code, visible
--   FROM sys_menu WHERE menu_code = 'insight:cockpit:profit'
--    AND app_type = 'client' AND is_deleted = 0;
