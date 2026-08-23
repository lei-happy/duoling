const { toast } = require('./request');
const { DISPATCHER, RECEIVER, FLEET } = require('../services/mock/contacts');

const REJECT_REASONS = [
  '车辆故障，没法按时出发',
  '时间冲突，已经有别的单',
  '路线不熟 / 限行过不去',
  '身体不适',
  '其他'
];

function callPhone(phone) {
  if (!phone) {
    toast('电话还没配好，先在工作台找调度');
    return;
  }
  wx.makePhoneCall({
    phoneNumber: String(phone).replace(/\D/g, '') || phone,
    fail() {}
  });
}

function callDispatcher() {
  callPhone(DISPATCHER.phone);
}

function callReceiver() {
  callPhone(RECEIVER.phone);
}

function callFleet() {
  callPhone(FLEET.phone);
}

function goNav(opts) {
  const q = [];
  const o = opts || {};
  if (o.taskId) q.push(`id=${o.taskId}`);
  if (o.dest) q.push(`dest=${encodeURIComponent(o.dest)}`);
  if (o.taskNo) q.push(`no=${encodeURIComponent(o.taskNo)}`);
  wx.navigateTo({ url: `/pages/location/nav${q.length ? `?${q.join('&')}` : ''}` });
}

function goException(opts) {
  const q = [];
  const o = opts || {};
  if (o.taskId) q.push(`id=${o.taskId}`);
  if (o.taskNo) q.push(`no=${encodeURIComponent(o.taskNo)}`);
  if (o.route) q.push(`route=${encodeURIComponent(o.route)}`);
  wx.navigateTo({ url: `/pages/exception/pick${q.length ? `?${q.join('&')}` : ''}` });
}

function copyText(text, ok) {
  if (!text) {
    toast('没有可复制的内容');
    return;
  }
  wx.setClipboardData({
    data: String(text),
    success: () => toast(ok || '已复制')
  });
}

module.exports = {
  REJECT_REASONS,
  callPhone,
  callDispatcher,
  callReceiver,
  callFleet,
  goNav,
  goException,
  copyText
};
