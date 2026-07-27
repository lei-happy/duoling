/** 产品端 */
export const PRODUCT_LINE_OPTIONS = [
  { value: 'console', label: '运营端' },
  { value: 'client', label: '企业端' },
  { value: 'mobile', label: '移动端' },
  { value: 'lite', label: 'LITE端' },
  { value: 'other', label: '其他' }
];

/** 优先级 */
export const PRIORITY_OPTIONS = [
  { value: 0, label: '低', type: 'info' as const },
  { value: 1, label: '中', type: '' as const },
  { value: 2, label: '高', type: 'warning' as const },
  { value: 3, label: '紧急', type: 'danger' as const }
];

/** 状态 */
export const STATUS_OPTIONS = [
  { value: 0, label: '待原型' },
  { value: 1, label: '原型已出' },
  { value: 2, label: '设计中' },
  { value: 3, label: '设计完成' },
  { value: 4, label: '开发中' },
  { value: 5, label: '已完成' },
  { value: 6, label: '已搁置' }
];

export function productLineLabel(value?: string | null) {
  return PRODUCT_LINE_OPTIONS.find((o) => o.value === value)?.label ?? value ?? '-';
}

export function priorityLabel(value?: number | null) {
  return PRIORITY_OPTIONS.find((o) => o.value === value)?.label ?? '-';
}

export function priorityType(value?: number | null) {
  return PRIORITY_OPTIONS.find((o) => o.value === value)?.type ?? 'info';
}

export function statusLabel(value?: number | null) {
  return STATUS_OPTIONS.find((o) => o.value === value)?.label ?? '-';
}

/** Figma 嵌入地址 */
export function toFigmaEmbedUrl(url?: string | null): string | null {
  if (!url || !url.includes('figma.com')) return null;
  try {
    const encoded = encodeURIComponent(url.trim());
    return `https://www.figma.com/embed?embed_host=share&url=${encoded}`;
  } catch {
    return null;
  }
}
