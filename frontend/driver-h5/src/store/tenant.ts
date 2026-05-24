import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getItem, setItem, STORAGE_KEYS } from '@/utils/storage';
import {
  getUserTenants,
  switchTenant as apiSwitchTenant,
  type TenantOption
} from '@/api/auth';
import { useUserStore } from './user';

export const useTenantStore = defineStore('tenant', () => {
  const tenants = ref<TenantOption[]>(getItem<TenantOption[]>(STORAGE_KEYS.TENANT_LIST, []));
  const loading = ref(false);

  async function fetchTenants() {
    loading.value = true;
    try {
      const list = await getUserTenants();
      tenants.value = list;
      setItem(STORAGE_KEYS.TENANT_LIST, list);
      return list;
    } finally {
      loading.value = false;
    }
  }

  async function switchTo(tenantCode: string) {
    const user = useUserStore();
    const result = await apiSwitchTenant({ tenantCode });
    user.setLoginResult(result);
    return result;
  }

  return { tenants, loading, fetchTenants, switchTo };
});
