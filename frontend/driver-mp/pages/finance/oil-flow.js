const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getOilFlows, getGroupedFlows } = require('../../services/mock/oil');

Page({
  data: { fontClass: 'font-lg', tab: 'all', list: [], groups: [] },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className, groups: getGroupedFlows() });
    this.apply();
  },

  setTab(e) {
    this.setData({ tab: e.currentTarget.dataset.v });
    this.apply();
  },

  apply() {
    const all = getOilFlows();
    const tab = this.data.tab;
    this.setData({ list: tab === 'all' ? all : all.filter((x) => x.kind === tab) });
  }
});
