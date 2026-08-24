Page({
  data: { item: {} },
  onLoad(q) {
    this.setData({
      item: {
        type: q.type,
        id: q.id,
        title: decodeURIComponent(q.title || ''),
        phone: q.phone || '',
        subtitle: decodeURIComponent(q.subtitle || '')
      }
    });
  },
  onCall() {
    if (this.data.item.phone) wx.makePhoneCall({ phoneNumber: this.data.item.phone });
  },
  onCopy() {
    wx.setClipboardData({ data: this.data.item.phone || this.data.item.title });
  }
});
