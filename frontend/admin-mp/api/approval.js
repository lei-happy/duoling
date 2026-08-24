const { get, post } = require('../utils/request');

function pending(params) {
  return get('/approval/pending', { params: { page: 1, limit: 20, ...params } });
}

function pendingCount() {
  return get('/approval/pending/count');
}

function initiated(params) {
  return get('/approval/initiated', { params: { page: 1, limit: 20, ...params } });
}

function history(params) {
  return get('/approval/history', { params: { page: 1, limit: 20, ...params } });
}

function getInstance(id) {
  return get(`/approval/instance/${id}`);
}

function agree(taskId, comment) {
  return post(`/approval/task/${taskId}/agree`, { comment: comment || '' });
}

function reject(taskId, comment) {
  return post(`/approval/task/${taskId}/reject`, { comment });
}

function transfer(taskId, data) {
  return post(`/approval/task/${taskId}/transfer`, data);
}

module.exports = {
  pending,
  pendingCount,
  initiated,
  history,
  getInstance,
  agree,
  reject,
  transfer
};
