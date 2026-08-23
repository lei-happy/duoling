const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getManualDefaults } = require('../../services/mock/location');
const { toast } = require('../../utils/request');

Page({
  data: {
    fontClass: 'font-lg',
    place: '',
    situations: [],
    etas: [],
    sit: '正常行驶',
    eta: '按原计划',
    remark: ''
  },

  onShow() {
    if (!ensureAuth({})) return;
    const d = getManualDefaults();
    this.setData({
      fontClass: getFontScale().className,
      place: d.place,
      situations: d.situations,
      etas: d.etaOptions
    });
  },

  setSit(e) {
    this.setData({ sit: e.currentTarget.dataset.v });
  },

  setEta(e) {
    this.setData({ eta: e.currentTarget.dataset.v });
  },

  onRemark(e) {
    this.setData({ remark: (e.detail && e.detail.value) || '' });
  },

  submit() {
    toast('位置已报给调度');
    setTimeout(() => wx.navigateBack(), 400);
  }
});
