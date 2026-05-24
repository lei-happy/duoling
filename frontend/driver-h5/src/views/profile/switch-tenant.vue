<template>
  <PageContainer title="切换企业">
    <div class="tip card">
      <div class="tip-title">当前企业</div>
      <div class="tip-current">
        <van-icon name="apartment-o" />
        {{ currentName }}
      </div>
    </div>

    <van-cell-group inset class="list">
      <van-cell
        v-for="t in tenants"
        :key="t.tenantCode"
        clickable
        is-link
        :title="t.tenantName"
        :label="t.tenantCode"
        @click="onSwitch(t)"
      >
        <template #icon>
          <div class="tenant-icon">{{ t.tenantName.slice(0, 1) }}</div>
        </template>
        <template #right-icon>
          <van-tag v-if="t.tenantCode === currentCode" type="primary">当前</van-tag>
          <van-icon v-else name="arrow" />
        </template>
      </van-cell>
    </van-cell-group>

    <van-empty v-if="!loading && tenants.length === 0" description="暂无可切换的企业" />
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { closeToast, showConfirmDialog, showLoadingToast, showToast } from 'vant';
import PageContainer from '@/components/PageContainer.vue';
import { useTenantStore } from '@/store/tenant';
import { useUserStore } from '@/store/user';
import { useAuth } from '@/composables/useAuth';
import type { TenantOption } from '@/api/auth';

const tenantStore = useTenantStore();
const userStore = useUserStore();
const { switchTo } = useAuth();

const tenants = computed(() => tenantStore.tenants);
const currentCode = computed(() => userStore.currentTenantCode);
const currentName = computed(
  () => userStore.userInfo?.tenantName || userStore.currentTenantCode || '-'
);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    await tenantStore.fetchTenants();
  } finally {
    loading.value = false;
  }
});

async function onSwitch(t: TenantOption) {
  if (t.tenantCode === currentCode.value) {
    showToast('当前已在该企业');
    return;
  }
  try {
    await showConfirmDialog({
      title: '切换企业',
      message: `确定切换到「${t.tenantName}」？\n切换后将重新加载数据`
    });
  } catch {
    return;
  }
  showLoadingToast({ message: '切换中', forbidClick: true });
  try {
    await switchTo(t);
  } finally {
    closeToast();
  }
}
</script>

<style lang="scss" scoped>
.tip {
  margin: $spacing-md;
  padding: $spacing-md $spacing-lg;
  background: #fff;
  border-radius: $border-radius-md;
  .tip-title {
    color: $text-secondary;
    font-size: $font-size-sm;
  }
  .tip-current {
    margin-top: 6px;
    font-size: $font-size-lg;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    :deep(.van-icon) {
      color: $brand-primary;
    }
  }
}
.list {
  margin-top: $spacing-md;
}
.tenant-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: $brand-primary;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-md;
}
</style>
