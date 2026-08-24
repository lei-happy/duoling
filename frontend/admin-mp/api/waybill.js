const { get, post, put, del } = require('../utils/request');

function listWaybills(params) {
  return get('/business/waybill', { params: { page: 1, limit: 20, ...params } });
}

function waybillStats(params) {
  return get('/business/waybill/workbench-stats', { params });
}

function getWaybill(id) {
  return get(`/business/waybill/${id}`);
}

function updateStatus(id, status) {
  return put(`/business/waybill/${id}/status`, { status });
}

function batchStatus(ids, status) {
  return post('/business/waybill/batch-status', { ids, status });
}

function listReceipts(id) {
  return get(`/business/waybill/${id}/receipts`);
}

function confirmReceipt(id, data) {
  return post(`/business/waybill/${id}/receipt`, data || {});
}

function revokeReceipt(id) {
  return del(`/business/waybill/${id}/receipt`);
}

module.exports = {
  listWaybills,
  waybillStats,
  getWaybill,
  updateStatus,
  batchStatus,
  listReceipts,
  confirmReceipt,
  revokeReceipt
};
