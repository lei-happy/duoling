const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getMaint } = require('../../services/mock/vehicle');

Page({
  data: { fontClass: 'font-lg', maint: {} },
  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className, maint: getMaint() });
  }
});
