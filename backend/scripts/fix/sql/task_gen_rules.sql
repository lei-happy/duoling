-- 为已有租户业务库补充任务单号/名称生成策略（默认 TASK+YYYYMMDD+4 位序号；名称：路线+首条商品车+承运）
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
  'task.no_gen_rule',
  '{"parts":[{"type":"prefix","value":"TASK"},{"type":"date","format":"YYYYMMDD"},{"type":"seq","digits":4,"reset":"daily"}]}',
  'task',
  '任务单号生成规则 JSON（parts 三段 prefix/date/seq）',
  'json',
  '{"parts":[{"type":"prefix","value":"TASK"},{"type":"date","format":"YYYYMMDD"},{"type":"seq","digits":4,"reset":"daily"}]}',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'task.no_gen_rule'
    AND `is_deleted` = 0
);

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
  'task.name_gen_rule',
  '{"joiner":" ","parts":[{"kind":"route_od"},{"kind":"vehicle_first"},{"kind":"carrier_driver_plate"}]}',
  'task',
  '任务名称生成规则 JSON（joiner + parts 三段 kind）',
  'json',
  '{"joiner":" ","parts":[{"kind":"route_od"},{"kind":"vehicle_first"},{"kind":"carrier_driver_plate"}]}',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'task.name_gen_rule'
    AND `is_deleted` = 0
);
