const { getItem, setItem } = require('../../utils/storage');

const SEED = [
  {
    id: 'msg-1',
    kind: 'task',
    title: '新调令 TK2608090052',
    desc: '李敏派给你 · 明日 07:30 萧山中转库装车 · 6 台',
    time: '12 分钟前',
    unread: true,
    taskNo: 'TK2608090052',
    route: '杭州萧山中转库 → 宁波北仑港',
    loadTime: '2026-08-10 07:30',
    goods: '别克君威 6 台',
    dispatcher: '李敏 138****2043'
  },
  {
    id: 'msg-2',
    kind: 'money',
    title: '结算单已支付 ¥2,400',
    desc: 'TK2608080019 · 已转入工商银行 尾号 4218',
    time: '09:12',
    unread: true
  },
  {
    id: 'msg-3',
    kind: 'alert',
    title: '从业资格证 28 天后到期',
    desc: '把新证拍给车管李敏就行，别等到路上被查',
    time: '08:00',
    unread: true
  },
  {
    id: 'msg-4',
    kind: 'task',
    title: '回单已通过审核',
    desc: 'TK2608070008 · 结算单已生成，等财务打款',
    time: '昨天',
    unread: false
  },
  {
    id: 'msg-5',
    kind: 'money',
    title: '油卡余额低于 1,500 元',
    desc: '当前 ¥1,240，长途前记得申请充值',
    time: '昨天',
    unread: false
  },
  {
    id: 'msg-6',
    kind: 'alert',
    title: '调度 李敏',
    desc: '明天那单客户要求早点到，你看着安排',
    time: '08-08',
    unread: false
  }
];

function loadState() {
  return getItem('msg_state', { deleted: [], read: [] }) || { deleted: [], read: [] };
}

function saveState(state) {
  setItem('msg_state', state);
}

function listMessages() {
  const { deleted, read } = loadState();
  return SEED.filter((m) => deleted.indexOf(m.id) < 0).map((m) => ({
    ...m,
    unread: m.unread && read.indexOf(m.id) < 0
  }));
}

function getUnreadCount() {
  return listMessages().filter((m) => m.unread).length;
}

function getMessage(id) {
  return listMessages().find((m) => m.id === id) || null;
}

function markRead(id) {
  const state = loadState();
  if (state.read.indexOf(id) < 0) state.read.push(id);
  saveState(state);
}

function removeMessage(id) {
  const state = loadState();
  if (state.deleted.indexOf(id) < 0) state.deleted.push(id);
  saveState(state);
}

module.exports = {
  listMessages,
  getUnreadCount,
  getMessage,
  markRead,
  removeMessage
};
