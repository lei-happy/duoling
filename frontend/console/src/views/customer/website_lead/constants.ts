/** 官网线索的枚举口径，列表、搜索、跟进弹窗共用一份 */

export const STATUS_OPTIONS = [
  { label: '待联系', value: 0 },
  { label: '已联系', value: 1 },
  { label: '已转化', value: 2 },
  { label: '无效', value: 3 }
] as const;

export const FLEET_OPTIONS = [
  { label: '10 台以内', value: 'lt10' },
  { label: '10–30 台', value: '10-30' },
  { label: '30–100 台', value: '30-100' },
  { label: '100 台以上', value: 'gt100' }
] as const;

export const STAGE_BANDS = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8'];

/** 画像题的题面与选项，用来把 P1/P2/P3 的原始值翻译成人话 */
const PROFILE_LABELS: Record<string, { text: string; map: Record<string, string> }> = {
  P1: {
    text: '自有板车规模',
    map: {
      lt10: '10 台以内',
      '10-30': '10–30 台',
      '30-100': '30–100 台',
      gt100: '100 台以上'
    }
  },
  P2: {
    text: '目前靠什么管业务',
    map: {
      excel: 'Excel 和微信',
      bypass: '有系统，但一线常绕路',
      online: '系统已是主流程'
    }
  },
  P3: {
    text: '最想先解决的一块',
    map: {
      plan: '计划调度',
      receipt: '回单在途',
      recon: '对账结算',
      cost: '成本利润',
      energy: '能源加油'
    }
  }
};

export const statusLabel = (s?: number | null) =>
  STATUS_OPTIONS.find((o) => o.value === s)?.label || '-';

export const statusTagType = (s?: number | null) =>
  ({ 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' })[s ?? -1] || 'info';

export const fleetLabel = (v?: string | null) =>
  FLEET_OPTIONS.find((o) => o.value === v)?.label || '-';

/** 把 {P1:'gt100'} 翻成 [{题面, 答案}]，运营看的是中文不是枚举值 */
export function readableProfile(answers?: Record<string, string> | null) {
  if (!answers) {
    return [];
  }
  return Object.entries(answers).map(([key, value]) => {
    const meta = PROFILE_LABELS[key];
    return {
      label: meta?.text || key,
      value: meta?.map[value] || value
    };
  });
}
