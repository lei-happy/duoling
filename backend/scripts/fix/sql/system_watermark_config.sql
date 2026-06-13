-- 为已有租户业务库补充系统水印配置项（默认关闭）
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
  'system.watermark_enabled',
  'false',
  'security',
  '是否启用页面水印（默认关闭）',
  'boolean',
  'false',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'system.watermark_enabled'
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
  'system.watermark_content',
  '{nickname} {phoneLast4} {date}',
  'security',
  '页面水印文本模板，支持 {nickname} {phoneLast4} {date} 等变量',
  'string',
  '{nickname} {phoneLast4} {date}',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'system.watermark_content'
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
  'system.watermark_style',
  '{"fontSize":14,"color":"rgba(0, 0, 0, 0.12)","rotate":-22,"gap":[200,160],"zIndex":9999}',
  'security',
  '页面水印样式 JSON：fontSize/color/rotate/gap/zIndex',
  'json',
  '{"fontSize":14,"color":"rgba(0, 0, 0, 0.12)","rotate":-22,"gap":[200,160],"zIndex":9999}',
  0
FROM (SELECT 1 AS _) AS t
WHERE NOT EXISTS (
  SELECT 1
  FROM `biz_system_config`
  WHERE `config_key` = 'system.watermark_style'
    AND `is_deleted` = 0
);
