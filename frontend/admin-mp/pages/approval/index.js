const { ensureAuth } = require('../../utils/auth');
const { pending, initiated, history, agree, reject } = require('../../api/approval');
const { listOf, money } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: { tab: 0, list: [] },
  onShow() {
    if (!ensureAuth()) return;
    this.reload();
  },
  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },
  onTab(e) {
    this.setData({ tab: Number(e.currentTarget.dataset.tab) });
    this.reload();
  },
  async reload() {
    const fn = this.data.tab === 0 ? pending : this.data.tab === 1 ? initiated : history;
    try {
      const page = await fn();
      this.setData({
        list: listOf(page).map((x) => ({
          ...x,
          amountText: x.amount != null ? money(x.amount, 0) : '',
          tone: /超|低/.test(x.title || '') ? 'warn' : 'normal'
        }))
      });
    } catch (e) { /* toast */ }
  },
  onItem(e) {
    const item = this.data.list.find((x) => String(x.taskId || x.instanceId) === String(e.currentTarget.dataset.id));
    const instanceId = (item && item.instanceId) || e.currentTarget.dataset.iid;
    wx.navigateTo({ url: `/pages/approval/detail?id=${instanceId}&taskId=${e.currentTarget.dataset.id}` });
  },
  async onAgree(e) {
    try {
      await agree(e.currentTarget.dataset.id);
      toast('已通过');
      this.reload();
    } catch (err) { /* toast */ }
  },
  async onReject(e) {
    wx.showModal({
      title: '驳回理由',
      editable: true,
      placeholderText: '会原样发给提交人',
      success: async (res) => {
        if (!res.confirm) return;
        if (!res.content) {
          toast('驳回必须写理由');
          return;
        }
        try {
          await reject(e.currentTarget.dataset.id, res.content);
          toast('已驳回，会通知提交人');
          this.reload();
        } catch (err) { /* toast */ }
      }
    });
  }
});
