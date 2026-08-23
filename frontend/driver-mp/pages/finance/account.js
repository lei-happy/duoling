const { ensureAuth } = require('../../utils/auth');
const { listMyAccounts } = require('../../api/finance');
const { ACCOUNT_TYPE } = require('../../utils/constants');
const { formatMoney, maskBankAccount } = require('../../utils/format');
const { getFontScale } = require('../../utils/font');

Page({
  data: {
    fontClass: 'font-lg',
    banks: [],
    others: [],
    loading: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    this.setData({ loading: true });
    try {
      const accounts = (await listMyAccounts()) || [];
      const mapped = accounts.map((a) => ({
        ...a,
        typeLabel: ACCOUNT_TYPE[a.accountType] || '账户',
        accountNoMasked: maskBankAccount(a.accountNo),
        balanceText: formatMoney(a.balance)
      }));
      this.setData({
        banks: mapped.filter((a) => a.accountType === 1),
        others: mapped.filter((a) => a.accountType !== 1)
      });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  }
});
