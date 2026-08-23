/** 任务 / 财务展示常量（与 H5 status-config 对齐） */

const STATUS_MAP = {
  '-1': { label: '待分配', level: 'default' },
  0: { label: '待派车', level: 'warning' },
  1: { label: '已派车', level: 'primary' },
  2: { label: '已装车', level: 'primary' },
  3: { label: '在途', level: 'info' },
  4: { label: '已到达', level: 'info' },
  5: { label: '已交车', level: 'success' },
  7: { label: '已关闭', level: 'default' },
  9: { label: '已取消', level: 'danger' }
};

function getTaskStatusInfo(status) {
  return STATUS_MAP[status] || { label: '未知', level: 'default' };
}

function getDriverDisplayStatus(status, accepted) {
  if (status === 1) {
    return accepted
      ? { label: '待装车', level: 'default' }
      : { label: '待接收', level: 'warning' };
  }
  if (status === 4) return { label: '已到达', level: 'info' };
  if (status === 5) return { label: '已完成', level: 'success' };
  return getTaskStatusInfo(status);
}

/** 进行中任务筛选（已完成单独成页） */
const VISIBLE_STATUS_TABS = [
  { label: '全部', value: 'all' },
  { label: '待接收', value: 'waitAccept' },
  { label: '待装车', value: 'waitLoad' },
  { label: '在途', value: '3' },
  { label: '已到达', value: '4' }
];

const ITEM_STATUS_MAP = {
  0: { label: '待装车', level: 'warning' },
  1: { label: '已装车', level: 'primary' },
  2: { label: '已卸车', level: 'info' },
  3: { label: '已签收', level: 'success' }
};

function getItemStatusInfo(status) {
  return ITEM_STATUS_MAP[status] || { label: '未知', level: 'default' };
}

function getAvailableActions(status, accepted) {
  switch (status) {
    case 1:
      return accepted
        ? [{ key: 'confirm-load', label: '确认装车', level: 'primary' }]
        : [
            { key: 'accept', label: '接收调令', level: 'primary' },
            { key: 'reject', label: '拒绝', level: 'danger' }
          ];
    case 2:
      return [{ key: 'depart', label: '确认出发', level: 'primary' }];
    case 3:
      return [{ key: 'confirm-arrive', label: '确认到达', level: 'primary' }];
    case 4:
      return [{ key: 'sign-items', label: '去签收', level: 'success' }];
    default:
      return [];
  }
}

const FINANCE_DOC_TYPE = {
  1: '预付单',
  2: '补款单',
  3: '结算单'
};

const FINANCE_STATUS = {
  0: { label: '草稿', level: 'default' },
  1: { label: '待审批', level: 'warning' },
  2: { label: '已审批', level: 'info' },
  3: { label: '已支付', level: 'success' },
  4: { label: '已撤销', level: 'default' }
};

const PAY_METHOD = {
  1: '银行转账',
  2: '油卡',
  3: '油气款',
  4: '现金',
  5: '微信',
  6: '支付宝'
};

const ACCOUNT_TYPE = {
  1: '银行卡',
  2: '油气款',
  3: '积分'
};

const FUND_BIZ_TYPE_LABELS = {
  1: '预付登记',
  2: '退款入账',
  3: '人工入账',
  4: '人工出账',
  5: '人工调整',
  6: '任务抵扣',
  7: '任务结算入账'
};

function fundBizTypeLabel(v) {
  return v != null ? FUND_BIZ_TYPE_LABELS[v] || '其他' : '其他';
}

const LEVEL_COLOR = {
  default: '#94a3b8',
  primary: '#1d4ed8',
  success: '#16a34a',
  warning: '#f59e0b',
  danger: '#dc2626',
  info: '#0ea5e9'
};

module.exports = {
  getTaskStatusInfo,
  getDriverDisplayStatus,
  VISIBLE_STATUS_TABS,
  getItemStatusInfo,
  getAvailableActions,
  FINANCE_DOC_TYPE,
  FINANCE_STATUS,
  PAY_METHOD,
  ACCOUNT_TYPE,
  fundBizTypeLabel,
  LEVEL_COLOR
};
