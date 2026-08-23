const IDLE_STOPS = [
  { key: 'load', label: '装车', state: '' },
  { key: 'depart', label: '出发', state: '' },
  { key: 'arrive', label: '到达', state: '' },
  { key: 'arriveDest', label: '运抵', state: '' }
];

Component({
  options: {
    multipleSlots: true
  },
  properties: {
    view: { type: Object, value: {} },
    idle: { type: Boolean, value: false },
    showRoad: { type: Boolean, value: true }
  },
  data: {
    idleStops: IDLE_STOPS
  },
  methods: {
    onTap() {
      const id = this.data.view && this.data.view.id;
      if (id) this.triggerEvent('tap', { id });
    },
    onAction(e) {
      const action = e.currentTarget.dataset.action;
      const id = this.data.view && this.data.view.id;
      this.triggerEvent('action', { action, id, view: this.data.view });
    }
  }
});
