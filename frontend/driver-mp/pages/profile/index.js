const { ensureAuth } = require('../../utils/auth');
const { getUserInfo, getTenantCode } = require('../../services/session');
const { getMyProfile } = require('../../api/profile');
const { getCapsuleSafe } = require('../../utils/nav');
const { getFontScale } = require('../../utils/font');
const { maskPhone } = require('../../utils/format');
const { getHonor } = require('../../services/mock/honor');
const { callDispatcher, callFleet } = require('../../utils/action');

Page({
  data: {
    fontClass: 'font-lg',
    padTop: 48,
    padRight: 96,
    realName: '司机',
    avatarText: '司',
    subText: '',
    tenantName: '-',
    sheet: '',
    honor: getHonor(),
    notifyExtra: '已开 4 项'
  },

  onShow() {
    if (!ensureAuth({})) return;
    const safe = getCapsuleSafe();
    const user = getUserInfo() || {};
    const name = user.realName || '司机';
    this.setData({
      fontClass: getFontScale().className,
      padTop: safe.padTop,
      padRight: safe.padRight,
      realName: name,
      avatarText: name.slice(0, 1),
      tenantName: user.tenantName || getTenantCode() || '-',
      subText: maskPhone(user.phone) || ''
    });
    this.loadProfile();
  },

  async loadProfile() {
    try {
      const p = await getMyProfile();
      const parts = [];
      if (p.driverCode) parts.push(`工号 ${p.driverCode}`);
      if (p.phone) parts.push(maskPhone(p.phone));
      this.setData({
        realName: p.name || this.data.realName,
        avatarText: (p.name || this.data.realName).slice(0, 1),
        subText: parts.join(' · ')
      });
    } catch (e) {
      /* handled */
    }
  },

  goInfo() {
    wx.navigateTo({ url: '/pages/profile/info' });
  },

  goSwitchTenant() {
    wx.navigateTo({ url: '/pages/profile/switch-tenant' });
  },

  goHonor() {
    wx.navigateTo({ url: '/pages/profile/honor' });
  },

  goSettings() {
    wx.navigateTo({ url: '/pages/profile/settings' });
  },

  goVehicles() {
    wx.navigateTo({ url: '/pages/profile/vehicles' });
  },

  goNotify() {
    wx.navigateTo({ url: '/pages/profile/notify' });
  },

  openHelp() {
    this.setData({ sheet: 'help' });
  },

  closeSheet() {
    this.setData({ sheet: '' });
  },

  callDispatch() {
    this.setData({ sheet: '' });
    callDispatcher();
  },

  callFleet() {
    this.setData({ sheet: '' });
    callFleet();
  }
});
