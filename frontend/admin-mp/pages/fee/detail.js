const { ensureAuth } = require('../../utils/auth');
const { getDoc, payDoc, approveDoc } = require('../../api/finance');
const { money } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: { doc: null, actual: '', remark: '', loading: false },
  onLoad(q) { this.id = q.id; this.load(); },
  async load() {
    if (!ensureAuth()) return;
    const doc = await getDoc(this.id);
    this.setData({
      doc: { ...doc, amountText: money(doc.plannedAmount, 2) },
      actual: String(doc.plannedAmount || '')
    });
  },
  onActual(e) { this.setData({ actual: e.detail.value }); },
  onRemark(e) { this.setData({ remark: e.detail.value }); },
  async onApprove() {
    this.setData({ loading: true });
    try {
      await approveDoc(this.id);
      toast('已审批通过');
      this.load();
    } catch (e) { /* toast */ }
    finally { this.setData({ loading: false }); }
  },
  async onPay() {
    const actual = Number(this.data.actual);
    if (!actual) {
      toast('请填写实付金额');
      return;
    }
    if (actual !== Number(this.data.doc.plannedAmount) && !this.data.remark) {
      toast('实付与应付不一致时，请写明原因');
      return;
    }
    this.setData({ loading: true });
    try {
      await payDoc(this.id, {
        actualAmount: actual,
        payMethod: 1,
        actualPayTime: new Date().toISOString().slice(0, 19),
        remark: this.data.remark || undefined
      });
      toast('已标记为已支付');
      wx.navigateBack();
    } catch (e) { /* toast */ }
    finally { this.setData({ loading: false }); }
  }
});
