const { ensureAuth } = require('../../utils/auth');
const { getTaskDetail, confirmLoad, depart, confirmArrive } = require('../../api/task');
const { uploadImage } = require('../../api/file');
const { UPLOAD_BASE } = require('../../config/env');
const { toast } = require('../../utils/request');
const { getFontScale } = require('../../utils/font');
const { getManualDefaults } = require('../../services/mock/location');

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

const META = {
  'confirm-load': {
    title: '确认装车',
    noticeTitle: '核对台数和现场照片',
    noticeDesc: '装上车再点确认。照片能帮调度对上现场。',
    photoLabel: '装车照片',
    submit: '确认装车',
    needPhotos: true
  },
  depart: {
    title: '确认出发',
    noticeTitle: '出发后会开始记在途位置',
    noticeDesc: '下一站按调令走。到了再点到达。',
    photoLabel: '出发照片',
    submit: '确认出发',
    needPhotos: false
  },
  'confirm-arrive': {
    title: '确认到达',
    noticeTitle: '到了卸货点再点',
    noticeDesc: '点完就可以开始逐台签收。',
    photoLabel: '卸车照片',
    submit: '确认到达',
    needPhotos: true
  }
};

Page({
  data: {
    fontClass: 'font-lg',
    ready: false,
    taskId: 0,
    action: '',
    taskNo: '',
    route: '',
    place: '',
    qty: 0,
    remark: '',
    files: [],
    mediaType: ['image'],
    needPhotos: false,
    photoLabel: '照片',
    noticeTitle: '',
    noticeDesc: '',
    submitLabel: '确认',
    acting: false,
    uploadPhotos(files) {
      return Promise.all(
        (files || []).map(async (file) => {
          const up = await uploadImage(file.url, 'task_loading');
          file.url = resolveUrl(up.url);
          file.remoteUrl = up.url;
          file.status = 'done';
          file.percent = 100;
        })
      );
    }
  },

  onLoad(query) {
    this.setData({
      taskId: Number(query.id) || 0,
      action: query.action || 'confirm-arrive',
      place: getManualDefaults().place
    });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.boot();
  },

  async boot() {
    const meta = META[this.data.action] || META['confirm-arrive'];
    wx.setNavigationBarTitle({ title: meta.title });
    try {
      const task = await getTaskDetail(this.data.taskId);
      this.setData({
        ready: true,
        taskNo: task.taskNo,
        route: `${task.origin || ''} → ${task.destination || ''}`,
        qty: task.totalQuantity || 0,
        needPhotos: meta.needPhotos,
        photoLabel: meta.photoLabel,
        noticeTitle: meta.noticeTitle,
        noticeDesc: meta.noticeDesc,
        submitLabel: meta.submit
      });
    } catch (e) {
      /* handled */
    }
  },

  inc() {
    this.setData({ qty: this.data.qty + 1 });
  },

  dec() {
    this.setData({ qty: Math.max(0, this.data.qty - 1) });
  },

  onRemark(e) {
    this.setData({ remark: e.detail.value || '' });
  },

  onUploadSuccess(e) {
    this.setData({ files: (e.detail && e.detail.files) || [] });
  },

  onUploadRemove(e) {
    const files = (this.data.files || []).slice();
    const { index } = e.detail || {};
    if (index == null) return;
    files.splice(index, 1);
    this.setData({ files });
  },

  onUploadFail() {
    toast('照片上传失败，请重试');
  },

  async submit() {
    if (this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在确认，请稍候…', mask: true });
    try {
      const remark = (this.data.remark || '').trim() || undefined;
      const photos = collectRemoteUrls(this.data.files);
      const photoUrls = photos.length ? photos : undefined;
      const id = this.data.taskId;
      const action = this.data.action;
      if (action === 'confirm-load') await confirmLoad(id, { remark, photoUrls, location: this.data.place });
      else if (action === 'depart') await depart(id, { remark });
      else await confirmArrive(id, { remark, photoUrls, location: this.data.place });
      toast('已确认');
      setTimeout(() => wx.navigateBack(), 400);
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  }
});
