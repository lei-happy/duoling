const { ensureAuth } = require('../../utils/auth');
const { loginByPassword, handleLoginResult } = require('../../api/auth');
const { toast } = require('../../utils/request');
const { getStatusBarHeight, getPolicy } = require('../../utils/auth-ui');

Page({
  data: {
    statusBarHeight: 20,
    phone: '',
    password: '',
    agreed: false,
    loading: false,
    policyVisible: false,
    policyTitle: '',
    policyText: ''
  },

  onLoad() {
    this.setData({ statusBarHeight: getStatusBarHeight() });
  },

  onShow() {
    ensureAuth({ noAuth: true });
  },

  onPhone(e) {
    this.setData({ phone: (e.detail.value || '').trim() });
  },

  onPassword(e) {
    this.setData({ password: e.detail.value || '' });
  },

  onToggleAgree() {
    this.setData({ agreed: !this.data.agreed });
  },

  onOpenPolicy(e) {
    const policy = getPolicy(e.currentTarget.dataset.key);
    this.setData({
      policyVisible: true,
      policyTitle: policy.title,
      policyText: policy.text
    });
  },

  closePolicy() {
    this.setData({ policyVisible: false });
  },

  noop() {},

  onHelp() {
    toast('联系企业调度员，让他在「运力中心-驾驶员管理」添加你');
  },

  async onSubmit() {
    const { phone, password, loading, agreed } = this.data;
    if (loading) return;
    if (!agreed) {
      toast('请先阅读并同意服务协议与隐私政策');
      return;
    }
    if (!/^1\d{10}$/.test(phone)) {
      toast('请输入正确的手机号');
      return;
    }
    if (!password) {
      toast('请输入密码');
      return;
    }

    this.setData({ loading: true });
    wx.showLoading({ title: '正在登录，请稍候…', mask: true });
    try {
      const result = await loginByPassword({ phone, password });
      handleLoginResult(result, { phone, password });
    } catch (e) {
      /* toast 已在 request 中处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  },

  goSms() {
    wx.navigateTo({ url: '/pages/sms-login/sms-login' });
  }
});
