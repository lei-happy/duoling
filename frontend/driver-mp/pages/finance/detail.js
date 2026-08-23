const { ensureAuth } = require('../../utils/auth');
const { getFinanceDetail } = require('../../api/finance');
const { FINANCE_DOC_TYPE, FINANCE_STATUS, PAY_METHOD } = require('../../utils/constants');
const { formatDateTime, formatMoney } = require('../../utils/format');
const { toast } = require('../../utils/request');
const { getFontScale } = require('../../utils/font');

Page({
  data: {
    fontClass: 'font-lg',
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
    actualPayText: '-',
    flow: []
  },

  onLoad(query) {
    this.setData({ docId: Number(query.id) || 0 });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
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
        actualPayText: formatDateTime(doc.actualPayTime),
        flow: [
          { title: '已提交', sub: formatDateTime(doc.createdAt) || '企业已出单' },
          { title: st.label, sub: formatDateTime(doc.actualPayTime || doc.plannedPayTime) || '按审批进度走' },
          { title: doc.status === 3 ? '已打到卡上' : '等财务打款', sub: formatDateTime(doc.actualPayTime) || '到账后会通知你' }
        ]
      });
    } catch (e) {
      /* handled */
    }
  }
});
