function getCapsuleSafe() {
  try {
    const sys = wx.getSystemInfoSync();
    const menu = wx.getMenuButtonBoundingClientRect();
    const statusBarHeight = sys.statusBarHeight || 20;
    return {
      statusBarHeight,
      padTop: menu.top || statusBarHeight + 6,
      padRight: Math.max(16, sys.windowWidth - menu.left + 8),
      capsuleHeight: menu.height || 32
    };
  } catch (e) {
    return {
      statusBarHeight: 20,
      padTop: 48,
      padRight: 96,
      capsuleHeight: 32
    };
  }
}

function greetingByHour(name) {
  const hour = new Date().getHours();
  const who = name || '师傅';
  const title = who.indexOf('师傅') >= 0 ? who : `${who}师傅`;
  if (hour < 6) return `${title}，夜深了`;
  if (hour < 11) return `${title}，早上好`;
  if (hour < 14) return `${title}，中午好`;
  if (hour < 18) return `${title}，下午好`;
  return `${title}，晚上好`;
}

module.exports = {
  getCapsuleSafe,
  greetingByHour
};
