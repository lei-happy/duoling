<template>
  <div class="tenant-select">
    <van-nav-bar title="选择企业" :left-arrow="canBack" @click-left="onBack" />

    <div class="tenant-tip card">
      <div class="tip-title">该手机号已关联多个企业</div>
      <div class="tip-desc">请选择您本次要进入的企业</div>
    </div>

    <van-cell-group inset class="tenant-list">
      <van-cell
        v-for="t in tenants"
        :key="t.tenantCode"
        clickable
        is-link
        :title="t.tenantName"
        :label="t.tenantCode"
        @click="onPick(t)"
      >
        <template #icon>
          <div class="tenant-icon">{{ t.tenantName.slice(0, 1) }}</div>
        </template>
      </van-cell>
    </van-cell-group>

    <div v-if="tenants.length === 0" class="empty">
      <van-empty description="暂无可用企业，请联系企业管理员开通" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showLoadingToast, closeToast, showFailToast } from 'vant';
import { useTenantStore } from '@/store/tenant';
import { useUserStore } from '@/store/user';
import { useAuth } from '@/composables/useAuth';
import {
  loginByPassword,
  loginBySms,
  loadPendingLogin,
  clearPendingLogin,
  type LoginResponseData,
  type TenantOption
} from '@/api/auth';

const route = useRoute();
const router = useRouter();
const tenantStore = useTenantStore();
const userStore = useUserStore();
const { switchTo, afterLogin } = useAuth();

const tenants = computed(() => tenantStore.tenants);
const canBack = computed(() => !userStore.isLoggedIn || !!userStore.currentTenantCode);

const phoneQuery = ref('');

onMounted(async () => {
  phoneQuery.value = (route.query.phone as string) || '';

  // 已登录场景（从"我的→切换企业"过来）：直接拉远端列表
  if (userStore.isLoggedIn && userStore.currentTenantCode) {
    showLoadingToast({ message: '正在加载企业列表，请稍候…', forbidClick: true });
    try {
      await tenantStore.fetchTenants();
    } finally {
      closeToast();
    }
  }
});

function onBack() {
  if (canBack.value) router.back();
}

async function onPick(t: TenantOption) {
  // 已登录：调用 switch-tenant
  if (userStore.isLoggedIn && userStore.currentTenantCode) {
    showLoadingToast({ message: '正在切换企业，请稍候…', forbidClick: true });
    try {
      await switchTo(t);
    } finally {
      closeToast();
    }
    return;
  }

  // 未登录（多企业第一步）：从 sessionStorage 取凭证再登录
  const pending = loadPendingLogin();
  const phone = pending?.phone || phoneQuery.value;
  showLoadingToast({ message: '正在登录，请稍候…', forbidClick: true });
  try {
    let result: LoginResponseData;
    if (pending?.password) {
      result = (await loginByPassword({
        phone,
        password: pending.password,
        tenantCode: t.tenantCode
      })) as LoginResponseData;
    } else if (pending?.code) {
      result = (await loginBySms({
        phone,
        code: pending.code,
        tenantCode: t.tenantCode
      })) as LoginResponseData;
    } else {
      showFailToast('登录信息已失效，请返回重新登录');
      await router.replace({ name: 'Login' });
      return;
    }
    if (!result.accessToken) {
      showFailToast('登录失败，请返回重新登录');
      return;
    }
    clearPendingLogin();
    userStore.setLoginResult(result);
    await afterLogin();
  } finally {
    closeToast();
  }
}
</script>

<style lang="scss" scoped>
.tenant-select {
  min-height: 100vh;
  background: $bg-page;
}
.tenant-tip {
  margin: $spacing-lg;
  .tip-title {
    font-size: $font-size-lg;
    font-weight: 600;
    margin-bottom: 4px;
  }
  .tip-desc {
    font-size: $font-size-sm;
    color: $text-secondary;
  }
}
.tenant-list {
  margin-top: $spacing-md;
}
.tenant-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: $brand-primary;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-md;
}
.empty {
  padding-top: 80px;
}
</style>
