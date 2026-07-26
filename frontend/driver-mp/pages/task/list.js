const { ensureAuth } = require('../../utils/auth');
const { listMyTasks } = require('../../api/task');
const { VISIBLE_STATUS_TABS } = require('../../utils/constants');

Page({
  data: {
    tabs: VISIBLE_STATUS_TABS,
    activeStatus: '',
    keyword: '',
    list: [],
    page: 1,
    pageSize: 10,
    total: 0,
    loading: false,
    loadingMore: false,
    finished: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    const app = getApp();
    if (app && app.globalData.taskStatusFilter !== undefined && app.globalData.taskStatusFilter !== null) {
      const filter = String(app.globalData.taskStatusFilter);
      app.globalData.taskStatusFilter = '';
      if (filter !== this.data.activeStatus) {
        this.setData({ activeStatus: filter });
      }
    }
    this.reload();
  },

  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    this.loadMore();
  },

  onTab(e) {
    const value = e.currentTarget.dataset.value;
    if (value === this.data.activeStatus) return;
    this.setData({ activeStatus: value == null ? '' : String(value) });
    this.reload();
  },

  onKeyword(e) {
    this.setData({ keyword: e.detail.value || '' });
  },

  onSearch() {
    this.reload();
  },

  async reload() {
    this.setData({ page: 1, finished: false, list: [] });
    await this.fetch(true);
  },

  async loadMore() {
    if (this.data.finished || this.data.loading || this.data.loadingMore) return;
    this.setData({ page: this.data.page + 1 });
    await this.fetch(false);
  },

  async fetch(reset) {
    if (reset) this.setData({ loading: true });
    else this.setData({ loadingMore: true });
    try {
      const params = {
        page: this.data.page,
        pageSize: this.data.pageSize
      };
      if (this.data.activeStatus !== '') {
        params.status = Number(this.data.activeStatus);
      }
      if (this.data.keyword) {
        params.keyword = this.data.keyword;
      }
      const res = await listMyTasks(params);
      const list = (res && res.list) || [];
      const total = (res && res.total) || 0;
      const merged = reset ? list : this.data.list.concat(list);
      this.setData({
        list: merged,
        total,
        finished: merged.length >= total || list.length === 0
      });
    } catch (e) {
      if (!reset) {
        this.setData({ page: Math.max(1, this.data.page - 1) });
      }
    } finally {
      this.setData({ loading: false, loadingMore: false });
    }
  },

  onTaskTap(e) {
    const id = e.detail.id;
    if (id) wx.navigateTo({ url: `/pages/task/detail?id=${id}` });
  }
});
