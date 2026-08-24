const { notifySettings } = require('../../services/mock/index');

Page({
  data: { settings: notifySettings },
  onToggle(e) {
    const key = e.currentTarget.dataset.key;
    const settings = { ...this.data.settings, [key]: !this.data.settings[key] };
    this.setData({ settings });
  }
});
