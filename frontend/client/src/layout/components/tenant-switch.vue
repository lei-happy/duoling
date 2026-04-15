<!-- 租户切换（仅由父级在 tenants.length > 1 时挂载） -->
<template>
  <ele-dropdown
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
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { OfficeBuilding, ArrowDown } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import { setToken, setRefreshToken, isRememberToken } from '@/utils/token-util';
  import { useUserStore } from '@/store/modules/user';
  import { switchTenant } from '@/api/login';
  import type { TenantOption } from '@/api/login/model';

  const props = defineProps<{
    /** 当前用户所属企业列表（至少 2 条时父级才会渲染本组件） */
    tenants: TenantOption[];
  }>();

  const userStore = useUserStore();

  const currentTenantName = computed(() => {
    const info = userStore.info as any;
    if (!info?.tenant_code && !info?.tenantCode) return '';
    const code = info.tenant_code || info.tenantCode;
    const found = props.tenants.find((t) => t.tenantCode === code);
    return found?.tenantName || code;
  });

  const dropdownItems = computed(() =>
    props.tenants.map((t) => ({
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
</script>
