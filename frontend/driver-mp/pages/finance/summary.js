const { ensureAuth } = require('../../utils/auth');
const { getFinanceSummary, listMyAccounts } = require('../../api/finance');
const { ACCOUNT_TYPE } = require('../../utils/constants');
const { formatMoney, maskBankAccount } = require('../../utils/format');

Page({
  data: {
    totalIncomeText: '0.00',
    prepaidText: '0.00',
    supplementText: '0.00',
    settledText: '0.00',
    byMonth: [],
    accounts: []
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    try {
      const [summary, accounts] = await Promise.all([
        getFinanceSummary(),
        listMyAccounts().catch(() => [])
      ]);
      this.setData({
        totalIncomeText: formatMoney(summary.totalIncome),
        prepaidText: formatMoney(summary.prepaidAmount),
        supplementText: formatMoney(summary.supplementAmount),
        settledText: formatMoney(summary.settledAmount),
        byMonth: (summary.byMonth || []).map((m) => ({
          month: m.month,
          amountText: formatMoney(m.amount)
        })),
        accounts: (accounts || []).map((a) => ({
          ...a,
          typeLabel: ACCOUNT_TYPE[a.accountType] || '账户',
          accountNoMasked: maskBankAccount(a.accountNo)
        }))
      });
    } catch (e) {
      /* handled */
    }
  }
});
