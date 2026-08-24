const { ensureAuth } = require('../../utils/auth');
const { getWaybill, updateStatus } = require('../../api/waybill');
const { routeText, shortTime } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: { item: null, loading: false },
  onLoad(q) { this.id = q.id; this.load(); },
  async load() {
    if (!ensureAuth()) return;
    const w = await getWaybill(this.id);
    this.setData({
      item: {
        ...w,
        route: routeText(w.origin, w.destination),
        time: shortTime(w.requiredDeliverTime),
        cargoes: w.cargoes || []
      }
    });
  },
  async onConfirm() {
    if (this.data.item.status !== 0 || this.data.loading) return;
    this.setData({ loading: true });
    try {
      await updateStatus(this.id, 1);
      toast('计划已确认，进入调度池');
      this.load();
    } catch (e) { /* toast */ }
    finally { this.setData({ loading: false }); }
  }
});
