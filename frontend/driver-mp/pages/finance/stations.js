const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getStations } = require('../../services/mock/oil');

Page({
  data: { fontClass: 'font-lg', list: [] },
  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className, list: getStations() });
  }
});
