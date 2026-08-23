function getRig() {
  return {
    tractor: { plate: '苏A·8F236', model: '解放 J7 · 6×4', year: '2023 年上牌' },
    trailer: { plate: '苏A·H7712挂', model: '中集 8 位商品车半挂', spec: '核定 8 台' },
    km: '18.6',
    fuel: '32.4',
    ontime: '96'
  };
}

function getLicenses() {
  return [
    { id: 'l1', title: '道路运输从业资格证', sub: '2026-09-06 到期 · 本人', tag: '28 天', warn: true, owner: 'me', bar: 23 },
    { id: 'l2', title: '挂车年检', sub: '2026-09-19 到期 · 苏A·H7712挂', tag: '41 天', warn: true, owner: 'car', bar: 34 },
    { id: 'l3', title: '机动车驾驶证 A2', sub: '2029-04-12 到期 · 本人', tag: '正常', warn: false, owner: 'me', bar: 72 },
    { id: 'l4', title: '交强险 + 商业险', sub: '2027-01-30 到期 · 苏A·8F236', tag: '正常', warn: false, owner: 'car', bar: 68 }
  ];
}

function getMaint() {
  return {
    nextKm: '1,400',
    records: [
      { id: 'm1', title: '更换左后轮胎', sub: '07-28 · 德清服务区应急换胎', extra: '¥680' },
      { id: 'm2', title: '常规保养', sub: '06-12 · 南京江宁专修厂', extra: '¥1,260' },
      { id: 'm3', title: '气路检修', sub: '04-03 · 仪征基地门口', extra: '¥420' }
    ],
    violation: '1 条待处理 · 08-05 超速 10% 以内'
  };
}

module.exports = { getRig, getLicenses, getMaint };
