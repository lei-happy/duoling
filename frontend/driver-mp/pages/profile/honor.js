const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getHonor } = require('../../services/mock/honor');

Page({
  data: { fontClass: 'font-lg', honor: {} },
  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className, honor: getHonor() });
  }
});
