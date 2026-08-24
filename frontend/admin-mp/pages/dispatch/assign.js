const { ensureAuth } = require('../../utils/auth');
const { getTask, assignCarrier, completeCarrier, recommendCapacity } = require('../../api/task');
const { toast } = require('../../utils/request');
const { routeText } = require('../../utils/format');

Page({
  data: {
    ids: [],
    stage: 0,
    summary: {},
    caps: [],
    picked: null,
    margin: 18.6,
    loading: false
  },

  onLoad(query) {
    const ids = query.ids ? String(query.ids).split(',').filter(Boolean) : query.id ? [query.id] : [];
    this.setData({ ids, stage: Number(query.stage || 0) });
    this.load();
  },

  async load() {
    if (!ensureAuth()) return;
    const id = this.data.ids[0];
    if (!id) return;
    wx.showLoading({ title: '正在加载，请稍候…', mask: true });
    try {
      const [task, rec] = await Promise.all([
        getTask(id),
        recommendCapacity(id).catch(() => ({ items: [] }))
      ]);
      const items = (rec && rec.items) || (Array.isArray(rec) ? rec : []);
      this.setData({
        summary: {
          no: this.data.ids.length > 1 ? `${this.data.ids.length} 单` : task.taskNo,
          route: routeText(task.origin, task.destination),
          qty: task.totalQuantity
        },
        caps: items.map((x, i) => ({
          ...x,
          reason: (x.reasons && x.reasons[0] && x.reasons[0].text) || '可派',
          best: i === 0
        })),
        picked: items[0] || null
      });
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
    }
  },

  onPick(e) {
    const id = Number(e.currentTarget.dataset.id);
    const picked = this.data.caps.find((x) => x.capacityId === id);
    this.setData({ picked, margin: picked ? 18.6 : 12 });
  },

  onConfirm() {
    const picked = this.data.picked;
    if (!picked) {
      toast('请先选一台车');
      return;
    }
    wx.showModal({
      title: '确认派车',
      content: `派给 ${picked.plateNumber} ${picked.driverName}。派车后会立刻通知司机。`,
      confirmText: '确认派出',
      success: (res) => {
        if (res.confirm) this.submit();
      }
    });
  },

  async submit() {
    const { ids, stage, picked, loading } = this.data;
    if (!picked || loading) return;
    this.setData({ loading: true });
    wx.showLoading({ title: '正在派车，请稍候…', mask: true });
    try {
      const carrier = {
        carrierType: 1,
        capacityId: picked.capacityId,
        mainDriverName: picked.driverName,
        mainDriverPhone: picked.driverPhone,
        plateNumber: picked.plateNumber
      };
      for (const id of ids) {
        if (stage === -1) {
          await completeCarrier(id, carrier);
        } else {
          await assignCarrier(id, { carrier });
        }
      }
      toast('已派出');
      setTimeout(() => wx.navigateBack(), 400);
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
