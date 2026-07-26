const { API_BASE, OPEN_BASE } = require('../config/env');
const { STORAGE_KEYS, getItem, setItem, clearSession } = require('./storage');

const AUTH_LOGIN_URLS = ['/auth/login', '/auth/sms-login', '/auth/switch-tenant'];

function isAuthLoginRequest(url) {
  if (!url) return false;
  return AUTH_LOGIN_URLS.some((p) => url.indexOf(p) !== -1);
}

function buildQuery(params) {
  if (!params) return '';
  const parts = [];
  Object.keys(params).forEach((k) => {
    const v = params[k];
    if (v === undefined || v === null || v === '') return;
    if (Array.isArray(v)) {
      v.forEach((item) => parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(item)}`));
    } else {
      parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
    }
  });
  return parts.length ? `?${parts.join('&')}` : '';
}

function toast(title) {
  wx.showToast({ title: title || '操作失败，请稍后重试', icon: 'none', duration: 2500 });
}

function goLogin() {
  const pages = getCurrentPages();
  const cur = pages[pages.length - 1];
  const route = cur ? `/${cur.route}` : '';
  if (route.indexOf('/pages/login/') !== -1 || route.indexOf('/pages/sms-login/') !== -1) {
    return;
  }
  clearSession();
  toast('登录已过期，请重新登录');
  setTimeout(() => {
    wx.reLaunch({ url: '/pages/login/login' });
  }, 400);
}

function request(options) {
  const {
    url,
    method = 'GET',
    data,
    header = {},
    baseURL = API_BASE,
    silent = false
  } = options;

  const token = getItem(STORAGE_KEYS.ACCESS_TOKEN, '');
  const headers = {
    'Content-Type': 'application/json',
    ...header
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseURL}${url}`,
      method,
      data,
      header: headers,
      timeout: 20000,
      success(res) {
        const status = res.statusCode;
        const body = res.data || {};
        const refreshed = res.header && (res.header.Authorization || res.header.authorization);
        if (typeof refreshed === 'string' && refreshed.indexOf('Bearer ') === 0) {
          setItem(STORAGE_KEYS.ACCESS_TOKEN, refreshed.slice('Bearer '.length));
        }

        if (status === 401) {
          const msg = body.message || '登录失败，请重试';
          if (isAuthLoginRequest(url)) {
            if (!silent) toast(msg);
            reject(new Error(msg));
            return;
          }
          goLogin();
          reject(new Error(msg));
          return;
        }

        if (status === 403) {
          const msg = body.message || '暂无权限访问';
          if (!silent) toast(msg);
          reject(new Error(msg));
          return;
        }

        if (status >= 200 && status < 300) {
          if (body && typeof body === 'object' && 'code' in body) {
            if (body.code === 0) {
              resolve(body.data);
              return;
            }
            const msg = body.message || '操作失败，请稍后重试';
            if (!silent) toast(msg);
            reject(new Error(msg));
            return;
          }
          resolve(body);
          return;
        }

        const msg = (body && body.message) || '加载失败，请重试';
        if (!silent) toast(msg);
        reject(new Error(msg));
      },
      fail() {
        if (!silent) toast('网络不太稳定，请检查后重试');
        reject(new Error('网络不太稳定，请检查后重试'));
      }
    });
  });
}

function get(url, params, options) {
  return request({
    url: url + buildQuery(params),
    method: 'GET',
    ...(options || {})
  });
}

function post(url, data, options) {
  return request({
    url,
    method: 'POST',
    data: data || {},
    ...(options || {})
  });
}

function put(url, data, options) {
  return request({
    url,
    method: 'PUT',
    data: data || {},
    ...(options || {})
  });
}

function del(url, params, options) {
  return request({
    url: url + buildQuery(params),
    method: 'DELETE',
    ...(options || {})
  });
}

/** 开放接口（短信等），不走 driver base */
function openPost(url, data) {
  return request({
    url,
    method: 'POST',
    data: data || {},
    baseURL: OPEN_BASE
  });
}

module.exports = {
  request,
  get,
  post,
  put,
  del,
  openPost,
  toast
};
