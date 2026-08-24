const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { personaLabel } = require('../../utils/persona');

Page({
  data: { roles: [], personas: [], features: [] },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
    const roles = ((user.roles) || [])
      .map((item) => (typeof item === 'string' ? item : item.roleName || item.roleCode || ''))
      .filter(Boolean);
    this.setData({
      roles: roles.length ? roles : ['未分配角色'],
      personas: ((user.personas) || []).map(personaLabel).filter(Boolean),
      features: user.features || []
    });
  }
});
