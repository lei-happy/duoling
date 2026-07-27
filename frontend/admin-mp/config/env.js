/**
 * 环境配置
 * - develop：开发者工具 / 真机调试
 * - trial：体验版
 * - release：正式版
 *
 * 管理员端复用租户 Web 接口前缀 /api/client（后续按业务再拆）
 */
const ENV_MAP = {
  develop: {
    API_BASE: 'http://localhost:8000/api/client',
    OPEN_BASE: 'http://localhost:8000/api/open',
    UPLOAD_BASE: 'http://localhost:8000'
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
