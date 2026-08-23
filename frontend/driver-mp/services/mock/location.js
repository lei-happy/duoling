function getNavInfo(dest) {
  const title = dest && dest !== '-' ? dest : '杭州萧山中转库';
  return {
    destTitle: title,
    km: 86,
    eta: '16:20',
    lastAt: '14:48',
    lastPlace: '浙江省湖州市德清县 G25 长深高速',
    speed: 78,
    latitude: 30.1833,
    longitude: 120.2644,
    tracks: [
      { title: 'G25 长深高速 · 德清段', time: '14:48', desc: '当前位置 · 车速 78 km/h', now: true },
      { title: '南京江宁库 出发', time: '09:52', desc: '第 2 段起点' },
      { title: '南京江宁库 到达', time: '09:40', desc: '' },
      { title: '上汽仪征基地 装车完成', time: '07:12', desc: '8 台 · 上传现场照片 4 张' }
    ]
  };
}

function getManualDefaults() {
  return {
    place: '浙江省湖州市德清县 G25 长深高速',
    situations: ['正常行驶', '休息停车', '堵车缓行', '排队装卸'],
    etaOptions: ['按原计划', '晚 30 分钟', '晚 1 小时', '说不好']
  };
}

module.exports = { getNavInfo, getManualDefaults };
