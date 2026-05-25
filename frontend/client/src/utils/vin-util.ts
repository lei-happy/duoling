/**
 * VIN 展示格式化
 * - 标准 17 位：按 ISO 3779 分为 WMI(3) + VDS(6) + VIS(8)
 * - 非 17 位：每 4 位一组，便于阅读
 */
export function normalizeVinRaw(vin?: string | null): string {
  if (vin == null || vin === '') return '';
  return String(vin)
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '');
}

export function formatVinDisplay(
  vin?: string | null,
  emptyPlaceholder = ''
): string {
  const raw = normalizeVinRaw(vin);
  if (!raw) return emptyPlaceholder;
  if (raw.length === 17) {
    return `${raw.slice(0, 3)}-${raw.slice(3, 9)}-${raw.slice(9)}`;
  }
  return raw.match(/.{1,4}/g)?.join('-') ?? raw;
}
