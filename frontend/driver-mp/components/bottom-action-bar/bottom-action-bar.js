Component({
  properties: {
    actions: { type: Array, value: [] },
    loading: { type: Boolean, value: false },
    currentKey: { type: String, value: '' }
  },
  methods: {
    onTap(e) {
      const key = e.currentTarget.dataset.key;
      this.triggerEvent('action', { key });
    }
  }
});
