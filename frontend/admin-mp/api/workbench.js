const { get } = require('../utils/request');

function homeSummary(persona) {
  return get('/workbench/mp-home', { params: { persona } });
}

function lookup(keyword) {
  return get('/workbench/mp-lookup', { params: { keyword } });
}

function activities() {
  return get('/workbench/activities', { params: { page: 1, page_size: 20 } });
}

module.exports = { homeSummary, lookup, activities };
