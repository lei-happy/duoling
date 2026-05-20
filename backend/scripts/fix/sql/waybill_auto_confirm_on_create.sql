-- 为已有租户业务库补充配置项 waybill.auto_confirm_on_create（默认关闭=需手动确认）
-- 在对应租户库执行一次即可；若已存在同 config_key 则不会重复插入。

INSERT INTO `biz_system_config` (
  `config_key`,
  `config_value`,
  `config_group`,
  `description`,
  `value_type`,
  `default_value`,
  `is_deleted`
)
SELECT
  'waybill.auto_confirm_on_create',
  'false',
  'waybill',
  '新建/导入运单时是否自动完成确认（关闭：待确认；开启：直接进入待调度）',
  'boolean',
  'false',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'waybill.auto_confirm_on_create'
    AND `is_deleted` = 0
);
