-- ============================================================
-- 存量客户数据修复脚本
-- 功能：为已有客户补齐 basic 产品版本授权
-- 说明：新注册流程已自动开通 basic，此脚本用于修复历史数据
-- ============================================================

-- 1. 为没有 basic 授权的正常客户补齐 basic 授权
INSERT INTO sys_tenant_product (tenant_id, tenant_code, version_id, version_code, start_time, end_time, status, is_deleted, created_at, updated_at)
SELECT
    t.id,
    t.tenant_code,
    pv.id,
    'basic',
    NOW(),
    NULL,
    1,
    0,
    NOW(),
    NOW()
FROM sys_tenant t
CROSS JOIN sys_product_version pv
WHERE pv.version_code = 'basic'
  AND pv.status = 1
  AND pv.is_deleted = 0
  AND t.is_deleted = 0
  AND NOT EXISTS (
    SELECT 1 FROM sys_tenant_product tp
    WHERE tp.tenant_id = t.id
      AND tp.version_code = 'basic'
      AND tp.is_deleted = 0
  );

-- 2. 查看修复结果
SELECT
    '总客户数' AS metric,
    COUNT(*) AS value
FROM sys_tenant WHERE is_deleted = 0
UNION ALL
SELECT
    '已有basic授权',
    COUNT(DISTINCT tp.tenant_id)
FROM sys_tenant_product tp
JOIN sys_tenant t ON t.id = tp.tenant_id
WHERE tp.version_code = 'basic'
  AND tp.is_deleted = 0
  AND t.is_deleted = 0;
