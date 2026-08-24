const { get, post, put } = require('../utils/request');

function listTasks(params) {
  return get('/business/task', { params: { page: 1, limit: 20, ...params } });
}

function taskStats(params) {
  return get('/business/task/workbench-stats', { params });
}

function getTask(id) {
  return get(`/business/task/${id}`);
}

function assignCarrier(id, data) {
  return post(`/business/task/${id}/assign-carrier`, data);
}

function completeCarrier(id, data) {
  return post(`/business/task/${id}/complete-carrier-assignment`, data);
}

function recommendCapacity(id) {
  return get(`/business/task/${id}/capacity-recommendations`);
}

function batchStatus(ids, status) {
  return post('/business/task/batch-status', { ids, status });
}

function updateStatus(id, data) {
  return put(`/business/task/${id}/status`, data);
}

module.exports = {
  listTasks,
  taskStats,
  getTask,
  assignCarrier,
  completeCarrier,
  recommendCapacity,
  batchStatus,
  updateStatus
};
