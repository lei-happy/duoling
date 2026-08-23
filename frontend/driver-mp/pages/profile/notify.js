const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getItem, setItem } = require('../../utils/storage');
const { toast } = require('../../utils/request');

const DEFAULT = {
  dispatch: true,
  arrive: true,
  pay: true,
  license: true,
  notice: false,
  quiet: true
};

Page({
  data: {
    fontClass: 'font-lg',
    items: [],
    quiet: true
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.sync();
  },

  sync() {
    const s = Object.assign({}, DEFAULT, getItem('notify_pref', {}) || {});
    this.setData({
      quiet: !!s.quiet,
      items: [
        { key: 'dispatch', title: '新调令通知', desc: '调度派车后立刻推到微信。', on: !!s.dispatch },
        { key: 'arrive', title: '装车 / 到达提醒', desc: '关键节点提醒你别漏点。', on: !!s.arrive },
        { key: 'pay', title: '费用到账通知', desc: '预付、补款、结算到账时提醒。', on: !!s.pay },
        { key: 'license', title: '证照到期提醒', desc: '到期前 60 / 30 / 7 天各提醒一次。', on: !!s.license },
        { key: 'notice', title: '公司公告', desc: '制度调整、节假日安排。可以关。', on: !!s.notice }
      ]
    });
  },

  save(next) {
    setItem('notify_pref', next);
    this.sync();
  },

  current() {
    const map = { quiet: this.data.quiet };
    (this.data.items || []).forEach((i) => {
      map[i.key] = i.on;
    });
    return map;
  },

  toggle(e) {
    const key = e.currentTarget.dataset.k;
    const next = this.current();
    next[key] = !next[key];
    this.save(next);
  },

  toggleQuiet() {
    const next = this.current();
    next.quiet = !next.quiet;
    this.save(next);
  },

  reauth() {
    toast('已按你现在的开关记住了，微信那边开通后会按这个推');
  }
});
