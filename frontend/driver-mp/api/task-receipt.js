const { get, post, del } = require('../utils/request');

function uploadReceipt(payload) {
  return post('/task-receipt/upload', payload);
}

function listMyReceipts(params) {
  return get('/task-receipt/my', params);
}

function deleteReceipt(id) {
  return del(`/task-receipt/${id}`);
}

module.exports = {
  uploadReceipt,
  listMyReceipts,
  deleteReceipt
};
