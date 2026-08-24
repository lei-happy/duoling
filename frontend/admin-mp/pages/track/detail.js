const { ensureAuth } = require('../../utils/auth');
const { getTask } = require('../../api/task');
const { claimAlert, listAlerts } = require('../../api/alert');
const { routeText } = require('../../utils/format');
const { customerCopy } = require('../../services/mock/index');
const { toast } = require('../../utils/request');
const { listOf } = require('../../utils/format');

Page({
  data: { task: null, copy: '' },
  onLoad(q) { this.id = q.id; this.load(); },
  async load() {
    if (!ensureAuth()) return;
    const task = await getTask(this.id);
    this.setData({
      task: { ...task, route: routeText(task.origin, task.destination) },
      copy: customerCopy(task)
    });
  },
  onCall() {
    const p = this.data.task && this.data.task.mainDriverPhone;
    if (p) wx.makePhoneCall({ phoneNumber: p });
    else toast('没有司机电话');
  },
  async onUrge() {
    try {
      const page = await listAlerts({ keyword: this.data.task.taskNo, status: 0 });
      const first = listOf(page)[0];
      if (first) await claimAlert(first.id);
      toast('已催位置，请稍候司机回更');
    } catch (e) {
      toast('已记下催促，请稍候');
    }
  },
  onCopy() {
    wx.setClipboardData({ data: this.data.copy, success: () => toast('话术已复制，可发给客户') });
  }
});
