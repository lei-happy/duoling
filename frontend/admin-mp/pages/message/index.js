const { ensureAuth } = require('../../utils/auth');
const { pending, pendingCount } = require('../../api/approval');
const { listAlerts } = require('../../api/alert');
const { activities } = require('../../api/workbench');
const { listOf } = require('../../utils/format');

Page({
  data: { tab: 'todo', items: [], counts: { todo: 0, alert: 0, act: 0 } },
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
      const [todoPage, alertPage, actPage, count] = await Promise.all([
        pending().catch(() => ({})),
        listAlerts({ status: 0 }).catch(() => ({})),
        activities().catch(() => ({})),
        pendingCount().catch(() => ({ count: 0 }))
      ]);
      const todos = listOf(todoPage);
      const alerts = listOf(alertPage);
      const acts = listOf(actPage);
      const mapped = {
        todo: todos.map((x) => ({
          id: x.taskId,
          title: x.title || '待你审批',
          sub: x.bizNo || '',
          action: '去审批',
          url: `/pages/approval/detail?id=${x.instanceId}&taskId=${x.taskId}`
        })),
        alert: alerts.map((x) => ({
          id: x.id,
          title: x.ruleName || x.code || '预警',
          sub: x.taskNo || '',
          action: '去看看',
          url: `/pages/track/detail?id=${x.taskId}`
        })),
        act: acts.map((x, i) => ({
          id: x.id || i,
          title: x.summary || '企业动态',
          sub: x.display_time || x.displayTime || x.occurredAt || x.occurred_at || '',
          action: '',
          url: ''
        })),
        notice: [
          { id: 'n1', title: '系统公告（示意）', sub: '订阅消息模板尚未接通', action: '', url: '' }
        ]
      };
      this.setData({
        counts: {
          todo: (count && count.count) || todos.length,
          alert: alerts.length,
          act: acts.length
        },
        items: mapped[this.data.tab] || mapped.todo
      });
    } catch (e) { /* toast */ }
  },
  onOpen(e) {
    const url = e.currentTarget.dataset.url;
    if (url) wx.navigateTo({ url });
  },
  goNotify() {
    wx.navigateTo({ url: '/pages/message/notify' });
  }
});
