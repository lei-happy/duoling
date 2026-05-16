/** 任务单费用单状态/类型/支付方式映射 */

export const FIN_DOC_TYPE_OPTIONS = [
  { value: 1, label: '预付单', type: 'primary' },
  { value: 2, label: '补款单', type: 'warning' },
  { value: 3, label: '结算单', type: 'success' }
] as const;

export const FIN_DOC_TYPE_MAP: Record<number, { label: string; type: string }> =
  FIN_DOC_TYPE_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

export const FIN_STATUS_OPTIONS = [
  { value: 0, label: '草稿', type: 'info' },
  { value: 1, label: '待审批', type: 'warning' },
  { value: 2, label: '已审批', type: 'primary' },
  { value: 3, label: '已支付', type: 'success' },
  { value: 4, label: '已撤销', type: 'danger' }
] as const;

export const FIN_STATUS_MAP: Record<number, { label: string; type: string }> =
  FIN_STATUS_OPTIONS.reduce(
    (m, x) => {
      m[x.value] = { label: x.label, type: x.type };
      return m;
    },
    {} as Record<number, { label: string; type: string }>
  );

export const PAY_METHOD_OPTIONS = [
  { value: 1, label: '银行转账' },
  { value: 2, label: '油卡' },
  { value: 3, label: '油气款' },
  { value: 4, label: '现金' },
  { value: 5, label: '微信' },
  { value: 6, label: '支付宝' }
] as const;

export const PAYEE_TYPE_OPTIONS = [
  { value: 1, label: '司机', type: 'primary' },
  { value: 2, label: '承运商', type: 'success' },
  { value: 3, label: '其他', type: 'info' }
] as const;

export const EXPENSE_TYPE_OPTIONS = [
  { value: 'oil', label: '油费' },
  { value: 'toll', label: '过路费' },
  { value: 'loading', label: '装卸费' },
  { value: 'parking', label: '停车费' },
  { value: 'meal', label: '餐补' },
  { value: 'repair', label: '维修费' },
  { value: 'other', label: '其他' }
] as const;
