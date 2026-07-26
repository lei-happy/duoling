const { ensureAuth } = require('../../utils/auth');
const { getFinanceDetail } = require('../../api/finance');
const { FINANCE_DOC_TYPE, FINANCE_STATUS, PAY_METHOD } = require('../../utils/constants');
const { formatDateTime, formatMoney } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: {
    docId: 0,
    doc: null,
    statusLabel: '',
    statusLevel: 'default',
    typeLabel: '',
    payMethodText: '-',
    amountText: '0.00',
    plannedText: '0.00',
    actualText: '0.00',
    plannedPayText: '-',
    actualPayText: '-'
  },

  onLoad(query) {
    this.setData({ docId: Number(query.id) || 0 });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.load();
  },

  async load() {
    if (!this.data.docId) {
      toast('费用单不存在');
      return;
    }
    try {
      const doc = await getFinanceDetail(this.data.docId);
      const st = FINANCE_STATUS[doc.status] || { label: '未知', level: 'default' };
      const items = (doc.items || []).map((it) => ({
        ...it,
        amountText: formatMoney(it.amount)
      }));
      this.setData({
        doc: { ...doc, items },
        statusLabel: st.label,
        statusLevel: st.level,
        typeLabel: FINANCE_DOC_TYPE[doc.docType] || '费用单',
        payMethodText: PAY_METHOD[doc.payMethod] || '-',
        amountText: formatMoney(doc.actualAmount != null ? doc.actualAmount : doc.plannedAmount),
        plannedText: formatMoney(doc.plannedAmount),
        actualText: formatMoney(doc.actualAmount != null ? doc.actualAmount : 0),
        plannedPayText: formatDateTime(doc.plannedPayTime),
        actualPayText: formatDateTime(doc.actualPayTime)
      });
    } catch (e) {
      /* handled */
    }
  }
});
