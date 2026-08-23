const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getNavInfo } = require('../../services/mock/location');
const { callReceiver, copyText } = require('../../utils/action');
const { toast } = require('../../utils/request');

Page({
  data: {
    fontClass: 'font-lg',
    denied: false,
    autoOn: true,
    sheet: '',
    dest: '',
    nav: {}
  },

  onLoad(query) {
    const dest = decodeURIComponent(query.dest || '');
    this.setData({ dest, nav: getNavInfo(dest) });
    if (query.no) wx.setNavigationBarTitle({ title: `${decodeURIComponent(query.no)} 位置` });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.checkLoc();
  },

  checkLoc() {
    wx.getSetting({
      success: (res) => {
        const ok = !!(res.authSetting && res.authSetting['scope.userLocation']);
        if (ok) this.setData({ denied: false });
      }
    });
  },

  askLoc() {
    wx.authorize({
      scope: 'scope.userLocation',
      success: () => this.setData({ denied: false }),
      fail: () => {
        wx.openSetting({
          success: (r) => {
            if (r.authSetting && r.authSetting['scope.userLocation']) this.setData({ denied: false });
          }
        });
      }
    });
  },

  toggleAuto() {
    const next = !this.data.autoOn;
    this.setData({ autoOn: next });
    toast(next ? '已打开自动上报' : '已关掉自动上报，需要时手动报一次');
  },

  openMap() {
    this.setData({ sheet: 'map' });
  },

  closeSheet() {
    this.setData({ sheet: '' });
  },

  openWxMap() {
    const n = this.data.nav;
    this.setData({ sheet: '' });
    wx.openLocation({
      latitude: n.latitude,
      longitude: n.longitude,
      name: n.destTitle,
      address: n.destTitle,
      fail: () => copyText(n.destTitle, '地址已复制，贴到地图里用')
    });
  },

  copyDest() {
    this.setData({ sheet: '' });
    copyText(this.data.nav.destTitle, '地址已复制');
  },

  onCallRecv() {
    callReceiver();
  },

  goManual() {
    wx.navigateTo({ url: '/pages/location/manual' });
  }
});
