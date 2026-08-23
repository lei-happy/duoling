Component({
  properties: {
    items: { type: Array, value: [] },
    value: { type: String, value: '' }
  },
  methods: {
    onTap(e) {
      const next = e.currentTarget.dataset.value;
      if (next === this.data.value) return;
      this.triggerEvent('change', { value: next });
    }
  }
});
