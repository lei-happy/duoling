const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');

Page({
  data: {
    realName: '管理员'
  },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, null) || getApp().globalData.userInfo;
    this.setData({
      realName: (user && (user.realName || user.name)) || '管理员'
    });
  }
});
