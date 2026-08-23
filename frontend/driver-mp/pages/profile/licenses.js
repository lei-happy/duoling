const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getLicenses } = require('../../services/mock/vehicle');
const { toast } = require('../../utils/request');

Page({
  data: { fontClass: 'font-lg', tab: 'all', warns: [], ok: [], sheet: false },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.apply();
  },

  setTab(e) {
    this.setData({ tab: e.currentTarget.dataset.v });
    this.apply();
  },

  apply() {
    const tab = this.data.tab;
    let list = getLicenses();
    if (tab !== 'all') list = list.filter((x) => x.owner === tab);
    this.setData({
      warns: list.filter((x) => x.warn),
      ok: list.filter((x) => !x.warn)
    });
  },

  openRenew() {
    this.setData({ sheet: true });
  },

  closeSheet() {
    this.setData({ sheet: false });
  },

  submit() {
    this.setData({ sheet: false });
    toast('材料已交给车管');
  }
});
