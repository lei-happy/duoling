const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getMessage, markRead } = require('../../services/mock/message');
const { toast } = require('../../utils/request');

Page({
  data: { fontClass: 'font-lg', msg: null },

  onLoad(query) {
    const msg = getMessage(query.id);
    if (!msg) {
      toast('这条消息找不到了');
      return;
    }
    markRead(msg.id);
    this.setData({ msg });
    wx.setNavigationBarTitle({ title: msg.title.slice(0, 12) });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
  },

  goTask() {
    const app = getApp();
    if (app) app.globalData.taskStatusFilter = 'waitAccept';
    wx.switchTab({ url: '/pages/task/list' });
  }
});
