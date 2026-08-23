const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getRig, getLicenses, getMaint } = require('../../services/mock/vehicle');
const { callFleet } = require('../../utils/action');
const { toast } = require('../../utils/request');

Page({
  data: {
    fontClass: 'font-lg',
    rig: {},
    licenses: [],
    maint: {},
    sheet: '',
    issue: '保养',
    remark: ''
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({
      fontClass: getFontScale().className,
      rig: getRig(),
      licenses: getLicenses(),
      maint: getMaint()
    });
  },

  goLic() {
    wx.navigateTo({ url: '/pages/profile/licenses' });
  },

  goMaint() {
    wx.navigateTo({ url: '/pages/profile/maint' });
  },

  onViolation() {
    toast('违章由车管统一处理，扣款走往来账');
  },

  onCall() {
    callFleet();
  },

  openRepair() {
    this.setData({ sheet: 'repair' });
  },

  closeSheet() {
    this.setData({ sheet: '' });
  },

  setIssue(e) {
    this.setData({ issue: e.currentTarget.dataset.v });
  },

  onRemark(e) {
    this.setData({ remark: (e.detail && e.detail.value) || '' });
  },

  submitRepair() {
    this.setData({ sheet: '' });
    toast('已交给车管，李敏会回你');
  }
});
