const { get } = require('../utils/request');

function kpiSummary(params) {
  return get('/insight/cockpit/kpi-summary', { params });
}

function revenueTrend(params) {
  return get('/insight/cockpit/revenue-trend', { params: { granularity: 'day', ...params } });
}

function customerRank(params) {
  return get('/insight/cockpit/customer-rank', { params: { limit: 5, ...params } });
}

function operationEfficiency(params) {
  return get('/insight/cockpit/operation-efficiency', { params });
}

module.exports = { kpiSummary, revenueTrend, customerRank, operationEfficiency };
