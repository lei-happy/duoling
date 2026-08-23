Component({
  properties: {
    theme: { type: String, value: 'amber' },
    title: { type: String, value: '' },
    desc: { type: String, value: '' },
    link: { type: String, value: '' }
  },
  methods: {
    onLink() {
      this.triggerEvent('link');
    }
  }
});
