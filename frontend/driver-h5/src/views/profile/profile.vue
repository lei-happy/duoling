<template>
  <PageContainer title="我的" :show-tabbar="true" :hide-back="true">
    <div class="profile">
      <div class="user-card">
        <div class="user-card__row">
          <van-image
            v-if="user.userInfo?.avatar"
            round
            width="60"
            height="60"
            :src="user.userInfo.avatar"
          />
          <div v-else class="avatar-fallback">{{ user.realName.slice(0, 1) }}</div>
          <div class="user-info">
            <div class="name">{{ user.realName }}</div>
            <div class="phone">{{ maskPhone(user.userInfo?.phone) }}</div>
          </div>
        </div>
        <div class="user-card__tenant">
          <van-icon name="apartment-o" />
          <span class="text-ellipsis">当前企业：{{ tenantName }}</span>
        </div>
      </div>

      <van-cell-group inset class="menu-group">
        <van-cell title="个人信息" is-link icon="user-o" to="/profile/info" />
        <van-cell title="切换企业" is-link icon="exchange" to="/profile/switch-tenant" />
        <van-cell title="修改密码" is-link icon="lock" to="/change-password" />
      </van-cell-group>

      <van-cell-group inset class="menu-group">
        <van-cell title="收入汇总" is-link icon="balance-o" to="/finance/summary" />
        <van-cell title="收款账户" is-link icon="bank-card" to="/finance/summary" />
      </van-cell-group>

      <van-cell-group inset class="menu-group">
        <van-cell title="关于" is-link icon="info-o" @click="onAbout" />
      </van-cell-group>

      <div class="logout">
        <van-button block round type="default" @click="onLogout">退出登录</van-button>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { showConfirmDialog, showDialog } from 'vant';
import PageContainer from '@/components/PageContainer.vue';
import { useUserStore } from '@/store/user';
import { useAuth } from '@/composables/useAuth';
import { maskPhone } from '@/utils/format';

const user = useUserStore();
const { logout } = useAuth();

const tenantName = computed(
  () => user.userInfo?.tenantName || user.currentTenantCode || '-'
);

async function onLogout() {
  try {
    await showConfirmDialog({
      title: '退出登录',
      message: '确定要退出当前账号吗？'
    });
    await logout();
  } catch {
    /* user cancelled */
  }
}

function onAbout() {
  showDialog({
    title: '关于智途·司机端',
    message: `版本 ${import.meta.env.VITE_APP_NAME || ''}\nv0.1.0\n\n如有问题请联系企业管理员。`
  });
}
</script>

<style lang="scss" scoped>
.profile {
  padding-bottom: $spacing-xl;
}
.user-card {
  background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
  color: #fff;
  padding: 20px $spacing-lg;
  margin: $spacing-md;
  border-radius: $border-radius-md;
  &__row {
    display: flex;
    align-items: center;
    gap: $spacing-md;
  }
  .avatar-fallback {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    color: #fff;
    font-size: 24px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .user-info {
    flex: 1;
    min-width: 0;
    .name {
      font-size: $font-size-lg;
      font-weight: 600;
    }
    .phone {
      font-size: $font-size-sm;
      opacity: 0.88;
      margin-top: 2px;
    }
  }
  &__tenant {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: $spacing-md;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.18);
    border-radius: 8px;
    font-size: $font-size-sm;
  }
}
.menu-group {
  margin-top: $spacing-md;
}
.logout {
  margin: $spacing-xl $spacing-lg 0;
}
</style>
