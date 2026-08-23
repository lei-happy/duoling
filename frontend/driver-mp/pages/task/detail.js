const { ensureAuth } = require('../../utils/auth');
const {
  getTaskDetail,
  acceptTask,
  rejectTask,
  signItem
} = require('../../api/task');
const { formatDateTime, formatMoney } = require('../../utils/format');
const {
  getDriverDisplayStatus,
  getItemStatusInfo,
  getAvailableActions
} = require('../../utils/constants');
const { buildTicketView } = require('../../utils/task-view');
const { toast } = require('../../utils/request');
const {
  goNav,
  goException,
  callDispatcher,
  callReceiver,
  copyText,
  REJECT_REASONS
} = require('../../utils/action');

const CARRIER = { 1: '自有车', 2: '承运商', 3: '社会运力' };

function buildLogs(task) {
  const logs = [{ title: '调度已派车', sub: formatDateTime(task.plannedLoadTime) || '待定' }];
  if (task.accepted || task.acceptedAt) logs.push({ title: '已接收调令', sub: formatDateTime(task.acceptedAt) || '已接收' });
  if (task.actualLoadTime) logs.push({ title: '已确认装车', sub: formatDateTime(task.actualLoadTime) });
  if (task.status >= 3) logs.push({ title: '已确认出发', sub: formatDateTime(task.actualLoadTime) || '在途' });
  if (task.actualArriveTime) logs.push({ title: '已确认到达', sub: formatDateTime(task.actualArriveTime) });
  if (task.status >= 5) logs.push({ title: '已逐台签收', sub: formatDateTime(task.actualArriveTime) });
  return logs;
}

Page({
  data: {
    taskId: 0,
    task: null,
    statusInfo: { label: '', level: 'default' },
    itemsView: [],
    ticketView: {},
    itemCount: 0,
    plannedArriveText: '-',
    prepaidText: '0.00',
    settledText: '0.00',
    pendingText: '0.00',
    trailerPlate: '苏A·H7712挂',
    carrierText: '自有车',
    dispatcherName: '李敏',
    logs: [],
    mainAction: null,
    acting: false,
    sheet: '',
    rejectReason: '',
    rejectPick: '',
    rejectReasons: REJECT_REASONS,
    signVisible: false,
    signItemId: 0
  },

  onLoad(query) {
    this.setData({ taskId: Number(query.id) || 0 });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.load();
  },

  async load() {
    const id = this.data.taskId;
    if (!id) {
      toast('任务不存在');
      setTimeout(() => wx.navigateBack(), 500);
      return;
    }
    try {
      const task = await getTaskDetail(id);
      task.segments = task.segments || [];
      task.items = task.items || [];
      const statusInfo = getDriverDisplayStatus(task.status, task.accepted);
      const actions = getAvailableActions(task.status, task.accepted);
      const items = task.items || [];
      const prepaid = Number(task.prepaidAmount || 0);
      const settled = Number(task.settledAmount || 0);
      const cost = Number(task.carrierCostAmount || 0);
      const pending = Math.max(0, cost - settled - prepaid);
      this.setData({
        task,
        ticketView: buildTicketView(task),
        statusInfo,
        itemsView: items.map((it) => {
          const st = getItemStatusInfo(it.status);
          return {
            ...it,
            brandText: `${it.vehicleBrand || '-'} ${it.vehicleModel || ''}`.trim(),
            statusLabel: st.label,
            statusLevel: st.level,
            metaText: `${it.waybillNo || '-'} · ${it.customerName || '-'} · ${it.quantity} 台`
          };
        }),
        itemCount: items.length,
        plannedArriveText: formatDateTime(task.plannedArriveTime),
        prepaidText: formatMoney(prepaid),
        settledText: formatMoney(settled),
        pendingText: formatMoney(pending || Math.max(0, 3600 - prepaid - settled)),
        carrierText: CARRIER[task.carrierType] || '自有车',
        logs: buildLogs(task),
        mainAction: actions.find((a) => a.level !== 'danger') || actions[0] || null
      });
      wx.setNavigationBarTitle({ title: task.taskNo || '任务详情' });
    } catch (e) {
      /* handled */
    }
  },

  onMain() {
    const key = this.data.mainAction && this.data.mainAction.key;
    if (!key) return;
    if (key === 'sign-items') {
      wx.navigateTo({ url: `/pages/task/sign?id=${this.data.taskId}` });
      return;
    }
    if (key === 'reject') {
      this.setData({ sheet: 'reject', rejectReason: '', rejectPick: '' });
      return;
    }
    if (key === 'accept') {
      this.doAccept();
      return;
    }
    wx.navigateTo({ url: `/pages/task/execute?id=${this.data.taskId}&action=${key}` });
  },

  async doAccept() {
    if (this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在接收调令，请稍候…', mask: true });
    try {
      await acceptTask(this.data.taskId);
      toast('已接收调令，记得按时到装车点');
      await this.load();
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  onCall() {
    callDispatcher();
  },

  onCallRecv() {
    this.setData({ sheet: '' });
    callReceiver();
  },

  openMore() {
    this.setData({ sheet: 'more' });
  },

  closeSheet() {
    this.setData({ sheet: '' });
  },

  onNav() {
    this.setData({ sheet: '' });
    const t = this.data.task;
    goNav({ taskId: t.id, dest: t.destination, taskNo: t.taskNo });
  },

  onExcp() {
    this.setData({ sheet: '' });
    const t = this.data.task;
    goException({
      taskId: t.id,
      taskNo: t.taskNo,
      route: `${t.origin || ''} → ${t.destination || ''}`
    });
  },

  onCopy() {
    this.setData({ sheet: '' });
    copyText(this.data.task.taskNo, '单号已复制');
  },

  pickReject(e) {
    this.setData({ rejectPick: e.currentTarget.dataset.v });
  },

  onRejectReason(e) {
    this.setData({ rejectReason: e.detail.value || '' });
  },

  async submitReject() {
    const extra = (this.data.rejectReason || '').trim();
    const pick = this.data.rejectPick;
    const reason = pick === '其他' || !pick ? extra : (extra ? `${pick}；${extra}` : pick);
    if (!reason) {
      toast('请选择或填写拒单原因');
      return;
    }
    if (this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在提交，请稍候…', mask: true });
    try {
      await rejectTask(this.data.task.id, { reason });
      toast('已拒单');
      this.setData({ sheet: '' });
      setTimeout(() => wx.navigateBack(), 400);
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  onSignItem(e) {
    const itemId = e.currentTarget.dataset.id;
    if (!itemId || this.data.acting) return;
    this.setData({ signVisible: true, signItemId: itemId });
  },

  closeSign() {
    if (this.data.acting) return;
    this.setData({ signVisible: false, signItemId: 0 });
  },

  async submitSign() {
    const itemId = this.data.signItemId;
    if (!itemId || this.data.acting) return;
    this.setData({ acting: true, signVisible: false });
    wx.showLoading({ title: '正在确认交车，请稍候…', mask: true });
    try {
      await signItem(itemId);
      toast('交车成功');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false, signItemId: 0 });
    }
  },

  goReceipt() {
    wx.navigateTo({ url: `/pages/task/receipt?id=${this.data.taskId}` });
  },

  goFinance() {
    wx.navigateTo({ url: '/pages/finance/docs' });
  }
});
