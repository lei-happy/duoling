const { STORAGE_KEYS, getItem } = require('./utils/storage');

App({
  globalData: {
    userInfo: null,
    tenantCode: '',
    pendingTenants: [],
    /** 任务列表页待应用的状态筛选（工作台 KPI 跳转用） */
    taskStatusFilter: ''
  },

  onLaunch() {
    const userInfo = getItem(STORAGE_KEYS.USER_INFO, null);
    const tenantCode = getItem(STORAGE_KEYS.TENANT_CODE, '');
    this.globalData.userInfo = userInfo;
    this.globalData.tenantCode = tenantCode;
  }
});
