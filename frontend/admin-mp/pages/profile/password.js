const { ensureAuth } = require('../../utils/auth');
const { changePassword } = require('../../api/auth');
const { toast } = require('../../utils/request');

Page({
  data: { oldPassword: '', newPassword: '', confirm: '', loading: false },

  onShow() {
    ensureAuth();
  },

  onOld(e) { this.setData({ oldPassword: e.detail.value || '' }); },
  onNew(e) { this.setData({ newPassword: e.detail.value || '' }); },
  onConfirm(e) { this.setData({ confirm: e.detail.value || '' }); },

  async onSubmit() {
    const { oldPassword, newPassword, confirm, loading } = this.data;
    if (loading) return;
    if (!oldPassword) {
      toast('请输入当前密码');
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      toast('新密码至少 6 位');
      return;
    }
    if (newPassword !== confirm) {
      toast('两次输入的新密码不一致');
      return;
    }
    if (newPassword === oldPassword) {
      toast('新密码不能和当前密码一样');
      return;
    }
    this.setData({ loading: true });
    wx.showLoading({ title: '正在修改密码，请稍候…', mask: true });
    try {
      await changePassword({ oldPassword, newPassword });
      toast('密码已改好，下次用新密码登录');
      setTimeout(() => wx.navigateBack(), 400);
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
