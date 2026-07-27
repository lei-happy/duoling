const { STORAGE_KEYS, getItem } = require('./utils/storage');

App({
  globalData: {
    userInfo: null,
    tenantCode: ''
  },

  onLaunch() {
    this.globalData.userInfo = getItem(STORAGE_KEYS.USER_INFO, null);
    this.globalData.tenantCode = getItem(STORAGE_KEYS.TENANT_CODE, '');
  }
});
