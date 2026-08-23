const { getDriverDisplayStatus } = require('./constants');
const { formatDateTime, formatDate } = require('./format');

const STUB = {
  waitAccept: '#1d4ed8',
  waitLoad: '#94a3b8',
  loaded: '#94a3b8',
  inTransit: '#f5a524',
  waitSign: '#0ea5e9',
  done: '#16a34a',
  idle: '#b7c0ce',
  other: '#94a3b8'
};

function displayKey(status, accepted) {
  if (status === 1) return accepted ? 'waitLoad' : 'waitAccept';
  if (status === 2) return 'loaded';
  if (status === 3) return 'inTransit';
  if (status === 4) return 'waitSign';
  if (status === 5) return 'done';
  return 'other';
}

function getStubColor(status, accepted) {
  return STUB[displayKey(status, accepted)] || STUB.other;
}

function getRoadState(status, accepted) {
  const stops = [
    { key: 'load', label: '装车', state: '' },
    { key: 'depart', label: '出发', state: '' },
    { key: 'arrive', label: '到达', state: '' },
    { key: 'sign', label: '签收', state: '' }
  ];
  let percent = 0;
  let current = -1;
  if (status === 1 && accepted) {
    current = 0;
    percent = 8;
    stops[0].state = 'is-now';
  } else if (status === 2) {
    current = 1;
    percent = 33;
    stops[0].state = 'is-done';
    stops[1].state = 'is-now';
  } else if (status === 3) {
    current = 2;
    percent = 62;
    stops[0].state = 'is-done';
    stops[1].state = 'is-done';
    stops[2].state = 'is-now';
  } else if (status === 4) {
    current = 3;
    percent = 85;
    stops[0].state = 'is-done';
    stops[1].state = 'is-done';
    stops[2].state = 'is-done';
    stops[3].state = 'is-now';
  } else if (status >= 5) {
    current = 3;
    percent = 100;
    stops.forEach((s) => {
      s.state = 'is-done';
    });
  }
  return { percent, current, stops, parked: status < 2 };
}

function remainText(plannedArriveTime) {
  if (!plannedArriveTime) return '';
  const d = new Date(plannedArriveTime);
  if (Number.isNaN(d.getTime())) return '';
  const diff = d.getTime() - Date.now();
  if (diff <= 0) return '已过到货时间';
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  if (h >= 48) return '';
  if (h <= 0) return `还剩 ${m} 分`;
  return `还剩 ${h} 小时 ${m} 分`;
}

function shortTime(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  const mm = `${d.getMonth() + 1}`.padStart(2, '0');
  const dd = `${d.getDate()}`.padStart(2, '0');
  const hh = `${d.getHours()}`.padStart(2, '0');
  const mi = `${d.getMinutes()}`.padStart(2, '0');
  return `${mm}-${dd} ${hh}:${mi}`;
}

function dayKey(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return `${d.getFullYear()}-${`${d.getMonth() + 1}`.padStart(2, '0')}-${`${d.getDate()}`.padStart(2, '0')}`;
}

function dayLabel(value) {
  if (!value) return '待定日期';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '待定日期';
  const today = new Date();
  const t0 = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
  const d0 = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  const diff = Math.round((d0 - t0) / 86400000);
  const md = `${`${d.getMonth() + 1}`.padStart(2, '0')}-${`${d.getDate()}`.padStart(2, '0')}`;
  if (diff === 0) return `今天 · ${md}`;
  if (diff === 1) return `明天 · ${md}`;
  if (diff === -1) return `昨天 · ${md}`;
  const week = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()];
  return `周${week} · ${md}`;
}

function splitPlace(text) {
  const raw = (text || '').trim();
  if (!raw) return { title: '-', sub: '' };
  return { title: raw, sub: '' };
}

function isActiveTask(task) {
  const s = Number(task && task.status);
  return s >= 1 && s <= 4;
}

function matchChip(task, chip) {
  if (!chip || chip === 'all') return isActiveTask(task);
  if (chip === 'waitAccept') return task.status === 1 && !task.accepted;
  if (chip === 'waitLoad') return task.status === 1 && !!task.accepted;
  if (chip === '2') return task.status === 2;
  if (chip === '3') return task.status === 3;
  if (chip === '4') return task.status === 4;
  if (chip === '5') return task.status === 5;
  return String(task.status) === String(chip);
}

