/** 左侧菜单与卡片标题 */
export const GROUP_LABELS: Record<string, string> = {
  waybill: '运单设置',
  default: '其它'
};

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
