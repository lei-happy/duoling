function getHonor() {
  return {
    title: '金牌司机',
    rank: '本企业第 6 名',
    safeDays: 412,
    ontime: 96,
    score: '4.9',
    kpis: [
      { label: '准点率', value: '96%', width: 96 },
      { label: '回单及时', value: '92%', width: 92 },
      { label: '货损为零', value: '100%', width: 100 },
      { label: '油耗达标', value: '88%', width: 88 }
    ],
    reviews: [
      { id: 'r1', who: '杭州萧山中转库', text: '到得准时，卸车配合好，下次还想派这台车。', time: '08-08' },
      { id: 'r2', who: '宁波北仑港', text: '单据齐全，商品车无划痕。', time: '08-03' },
      { id: 'r3', who: '常州武进库', text: '路上报过一次延误，沟通清楚。', time: '07-26' }
    ]
  };
}

module.exports = { getHonor };
