import type { FreightContract } from '@/api/billing/contract/model';

/** 解析 YYYY-MM-DD 为本地日历日 0 点 */
export function parseContractYmd(s?: string | null): Date | null {
  if (!s?.trim()) return null;
  const p = s
    .trim()
    .split('-')
    .map((x) => Number(x));
  if (p.length !== 3 || p.some((n) => !Number.isFinite(n))) return null;
  return new Date(p[0], p[1] - 1, p[2]);
}

export function isContractExpiredByDate(expiryDate?: string | null): boolean {
  const d = parseContractYmd(expiryDate ?? undefined);
  if (!d) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  d.setHours(0, 0, 0, 0);
  return d < today;
}

/** 列表/详情展示用：结合 DB status 与有效期判断「已过期」 */
export function getContractStatusDisplay(
  row: Pick<FreightContract, 'status' | 'expiryDate'>
) {
  const s = row.status;
  if (s === 0) {
    return { text: '草稿', elType: 'info' as const };
  }
  if (s === 2) {
    return { text: '已终止', elType: 'danger' as const };
  }
  if (s === 3) {
    return { text: '已终止', elType: 'danger' as const };
  }
  if (s === 1 && isContractExpiredByDate(row.expiryDate)) {
    return { text: '已过期', elType: 'warning' as const };
  }
  if (s === 1) {
    return { text: '生效', elType: 'success' as const };
  }
  return { text: '-', elType: 'info' as const };
}

export function formatContractValidPeriod(
  effective?: string | null,
  expiry?: string | null
): string {
  const a = effective?.trim() || '—';
  const b = expiry?.trim() || '—';
  return `${a} ~ ${b}`;
}
