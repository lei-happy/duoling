const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');

Page({
  data: { fontClass: 'font-lg' },
  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
  }
});
