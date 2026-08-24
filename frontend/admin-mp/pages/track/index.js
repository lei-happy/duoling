const { ensureAuth } = require('../../utils/auth');
const { listTasks } = require('../../api/task');
const { listAlerts, claimAlert } = require('../../api/alert');
const { listOf, routeText } = require('../../utils/format');
const { customerCopy } = require('../../services/mock/index');
const { toast } = require('../../utils/request');

Page({
  data: { tab: 'all', list: [] },
  onShow() {
    if (!ensureAuth()) return;
    this.reload();
  },
  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },
  onTab(e) {
    this.setData({ tab: e.currentTarget.dataset.tab });
    this.reload();
  },
  async reload() {
    try {
      const params = { status: 3 };
      if (this.data.tab === 'late') params.alertLevel = 'critical';
      if (this.data.tab === 'warn') params.alertLevel = 'any';
      const page = await listTasks(params);
      this.setData({
        list: listOf(page).map((t) => ({
          id: t.id,
          no: t.taskNo,
          route: routeText(t.origin, t.destination),
          plate: t.plateNumber || '',
          driver: t.mainDriverName || '',
          phone: t.mainDriverPhone || '',
          alert: t.alertLevel >= 2 ? '已超时' : t.alertLevel === 1 ? '临期' : '在途',
          copy: customerCopy(t)
        }))
      });
    } catch (e) { /* toast */ }
  },
  onItem(e) {
    wx.navigateTo({ url: `/pages/track/detail?id=${e.currentTarget.dataset.id}` });
  },
  noop() {},
  onCall(e) {
    const phone = e.currentTarget.dataset.phone;
    if (phone) wx.makePhoneCall({ phoneNumber: String(phone) });
    else toast('没有司机电话');
  },
  async onUrge(e) {
    const id = e.currentTarget.dataset.id;
    const item = this.data.list.find((x) => String(x.id) === String(id));
    try {
      const page = await listAlerts({ keyword: (item && item.no) || '', status: 0 });
      const first = listOf(page)[0];
      if (first) await claimAlert(first.id);
      toast('已催位置，请稍候司机回更');
    } catch (err) {
      toast('已记下催促，请稍候');
    }
  },
  onCopy(e) {
    const copy = e.currentTarget.dataset.copy || '';
    if (!copy) return;
    wx.setClipboardData({ data: copy, success: () => toast('话术已复制，可发给客户') });
  }
});
