const { ensureAuth } = require('../../utils/auth');
const { getUserInfo, getTenantCode, isRealTenantName, updateUserInfo } = require('../../services/session');
const { getUserInfoApi, getUserTenants } = require('../../api/auth');
const { listMyTasks, acceptTask, rejectTask } = require('../../api/task');
const { listMyReceipts } = require('../../api/task-receipt');
const { toast } = require('../../utils/request');
const { getCapsuleSafe } = require('../../utils/nav');
const { getFontScale } = require('../../utils/font');
const { buildWorkbenchView, weekDays, isActiveTask, shortTime } = require('../../utils/task-view');
const { getWeather } = require('../../services/mock/weather');
const { goNav, goException, callDispatcher, REJECT_REASONS } = require('../../utils/action');

Page({
  data: {
    fontClass: 'font-lg',
    padTop: 48,
    padRight: 96,
    displayName: '师傅',
    plateText: '',
    avatar: '',
    avatarText: '司',
    tenantName: '',
    kpi: { waitAccept: 0, waitLoad: 0, inTransit: 0, waitSign: 0 },
    running: null,
    pending: [],
    receiptHint: null,
    week: { days: [], rangeText: '', tripCount: 0, kmText: '0', sundayRest: false },
    weather: getWeather(),
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
      displayName: name,
      avatar: user.avatar || '',
      avatarText: name.slice(0, 1),
      tenantName: isRealTenantName(user.tenantName) ? user.tenantName : '当前企业',
      weather: getWeather()
    });
    this.refreshIdentity(user);
    this.load();
  },

  async refreshIdentity(user) {
    const code = (user && user.tenantCode) || getTenantCode();
    let tenantName = user && user.tenantName;
    let avatar = (user && user.avatar) || '';
    let displayName = (user && user.realName) || this.data.displayName;
    try {
      const info = await getUserInfoApi();
      if (info) {
        if (isRealTenantName(info.tenantName)) tenantName = info.tenantName;
        if (info.avatar) avatar = info.avatar;
        if (info.realName) displayName = info.realName;
      }
    } catch (e) {
      /* handled */
    }
    if (!isRealTenantName(tenantName) && code) {
      try {
        const raw = await getUserTenants();
        const list = Array.isArray(raw) ? raw : (raw && raw.list) || [];
        const hit = list.find((t) => (t.tenantCode || t.tenant_code) === code);
        const n = hit && (hit.tenantName || hit.tenant_name);
        if (isRealTenantName(n)) tenantName = n;
      } catch (e) {
        /* handled */
      }
    }
    const nextName = isRealTenantName(tenantName) ? tenantName : '当前企业';
    updateUserInfo({
      tenantName: nextName === '当前企业' ? user.tenantName : nextName,
      avatar,
      realName: displayName
    });
    this.setData({
      tenantName: nextName,
      avatar,
      displayName,
      avatarText: String(displayName || '司').slice(0, 1)
    });
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
        running: runningTask ? buildWorkbenchView(runningTask) : null,
        pending: waitAccept.slice(0, 3).map(buildWorkbenchView),
        plateText:
          (runningTask && runningTask.plateNumber) ||
          (all.find((t) => t.plateNumber) || {}).plateNumber ||
          '',
        receiptHint: needReceipt
          ? {
              id: needReceipt.id,
              title: `${needReceipt.taskNo} 的回单还没传`,
              desc: needReceipt.actualArriveTime
                ? `${shortTime(needReceipt.actualArriveTime)} 已签收，去上传回单即可结算。`
                : '签收后记得上传回单，才能结算。'
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

  goProfile() {
    wx.switchTab({ url: '/pages/profile/index' });
  },

  onTaskTap(e) {
    const id = e.detail && e.detail.id;
    if (id) wx.navigateTo({ url: `/pages/task/detail?id=${id}` });
  },

  onCardAction(e) {
    const detail = e.detail || {};
    const action = detail.action;
    const id = Number(detail.id);
    if (action === 'nav') this.onNav();
    else if (action === 'arrive') this.onArrive();
    else if (action === 'depart') this.onDepart();
    else if (action === 'reject') this.openReject({ currentTarget: { dataset: { id } } });
    else if (action === 'accept') this.onAccept({ currentTarget: { dataset: { id } } });
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