function apiStatusForChip(chip) {
  if (!chip || chip === 'all') return '';
  if (chip === 'waitAccept' || chip === 'waitLoad') return 1;
  if (chip === '2' || chip === '3' || chip === '4' || chip === '5') return Number(chip);
  return '';
}

function buildTicketView(task) {
  const t = task || {};
  const display = getDriverDisplayStatus(t.status, t.accepted);
  const road = getRoadState(t.status, t.accepted);
  const key = displayKey(t.status, t.accepted);
  const qty = t.totalQuantity || 0;
  const remain = t.status === 3 ? remainText(t.plannedArriveTime) : '';
  let timeMeta = '';
  if (t.status === 1 && !t.accepted && t.plannedLoadTime) {
    timeMeta = `计划装车 ${shortTime(t.plannedLoadTime)}`;
  } else if (t.status === 1 && t.accepted && t.plannedLoadTime) {
    timeMeta = `计划装车 ${shortTime(t.plannedLoadTime)}`;
  } else if (t.plannedArriveTime) {
    timeMeta = `要求 ${shortTime(t.plannedArriveTime)} 前到货`;
  } else if (t.actualArriveTime) {
    timeMeta = `${shortTime(t.actualArriveTime)} 到达`;
  } else if (t.plannedLoadTime) {
    timeMeta = `计划装车 ${shortTime(t.plannedLoadTime)}`;
  }

  return {
    id: t.id,
    taskNo: t.taskNo || '',
    typeLabel: t.taskName || '',
    statusLabel: display.label,
    statusLevel: display.level,
    stubColor: getStubColor(t.status, t.accepted),
    origin: splitPlace(t.origin),
    destination: splitPlace(t.destination),
    quantity: qty,
    qtyText: qty ? `${qty} 台` : '',
    plateNumber: t.plateNumber || '',
    timeMeta,
    remain,
    showRoad: t.status >= 2 && t.status <= 4,
    roadPercent: road.percent,
    roadStops: road.stops,
    showPulse: t.status === 3,
    accepted: !!t.accepted,
    status: t.status,
    canAccept: t.status === 1 && !t.accepted,
    canSign: t.status === 4,
    canDepart: t.status === 2,
    canArrive: t.status === 3,
    dayKey: dayKey(t.plannedLoadTime || t.plannedArriveTime),
    daySort: t.plannedLoadTime || t.plannedArriveTime || '',
    carrierType: t.carrierType
  };
}

function groupByDay(views) {
  const map = {};
  const order = [];
  (views || []).forEach((v) => {
    const key = v.dayKey || 'unknown';
    if (!map[key]) {
      map[key] = { key, label: dayLabel(v.daySort), list: [] };
      order.push(key);
    }
    map[key].list.push(v);
  });
  return order.map((k) => {
    const g = map[k];
    return { ...g, count: g.list.length };
  });
}

function weekDays(tasks) {
  const now = new Date();
  const dow = now.getDay() === 0 ? 7 : now.getDay();
  const monday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - (dow - 1));
  const weekLabels = ['一', '二', '三', '四', '五', '六', '日'];
  const keys = new Set();
  (tasks || []).forEach((t) => {
    const raw = t.plannedLoadTime || t.actualLoadTime || t.plannedArriveTime;
    if (!raw) return;
    keys.add(dayKey(raw));
  });
  const days = [];
  let hasCount = 0;
  for (let i = 0; i < 7; i += 1) {
    const d = new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + i);
    const key = dayKey(d);
    const today = dayKey(now);
    const has = keys.has(key);
    if (has) hasCount += 1;
    days.push({
      key,
      week: weekLabels[i],
      date: d.getDate(),
      on: key === today,
      has
    });
  }
  const sundayRest = !keys.has(dayKey(new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + 6)));
  return {
    days,
    rangeText: `${shortMd(monday)} 至 ${shortMd(new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + 6))}`,
    tripCount: hasCount,
    sundayRest
  };
}

function shortMd(d) {
  return `${`${d.getMonth() + 1}`.padStart(2, '0')}-${`${d.getDate()}`.padStart(2, '0')}`;
}

module.exports = {
  displayKey,
  getStubColor,
  getRoadState,
  remainText,
  shortTime,
  dayKey,
  dayLabel,
  isActiveTask,
  matchChip,
  apiStatusForChip,
  buildTicketView,
  groupByDay,
  weekDays,
  formatDateTime,
  formatDate
};
