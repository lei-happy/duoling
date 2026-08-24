const { API_BASE, OPEN_BASE } = require('../config/env');
const { STORAGE_KEYS, getItem, setItem, clearSession } = require('./storage');

function toast(title) {
  wx.showToast({ title: title || '操作失败，请稍后重试', icon: 'none' });
}

function buildQuery(params) {
  if (!params) return '';
  const parts = [];
  Object.keys(params).forEach((k) => {
    const v = params[k];
    if (v === undefined || v === null || v === '') return;
    parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
  });
  return parts.length ? `?${parts.join('&')}` : '';
}

let refreshing = null;

function applyTokenPair(data) {
  const access = data.accessToken || data.access_token;
  const refresh = data.refreshToken || data.refresh_token;
  if (access) setItem(STORAGE_KEYS.TOKEN, access);
  if (refresh) setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh);
}

function tryRefresh() {
  if (refreshing) return refreshing;
  const refreshToken = getItem(STORAGE_KEYS.REFRESH_TOKEN, '');
  if (!refreshToken) return Promise.resolve(false);
  refreshing = rawRequest({
    url: '/auth/refresh',
    method: 'POST',
    data: { refresh_token: refreshToken },
    skipAuth: true,
    skipRefresh: true,
    showError: false
  })
    .then((data) => {
      applyTokenPair(data || {});
      return true;
    })
    .catch(() => false)
    .finally(() => {
      refreshing = null;
    });
  return refreshing;
}

function kickToLogin() {
  clearSession();
  toast('登录已过期，请重新登录');
  wx.reLaunch({ url: '/pages/login/login' });
}

function rawRequest(options) {
  const {
    url,
    method = 'GET',
    data,
    params,
    header = {},
    base = 'api',
    showError = true,
    skipAuth = false
  } = options;

  const baseUrl = base === 'open' ? OPEN_BASE : API_BASE;
  const token = skipAuth ? '' : getItem(STORAGE_KEYS.TOKEN, '');
  const finalUrl = `${baseUrl}${url}${buildQuery(params)}`;

  return new Promise((resolve, reject) => {
    wx.request({
      url: finalUrl,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...header
      },
      success(res) {
        const body = res.data || {};
        const code = body.code !== undefined ? body.code : res.statusCode;
        if (res.statusCode === 401 || code === 401) {
          reject({ __unauthorized: true, body });
          return;
        }
        if (res.statusCode >= 200 && res.statusCode < 300 && (code === 0 || code === 200 || code === undefined)) {
          resolve(body.data !== undefined ? body.data : body);
          return;
        }
        const msg = body.message || body.msg || '加载失败，请重试';
        if (showError) toast(msg);
        reject(body);
      },
      fail() {
        const usingLoopback = /localhost|127\.0\.0\.1/.test(finalUrl);
        if (showError) {
          toast(
            usingLoopback
              ? '真机连不上本机地址，请把电脑局域网 IP 写进 config/env.local.js'
              : '网络不太稳定，请稍后重试'
          );
        }
        reject(new Error('network'));
      }
    });
  });
}

async function request(options) {
  try {
    return await rawRequest(options);
  } catch (err) {
    if (!err || !err.__unauthorized || options.skipRefresh) {
      throw err;
    }
    const ok = await tryRefresh();
    if (!ok) {
      kickToLogin();
      throw err.body || err;
    }
    return rawRequest({ ...options, skipRefresh: true });
  }
}

module.exports = {
  request,
  toast,
  get: (url, options = {}) => request({ ...options, url, method: 'GET' }),
  post: (url, data, options = {}) => request({ ...options, url, method: 'POST', data }),
  put: (url, data, options = {}) => request({ ...options, url, method: 'PUT', data }),
  del: (url, options = {}) => request({ ...options, url, method: 'DELETE' })
};
