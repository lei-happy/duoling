const { API_BASE } = require('../config/env');
const { STORAGE_KEYS, getItem } = require('../utils/storage');
const { toast, goLogin, isSessionExpired } = require('../utils/request');

/**
 * 上传本地图片临时路径
 * @param {string} filePath wx.chooseMedia 返回的 tempFilePath
 * @param {string} scene task_loading | task_receipt | avatar
 */
function uploadImage(filePath, scene) {
  const token = getItem(STORAGE_KEYS.ACCESS_TOKEN, '');
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${API_BASE}/file/upload`,
      filePath,
      name: 'file',
      formData: { scene: scene || 'task_receipt' },
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success(res) {
        let body = {};
        try {
          body = JSON.parse(res.data);
        } catch (e) {
          toast('上传失败，请重试');
          reject(new Error('上传失败，请重试'));
          return;
        }
        if (isSessionExpired(res.statusCode, body)) {
          goLogin();
          reject(new Error(body.message || '登录已过期，请重新登录'));
          return;
        }
        if (body.code === 0 && body.data && body.data.url) {
          resolve(body.data);
          return;
        }
        const msg = body.message || '上传失败，请重试';
        toast(msg);
        reject(new Error(msg));
      },
      fail() {
        toast('上传失败，请检查网络后重试');
        reject(new Error('上传失败，请检查网络后重试'));
      }
    });
  });
}

module.exports = {
  uploadImage
};
