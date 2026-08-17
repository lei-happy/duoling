const POLICIES = {
  service: {
    title: '服务协议',
    text:
      '智途司机端为你所在企业的驾驶员提供接单、装车、签收和收入查询。登录后，系统只用你的手机号匹配企业里的司机档案，不会用它注册其他账号。任务、收入按你当前进入的企业分开计算。如信息有误，请联系企业调度员处理。'
  },
  privacy: {
    title: '隐私政策',
    text:
      '我们会收集你的手机号，用于登录和匹配司机档案；在你使用拍照回单、位置上报等功能时，才会申请对应权限。数据仅用于当前企业的运输作业，不会出售给第三方。你可以在「我的」里退出登录，退出后本机不再保留登录状态。'
  }
};

function getStatusBarHeight() {
  try {
    const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
    return Number(info.statusBarHeight) || 20;
  } catch (e) {
    return 20;
  }
}

function getPolicy(key) {
  return POLICIES[key] || POLICIES.privacy;
}

module.exports = {
  getStatusBarHeight,
  getPolicy
};
