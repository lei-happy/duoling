const LEVEL_THEME = {
  default: 'default',
  primary: 'primary',
  success: 'success',
  warning: 'warning',
  danger: 'danger',
  info: 'primary'
};

Component({
  properties: {
    label: { type: String, value: '' },
    level: { type: String, value: 'default' }
  },
  data: {
    tagTheme: 'default'
  },
  lifetimes: {
    attached() {
      this.setData({ tagTheme: LEVEL_THEME[this.data.level] || 'default' });
    }
  },
  observers: {
    level(level) {
      this.setData({ tagTheme: LEVEL_THEME[level] || 'default' });
    }
  }
});

