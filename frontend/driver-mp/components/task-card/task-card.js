const { getDriverDisplayStatus } = require('../../utils/constants');
const { formatDateTime } = require('../../utils/format');

Component({
  properties: {
    task: { type: Object, value: {} }
  },
  data: {
    statusInfo: { label: '', level: 'default' },
    loadTime: ''
  },
  observers: {
    task(task) {
      if (!task) return;
      this.setData({
        statusInfo: getDriverDisplayStatus(task.status, task.accepted),
        loadTime: formatDateTime(task.plannedLoadTime)
      });
    }
  },
  methods: {
    onTap() {
      this.triggerEvent('tap', { id: this.data.task.id });
    }
  }
});
