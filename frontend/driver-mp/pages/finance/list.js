const { ensureAuth } = require('../../utils/auth');
const { listMyFinance, getFinanceSummary, listMyAccounts } = require('../../api/finance');
const { FINANCE_DOC_TYPE, FINANCE_STATUS, ACCOUNT_TYPE } = require('../../utils/constants');
const { formatMoney, formatDate, maskBankAccount } = require('../../utils/format');
const { getFontScale } = require('../../utils/font');

function mapDoc(d) {
  const st = FINANCE_STATUS[d.status] || { label: '未知', level: 'default' };
  const paid = d.status === 3;
  const revoked = d.status === 4;
  let icon = 'clock';
  let tone = 'amber';
  if (paid) {
    icon = 'check';
    tone = 'green';
  } else if (revoked) {
    icon = 'info';
    tone = '';
  } else if (d.status === 1 || d.status === 2) {
    icon = 'clock';
    tone = 'amber';
  }
  const amount = d.actualAmount != null ? d.actualAmount : d.plannedAmount;
  return {
    id: d.id,
    icon,
    tone,
    title: `${FINANCE_DOC_TYPE[d.docType] || '费用单'} · ${d.taskNo || d.docNo}`,
    subtitle: paid
      ? `${formatDate(d.actualPayTime)} 已到账`
      : revoked
        ? '已撤销'
        : st.label,
    amountText: `${paid ? '+' : ''}${formatMoney(amount)}`,
    extraTone: paid ? 'ok' : revoked ? 'dim' : '',
    status: d.status,
    amount
  };
}

Page({
  data: {
    fontClass: 'font-lg',
    monthLabel: '',
    totalIncomeText: '0.00',
    prepaidText: '0.00',
    supplementText: '0.00',
    settledText: '0.00',
    unpaidText: '',
    accountHint: '由企业侧维护',
    preview: [],
    loading: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    const now = new Date();
    this.setData({
      fontClass: getFontScale().className,
      monthLabel: `${now.getFullYear()} 年 ${now.getMonth() + 1} 月`
    });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    this.setData({ loading: true });
    try {
      const [summary, docs, accounts] = await Promise.all([
        getFinanceSummary(),
        listMyFinance({ page: 1, pageSize: 8 }),
        listMyAccounts().catch(() => [])
      ]);
      const list = ((docs && docs.list) || []).map(mapDoc);
      const unpaid = ((docs && docs.list) || [])
        .filter((d) => d.status === 1 || d.status === 2)
        .reduce((s, d) => s + Number(d.actualAmount != null ? d.actualAmount : d.plannedAmount || 0), 0);
      const bank = (accounts || []).find((a) => a.accountType === 1) || (accounts || [])[0];
      this.setData({
        totalIncomeText: formatMoney(summary && summary.totalIncome),
        prepaidText: formatMoney(summary && summary.prepaidAmount),
        supplementText: formatMoney(summary && summary.supplementAmount),
        settledText: formatMoney(summary && summary.settledAmount),
        unpaidText: unpaid > 0 ? formatMoney(unpaid) : '',
        accountHint: bank
          ? `${ACCOUNT_TYPE[bank.accountType] || '账户'} ${maskBankAccount(bank.accountNo)}`
          : '由企业侧维护',
        preview: list.slice(0, 4)
      });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  },

  goFund() {
    wx.navigateTo({ url: '/pages/finance/fund-account' });
  },

  goSummary() {
    wx.navigateTo({ url: '/pages/finance/summary' });
  },

  goAccount() {
    wx.navigateTo({ url: '/pages/finance/account' });
  },

  goDocs() {
    wx.navigateTo({ url: '/pages/finance/docs' });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    if (id) wx.navigateTo({ url: `/pages/finance/detail?id=${id}` });
  }
});
