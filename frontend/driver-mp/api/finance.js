const { get } = require('../utils/request');

function listMyFinance(params) {
  return get('/finance/my', params);
}

function getFinanceDetail(docId) {
  return get(`/finance/${docId}`);
}

function getFinanceSummary(params) {
  return get('/finance/summary', params);
}

function listMyAccounts() {
  return get('/finance/account');
}

function getMyFundAccount() {
  return get('/finance/fund-account');
}

function listMyFundTransactions(params) {
  return get('/finance/fund-account/transactions', params);
}

module.exports = {
  listMyFinance,
  getFinanceDetail,
  getFinanceSummary,
  listMyAccounts,
  getMyFundAccount,
  listMyFundTransactions
};
