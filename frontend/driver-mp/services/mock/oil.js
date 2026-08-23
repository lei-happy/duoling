function getOilCard() {
  return {
    brand: '中石化',
    balance: '1,240',
    cardNo: '1001****7736',
    monthUsed: '2,860',
    points: '3,860'
  };
}

function getOilFlows() {
  return [
    { id: 'o1', kind: 'fuel', title: '中石化 G25 德清服务区', sub: '08-09 14:30 · TK2608090037 · 加柴油 82L', amount: '-620', tone: 'danger' },
    { id: 'o2', kind: 'recharge', title: '车管充值', sub: '08-08 09:00 · 李敏操作', amount: '+2,000', tone: 'ok' },
    { id: 'o3', kind: 'fuel', title: '中石油 沪宁高速仙人山站', sub: '08-07 11:12 · TK2608070008 · 加柴油 95L', amount: '-712', tone: 'danger' },
    { id: 'o4', kind: 'deduct', title: '违章罚款代扣', sub: '08-05 · 苏A·8F236 超速 10% 以内', amount: '-200', tone: 'danger' }
  ];
}

function getStations() {
  return [
    { id: 's1', name: '中石化 G25 德清服务区站', sub: '柴油 0# ¥7.56 / L · 顺路，不用下高速', km: '2.4 km' },
    { id: 's2', name: '中石化 德清武康站', sub: '柴油 0# ¥7.52 / L · 下高速 6 分钟', km: '8.1 km' },
    { id: 's3', name: '中石油 杭宁高速湖州站', sub: '柴油 0# ¥7.58 / L · 前方服务区', km: '31 km' },
    { id: 's4', name: '中石化 萧山机场路站', sub: '柴油 0# ¥7.49 / L · 卸货点附近', km: '78 km' },
    { id: 's5', name: '中石化 杭州萧然南路站', sub: '柴油 0# ¥7.51 / L · 可过夜停车', km: '84 km' },
    { id: 's6', name: '中石油 宁波北仑港站', sub: '柴油 0# ¥7.55 / L · 下一单装车点', km: '168 km' }
  ];
}

function getGroupedFlows() {
  return [
    { title: 'TK2608090037', sub: '上汽仪征基地 → 杭州萧山中转库 · 1 笔', amount: '-620' },
    { title: 'TK2608070008', sub: '上汽仪征基地 → 常州武进库 · 2 笔', amount: '-1,140' },
    { title: 'TK2608050031', sub: '上汽仪征基地 → 扬州邗江仓 · 1 笔', amount: '-560' },
    { title: '未关联任务', sub: '违章代扣、日常杂项 · 2 笔', amount: '-540' }
  ];
}

module.exports = { getOilCard, getOilFlows, getStations, getGroupedFlows };
