/**
 * 环境配置
 * - develop：开发者工具 / 真机调试
 * - trial：体验版
 * - release：正式版
 *
 * 模拟器可以用 localhost；真机必须走电脑局域网 IP。
 * 本机 IP 写在 env.local.js（不入库），复制 env.local.example.js 即可。
 */
let local = {};
try {
  local = require('./env.local');
} catch (e) {
  local = {};
}

const ENV_MAP = {
  develop: {
    API_BASE: local.API_BASE || 'http://localhost:8000/api/client',
    OPEN_BASE: local.OPEN_BASE || 'http://localhost:8000/api/open',
    UPLOAD_BASE: local.UPLOAD_BASE || 'http://localhost:8000'
  },
  trial: {
    API_BASE: 'https://api.example.com/api/client',
    OPEN_BASE: 'https://api.example.com/api/open',
    UPLOAD_BASE: 'https://api.example.com'
  },
  release: {
    API_BASE: 'https://api.example.com/api/client',
    OPEN_BASE: 'https://api.example.com/api/open',
    UPLOAD_BASE: 'https://api.example.com'
  }
};

function getEnvVersion() {
  try {
    const info = wx.getAccountInfoSync();
    return (info && info.miniProgram && info.miniProgram.envVersion) || 'develop';
  } catch (e) {
    return 'develop';
  }
}

const env = ENV_MAP[getEnvVersion()] || ENV_MAP.develop;

module.exports = {
  ...env,
  ENV_VERSION: getEnvVersion()
};
