const { buildTicketView } = require('../../utils/task-view');

Component({
  properties: {
    task: { type: Object, value: {} }
  },
  data: {
    view: {}
  },
  observers: {
    task(task) {
      if (!task) return;
      this.setData({ view: buildTicketView(task) });
    }
  },
  methods: {
    onTap(e) {
      this.triggerEvent('tap', e.detail);
    },
    onAction(e) {
      this.triggerEvent('action', e.detail);
    }
  }
});
