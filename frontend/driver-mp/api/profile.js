const { get, put } = require('../utils/request');

function getMyProfile() {
  return get('/profile/me');
}

function updateMyProfile(payload) {
  return put('/profile/me', payload);
}

module.exports = {
  getMyProfile,
  updateMyProfile
};
