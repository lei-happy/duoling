const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, setItem } = require('../../utils/storage');
const {
  loginByPassword,
  loginBySms,
  sendSmsCode,
  finishLogin,
  isMultiTenant
} = require('../../api/auth');
const { toast } = require('../../utils/request');

Page({
  data: {
    mode: 'sms',
    phone: '',
    password: '',
    code: '',
    loading: false,
    counting: 0,
    agreed: true,
    statusBarHeight: 20
  },

  onLoad() {
    const sys = wx.getSystemInfoSync();
    this.setData({ statusBarHeight: sys.statusBarHeight || 20 });
  },

  onShow() {
    ensureAuth({ noAuth: true });
  },

  onUnload() {
    if (this._timer) clearInterval(this._timer);
  },

  onSwitch(e) {
    this.setData({ mode: e.currentTarget.dataset.mode });
  },

  onPhone(e) {
    this.setData({ phone: (e.detail.value || '').trim() });
  },

  onPassword(e) {
    this.setData({ password: e.detail.value || '' });
  },

  onCode(e) {
    this.setData({ code: (e.detail.value || '').trim() });
  },

  onToggleAgree() {
    this.setData({ agreed: !this.data.agreed });
  },

  onHelp() {
    toast('请联系企业管理员在组织与权限里添加你');
  },

  async onSendCode() {
    const { phone, counting } = this.data;
    if (counting) return;
    if (!/^1\d{10}$/.test(phone)) {
      toast('请输入正确的手机号');
      return;
    }
    try {
      await sendSmsCode(phone);
      toast('验证码已发送，请查收短信');
      this.setData({ counting: 60 });
      this._timer = setInterval(() => {
        const n = this.data.counting - 1;
        if (n <= 0) {
          clearInterval(this._timer);
          this.setData({ counting: 0 });
        } else {
          this.setData({ counting: n });
        }
      }, 1000);
    } catch (e) {
      /* toast 已处理 */
    }
  },

  async onSubmit() {
    const { mode, phone, password, code, loading, agreed } = this.data;
    if (loading) return;
    if (!agreed) {
      toast('请先同意服务协议与隐私政策');
      return;
    }
    if (!/^1\d{10}$/.test(phone)) {
      toast('请输入正确的手机号');
      return;
    }
    if (mode === 'pwd' && !password) {
      toast('请输入密码');
      return;
    }
    if (mode === 'sms' && !code) {
      toast('请输入验证码');
      return;
    }
    await this.doLogin();
  },

  async doLogin(tenantCode) {
    const { mode, phone, password, code } = this.data;
    this.setData({ loading: true });
    wx.showLoading({ title: '正在进入，请稍候…', mask: true });
    try {
      const result =
        mode === 'sms'
          ? await loginBySms({ phone, code, tenantCode })
          : await loginByPassword({ phone, password, tenantCode });
      if (isMultiTenant(result)) {
        setItem(STORAGE_KEYS.PENDING_LOGIN, { mode, phone, password, code });
        setItem(STORAGE_KEYS.PENDING_TENANTS, result.tenants || []);
        wx.navigateTo({ url: '/pages/tenant-select/index' });
        return;
      }
      await finishLogin(result);
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
