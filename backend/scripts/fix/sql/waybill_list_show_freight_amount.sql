-- 为已有租户业务库补充配置项 waybill.list_show_freight_amount（默认不显示列表运费）
-- 在对应租户库执行一次即可；若已存在同 config_key 则不会插入。

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
  'waybill.list_show_freight_amount',
  'false',
  'waybill',
  '运单列表是否展示运费金额（敏感信息，默认关闭）',
  'boolean',
  'false',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'waybill.list_show_freight_amount'
    AND `is_deleted` = 0
);
