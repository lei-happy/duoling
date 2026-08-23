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
const { buildTicketView } = require('../../utils/task-view');
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
    task: null,
    statusInfo: { label: '', level: 'default' },
    actions: [],
    itemsView: [],
    ticketView: {},
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
    confirmFiles: [],
    mediaType: ['image'],
    confirmBtn: { content: '确认', loading: false },
    rejectVisible: false,
    rejectReason: '',
    rejectBtn: { content: '确认拒绝', theme: 'danger', loading: false },
    signVisible: false,
    signItemId: 0,
    /** 供 t-upload 使用：写在 data 初始值里才能作为属性传入 */
    uploadConfirmPhotos(files) {
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
        ticketView: buildTicketView(task),
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
      wx.navigateTo({ url: `/pages/task/sign?id=${this.data.taskId}` });
      return;
    }
    if (key === 'reject') {
      this.setData({
        rejectVisible: true,
        rejectReason: '',
        rejectBtn: { content: '确认拒绝', theme: 'danger', loading: false }
      });
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
      confirmFiles: [],
      confirmBtn: { content: '确认', loading: false },
      currentAction: key
    });
  },

  onConfirmRemark(e) {
    this.setData({ confirmRemark: e.detail.value || '' });
  },

  closeConfirm() {
    if (this.data.acting) return;
    this.setData({ confirmVisible: false, currentAction: '', confirmFiles: [] });
  },

  onConfirmUploadSuccess(e) {
    const files = (e.detail && e.detail.files) || [];
    this.setData({ confirmFiles: files });
  },

  onConfirmUploadRemove(e) {
    const { index } = e.detail || {};
    const files = (this.data.confirmFiles || []).slice();
    if (index == null || index < 0) return;
    files.splice(index, 1);
    this.setData({ confirmFiles: files });
  },

  onUploadFail() {
    toast('照片上传失败，请重试');
  },

  async submitConfirm() {
    if (!this.data.task || this.data.acting) return;
    this.setData({
      acting: true,
      confirmBtn: { content: '确认', loading: true }
    });
    wx.showLoading({ title: '正在确认，请稍候…', mask: true });
    try {
      const taskId = this.data.task.id;
      const remark = (this.data.confirmRemark || '').trim() || undefined;
      const photos = collectRemoteUrls(this.data.confirmFiles);
      const photoUrls = photos.length ? photos : undefined;
      const action = this.data.confirmAction;
      if (action === 'accept') await acceptTask(taskId, { remark });
      else if (action === 'confirm-load') await confirmLoad(taskId, { remark, photoUrls });
      else if (action === 'depart') await depart(taskId, { remark });
      else if (action === 'confirm-arrive') await confirmArrive(taskId, { remark, photoUrls });
      toast('已确认');
      this.setData({ confirmVisible: false, currentAction: '', confirmFiles: [] });
      await this.load();
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({
        acting: false,
        confirmBtn: { content: '确认', loading: false }
      });
    }
  },

  onRejectReason(e) {
    this.setData({ rejectReason: e.detail.value || '' });
  },

  closeReject() {
    if (this.data.acting) return;
    this.setData({ rejectVisible: false });
  },

  async submitReject() {
    const reason = (this.data.rejectReason || '').trim();
    if (!reason) {
      toast('请填写拒单原因');
      return;
    }
    if (!this.data.task || this.data.acting) return;
    this.setData({
      acting: true,
      rejectBtn: { content: '确认拒绝', theme: 'danger', loading: true }
    });
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
      this.setData({
        acting: false,
        rejectBtn: { content: '确认拒绝', theme: 'danger', loading: false }
      });
    }
  },

  onSignItem(e) {
    const itemId =
      (e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.id) ||
      (e.target && e.target.dataset && e.target.dataset.id);
    if (!itemId || this.data.acting) return;
    this.setData({ signVisible: true, signItemId: itemId });
  },

  closeSign() {
    if (this.data.acting) return;
    this.setData({ signVisible: false, signItemId: 0 });
  },

  async submitSign() {
    const itemId = this.data.signItemId;
    if (!itemId || this.data.acting) return;
    this.setData({ acting: true, signVisible: false });
    wx.showLoading({ title: '正在确认交车，请稍候…', mask: true });
    try {
      await signItem(itemId);
      toast('交车成功');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false, signItemId: 0 });
    }
  },

  onTicketAction(e) {
    if (e.detail && e.detail.action === 'sign') {
      wx.navigateTo({ url: `/pages/task/sign?id=${this.data.taskId}` });
    }
  },

  goReceipt() {
    wx.navigateTo({ url: `/pages/task/receipt?id=${this.data.taskId}` });
  },

  goFinance() {
    wx.navigateTo({ url: '/pages/finance/docs' });
  }
});
