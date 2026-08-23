Component({
  properties: {
    icon: { type: String, value: '' },
    tone: { type: String, value: '' },
    title: { type: String, value: '' },
    subtitle: { type: String, value: '' },
    extra: { type: String, value: '' },
    extraTone: { type: String, value: '' },
    arrow: { type: Boolean, value: true },
    initial: { type: String, value: '' }
  },
  methods: {
    onTap() {
      this.triggerEvent('tap');
    }
  }
});
