const { ensureAuth } = require('../../utils/auth');
const { getTaskDetail, signItem } = require('../../api/task');
const { getItemStatusInfo } = require('../../utils/constants');
const { toast } = require('../../utils/request');
const { getFontScale } = require('../../utils/font');
const { callReceiver } = require('../../utils/action');

Page({
  data: {
    fontClass: 'font-lg',
    taskId: 0,
    task: null,
    itemsView: [],
    pendingCount: 0,
    pickedCount: 0,
    acting: false,
    signVisible: false,
    signItemId: 0
  },

  onLoad(query) {
    this.setData({ taskId: Number(query.id) || 0 });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.load();
  },

  async load() {
    const id = this.data.taskId;
    if (!id) {
      toast('任务不存在');
      setTimeout(() => wx.navigateBack(), 400);
      return;
    }
    try {
      const task = await getTaskDetail(id);
      const items = task.items || [];
      wx.setNavigationBarTitle({ title: `签收 ${task.taskNo || ''}` });
      this.setData({
        task,
        pendingCount: items.filter((it) => it.status < 3).length,
        itemsView: items.map((it) => {
          const st = getItemStatusInfo(it.status);
          return {
            ...it,
            brandText: `${it.vehicleBrand || '-'} ${it.vehicleModel || ''}`.trim(),
            statusLabel: st.label,
            statusLevel: st.level,
            metaText: `${it.waybillNo || '-'} · ${it.quantity} 台`,
            picked: it.status < 3
          };
        })
      });
      this.syncPicked();
    } catch (e) {
      /* handled */
    }
  },

  toggle(e) {
    const id = Number(e.currentTarget.dataset.id);
    const itemsView = this.data.itemsView.map((it) =>
      it.id === id ? { ...it, picked: !it.picked } : it
    );
    this.setData({ itemsView });
    this.syncPicked();
  },

  syncPicked() {
    this.setData({
      pickedCount: this.data.itemsView.filter((it) => it.status < 3 && it.picked).length
    });
  },

  onCallRecv() {
    callReceiver();
  },

  onDamage() {
    toast('这台先记下货损，调度和客户会看到。其余台可以继续签。');
  },

  async batchSign() {
    const ids = this.data.itemsView.filter((it) => it.status < 3 && it.picked).map((it) => it.id);
    if (!ids.length) {
      toast('先勾选要签的台');
      return;
    }
    if (this.data.acting) return;
    this.setData({ acting: true });
    wx.showLoading({ title: '正在批量签收，请稍候…', mask: true });
    try {
      for (const id of ids) {
        await signItem(id);
      }
      toast(`已签收 ${ids.length} 台`);
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false });
    }
  },

  onSignItem(e) {
    const itemId = e.currentTarget.dataset.id;
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
    wx.showLoading({ title: '正在确认签收，请稍候…', mask: true });
    try {
      await signItem(itemId);
      toast('已签收');
      await this.load();
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ acting: false, signItemId: 0 });
    }
  }
});
