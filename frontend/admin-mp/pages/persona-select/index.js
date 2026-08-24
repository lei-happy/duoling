const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { PERSONA_OPTIONS, personaLabel } = require('../../utils/persona');
const { saveDefaultPersona } = require('../../api/auth');
const { toast } = require('../../utils/request');

const COPY = {
  dispatch: '五阶段任务池、派车分配、在途盯梢、回单签收。',
  boss: '经营驾驶舱、异常预警、审批放行。',
  finance: '费用工作台、待付台账、标记支付。',
  captain: '自有运力、证照预警、催司机回位。'
};

Page({
  data: { name: '', cards: [], picked: '', loading: false },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
    const personas = user.personas || [];
    const cards = PERSONA_OPTIONS.filter((x) => personas.indexOf(x.value) >= 0).map((x) => ({
      ...x,
      desc: COPY[x.value] || ''
    }));
    this.setData({
      name: user.realName || '同事',
      cards,
      picked: (cards[0] && cards[0].value) || ''
    });
  },

  onPick(e) {
    this.setData({ picked: e.currentTarget.dataset.value });
  },

  async onEnter() {
    const { picked, loading } = this.data;
    if (!picked || loading) return;
    this.setData({ loading: true });
    try {
      await saveDefaultPersona(picked);
      wx.switchTab({ url: '/pages/home/index' });
    } catch (e) {
      toast('切换视图失败，请重试');
    } finally {
      this.setData({ loading: false });
    }
  }
});
