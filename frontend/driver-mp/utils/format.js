function pad(n) {
  return `${n}`.padStart(2, '0');
}

function formatDateTime(value) {
  if (!value) return '-';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '-';
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function formatDate(value) {
  if (!value) return '-';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '-';
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function formatMoney(value, digits) {
  const d = digits == null ? 2 : digits;
  if (value == null || value === '') return '0.00';
  const n = Number(value);
  if (Number.isNaN(n)) return '0.00';
  return n.toFixed(d).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function maskPhone(phone) {
  if (!phone) return '';
  return phone.replace(/^(\d{3})\d{4}(\d{4})$/, '$1****$2');
}

function maskBankAccount(value) {
  if (!value) return '';
  if (value.length <= 8) return value;
  return `${value.slice(0, 4)}****${value.slice(-4)}`;
}

module.exports = {
  formatDateTime,
  formatDate,
  formatMoney,
  maskPhone,
  maskBankAccount
};
