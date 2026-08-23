const { ensureAuth } = require('../../utils/auth');
const { getUserInfo, getTenantCode } = require('../../services/session');
const { listMyTasks, acceptTask, rejectTask, depart, confirmArrive } = require('../../api/task');
const { listMyReceipts } = require('../../api/task-receipt');
const { toast } = require('../../utils/request');
const { getCapsuleSafe, greetingByHour } = require('../../utils/nav');
const { getFontScale } = require('../../utils/font');
const { buildTicketView, weekDays, isActiveTask } = require('../../utils/task-view');

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
    week: { days: [], rangeText: '', tripCount: 0, sundayRest: false },
    sheet: '',
    rejectReason: '',
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
      tenantName: user.tenantName || getTenantCode() || '未选择企业'
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

  onNavHint() {
    const dest = this.data.running && this.data.running.destination && this.data.running.destination.title;
    if (dest && dest !== '-') {
      wx.setClipboardData({
        data: dest,
        success: () => toast('目的地已复制，导航还没接上，先贴到地图里用')
      });
      return;
    }
    toast('导航还没接上，先到任务详情里看卸货点');
  },

  onReceipt() {
    if (this.data.receiptHint) {
      this.goReceiptHint();
      return;
    }
    toast('这会儿没有待传的回单');
  },

  goReceiptHint() {
    const id = this.data.receiptHint && this.data.receiptHint.id;
    if (id) wx.navigateTo({ url: `/pages/task/receipt?id=${id}` });
  },

  goFuel() {
    toast('油卡流水还没接上，先去看资金账户');
    wx.navigateTo({ url: '/pages/finance/fund-account' });
  },

  openExcp() {
    this.setData({ sheet: 'excp' });
  },

  openReject(e) {
    const id = Number(e.currentTarget.dataset.id);
    this.setData({ sheet: 'reject', rejectId: id, rejectReason: '' });
  },

  closeSheet() {
    if (this.data.acting) return;
    this.setData({ sheet: '', rejectId: 0, rejectReason: '' });
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
    const reason = (this.data.rejectReason || '').trim();
    if (!reason) {
      toast('请填写拒单原因');
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

  async onDepart() {
    const id = this.data.running && this.data.running.id;
    if (!id || this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在确认出发，请稍候…', mask: true });
    try {
      await depart(id);
      toast('已确认出发');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  async onArrive() {
    const id = this.data.running && this.data.running.id;
    if (!id || this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在确认到达，请稍候…', mask: true });
    try {
      await confirmArrive(id);
      toast('已确认到达');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  }
});
