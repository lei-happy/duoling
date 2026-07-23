/** 左侧菜单分组文案 */
export const GROUP_LABELS: Record<string, string> = {
  waybill: '计划设置',
  task: '任务单设置',
  finance: '财务设置',
  security: '水印设置',
  default: '其它'
};

/** 右侧内容区卡片标题（可与侧栏不同，例如任务单：侧栏「任务单设置」、卡片「任务编号生成设置」） */
export const GROUP_CARD_HEADER_LABELS: Record<string, string> = {
  task: '任务编号生成设置',
  finance: '费用单发起节点设置'
};

/** 侧栏分组顺序（避免按字母序 task 排在 waybill 前） */
export const CONFIG_GROUP_SORT_ORDER = [
  'waybill',
  'task',
  'finance',
  'security',
  'default'
];

/** 与后端种子一致的默认 JSON（用于表单初始化/展示默认值文案） */
export const TASK_NO_GEN_DEFAULT_JSON =
  '{"parts":[{"type":"prefix","value":"TASK"},{"type":"date","format":"YYYYMMDD"},{"type":"seq","digits":4,"reset":"daily"}]}';

export const TASK_NAME_GEN_DEFAULT_JSON =
  '{"joiner":" ","parts":[{"kind":"route_od"},{"kind":"vehicle_first"},{"kind":"carrier_driver_plate"}]}';

/** 各配置项在通用表单中的短标题（避免使用接口返回的长 description 作为表单项标签） */
export const CONFIG_FIELD_LABELS: Record<string, string> = {};

/** 枚举类配置的可选项（按 configKey） */
export const CONFIG_ENUM_OPTIONS: Record<
  string,
  { value: string; label: string }[]
> = {
  'waybill.freight_calc_mode': [
    { value: 'auto_required', label: '强制自动计费' },
    { value: 'auto_preferred', label: '优先自动，允许手动' },
    { value: 'manual_only', label: '仅手动填写' }
  ]
};

export function getEnumOptions(key: string) {
  return CONFIG_ENUM_OPTIONS[key] || [];
}

export function getEnumDisplayLabel(key: string, value: string) {
  const opts = CONFIG_ENUM_OPTIONS[key];
  if (opts) {
    const opt = opts.find((o) => o.value === value);
    if (opt) return opt.label;
  }
  return value;
}

function formatKeyAsLabel(configKey: string) {
  const last = configKey.split('.').pop() || configKey;
  return last.replace(/_/g, ' ');
}

/** 通用表单：表单项标题 */
export function getConfigFieldLabel(item: {
  configKey: string;
  description?: string;
}) {
  const override = CONFIG_FIELD_LABELS[item.configKey];
  if (override) return override;
  const d = item.description?.trim();
  if (d && !d.includes('\n') && d.length <= 32) {
    return d;
  }
  return formatKeyAsLabel(item.configKey);
}
