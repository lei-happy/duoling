const ICON_BY_THEME = {
  amber: 'warn',
  danger: 'warn',
  info: 'info',
  ok: 'check'
};

Component({
  properties: {
    theme: { type: String, value: 'amber' },
    title: { type: String, value: '' },
    desc: { type: String, value: '' },
    link: { type: String, value: '' }
  },
  data: { iconName: 'warn' },
  observers: {
    theme(theme) {
      this.setData({ iconName: ICON_BY_THEME[theme] || 'warn' });
    }
  },
  methods: {
    onLink() {
      this.triggerEvent('link');
    }
  }
});
