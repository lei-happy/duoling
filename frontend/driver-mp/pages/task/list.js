const { ensureAuth } = require('../../utils/auth');
const { listMyTasks, acceptTask, rejectTask } = require('../../api/task');
const { VISIBLE_STATUS_TABS } = require('../../utils/constants');
const { toast } = require('../../utils/request');
const { getFontScale } = require('../../utils/font');
const {
  buildTicketView,
  groupByDay,
  matchChip,
  apiStatusForChip
} = require('../../utils/task-view');

const EMPTY_FILTER = { range: '15', timeType: 'plannedLoad', carrier: '' };

function withinRange(task, filter) {
  const days = filter.range === '3' ? 3 : filter.range === '7' ? 7 : filter.range === 'month' ? 31 : 15;
  const field = filter.timeType === 'plannedArrive' ? task.plannedArriveTime : task.plannedLoadTime;
  if (!field) return filter.range === '15' || filter.range === '';
  const t = new Date(field).getTime();
  if (Number.isNaN(t)) return true;
  if (filter.range === 'month') {
    const now = new Date();
    const d = new Date(field);
    return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
  }
  return Date.now() - t <= days * 86400000 && t - Date.now() <= days * 86400000;
}

Page({
  data: {
    fontClass: 'font-lg',
    chips: [],
    activeChip: 'all',
    keyword: '',
    groups: [],
    loading: false,
    sheet: '',
    filter: { ...EMPTY_FILTER },
    filterOn: false,
    rejectReason: '',
    rejectId: 0,
    acting: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    const app = getApp();
    if (app && app.globalData.taskStatusFilter) {
      const next = String(app.globalData.taskStatusFilter);
      app.globalData.taskStatusFilter = '';
      if (next && next !== this.data.activeChip) {
        this.setData({ activeChip: next === '1' ? 'waitAccept' : next });
      }
    }
    this.reload();
  },

  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },

  onChipChange(e) {
    const value = (e.detail && e.detail.value) || 'all';
    if (value === 'done') {
      wx.navigateTo({ url: '/pages/task/done' });
      return;
    }
    this.setData({ activeChip: value });
    this.reload();
  },

  onKeyword(e) {
    this.setData({ keyword: (e.detail && e.detail.value) || '' });
  },

  onSearch() {
    this.reload();
  },

  async reload() {
    this.setData({ loading: true });
    try {
      const chip = this.data.activeChip;
      const params = { page: 1, pageSize: 50 };
      const status = apiStatusForChip(chip);
      if (status !== '') params.status = status;
      if (this.data.keyword) params.keyword = this.data.keyword;
      const [res, countPack] = await Promise.all([
        listMyTasks(params),
        this.fetchCounts()
      ]);
      let list = (res && res.list) || [];
      list = list.filter((t) => matchChip(t, chip));
      const filter = this.data.filter;
      list = list.filter((t) => withinRange(t, filter));
      if (filter.carrier) {
        list = list.filter((t) => String(t.carrierType) === String(filter.carrier));
      }
      const views = list.map((t) => ({ ...buildTicketView(t), offset: 0 }));
      this.setData({
        groups: groupByDay(views),
        chips: this.buildChips(countPack)
      });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  },

  async fetchCounts() {
    try {
      const [all, s1, s3, s4] = await Promise.all([
        listMyTasks({ page: 1, pageSize: 50 }),
        listMyTasks({ status: 1, page: 1, pageSize: 50 }),
        listMyTasks({ status: 3, page: 1, pageSize: 1 }),
        listMyTasks({ status: 4, page: 1, pageSize: 1 })
      ]);
      const active = ((all && all.list) || []).filter((t) => matchChip(t, 'all'));
      const status1 = (s1 && s1.list) || [];
      return {
        all: active.length,
        waitAccept: status1.filter((t) => !t.accepted).length,
        waitLoad: status1.filter((t) => t.accepted).length,
        inTransit: (s3 && s3.total) || 0,
        waitSign: (s4 && s4.total) || 0
      };
    } catch (e) {
      return { all: 0, waitAccept: 0, waitLoad: 0, inTransit: 0, waitSign: 0 };
    }
  },

  buildChips(c) {
    const map = {
      all: c.all,
      waitAccept: c.waitAccept,
      waitLoad: c.waitLoad,
      '3': c.inTransit,
      '4': c.waitSign
    };
    return VISIBLE_STATUS_TABS.map((t) => ({
      ...t,
      count: map[t.value]
    })).concat([{ label: '已完成', value: 'done' }]);
  },

  onTaskTap(e) {
    const id = e.detail && e.detail.id;
    if (id) wx.navigateTo({ url: `/pages/task/detail?id=${id}` });
  },

  onTicketAction(e) {
    const { action, id } = e.detail || {};
    if (action === 'sign' && id) {
      wx.navigateTo({ url: `/pages/task/sign?id=${id}` });
    }
  },

  onNav(e) {
    const dest = e.currentTarget.dataset.dest;
    if (dest && dest !== '-') {
      wx.setClipboardData({
        data: dest,
        success: () => toast('目的地已复制，导航还没接上，先贴到地图里用')
      });
      return;
    }
    toast('导航还没接上，先到任务详情里看卸货点');
  },

  onDispatch() {
    toast('调度电话由企业配置后才能拨打');
  },

  onTouchStart(e) {
    this._sx = e.touches[0].clientX;
    this._sy = e.touches[0].clientY;
    this._gid = e.currentTarget.dataset.gid;
    this._tid = e.currentTarget.dataset.tid;
    this._lock = '';
  },

  onTouchMove(e) {
    if (this._sx == null) return;
    const dx = e.touches[0].clientX - this._sx;
    const dy = e.touches[0].clientY - this._sy;
    if (!this._lock) {
      if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
      this._lock = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
    }
    if (this._lock !== 'x') return;
    const offset = Math.min(0, Math.max(-152, dx));
    this.patchOffset(this._tid, offset);
  },

  onTouchEnd() {
    if (this._tid == null) return;
    const groups = this.data.groups;
    let current = 0;
    groups.forEach((g) => {
      g.list.forEach((t) => {
        if (t.id === this._tid) current = t.offset || 0;
      });
    });
    this.patchOffset(this._tid, current < -76 ? -152 : 0);
    this._sx = null;
    this._tid = null;
  },

  patchOffset(id, offset) {
    const groups = (this.data.groups || []).map((g) => ({
      ...g,
      list: g.list.map((t) => (t.id === id ? { ...t, offset } : { ...t, offset: t.id === id ? offset : 0 }))
    }));
    this.setData({ groups });
  },

  openFilter() {
    this.setData({ sheet: 'filter' });
  },

  setFilter(e) {
    const { k, v } = e.currentTarget.dataset;
    this.setData({ [`filter.${k}`]: v });
  },

  clearFilter() {
    this.setData({ filter: { ...EMPTY_FILTER }, filterOn: false, sheet: '' });
    this.reload();
  },

  applyFilter() {
    const f = this.data.filter;
    const on = f.range !== '15' || f.carrier !== '' || f.timeType !== 'plannedLoad';
    this.setData({ sheet: '', filterOn: on });
    this.reload();
  },

  openReject(e) {
    this.setData({
      sheet: 'reject',
      rejectId: Number(e.currentTarget.dataset.id),
      rejectReason: ''
    });
  },

  closeSheet() {
    if (this.data.acting) return;
    this.setData({ sheet: '', rejectId: 0 });
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
      await this.reload();
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
      this.setData({ sheet: '', rejectId: 0 });
      await this.reload();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  }
});
