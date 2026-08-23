const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { TYPES, REASONS, DELAYS, addReport } = require('../../services/mock/exception');
const { callDispatcher } = require('../../utils/action');
const { toast } = require('../../utils/request');

Page({
  data: {
    fontClass: 'font-lg',
    type: 'delay',
    reasons: [],
    delays: DELAYS,
    reason: '',
    delay: '1 小时左右',
    remark: '',
    taskNo: 'TK2608090037',
    route: '上汽仪征基地 → 杭州萧山中转库',
    hurt: 'no',
    drive: 'ok',
    cargo: 'no'
  },

  onLoad(query) {
    const type = query.type || 'delay';
    const found = TYPES.find((t) => t.key === type);
    const reasons = REASONS[type] || [];
    wx.setNavigationBarTitle({ title: found ? `上报${found.title}` : '填写上报' });
    this.setData({
      type,
      reasons,
      reason: reasons[0] || '',
      taskNo: query.no ? decodeURIComponent(query.no) : 'TK2608090037',
      route: query.route ? decodeURIComponent(query.route) : '上汽仪征基地 → 杭州萧山中转库'
    });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
  },

  setReason(e) {
    this.setData({ reason: e.currentTarget.dataset.v });
  },

  setDelay(e) {
    this.setData({ delay: e.currentTarget.dataset.v });
  },

  setKV(e) {
    const { k, v } = e.currentTarget.dataset;
    this.setData({ [k]: v });
  },

  onRemark(e) {
    this.setData({ remark: (e.detail && e.detail.value) || '' });
  },

  callDispatch() {
    callDispatcher();
  },

  submit() {
    const row = addReport({
      type: this.data.type,
      title: this.data.remark || this.data.reason || TYPES.find((t) => t.key === this.data.type).title,
      taskNo: this.data.taskNo,
      oldEta: '',
      newEta: this.data.type === 'delay' ? this.data.delay : '',
      reply: '调度已收到，正在处理。'
    });
    toast('已上报，调度那边立刻能看到');
    wx.redirectTo({ url: `/pages/exception/track?id=${row.id}` });
  }
});
