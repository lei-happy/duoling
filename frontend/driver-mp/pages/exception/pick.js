const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { TYPES, ICON_BY_TYPE, listHistory } = require('../../services/mock/exception');
const { DISPATCHER, SAFETY, RESCUE } = require('../../services/mock/contacts');
const { callPhone } = require('../../utils/action');

Page({
  data: {
    fontClass: 'font-lg',
    types: TYPES,
    history: [],
    sheet: '',
    q: ''
  },

  onLoad(query) {
    const parts = [];
    if (query.id) parts.push(`id=${query.id}`);
    if (query.no) parts.push(`no=${encodeURIComponent(query.no)}`);
    if (query.route) parts.push(`route=${encodeURIComponent(query.route)}`);
    this.setData({ q: parts.join('&') });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({
      fontClass: getFontScale().className,
      history: listHistory().map((row) => ({
        ...row,
        icon: ICON_BY_TYPE[row.type] || 'clock'
      }))
    });
  },

  goForm(e) {
    const key = e.currentTarget.dataset.key;
    const extra = this.data.q ? `&${this.data.q}` : '';
    wx.navigateTo({ url: `/pages/exception/form?type=${key}${extra}` });
  },

  goTrack(e) {
    wx.navigateTo({ url: `/pages/exception/track?id=${e.currentTarget.dataset.id}` });
  },

  openSos() {
    this.setData({ sheet: 'sos' });
  },

  closeSheet() {
    this.setData({ sheet: '' });
  },

  callWho(e) {
    const who = e.currentTarget.dataset.who;
    this.setData({ sheet: '' });
    if (who === 'dispatch') callPhone(DISPATCHER.phone);
    else if (who === 'safety') callPhone(SAFETY.phone);
    else if (who === 'rescue') callPhone(RESCUE.phone);
    else callPhone('122');
  }
});
