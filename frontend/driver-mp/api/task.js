const { get, post } = require('../utils/request');

function listMyTasks(params) {
  return get('/task/my', params);
}

function getTaskDetail(id) {
  return get(`/task/${id}`);
}

function acceptTask(id, payload) {
  return post(`/task/${id}/accept`, payload || {});
}

function rejectTask(id, payload) {
  return post(`/task/${id}/reject`, payload);
}

function confirmLoad(id, payload) {
  return post(`/task/${id}/confirm-load`, payload || {});
}

function depart(id, payload) {
  return post(`/task/${id}/depart`, payload || {});
}

function confirmArrive(id, payload) {
  return post(`/task/${id}/confirm-arrive`, payload || {});
}

function signItem(itemId, payload) {
  return post(`/task/items/${itemId}/sign`, payload || {});
}

module.exports = {
  listMyTasks,
  getTaskDetail,
  acceptTask,
  rejectTask,
  confirmLoad,
  depart,
  confirmArrive,
  signItem
};
