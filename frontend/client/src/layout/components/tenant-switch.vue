<!-- 租户切换 -->
<template>
  <ele-dropdown
    v-if="tenantList.length > 1"
    :items="dropdownItems"
    :popper-options="{
      modifiers: [{ name: 'offset', options: { offset: [0, 5] } }]
    }"
    @command="handleSwitch"
  >
    <div style="display: flex; align-items: center; height: 100%; cursor: pointer">
      <el-icon :size="16" style="margin-right: 4px">
        <OfficeBuilding />
      </el-icon>
      <span class="hidden-sm-and-down" style="line-height: 1.5; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">
        {{ currentTenantName }}
      </span>
      <el-icon :size="12" style="margin: 0 -4px 0 2px">
        <ArrowDown />
      </el-icon>
    </div>
  </ele-dropdown>
  <div
    v-else-if="currentTenantName"
    style="display: flex; align-items: center; height: 100%; padding: 0 8px"
  >
    <el-icon :size="16" style="margin-right: 4px">
      <OfficeBuilding />
    </el-icon>
    <span class="hidden-sm-and-down" style="line-height: 1.5">{{ currentTenantName }}</span>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted } from 'vue';
  import { OfficeBuilding, ArrowDown } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { setToken, setRefreshToken, isRememberToken } from '@/utils/token-util';
  import { useUserStore } from '@/store/modules/user';
  import { getUserTenants, switchTenant } from '@/api/login';
  import type { TenantOption } from '@/api/login/model';

  const userStore = useUserStore();

  const tenantList = ref<TenantOption[]>([]);

  const currentTenantName = computed(() => {
    const info = userStore.info as any;
    if (!info?.tenant_code && !info?.tenantCode) return '';
    const code = info.tenant_code || info.tenantCode;
    const found = tenantList.value.find((t) => t.tenantCode === code);
    return found?.tenantName || code;
  });

  const dropdownItems = computed(() =>
    tenantList.value.map((t) => ({
      title: t.tenantName,
      command: t.tenantCode
    }))
  );

  const handleSwitch = async (tenantCode: string) => {
    try {
      const result = await switchTenant(tenantCode);
      if (result?.access_token) {
        const remember = isRememberToken();
        setToken(result.access_token, remember);
        setRefreshToken(result.refresh_token, remember);
        EleMessage.success({ message: '切换成功，正在刷新...', plain: true });
        setTimeout(() => {
          window.location.reload();
        }, 500);
      }
    } catch (e: any) {
      EleMessage.error({ message: e.message || '切换失败', plain: true });
    }
  };

  onMounted(async () => {
    try {
      tenantList.value = await getUserTenants();
    } catch (e) {
      console.error('获取租户列表失败', e);
    }
  });
</script>
