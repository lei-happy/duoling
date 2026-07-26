/**
 * 环境配置
 * - develop：开发者工具 / 真机调试
 * - trial：体验版
 * - release：正式版
 *
 * 开发时请把 API_BASE 改成可访问的后端地址（本机需用局域网 IP，不能写 localhost 给真机用）
 */
const ENV_MAP = {
  develop: {
    API_BASE: 'http://localhost:8000/api/driver',
    OPEN_BASE: 'http://localhost:8000/api/open',
    UPLOAD_BASE: 'http://localhost:8000'
  },
  trial: {
    API_BASE: 'https://api.example.com/api/driver',
    OPEN_BASE: 'https://api.example.com/api/open',
    UPLOAD_BASE: 'https://api.example.com'
  },
  release: {
    API_BASE: 'https://api.example.com/api/driver',
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
