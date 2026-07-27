Component({
  properties: {
    actions: { type: Array, value: [] },
    loading: { type: Boolean, value: false },
    currentKey: { type: String, value: '' }
  },
  data: {
    viewActions: []
  },
  lifetimes: {
    attached() {
      this.syncActions(this.data.actions);
    }
  },
  observers: {
    actions(actions) {
      this.syncActions(actions);
    }
  },

  methods: {
    syncActions(actions) {
      const list = (actions || []).map((item) => {
        let theme = 'primary';
        if (item.level === 'danger') theme = 'danger';
        else if (item.level === 'success') theme = 'success';
        return { ...item, theme };
      });
      this.setData({ viewActions: list });
    },
    onTap(e) {
      const key = e.currentTarget.dataset.key;
      this.triggerEvent('action', { key });
    }
  }
});

