const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { getById } = require('../../services/mock/exception');
const { callDispatcher } = require('../../utils/action');
const { toast } = require('../../utils/request');

Page({
  data: { fontClass: 'font-lg', item: null },

  onLoad(query) {
    const item = getById(query.id);
    if (!item) {
      toast('这条上报找不到了');
      return;
    }
    this.setData({ item });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
  },

  callDispatch() {
    callDispatcher();
  }
});
