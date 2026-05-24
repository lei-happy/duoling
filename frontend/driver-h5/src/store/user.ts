import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { getItem, removeItem, setItem, STORAGE_KEYS, clearAll } from '@/utils/storage';
import {
  getUserInfo,
  type DriverUserInfo,
  type LoginResponseData,
  changePassword as apiChangePassword
} from '@/api/auth';

export const useUserStore = defineStore('user', () => {
  const accessToken = ref<string>(getItem<string>(STORAGE_KEYS.ACCESS_TOKEN, ''));
  const refreshToken = ref<string>(getItem<string>(STORAGE_KEYS.REFRESH_TOKEN, ''));
  const userInfo = ref<DriverUserInfo | null>(
    getItem<DriverUserInfo | null>(STORAGE_KEYS.USER_INFO, null)
  );

  const isLoggedIn = computed(() => !!accessToken.value);
  const currentTenantCode = computed(() => userInfo.value?.tenantCode || '');
  const realName = computed(() => userInfo.value?.realName || userInfo.value?.phone || '司机');
  const permissions = computed(() => userInfo.value?.permissions || []);
  const roles = computed(() => userInfo.value?.roles || []);
  const needForceChangePwd = computed(() => userInfo.value?.forceChangePwd === 1);

  function setLoginResult(data: LoginResponseData) {
    accessToken.value = data.accessToken;
    refreshToken.value = data.refreshToken;
    userInfo.value = data.user;
    setItem(STORAGE_KEYS.ACCESS_TOKEN, data.accessToken);
    setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refreshToken);
    setItem(STORAGE_KEYS.USER_INFO, data.user);
    if (data.user.tenantCode) {
      setItem(STORAGE_KEYS.TENANT_CODE, data.user.tenantCode);
    }
  }

  async function fetchUserInfo() {
    const info = await getUserInfo();
    userInfo.value = info;
    setItem(STORAGE_KEYS.USER_INFO, info);
    return info;
  }

  async function logout() {
    accessToken.value = '';
    refreshToken.value = '';
    userInfo.value = null;
    clearAll();
  }

  function hasPermission(code: string): boolean {
    if (!code) return true;
    return permissions.value.includes(code);
  }

  function hasRole(role: string): boolean {
    return roles.value.includes(role);
  }

  async function doChangePassword(payload: { oldPassword: string; newPassword: string }) {
    await apiChangePassword(payload);
    if (userInfo.value) {
      userInfo.value.forceChangePwd = 0;
      setItem(STORAGE_KEYS.USER_INFO, userInfo.value);
    }
  }

  function clearTokenOnly() {
    accessToken.value = '';
    refreshToken.value = '';
    removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  }

  return {
    accessToken,
    refreshToken,
    userInfo,
    isLoggedIn,
    currentTenantCode,
    realName,
    permissions,
    roles,
    needForceChangePwd,
    setLoginResult,
    fetchUserInfo,
    logout,
    hasPermission,
    hasRole,
    doChangePassword,
    clearTokenOnly
  };
});
