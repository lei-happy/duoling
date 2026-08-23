const { ensureAuth } = require('../../utils/auth');
const { getUserInfo, getTenantCode } = require('../../services/session');
const { listMyTasks, acceptTask, rejectTask } = require('../../api/task');
const { listMyReceipts } = require('../../api/task-receipt');
const { toast } = require('../../utils/request');
const { getCapsuleSafe, greetingByHour } = require('../../utils/nav');
const { getFontScale } = require('../../utils/font');
const { buildTicketView, weekDays, isActiveTask } = require('../../utils/task-view');
const { getWeather } = require('../../services/mock/weather');
const { getUnreadCount } = require('../../services/mock/message');
const { goNav, goException, callDispatcher, REJECT_REASONS } = require('../../utils/action');

Page({
  data: {
    fontClass: 'font-lg',
    padTop: 48,
    padRight: 96,
    hello: '师傅，你好',
    tenantName: '',
    kpi: { waitAccept: 0, waitLoad: 0, inTransit: 0, waitSign: 0 },
    running: null,
    pending: [],
    receiptHint: null,
    week: { days: [], rangeText: '', tripCount: 0, kmText: '0', sundayRest: false },
    weather: getWeather(),
    unread: 0,
    sheet: '',
    rejectReason: '',
    rejectPick: '',
    rejectReasons: REJECT_REASONS,
    rejectId: 0,
    acting: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    const safe = getCapsuleSafe();
    const user = getUserInfo() || {};
    const name = user.realName || '师傅';
    this.setData({
      fontClass: getFontScale().className,
      padTop: safe.padTop,
      padRight: safe.padRight,
      hello: greetingByHour(name),
      tenantName: user.tenantName || getTenantCode() || '未选择企业',
      weather: getWeather(),
      unread: getUnreadCount()
    });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    try {
      const [dispatched, transit, arrived, recent, receipts] = await Promise.all([
        listMyTasks({ status: 1, page: 1, pageSize: 50 }),
        listMyTasks({ status: 3, page: 1, pageSize: 5 }),
        listMyTasks({ status: 4, page: 1, pageSize: 5 }),
        listMyTasks({ page: 1, pageSize: 40 }),
        listMyReceipts({ page: 1, pageSize: 50 }).catch(() => ({ list: [] }))
      ]);
      const status1 = (dispatched && dispatched.list) || [];
      const waitAccept = status1.filter((t) => !t.accepted);
      const waitLoad = status1.filter((t) => t.accepted);
      const inTransit = (transit && transit.list) || [];
      const waitSign = (arrived && arrived.list) || [];
      const all = (recent && recent.list) || [];
      const loaded = all.filter((t) => t.status === 2);
      const runningTask = inTransit[0] || loaded[0] || null;
      const receiptIds = new Set(((receipts && receipts.list) || []).map((r) => r.taskId));
      const needReceipt = all.find((t) => t.status === 5 && !receiptIds.has(t.id));

      this.setData({
        kpi: {
          waitAccept: waitAccept.length,
          waitLoad: waitLoad.length,
          inTransit: (transit && transit.total) || inTransit.length,
          waitSign: (arrived && arrived.total) || waitSign.length
        },
        running: runningTask ? buildTicketView(runningTask) : null,
        pending: waitAccept.slice(0, 3).map(buildTicketView),
        receiptHint: needReceipt
          ? {
              id: needReceipt.id,
              title: `${needReceipt.taskNo} 的回单还没传`,
              desc: '回单不传，这一单的结算就卡着。'
            }
          : null,
        week: weekDays(all.filter(isActiveTask).concat(all.filter((t) => t.status === 5)))
      });
    } catch (e) {
      /* handled */
    }
  },

  goTask(e) {
    const chip = (e.currentTarget.dataset && e.currentTarget.dataset.chip) || 'all';
    const app = getApp();
    if (app) app.globalData.taskStatusFilter = chip;
    wx.switchTab({ url: '/pages/task/list' });
  },

  goTaskAll() {
    const app = getApp();
    if (app) app.globalData.taskStatusFilter = 'all';
    wx.switchTab({ url: '/pages/task/list' });
  },

  goFinance() {
    wx.switchTab({ url: '/pages/finance/list' });
  },

  goSwitchTenant() {
    wx.navigateTo({ url: '/pages/profile/switch-tenant' });
  },

  goMessage() {
    wx.navigateTo({ url: '/pages/message/index' });
  },

  onTaskTap(e) {
    const id = e.detail && e.detail.id;
    if (id) wx.navigateTo({ url: `/pages/task/detail?id=${id}` });
  },

  onNav() {
    const run = this.data.running;
    goNav({
      taskId: run && run.id,
      dest: run && run.destination && run.destination.title,
      taskNo: run && run.taskNo
    });
  },

  onCallDispatch() {
    callDispatcher();
  },

  onReceipt() {
    wx.navigateTo({ url: '/pages/task/inbox' });
  },

  goReceiptHint() {
    const id = this.data.receiptHint && this.data.receiptHint.id;
    if (id) wx.navigateTo({ url: `/pages/task/receipt?id=${id}` });
  },

  goFuel() {
    wx.navigateTo({ url: '/pages/finance/fund-account' });
  },

  openExcp() {
    const run = this.data.running;
    goException({
      taskId: run && run.id,
      taskNo: run && run.taskNo,
      route: run ? `${run.origin.title} → ${run.destination.title}` : ''
    });
  },

  openReject(e) {
    const id = Number(e.currentTarget.dataset.id);
    this.setData({ sheet: 'reject', rejectId: id, rejectReason: '', rejectPick: '' });
  },

  closeSheet() {
    if (this.data.acting) return;
    this.setData({ sheet: '', rejectId: 0, rejectReason: '' });
  },

  pickReject(e) {
    this.setData({ rejectPick: e.currentTarget.dataset.v });
  },

  onRejectReason(e) {
    this.setData({ rejectReason: (e.detail && e.detail.value) || '' });
  },

  async onAccept(e) {
    const id = Number(e.currentTarget.dataset.id);
    if (!id || this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在接收调令，请稍候…', mask: true });
    try {
      await acceptTask(id);
      toast('已接收调令，记得按时到装车点');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  async submitReject() {
    const extra = (this.data.rejectReason || '').trim();
    const pick = this.data.rejectPick;
    const reason = pick === '其他' || !pick ? extra : (extra ? `${pick}；${extra}` : pick);
    if (!reason) {
      toast('请选择或填写拒单原因');
      return;
    }
    if (!this.data.rejectId || this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在提交，请稍候…', mask: true });
    try {
      await rejectTask(this.data.rejectId, { reason });
      toast('已拒单');
      this.setData({ sheet: '', rejectId: 0, rejectReason: '' });
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  onDepart() {
    const id = this.data.running && this.data.running.id;
    if (id) wx.navigateTo({ url: `/pages/task/execute?id=${id}&action=depart` });
  },

  onArrive() {
    const id = this.data.running && this.data.running.id;
    if (id) wx.navigateTo({ url: `/pages/task/execute?id=${id}&action=confirm-arrive` });
  }
});
