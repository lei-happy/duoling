const { ensureAuth } = require('../../utils/auth');
const { uploadImage } = require('../../api/file');
const { uploadReceipt, listMyReceipts, deleteReceipt } = require('../../api/task-receipt');
const { toast } = require('../../utils/request');
const { UPLOAD_BASE } = require('../../config/env');

function resolveUrl(u) {
  if (!u) return '';
  if (/^https?:\/\//.test(u)) return u;
  return UPLOAD_BASE + u;
}

Page({
  data: {
    taskId: 0,
    photos: [],
    uploadedUrls: [],
    remark: '',
    receipts: [],
    submitting: false,
    submitActions: [{ key: 'submit', label: '提交回单', level: 'primary' }]
  },

  onLoad(query) {
    this.setData({ taskId: Number(query.id) || 0 });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.loadReceipts();
  },

  async loadReceipts() {
    if (!this.data.taskId) return;
    try {
      const res = await listMyReceipts({ taskId: this.data.taskId, page: 1, pageSize: 50 });
      const list = (res && res.list) || [];
      this.setData({
        receipts: list.map((r) => ({
          ...r,
          displayUrls: (r.fileUrls || []).map(resolveUrl)
        }))
      });
    } catch (e) {
      /* handled */
    }
  },

  onRemark(e) {
    this.setData({ remark: e.detail.value || '' });
  },

  async choosePhoto() {
    try {
      const res = await wx.chooseMedia({
        count: 9 - this.data.photos.length,
        mediaType: ['image'],
        sourceType: ['album', 'camera'],
        sizeType: ['compressed']
      });
      const files = res.tempFiles || [];
      wx.showLoading({ title: '正在上传回单，请稍候…', mask: true });
      for (let i = 0; i < files.length; i += 1) {
        const up = await uploadImage(files[i].tempFilePath, 'task_receipt');
        this.setData({
          photos: this.data.photos.concat([resolveUrl(up.url)]),
          uploadedUrls: this.data.uploadedUrls.concat([up.url])
        });
      }
    } catch (e) {
      if (e && e.errMsg && e.errMsg.indexOf('cancel') !== -1) return;
    } finally {
      wx.hideLoading();
    }
  },

  removePhoto(e) {
    const index = e.currentTarget.dataset.index;
    const photos = this.data.photos.slice();
    const uploadedUrls = this.data.uploadedUrls.slice();
    photos.splice(index, 1);
    uploadedUrls.splice(index, 1);
    this.setData({ photos, uploadedUrls });
  },

  preview(e) {
    wx.previewImage({ current: e.currentTarget.dataset.url, urls: this.data.photos });
  },

  previewHistory(e) {
    const { urls, current } = e.currentTarget.dataset;
    wx.previewImage({ current, urls });
  },

  async onSubmit() {
    if (!this.data.uploadedUrls.length) {
      toast('请先上传回单图片');
      return;
    }
    if (this.data.submitting) return;
    this.setData({ submitting: true });
    wx.showLoading({ title: '正在提交回单，请稍候…', mask: true });
    try {
      await uploadReceipt({
        taskId: this.data.taskId,
        fileUrls: this.data.uploadedUrls,
        remark: (this.data.remark || '').trim() || undefined
      });
      toast('回单已提交');
      this.setData({ photos: [], uploadedUrls: [], remark: '' });
      await this.loadReceipts();
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ submitting: false });
    }
  },

  async onDelete(e) {
    const id = e.currentTarget.dataset.id;
    const ok = await new Promise((resolve) => {
      wx.showModal({
        title: '删除回单',
        content: '确认删除这组回单？',
        success: (r) => resolve(!!r.confirm),
        fail: () => resolve(false)
      });
    });
    if (!ok) return;
    wx.showLoading({ title: '正在删除，请稍候…', mask: true });
    try {
      await deleteReceipt(id);
      toast('已删除');
      await this.loadReceipts();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
    }
  }
});
