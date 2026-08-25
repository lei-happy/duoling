Component({
  properties: {
    view: { type: Object, value: {} }
  },
  methods: {
    onTap() {
      const id = this.data.view && this.data.view.id;
      if (id) this.triggerEvent('tap', { id });
    },
    onCopy() {
      const taskNo = this.data.view && this.data.view.taskNo;
      if (!taskNo) return;
      wx.setClipboardData({ data: taskNo });
      this.triggerEvent('copy', { taskNo });
    },
    onAction(e) {
      const action = e.currentTarget.dataset.action;
      const view = this.data.view || {};
      this.triggerEvent('action', { action, id: view.id, view });
    }
  }
});
