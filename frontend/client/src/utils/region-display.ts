/**
 * 行政区划展示：库存仍是「省/市/区」全称，列表单元格去掉省，保留市/区及行政后缀。
 */

const SKIP_SEGMENTS = new Set(['中国', '中华人民共和国', '市辖区']);

const PROVINCE_SUFFIX_RE = /(?:省|自治区|特别行政区)$/;

const PROVINCE_ALIASES = new Set([
  '内蒙古',
  '广西',
  '西藏',
  '宁夏',
  '新疆',
  '内蒙古自治区',
  '广西壮族自治区',
  '西藏自治区',
  '宁夏回族自治区',
  '新疆维吾尔自治区'
]);

function splitRegionPath(raw: string): string[] {
  return raw
    .replace(/[／\\]/g, '/')
    .split('/')
    .map((s) => s.trim())
    .filter(Boolean);
}

const MUNICIPALITY_RE = /^(?:北京|天津|上海|重庆)市?$/;

function isProvinceSegment(name: string): boolean {
  return (
    PROVINCE_SUFFIX_RE.test(name) ||
    PROVINCE_ALIASES.has(name) ||
    MUNICIPALITY_RE.test(name)
  );
}

function adminStem(name: string): string {
  return name.replace(
    /(?:特别行政区|维吾尔自治区|壮族自治区|回族自治区|自治区|省|市)$/g,
    ''
  );
}

/** 提取省级：安徽省/安庆市/迎江区 → 安徽省；无省级则空串 */
export function regionProvince(raw?: string | null): string {
  const text = (raw ?? '').trim();
  if (!text) return '';
  const parts = splitRegionPath(text).filter((p) => !SKIP_SEGMENTS.has(p));
  if (parts.length === 0) return '';
  return isProvinceSegment(parts[0]!) ? parts[0]! : '';
}

/** 列表短展示：安徽省/滁州市/南谯区 → 滁州市/南谯区 */
export function shortRegionPath(
  raw?: string | null,
  emptyPlaceholder = '--'
): string {
  const text = (raw ?? '').trim();
  if (!text) return emptyPlaceholder;
  const parts = splitRegionPath(text).filter((p) => !SKIP_SEGMENTS.has(p));
  if (parts.length === 0) return emptyPlaceholder;
  if (
    parts.length >= 2 &&
    adminStem(parts[0]!) &&
    adminStem(parts[0]!) === adminStem(parts[1]!)
  ) {
    parts.shift();
  }
  if (parts.length >= 2 && isProvinceSegment(parts[0]!)) {
    return parts.slice(1).join('/');
  }
  return parts.join('/');
}

/** 省 + 市/区拆开，供配载本单线路两行展示 */
export function parseRegionDisplay(
  raw?: string | null,
  emptyPlaceholder = '--'
): { province: string; cityDistrict: string } {
  return {
    province: regionProvince(raw),
    cityDistrict: shortRegionPath(raw, emptyPlaceholder)
  };
}

/** 悬停看全称，箭头不会丢 */
export function formatRouteTitle(
  origin?: string | null,
  destination?: string | null
): string {
  const from = (origin ?? '').trim();
  const to = (destination ?? '').trim();
  if (!from && !to) return '';
  return `${from || '--'} → ${to || '--'}`;
}

/** 多节点线路全称：起点 → 中转 → 终点 */
export function formatRouteNodesTitle(
  nodes?: Array<string | null | undefined> | null
): string {
  const parts = (nodes ?? [])
    .map((n) => (n ?? '').trim())
    .filter(Boolean);
  return parts.join(' → ');
}
