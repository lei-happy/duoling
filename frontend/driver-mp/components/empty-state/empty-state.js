Component({
  properties: {
    text: { type: String, value: '暂无数据' },
    hint: { type: String, value: '' },
    /** 兼容旧调用，已由 t-empty 默认图代替 */
    icon: { type: String, value: '' }
  }
});
