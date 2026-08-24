const { ensureAuth } = require('../../utils/auth');
const { getInstance, agree, reject } = require('../../api/approval');
const { toast } = require('../../utils/request');

Page({
  data: { detail: null, taskId: '', chain: [] },
  onLoad(q) {
    this.id = q.id;
    this.setData({ taskId: q.taskId || '' });
    this.load();
  },
  async load() {
    if (!ensureAuth()) return;
    const detail = await getInstance(this.id);
    const chain = (detail && (detail.nodes || detail.tasks)) || [];
    this.setData({ detail, chain });
  },
  async onAgree() {
    if (!this.data.taskId) return;
    await agree(this.data.taskId);
    toast('已通过');
    wx.navigateBack();
  },
  onReject() {
    wx.showModal({
      title: '驳回理由',
      editable: true,
      placeholderText: '会原样发给提交人',
      success: async (res) => {
        if (!res.confirm || !res.content) return;
        await reject(this.data.taskId, res.content);
        toast('已驳回');
        wx.navigateBack();
      }
    });
  }
});
