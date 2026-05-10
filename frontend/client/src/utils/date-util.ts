import dayjs from 'dayjs';

/** 列表、详情等场景统一展示格式：年-月-日 时:分:秒 */
export const DATE_TIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';

/**
 * 将接口返回的时间（含 ISO 8601 含 `T`）格式化为项目统一展示格式。
 * 空值返回占位符；无法解析时返回原值的字符串形式。
 */
export function formatDateTime(
  val?: string | number | Date | null,
  emptyPlaceholder = '-'
): string {
  if (val == null || val === '') return emptyPlaceholder;
  const d = dayjs(val);
  return d.isValid() ? d.format(DATE_TIME_FORMAT) : String(val);
}

/** 含今天在内涵盖 7 个自然日：自 (今天−6) 日 00:00:00 至当日 23:59:59 */
export function getLast7DaysDateTimeRange(): [string, string] {
  const end = dayjs().endOf('day');
  const start = dayjs().subtract(6, 'day').startOf('day');
  return [start.format(DATE_TIME_FORMAT), end.format(DATE_TIME_FORMAT)];
}
