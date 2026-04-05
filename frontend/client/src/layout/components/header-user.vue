<!-- 用户信息 -->
<template>
  <ele-dropdown
    :items="dropdownItems"
    :icon-props="{ size: 15 }"
    :popper-options="{
      modifiers: [{ name: 'offset', options: { offset: [0, 5] } }]
    }"
    @command="handleUserDropClick"
  >
    <div style="display: flex; align-items: center; height: 100%">
      <el-avatar
        :size="28"
        :src="loginUser.avatar"
        style="margin-left: -2px; background: none"
      />
      <div
        class="hidden-sm-and-down"
        style="margin-left: 4px; line-height: 1.5"
      >
        {{ loginUser.nickname }}
      </div>
      <el-icon :size="13" style="margin: 0 -4px 0 2px">
        <ArrowDown />
      </el-icon>
    </div>
  </ele-dropdown>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useRouter } from 'vue-router';
  import { useI18n } from 'vue-i18n';
  import { useModal } from 'ele-admin-plus';
  import {
    ArrowDown,
    UserOutlined,
    LockOutlined,
    LogoutOutlined,
    SettingOutlined
  } from '@/components/icons';
  import { useUserStore } from '@/store/modules/user';
  import { useLogin } from '@/utils/use-login';

  const { t } = useI18n();
  const { push } = useRouter();
  const userStore = useUserStore();
  const { showLogoutConfirm } = useLogin();
  const { openModal } = useModal();

  /** 当前用户信息 */
  const loginUser = computed(() => userStore.info ?? {});

  /** 下拉菜单项 */
  const dropdownItems = computed(() => {
    const items: any[] = [];
    if (userStore.isAdmin) {
      items.push({
        title: t('layout.header.enterprise'),
        command: 'enterprise',
        icon: SettingOutlined
      });
    }
    items.push(
      {
        title: t('layout.header.profile'),
        command: 'profile',
        icon: UserOutlined,
        divided: userStore.isAdmin
      },
      {
        title: t('layout.header.password'),
        command: 'password',
        icon: LockOutlined,
        iconStyle: { transform: 'translateY(-1px)' }
      },
      {
        title: t('layout.header.logout'),
        command: 'logout',
        icon: LogoutOutlined,
        divided: true
      }
    );
    return items;
  });

  /** 用户信息下拉点击 */
  const handleUserDropClick = (command: string) => {
    if (command === 'profile') {
      push('/user/profile');
    } else if (command === 'enterprise') {
      push('/enterprise/manage');
    } else if (command === 'logout') {
      showLogoutConfirm();
    } else if (command === 'password') {
      openModal({
        custom: true,
        asyncComponent: () => import('./password-modal.vue')
      });
    }
  };
</script>
