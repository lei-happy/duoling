const { ensureAuth } = require('../../utils/auth');
const {
  getTaskDetail,
  acceptTask,
  rejectTask,
  confirmLoad,
  depart,
  confirmArrive,
  signItem
} = require('../../api/task');
const { uploadImage } = require('../../api/file');
const { formatDateTime, formatMoney } = require('../../utils/format');
const {
  getDriverDisplayStatus,
  getItemStatusInfo,
  getAvailableActions
} = require('../../utils/constants');
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
    task: null,
    statusInfo: { label: '', level: 'default' },
    actions: [],
    itemsView: [],
    itemCount: 0,
    plannedLoadText: '-',
    plannedArriveText: '-',
    prepaidText: '0.00',
    settledText: '0.00',
    acting: false,
    currentAction: '',
    confirmVisible: false,
    confirmTitle: '',
    confirmMessage: '',
    confirmRemark: '',
    confirmAction: '',
    needPhotos: false,
    photoLabel: '照片',
    photos: [],
    photoUrls: [],
    rejectVisible: false,
    rejectReason: ''
  },

  onLoad(query) {
    this.setData({ taskId: Number(query.id) || 0 });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.load();
  },

  async load() {
    const id = this.data.taskId;
    if (!id) {
      toast('任务不存在');
      setTimeout(() => wx.navigateBack(), 500);
      return;
    }
    try {
      const task = await getTaskDetail(id);
      task.segments = task.segments || [];
      task.items = task.items || [];
      const statusInfo = getDriverDisplayStatus(task.status, task.accepted);
      const actions = getAvailableActions(task.status, task.accepted);
      const items = task.items || [];
      const itemsView = items.map((it) => {
        const st = getItemStatusInfo(it.status);
        return {
          ...it,
          brandText: `${it.vehicleBrand || '-'} ${it.vehicleModel || ''}`.trim(),
          statusLabel: st.label,
          statusLevel: st.level,
          metaText: `${it.waybillNo || '-'} · ${it.customerName || '-'} · ${it.quantity} 台`
        };
      });
      this.setData({
        task,
        statusInfo,
        actions,
        itemsView,
        itemCount: items.length,
        plannedLoadText: formatDateTime(task.plannedLoadTime),
        plannedArriveText: formatDateTime(task.plannedArriveTime),
        prepaidText: formatMoney(task.prepaidAmount || 0),
        settledText: formatMoney(task.settledAmount || 0)
      });
      wx.setNavigationBarTitle({ title: task.taskNo || '任务详情' });
    } catch (e) {
      /* handled */
    }
  },

  onAction(e) {
    const key = e.detail.key;
    if (key === 'sign-items') {
      const next = (this.data.task.items || []).find((it) => it.status < 3);
      if (next) this.onSignItem({ currentTarget: { dataset: { id: next.id } } });
      else toast('暂无可签收的运单');
      return;
    }
    if (key === 'reject') {
      this.setData({ rejectVisible: true, rejectReason: '' });
      return;
    }
    const configs = {
      accept: { title: '接收调令', message: '确认接收该调令？接收后即可确认装车' },
      'confirm-load': {
        title: '确认装车',
        message: '请确认车辆已完成装车，状态将更新为「已装车」'
      },
      depart: { title: '确认出发', message: '请确认已发车上路，状态将更新为「在途」' },
      'confirm-arrive': {
        title: '确认到达',
        message: '请确认已抵达卸货点，状态将更新为「已到达」'
      }
    };
    const cfg = configs[key];
    if (!cfg) return;
    const needPhotos = key === 'confirm-load' || key === 'confirm-arrive';
    this.setData({
      confirmVisible: true,
      confirmTitle: cfg.title,
      confirmMessage: cfg.message,
      confirmRemark: '',
      confirmAction: key,
      needPhotos,
      photoLabel: key === 'confirm-load' ? '装车照片' : '卸车照片',
      photos: [],
      photoUrls: [],
      currentAction: key
    });
  },

  onConfirmRemark(e) {
    this.setData({ confirmRemark: e.detail.value || '' });
  },

  closeConfirm() {
    this.setData({ confirmVisible: false, currentAction: '' });
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
      wx.showLoading({ title: '正在上传照片，请稍候…', mask: true });
      for (let i = 0; i < files.length; i += 1) {
        const up = await uploadImage(files[i].tempFilePath, 'task_loading');
        const display = resolveUrl(up.url);
        this.setData({
          photos: this.data.photos.concat([display]),
          photoUrls: this.data.photoUrls.concat([up.url])
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
    const photoUrls = this.data.photoUrls.slice();
    photos.splice(index, 1);
    photoUrls.splice(index, 1);
    this.setData({ photos, photoUrls });
  },

  previewPhoto(e) {
    const url = e.currentTarget.dataset.url;
    wx.previewImage({ current: url, urls: this.data.photos });
  },

  async submitConfirm() {
    if (!this.data.task || this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在确认，请稍候…', mask: true });
    try {
      const taskId = this.data.task.id;
      const remark = (this.data.confirmRemark || '').trim() || undefined;
      const photos = this.data.photoUrls.length ? this.data.photoUrls.slice() : undefined;
      const action = this.data.confirmAction;
      if (action === 'accept') await acceptTask(taskId, { remark });
      else if (action === 'confirm-load') await confirmLoad(taskId, { remark, photoUrls: photos });
      else if (action === 'depart') await depart(taskId, { remark });
      else if (action === 'confirm-arrive') await confirmArrive(taskId, { remark, photoUrls: photos });
      toast('已确认');
      this.setData({ confirmVisible: false, currentAction: '' });
      await this.load();
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  onRejectReason(e) {
    this.setData({ rejectReason: e.detail.value || '' });
  },

  closeReject() {
    this.setData({ rejectVisible: false });
  },

  async submitReject() {
    const reason = (this.data.rejectReason || '').trim();
    if (!reason) {
      toast('请填写拒单原因');
      return;
    }
    if (!this.data.task || this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在提交，请稍候…', mask: true });
    try {
      await rejectTask(this.data.task.id, { reason });
      toast('已拒单');
      this.setData({ rejectVisible: false });
      setTimeout(() => wx.navigateBack(), 400);
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  async onSignItem(e) {
    const itemId = e.currentTarget.dataset.id;
    if (!itemId || this.data.acting) return;
    const ok = await new Promise((resolve) => {
      wx.showModal({
        title: '确认签收',
        content: '确认该运单已签收？',
        success: (r) => resolve(!!r.confirm),
        fail: () => resolve(false)
      });
    });
    if (!ok) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在签收，请稍候…', mask: true });
    try {
      await signItem(itemId);
      toast('签收成功');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  goReceipt() {
    wx.navigateTo({ url: `/pages/task/receipt?id=${this.data.taskId}` });
  },

  goFinance() {
    wx.navigateTo({ url: `/pages/finance/list?taskId=${this.data.taskId}` });
  },

  noop() {}
});
