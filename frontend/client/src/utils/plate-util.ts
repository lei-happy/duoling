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

/** 省简称 + 发牌机关首字母后打点：`京A12345` → `京A · 12345`；无字母时退化为 `京 · xxx` */
function provinceThenLetterDot(provinceChar: string, afterProvince: string): string {
  const tail = afterProvince.trim();
  if (!tail) return `${provinceChar}${PLATE_DOT}`;
  const m = tail.match(/^([A-HJ-NP-Za-hj-np-z])(.*)$/);
  if (m) {
    return `${provinceChar}${m[1]}${PLATE_DOT}${m[2]}`;
  }
  return `${provinceChar}${PLATE_DOT}${tail}`;
}

/**
 * 车牌展示（不改变存储值）。
 * - 蓝/黄：`京A12345` → `京A · 12345`
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
    if (
      core.length >= 3 &&
      /^[\u4e00-\u9fa5][A-HJ-NP-Za-hj-np-z]/.test(core.slice(0, 2))
    ) {
      return `${core.slice(0, 2)}${PLATE_DOT}${core.slice(2)}`;
    }
    const normalized = s.match(/^([\u4e00-\u9fa5])\s*[·・]\s*(.+)$/);
    if (normalized) {
      return provinceThenLetterDot(normalized[1], normalized[2]);
    }
    const first = core[0];
    const rest = core.slice(1);
    if (/[\u4e00-\u9fa5]/.test(first) && rest.length > 0) {
      return provinceThenLetterDot(first, rest);
    }
    return s;
  }

  const normalized = s.match(/^([\u4e00-\u9fa5])\s*[·・]\s*(.+)$/);
  if (normalized) {
    return provinceThenLetterDot(normalized[1], normalized[2]);
  }

  const first = core[0];
  const rest = core.slice(1);
  if (/[\u4e00-\u9fa5]/.test(first) && rest.length > 0) {
    return provinceThenLetterDot(first, rest);
  }

  return s;
}
