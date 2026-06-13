import type { User } from '@/api/system/user/model';

export interface WatermarkFontStyle {
  color: string;
  fontSize: number;
  fontWeight: 'normal' | 'light' | 'weight' | number;
  fontFamily: string;
}

export interface WatermarkStyleConfig {
  fontSize: number;
  color: string;
  rotate: number;
  gap: [number, number];
  zIndex: number;
}

export const DEFAULT_WATERMARK_CONTENT = '{nickname} {phoneLast4} {date}';

export const DEFAULT_WATERMARK_STYLE: WatermarkStyleConfig = {
  fontSize: 14,
  color: 'rgba(0, 0, 0, 0.12)',
  rotate: -22,
  gap: [200, 160],
  zIndex: 9999
};

export const DEFAULT_WATERMARK_STYLE_JSON = JSON.stringify(
  DEFAULT_WATERMARK_STYLE
);

/** 水印模板可用变量 */
export const WATERMARK_VARIABLES = [
  { key: 'nickname', label: '昵称' },
  { key: 'realName', label: '姓名' },
  { key: 'phone', label: '手机号（脱敏）' },
  { key: 'phoneLast4', label: '手机后四位' },
  { key: 'tenantName', label: '企业名称' },
  { key: 'date', label: '当前日期' },
  { key: 'datetime', label: '当前时间' }
] as const;

export function maskPhone(phone?: string): string {
  if (!phone) {
    return '-';
  }
  const normalized = phone.replace(/\s/g, '');
  if (normalized.length >= 7) {
    return `${normalized.slice(0, 3)}****${normalized.slice(-4)}`;
  }
  return normalized || '-';
}

export function getPhoneLast4(phone?: string): string {
  if (!phone) {
    return '-';
  }
  const normalized = phone.replace(/\s/g, '');
  if (normalized.length >= 4) {
    return normalized.slice(-4);
  }
  return normalized || '-';
}

