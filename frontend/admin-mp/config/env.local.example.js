/**
 * 复制为本目录 env.local.js 后按本机局域网 IP 修改。
 * 真机和电脑必须同一 Wi-Fi；不要写 localhost。
 *
 * Windows 查 IP：ipconfig → 无线局域网适配器 WLAN → IPv4
 */
module.exports = {
  API_BASE: 'http://192.168.1.117:8000/api/client',
  OPEN_BASE: 'http://192.168.1.117:8000/api/open',
  UPLOAD_BASE: 'http://192.168.1.117:8000'
};
