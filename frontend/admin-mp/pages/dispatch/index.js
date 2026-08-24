const { ensureAuth } = require('../../utils/auth');
const { listTasks, taskStats } = require('../../api/task');
const { listOf, routeText, shortTime } = require('../../utils/format');

const STAGES = [
  { key: -1, label: '待分配', color: '#8c8cf0', totalKey: 'pendingAssign' },
  { key: 0, label: '待派车', color: '#2f54eb', totalKey: 'pendingDispatch' },
  { key: 1, label: '待装车', color: '#0ea5e9', totalKey: 'pendingLoad' },
  { key: 3, label: '在途', color: '#14b8a6', totalKey: 'onWay' },
  { key: 4, label: '待签收', color: '#16a34a', totalKey: 'pendingSign' }
];

const ACTION = {
  '-1': '确认承运',
  0: '派车',
  1: '看详情',
  3: '催位置',
  4: '催回单'
};

function mapRow(item) {
  return {
    id: item.id,
    taskNo: item.taskNo,
    route: routeText(item.origin, item.destination),
    qty: item.totalQuantity,
    plate: item.plateNumber || '',
    driver: item.mainDriverName || '',
    time: shortTime(item.plannedLoadTime || item.plannedArriveTime),
    alert: item.alertLevel >= 2 ? '超时' : item.alertLevel === 1 ? '临期' : '',
    phone: item.mainDriverPhone || ''
  };
}

Page({
  data: {
    stages: STAGES,
    stage: 0,
    counts: {},
    list: [],
    pickMode: false,
    picked: {},
    pickCount: 0,
    keyword: '',
    loading: false
  },

  onShow() {
    if (!ensureAuth()) return;
    this.reload();
  },

  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },

  async reload() {
    this.setData({ loading: true });
    try {
      const [stats, page] = await Promise.all([
        taskStats(),
        listTasks({ status: this.data.stage, keyword: this.data.keyword })
      ]);
      const totals = (stats && stats.totals) || {};
      this.setData({
        counts: totals,
        list: listOf(page).map(mapRow)
      });
    } catch (e) {
      /* toast 已处理 */
    } finally {
      this.setData({ loading: false });
    }
  },

  onStage(e) {
    const stage = Number(e.currentTarget.dataset.key);
    this.setData({ stage, pickMode: false, picked: {}, pickCount: 0 });
    this.reload();
  },

  onSearch(e) {
    this.setData({ keyword: (e.detail.value || '').trim() });
    this.reload();
  },

  togglePick() {
    this.setData({ pickMode: !this.data.pickMode, picked: {}, pickCount: 0 });
  },

  onCheck(e) {
    const id = e.currentTarget.dataset.id;
    const picked = { ...this.data.picked };
    if (picked[id]) delete picked[id];
    else picked[id] = true;
    this.setData({ picked, pickCount: Object.keys(picked).length });
  },

  onItem(e) {
    const id = e.currentTarget.dataset.id;
    if (this.data.pickMode) {
      this.onCheck(e);
      return;
    }
    const stage = this.data.stage;
    if (stage === 0 || stage === -1) {
      wx.navigateTo({ url: `/pages/dispatch/assign?id=${id}&stage=${stage}` });
      return;
    }
    if (stage === 3) {
      wx.navigateTo({ url: `/pages/track/detail?id=${id}` });
      return;
    }
    wx.navigateTo({ url: `/pages/dispatch/detail?id=${id}` });
  },

  onBatchAssign() {
    const ids = Object.keys(this.data.picked);
    if (!ids.length) return;
    wx.navigateTo({ url: `/pages/dispatch/assign?ids=${ids.join(',')}&stage=${this.data.stage}` });
  }
});