function formatDateTime(now: Date, withTime: boolean): string {
  const pad = (value: number) => String(value).padStart(2, '0');
  const date = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  if (!withTime) {
    return date;
  }
  return `${date} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
}

/** 将模板解析为多行水印文本 */
export function resolveWatermarkContent(
  template: string,
  user: User | null | undefined,
  now: Date = new Date()
): string[] {
  const source = template?.trim() || DEFAULT_WATERMARK_CONTENT;
  const variables: Record<string, string> = {
    nickname: user?.nickname || '-',
    realName: user?.nickname || '-',
    phone: maskPhone(user?.phone),
    phoneLast4: getPhoneLast4(user?.phone),
    tenantName: user?.tenantName || '-',
    date: formatDateTime(now, false),
    datetime: formatDateTime(now, true)
  };

  return source.split('\n').map((line) =>
    line.replace(/\{(\w+)\}/g, (match, key: string) => variables[key] ?? match)
  );
}

export function parseWatermarkStyle(json?: string): WatermarkStyleConfig {
  if (!json?.trim()) {
    return { ...DEFAULT_WATERMARK_STYLE };
  }
  try {
    const parsed = JSON.parse(json) as Partial<WatermarkStyleConfig>;
    const gap = parsed.gap;
    return {
      fontSize: Number(parsed.fontSize) || DEFAULT_WATERMARK_STYLE.fontSize,
      color: parsed.color || DEFAULT_WATERMARK_STYLE.color,
      rotate:
        parsed.rotate != null
          ? Number(parsed.rotate)
          : DEFAULT_WATERMARK_STYLE.rotate,
      gap:
        Array.isArray(gap) && gap.length === 2
          ? [Number(gap[0]) || 200, Number(gap[1]) || 160]
          : [...DEFAULT_WATERMARK_STYLE.gap],
      zIndex: Number(parsed.zIndex) || DEFAULT_WATERMARK_STYLE.zIndex
    };
  } catch {
    return { ...DEFAULT_WATERMARK_STYLE };
  }
}

export function serializeWatermarkStyle(style: WatermarkStyleConfig): string {
  return JSON.stringify({
    fontSize: Number(style.fontSize),
    color: style.color,
    rotate: Number(style.rotate),
    gap: [Number(style.gap[0]), Number(style.gap[1])],
    zIndex: Number(style.zIndex)
  });
}

/** 从 rgba 字符串提取 alpha（0~1） */
export function getColorAlpha(color: string): number {
  const match = color.match(
    /rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*(?:,\s*([\d.]+)\s*)?\)/
  );
  if (!match) {
    return 0.12;
  }
  if (match[1] == null) {
    return 1;
  }
  return Number(match[1]) || 0.12;
}

/** 更新 rgba 的 alpha，保留 rgb 分量 */
export function setColorAlpha(color: string, alpha: number): string {
  const rgbaMatch = color.match(
    /rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*[\d.]+\s*\)/
  );
  if (rgbaMatch) {
    return `rgba(${rgbaMatch[1]}, ${rgbaMatch[2]}, ${rgbaMatch[3]}, ${alpha})`;
  }
  const rgbMatch = color.match(
    /rgb\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)/
  );
  if (rgbMatch) {
    return `rgba(${rgbMatch[1]}, ${rgbMatch[2]}, ${rgbMatch[3]}, ${alpha})`;
  }
  return `rgba(0, 0, 0, ${alpha})`;
}

export function buildWatermarkFont(
  style: WatermarkStyleConfig,
  darkMode: boolean
): WatermarkFontStyle {
  let color = style.color;
  if (darkMode && color.includes('0, 0, 0')) {
    color = color.replace(/rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,/i, 'rgba(255, 255, 255,');
  }
  return {
    color,
    fontSize: style.fontSize,
    fontWeight: 'normal',
    fontFamily: 'sans-serif'
  };
}

export interface WatermarkPattern {
  url: string;
  width: number;
  height: number;
}

/** 生成平铺水印背景图（不依赖 EleWatermark 授权逻辑） */
export function createWatermarkPattern(
  contents: string[],
  font: WatermarkFontStyle,
  rotate: number,
  gap: [number, number]
): WatermarkPattern | null {
  const lines = contents.map((line) => line.trim()).filter(Boolean);
  if (!lines.length) {
    return null;
  }

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return null;
  }

  const [gapX, gapY] = gap;
  const lineGap = 3;
  ctx.font = `${font.fontWeight} ${font.fontSize}px ${font.fontFamily}`;
  const textWidth = Math.ceil(
    Math.max(...lines.map((line) => ctx.measureText(line).width))
  );
  const textHeight = font.fontSize * lines.length + (lines.length - 1) * lineGap;
  const angle = (Math.PI / 180) * rotate;
  const absCos = Math.abs(Math.cos(angle));
  const absSin = Math.abs(Math.sin(angle));
  const markWidth = Math.ceil(textWidth * absCos + textHeight * absSin);
  const markHeight = Math.ceil(textWidth * absSin + textHeight * absCos);
  const ratio = window.devicePixelRatio || 1;
  const canvasWidth = (gapX + markWidth) * ratio;
  const canvasHeight = (gapY + markHeight) * ratio;

  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  ctx.scale(ratio, ratio);

  const drawX = gapX / 2;
  const drawY = gapY / 2;
  const rotateX = drawX + markWidth / 2;
  const rotateY = drawY + markHeight / 2;

  ctx.save();
  ctx.translate(rotateX, rotateY);
  ctx.rotate(angle);
  ctx.translate(-rotateX, -rotateY);
  ctx.fillStyle = font.color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  const textLeft = rotateX - textWidth / 2;
  const textTop = rotateY - textHeight / 2;
  lines.forEach((line, index) => {
    ctx.fillText(
      line,
      textLeft + textWidth / 2,
      textTop + index * (font.fontSize + lineGap)
    );
  });
  ctx.restore();

  return {
    url: canvas.toDataURL(),
    width: gapX + markWidth,
    height: gapY + markHeight
  };
}
