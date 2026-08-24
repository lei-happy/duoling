const { API_BASE, OPEN_BASE } = require('../config/env');
const { STORAGE_KEYS, getItem, clearSession } = require('./storage');

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

function request(options) {
  const {
    url,
    method = 'GET',
    data,
    params,
    header = {},
    base = 'api',
    showError = true
  } = options;

  const baseUrl = base === 'open' ? OPEN_BASE : API_BASE;
  const token = getItem(STORAGE_KEYS.TOKEN, '');
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
          clearSession();
          if (showError) toast('登录已过期，请重新登录');
          wx.reLaunch({ url: '/pages/login/login' });
          reject(body);
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
        if (showError) toast('网络不太稳定，请稍后重试');
        reject(new Error('network'));
      }
    });
  });
}

module.exports = {
  request,
  toast,
  get: (url, options = {}) => request({ ...options, url, method: 'GET' }),
  post: (url, data, options = {}) => request({ ...options, url, method: 'POST', data }),
  put: (url, data, options = {}) => request({ ...options, url, method: 'PUT', data })
};
