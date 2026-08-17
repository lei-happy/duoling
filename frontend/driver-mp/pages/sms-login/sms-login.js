const { ensureAuth } = require('../../utils/auth');
const { loginBySms, sendSmsCode, handleLoginResult } = require('../../api/auth');
const { toast } = require('../../utils/request');
const { getStatusBarHeight, getPolicy } = require('../../utils/auth-ui');

Page({
  data: {
    statusBarHeight: 20,
    phone: '',
    code: '',
    agreed: false,
    loading: false,
    sending: false,
    countdown: 0,
    policyVisible: false,
    policyTitle: '',
    policyText: ''
  },

  _timer: null,

  onLoad() {
    this.setData({ statusBarHeight: getStatusBarHeight() });
  },

  onShow() {
    ensureAuth({ noAuth: true });
  },

  onUnload() {
    if (this._timer) clearInterval(this._timer);
  },

  onPhone(e) {
    this.setData({ phone: (e.detail.value || '').trim() });
  },

  onCode(e) {
    this.setData({ code: (e.detail.value || '').trim() });
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

  async onSendCode() {
    const { phone, countdown, sending } = this.data;
    if (countdown > 0 || sending) return;
    if (!/^1\d{10}$/.test(phone)) {
      toast('请输入正确的手机号');
      return;
    }
    this.setData({ sending: true });
    try {
      await sendSmsCode({ phone, purpose: 1 });
      toast('验证码已发送');
      this.setData({ countdown: 60 });
      this._timer = setInterval(() => {
        const next = this.data.countdown - 1;
        if (next <= 0) {
          clearInterval(this._timer);
          this._timer = null;
          this.setData({ countdown: 0 });
        } else {
          this.setData({ countdown: next });
        }
      }, 1000);
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ sending: false });
    }
  },

  async onSubmit() {
    const { phone, code, loading, agreed } = this.data;
    if (loading) return;
    if (!agreed) {
      toast('请先阅读并同意服务协议与隐私政策');
      return;
    }
    if (!/^1\d{10}$/.test(phone)) {
      toast('请输入正确的手机号');
      return;
    }
    if (!code || code.length < 4) {
      toast('请输入验证码');
      return;
    }
    this.setData({ loading: true });
    wx.showLoading({ title: '正在登录，请稍候…', mask: true });
    try {
      const result = await loginBySms({ phone, code });
      handleLoginResult(result, { phone, code });
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  },

  goPassword() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/login/login' }) });
  }
});
