const { ensureAuth } = require('../../utils/auth');
const { operationEfficiency } = require('../../api/insight');

Page({
  data: {
    score: 82,
    drag: '准点率（示意）',
    locked: 0,
    statusDist: [],
    mockHint: true
  },
  onShow() {
    if (!ensureAuth()) return;
    this.load();
  },
  async load() {
    try {
      const eff = await operationEfficiency();
      const dist = (eff && eff.statusDist) || [];
      this.setData({
        locked: (eff && (eff.lockedCount || eff.locked)) || 0,
        statusDist: dist,
        score: 82,
        drag: '准点率（示意）',
        mockHint: true
      });
    } catch (e) {
      this.setData({
        statusDist: [],
        locked: 0,
        score: 82,
        drag: '准点率（示意，真实对比线待补）',
        mockHint: true
      });
    }
  }
});
