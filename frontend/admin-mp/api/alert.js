const { get, post } = require('../utils/request');

function listAlerts(params) {
  return get('/business/task-alert', { params: { page: 1, limit: 20, ...params } });
}

function claimAlert(id) {
  return post(`/business/task-alert/${id}/claim`);
}

function resolveAlert(id, data) {
  return post(`/business/task-alert/${id}/resolve`, data || {});
}

module.exports = { listAlerts, claimAlert, resolveAlert };
