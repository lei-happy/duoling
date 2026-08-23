const { ensureAuth } = require('../../utils/auth');
const { listMyTasks } = require('../../api/task');
const { listMyReceipts } = require('../../api/task-receipt');
const { getFontScale } = require('../../utils/font');

Page({
  data: { fontClass: 'font-lg', todo: [], done: [], loading: false },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    this.setData({ loading: true });
    try {
      const [tasks, receipts] = await Promise.all([
        listMyTasks({ page: 1, pageSize: 50 }),
        listMyReceipts({ page: 1, pageSize: 50 }).catch(() => ({ list: [] }))
      ]);
      const ids = new Set(((receipts && receipts.list) || []).map((r) => r.taskId));
      const all = (tasks && tasks.list) || [];
      const doneTasks = all.filter((t) => t.status === 5);
      const todo = doneTasks.filter((t) => !ids.has(t.id)).map((t, i) => ({
        id: t.id,
        title: t.taskNo,
        sub: `${t.origin || ''} → ${t.destination || ''}`,
        extra: i === 0 ? '需重传' : '待上传',
        tone: i === 0 ? 'amber' : ''
      }));
      const done = doneTasks.filter((t) => ids.has(t.id)).map((t) => ({
        id: t.id,
        title: t.taskNo,
        sub: `${t.origin || ''} → ${t.destination || ''}`
      }));
      this.setData({ todo, done });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  },

  goUpload(e) {
    const id = e.currentTarget.dataset.id;
    if (id) wx.navigateTo({ url: `/pages/task/receipt?id=${id}` });
  }
});
