const { getItem, setItem } = require('../../utils/storage');

const TYPES = [
  { key: 'fault', title: '车辆故障', desc: '抛锚、爆胎、仪表报警', tone: 'amber', icon: 'wrench' },
  { key: 'crash', title: '交通事故', desc: '刮碰、追尾，需要立刻通知', tone: 'red', icon: 'warn' },
  { key: 'delay', title: '运输延误', desc: '堵车、排队、恶劣天气', tone: 'gold', icon: 'clock' },
  { key: 'damage', title: '货损 / 数量不符', desc: '商品车受损或台数对不上', tone: 'info', icon: 'box' }
];

const ICON_BY_TYPE = {
  fault: 'wrench',
  crash: 'warn',
  delay: 'clock',
  damage: 'box'
};

const REASONS = {
  delay: ['高速堵车', '前方事故封路', '恶劣天气', '装卸排队', '限行管制', '其他'],
  fault: ['爆胎', '仪表报警', '抛锚无法行驶', '其他'],
  crash: [],
  damage: ['外观刮碰', '数量不符', '淋雨受潮', '其他']
};

const DELAYS = ['30 分钟内', '1 小时左右', '2 小时以上', '说不好'];

const SEED = [
  {
    id: 'ex-1',
    type: 'delay',
    title: '长深高速堵车，延误约 1 小时',
    taskNo: 'TK2608060015',
    time: '08-06 15:22',
    status: '已处理',
    oldEta: '08-06 17:00',
    newEta: '08-06 18:10',
    reply: '已知晓，客户已通知，按新时间卸货即可。'
  },
  {
    id: 'ex-2',
    type: 'fault',
    title: '左后轮胎压报警，已换备胎',
    taskNo: 'TK2607280042',
    time: '07-28 09:05',
    status: '已处理',
    oldEta: '',
    newEta: '',
    reply: '备胎已换，继续跑。回场后到车管换新胎。'
  }
];

function listHistory() {
  const extra = getItem('excp_list', []) || [];
  return extra.concat(SEED);
}

function addReport(item) {
  const extra = getItem('excp_list', []) || [];
  const row = {
    id: `ex-${Date.now()}`,
    status: '处理中',
    time: formatNow(),
    ...item
  };
  extra.unshift(row);
  setItem('excp_list', extra);
  return row;
}

function getById(id) {
  return listHistory().find((x) => x.id === id) || null;
}

function formatNow() {
  const d = new Date();
  const mm = `${d.getMonth() + 1}`.padStart(2, '0');
  const dd = `${d.getDate()}`.padStart(2, '0');
  const hh = `${d.getHours()}`.padStart(2, '0');
  const mi = `${d.getMinutes()}`.padStart(2, '0');
  return `${mm}-${dd} ${hh}:${mi}`;
}

module.exports = {
  TYPES,
  ICON_BY_TYPE,
  REASONS,
  DELAYS,
  listHistory,
  addReport,
  getById
};
