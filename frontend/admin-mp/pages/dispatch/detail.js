const { ensureAuth } = require('../../utils/auth');
const { getTask } = require('../../api/task');
const { routeText, shortTime } = require('../../utils/format');

Page({
  data: { task: null },
  onLoad(q) {
    this.id = q.id;
    this.load();
  },
  async load() {
    if (!ensureAuth()) return;
    try {
      const task = await getTask(this.id);
      this.setData({
        task: {
          ...task,
          route: routeText(task.origin, task.destination),
          loadTime: shortTime(task.plannedLoadTime),
          arriveTime: shortTime(task.plannedArriveTime)
        }
      });
    } catch (e) { /* toast */ }
  },
  onAssign() {
    wx.navigateTo({ url: `/pages/dispatch/assign?id=${this.id}&stage=${this.data.task.status}` });
  },
  onCall() {
    const phone = this.data.task && this.data.task.mainDriverPhone;
    if (phone) wx.makePhoneCall({ phoneNumber: phone });
  }
});
