const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { PERSONA_OPTIONS, personaLabel, resolvePersona } = require('../../utils/persona');
const { saveDefaultPersona } = require('../../api/auth');
const { toast } = require('../../utils/request');

const VIEW_COPY = {
  dispatch: {
    hello: '调度工作台',
    sub: '先看待派与在途，权限仍按企业授权。',
    kpis: [
      { value: '--', label: '待派车' },
      { value: '--', label: '在途' },
      { value: '--', label: '超时' }
    ],
    entries: [
      { title: '去派车', note: '即将上线' },
      { title: '在途盯梢', note: '即将上线' },
      { title: '回单签收', note: '即将上线' }
    ]
  },
  boss: {
    hello: '老板工作台',
    sub: '先看经营水位与待批，看不到的数字是权限没开。',
    kpis: [
      { value: '--', label: '今日运单' },
      { value: '--', label: '待批' },
      { value: '--', label: '异常' }
    ],
    entries: [
      { title: '经营报表', note: '即将上线' },
      { title: '审批放行', note: '即将上线' },
      { title: '异常预警', note: '即将上线' }
    ]
  },
  finance: {
    hello: '财务工作台',
    sub: '先看待确认与待支付，金额以授权为准。',
    kpis: [
      { value: '--', label: '待审批' },
      { value: '--', label: '待支付' },
      { value: '--', label: '逾期' }
    ],
    entries: [
      { title: '费用确认', note: '即将上线' },
      { title: '标记支付', note: '即将上线' },
      { title: '对账工作台', note: '即将上线' }
    ]
  },
  captain: {
    hello: '车队长工作台',
    sub: '运力与证照视图即将上线。',
    kpis: [
      { value: '--', label: '在途车辆' },
      { value: '--', label: '证照预警' },
      { value: '--', label: '待催司机' }
    ],
    entries: [
      { title: '运力列表', note: '即将上线' },
      { title: '证照预警', note: '即将上线' },
      { title: '催司机', note: '即将上线' }
    ],
    comingSoon: true
  },
  generic: {
    hello: '工作台',
    sub: '还没设置岗位视图，先用通用首页。',
    kpis: [
      { value: '--', label: '今日运单' },
      { value: '--', label: '在途车辆' },
      { value: '--', label: '待调度' }
    ],
    entries: [
      { title: '调度待办', note: '即将上线' },
      { title: '财务确认', note: '即将上线' },
      { title: '经营报表', note: '即将上线' }
    ],
    emptyHint: '请让管理员在「组织管理 → 角色」里补上岗位视图。'
  }
};

function buildHomeState(user) {
  const personas = (user && user.personas) || [];
  const current = resolvePersona(user);
  const view = VIEW_COPY[current] || VIEW_COPY.generic;
  const switchers = PERSONA_OPTIONS.filter((item) => personas.indexOf(item.value) >= 0).map(
    (item) => ({
      ...item,
      selected: item.value === current
    })
  );
  return {
    realName: (user && (user.realName || user.nickname)) || '管理员',
    currentPersona: current,
    currentLabel: personaLabel(current) || '通用',
    switchers,
    showSwitcher: switchers.length > 1,
    hello: view.hello,
    sub: view.sub,
    kpis: view.kpis,
    entries: view.entries,
    comingSoon: !!view.comingSoon,
    emptyHint: view.emptyHint || ''
  };
}

Page({
  data: {
    realName: '管理员',
    currentPersona: '',
    currentLabel: '通用',
    switchers: [],
    showSwitcher: false,
    hello: '工作台',
    sub: '',
    kpis: [],
    entries: [],
    comingSoon: false,
    emptyHint: '',
    saving: false
  },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, null) || getApp().globalData.userInfo || {};
    this.setData(buildHomeState(user));
  },

  async onSwitch(e) {
    const persona = e.currentTarget.dataset.persona;
    if (!persona || persona === this.data.currentPersona || this.data.saving) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
    const personas = user.personas || [];
    if (personas.indexOf(persona) < 0) return;

    this.setData({ saving: true });
    try {
      await saveDefaultPersona(persona);
      const next = getItem(STORAGE_KEYS.USER_INFO, {}) || user;
      this.setData(buildHomeState(next));
    } catch (err) {
      toast('切换视图失败，请重试');
    } finally {
      this.setData({ saving: false });
    }
  }
});
