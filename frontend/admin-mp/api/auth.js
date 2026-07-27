/**
 * 登录相关接口占位。
 * 后续对接租户端鉴权（与 Web client 对齐），首版先走本地演示登录。
 */
const { setItem, STORAGE_KEYS } = require('../utils/storage');

async function demoLogin({ phone }) {
  const userInfo = {
    realName: '演示管理员',
    phone,
    roles: ['老板']
  };
  setItem(STORAGE_KEYS.TOKEN, 'demo-token');
  setItem(STORAGE_KEYS.USER_INFO, userInfo);
  setItem(STORAGE_KEYS.TENANT_CODE, 'demo');
  const app = getApp();
  if (app) {
    app.globalData.userInfo = userInfo;
    app.globalData.tenantCode = 'demo';
  }
  return userInfo;
}

module.exports = {
  demoLogin
};
