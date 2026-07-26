const { ensureAuth } = require('../../utils/auth');
const { getMyProfile, updateMyProfile } = require('../../api/profile');
const { toast } = require('../../utils/request');

function genderLabel(g) {
  return { 0: '未知', 1: '男', 2: '女' }[g == null ? 0 : g] || '未知';
}

Page({
  data: {
    loaded: false,
    profile: {},
    genderText: '-',
    form: {
      emergencyContact: '',
      emergencyPhone: '',
      homeAddress: ''
    },
    saving: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.load();
  },

  async load() {
    try {
      const profile = await getMyProfile();
      this.setData({
        loaded: true,
        profile,
        genderText: genderLabel(profile.gender),
        form: {
          emergencyContact: profile.emergencyContact || '',
          emergencyPhone: profile.emergencyPhone || '',
          homeAddress: profile.homeAddress || ''
        }
      });
    } catch (e) {
      /* handled */
    }
  },

  onContact(e) {
    this.setData({ 'form.emergencyContact': e.detail.value || '' });
  },
  onPhone(e) {
    this.setData({ 'form.emergencyPhone': e.detail.value || '' });
  },
  onAddress(e) {
    this.setData({ 'form.homeAddress': e.detail.value || '' });
  },

  async onSave() {
    if (this.data.saving) return;
    this.setData({ saving: true });
    wx.showLoading({ title: '正在保存，请稍候…', mask: true });
    try {
      const profile = await updateMyProfile({ ...this.data.form });
      this.setData({ profile });
      toast('已保存');
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ saving: false });
    }
  }
});
