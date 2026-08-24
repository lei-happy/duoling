const { get, post } = require('../utils/request');

function listDocs(params) {
  return get('/business/task-finance', { params: { page: 1, limit: 20, ...params } });
}

function financeStats() {
  return get('/business/task-finance/workbench-stats');
}

function getDoc(id) {
  return get(`/business/task-finance/${id}`);
}

function payDoc(id, data) {
  return post(`/business/task-finance/${id}/pay`, data);
}

function approveDoc(id) {
  return post(`/business/task-finance/${id}/approve`);
}

module.exports = { listDocs, financeStats, getDoc, payDoc, approveDoc };
