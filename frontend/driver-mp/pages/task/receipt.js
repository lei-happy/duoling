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

function collectRemoteUrls(files) {
  return (files || [])
    .map((f) => f.remoteUrl || f.url)
    .filter((u) => u && !/^wxfile:|^http:\/\/tmp|^https:\/\/tmp/i.test(u));
}

Page({
  data: {
    taskId: 0,
    fileList: [],
    mediaType: ['image'],
    remark: '',
    receipts: [],
    submitting: false,
    submitActions: [{ key: 'submit', label: '提交回单', level: 'primary' }],
    uploadReceiptPhotos(files) {
      return Promise.all(
        (files || []).map(async (file) => {
          const up = await uploadImage(file.url, 'task_receipt');
          file.url = resolveUrl(up.url);
          file.remoteUrl = up.url;
          file.status = 'done';
          file.percent = 100;
        })
      );
    }
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

  onUploadSuccess(e) {
    const files = (e.detail && e.detail.files) || [];
    this.setData({ fileList: files });
  },

  onUploadRemove(e) {
    const { index } = e.detail || {};
    const files = (this.data.fileList || []).slice();
    if (index == null || index < 0) return;
    files.splice(index, 1);
    this.setData({ fileList: files });
  },

  onUploadFail() {
    toast('图片上传失败，请重试');
  },

  previewHistory(e) {
    const { urls, current } = e.currentTarget.dataset;
    wx.previewImage({ current, urls });
  },

  async onSubmit() {
    const uploadedUrls = collectRemoteUrls(this.data.fileList);
    if (!uploadedUrls.length) {
      toast('请先上传回单图片');
      return;
    }
    if (this.data.submitting) return;
    this.setData({ submitting: true });
    wx.showLoading({ title: '正在提交回单，请稍候…', mask: true });
    try {
      await uploadReceipt({
        taskId: this.data.taskId,
        fileUrls: uploadedUrls,
        remark: (this.data.remark || '').trim() || undefined
      });
      toast('回单已提交');
      this.setData({ fileList: [], remark: '' });
      wx.redirectTo({ url: `/pages/task/receipt-ok?id=${this.data.taskId}` });
      return;
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
