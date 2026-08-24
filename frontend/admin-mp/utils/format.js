function pick(obj, camel, snake, fallback) {
  if (!obj) return fallback;
  const v = obj[camel] != null ? obj[camel] : obj[snake];
  return v == null ? fallback : v;
}

function money(n, digits) {
  const v = Number(n);
  if (!Number.isFinite(v)) return '--';
  const d = digits == null ? 0 : digits;
  return v.toFixed(d).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function wan(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return '--';
  return (v / 10000).toFixed(1);
}

function shortTime(v) {
  if (!v) return '';
  const s = String(v).replace('T', ' ');
  return s.slice(5, 16);
}

function routeText(origin, dest) {
  const a = origin || '起点未填';
  const b = dest || '终点未填';
  return `${a} → ${b}`;
}

function maskPhone(phone) {
  const s = String(phone || '');
  if (s.length < 7) return s || '--';
  return `${s.slice(0, 3)}****${s.slice(-4)}`;
}

function greet() {
  const h = new Date().getHours();
  if (h < 11) return '上午好';
  if (h < 14) return '中午好';
  if (h < 18) return '下午好';
  return '晚上好';
}

function listOf(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  return raw.list || raw.items || raw.records || [];
}

module.exports = {
  pick,
  money,
  wan,
  shortTime,
  routeText,
  maskPhone,
  greet,
  listOf
};
