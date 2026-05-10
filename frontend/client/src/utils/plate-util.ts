import type { PlateCategory } from '@/constants/plate-category';

/** 牌照展示用间隔符（半角空格 + 间隔号 + 半角空格） */
const PLATE_DOT = ' · ';

function stripSeparators(s: string): string {
  let t = s.trim();
  for (const ch of ['·', '・', '-', '－', ' ']) {
    t = t.split(ch).join('');
  }
  return t;
}

/**
 * 车牌展示（不改变存储值）。
 * - 蓝/黄：`京A12345` → `京 · A12345`
 * - 新能源：`粤BD12345` → `粤B · D12345`（发牌机关代号与序号之间）
 */
export function formatPlateNumberDisplay(
  raw: string | null | undefined,
  category?: PlateCategory
): string {
  const s = (raw ?? '').trim();
  if (!s) return '';

  const core = stripSeparators(s);
  if (!core) return '';

  if (category === 'NEW_ENERGY') {
    if (core.length >= 3 && /^[\u4e00-\u9fa5][A-HJ-NP-Z]/.test(core.slice(0, 2))) {
      return `${core.slice(0, 2)}${PLATE_DOT}${core.slice(2)}`;
    }
    const normalized = s.match(/^([\u4e00-\u9fa5])\s*[·・]\s*(.+)$/);
    if (normalized) {
      return `${normalized[1]}${PLATE_DOT}${normalized[2].trim()}`;
    }
    const first = core[0];
    const rest = core.slice(1);
    if (/[\u4e00-\u9fa5]/.test(first) && rest.length > 0) {
      return `${first}${PLATE_DOT}${rest}`;
    }
    return s;
  }

  const normalized = s.match(/^([\u4e00-\u9fa5])\s*[·・]\s*(.+)$/);
  if (normalized) {
    return `${normalized[1]}${PLATE_DOT}${normalized[2].trim()}`;
  }

  const first = core[0];
  const rest = core.slice(1);
  if (/[\u4e00-\u9fa5]/.test(first) && rest.length > 0) {
    return `${first}${PLATE_DOT}${rest}`;
  }

  return s;
}
