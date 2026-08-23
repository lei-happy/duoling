const { ensureAuth } = require('../../utils/auth');
const { listMyTasks } = require('../../api/task');
const { getFontScale } = require('../../utils/font');
const { formatDate } = require('../../utils/format');

function inMonth(value, offset) {
  if (!value) return false;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return false;
  const now = new Date();
  const y = now.getFullYear();
  const m = now.getMonth() + offset;
  const target = new Date(y, m, 1);
  return d.getFullYear() === target.getFullYear() && d.getMonth() === target.getMonth();
}

Page({
  data: {
    fontClass: 'font-lg',
    range: 'month',
    list: [],
    stats: { trips: 0, qty: 0 },
    loading: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  onRange(e) {
    this.setData({ range: e.currentTarget.dataset.v });
    this.load();
  },

  async load() {
    this.setData({ loading: true });
    try {
      const res = await listMyTasks({ status: 5, page: 1, pageSize: 50 });
      const offset = this.data.range === 'prev' ? -1 : 0;
      const raw = ((res && res.list) || []).filter((t) =>
        inMonth(t.actualArriveTime || t.plannedArriveTime || t.plannedLoadTime, offset)
      );
      const qty = raw.reduce((s, t) => s + (t.totalQuantity || 0), 0);
      this.setData({
        stats: { trips: raw.length, qty, km: raw.length ? raw.length * 322 : 0 },
        list: raw.map((t) => ({
          id: t.id,
          route: `${t.origin || '-'} → ${t.destination || '-'}`,
          sub: `${t.taskNo} · ${formatDate(t.actualArriveTime || t.plannedArriveTime)}`,
          qtyText: t.totalQuantity ? `${t.totalQuantity} 台` : ''
        }))
      });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  },

  onTap(e) {
    const id = e.currentTarget.dataset.id;
    if (id) wx.navigateTo({ url: `/pages/task/detail?id=${id}` });
  }
});
