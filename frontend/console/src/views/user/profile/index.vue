<template>
  <ele-page :multi-card="false">
    <div class="user-wrapper">
      <user-card :data="loginUser" @done="updateLoginUser" class="user-side" />
      <ele-card
        :header-style="{ padding: '0 24px' }"
        :body-style="{ padding: 0, minHeight: '462px' }"
        class="user-body"
      >
        <template #header>
          <ele-tabs
            type="plain"
            size="large"
            :items="[
              { name: 'info', label: '基本信息' },
              { name: 'account', label: '账号绑定' }
            ]"
            :modelValue="active"
            @update:modelValue="handleUpdateModelValue"
          />
        </template>
        <user-form
          v-if="active === 'info'"
          :data="loginUser"
          @done="updateLoginUser"
        />
        <user-account v-if="active === 'account'" :data="loginUser" />
      </ele-card>
    </div>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useUserStore } from '@/store/modules/user';
  import type { User } from '@/api/system/user/model';
  import UserCard from './components/user-card.vue';
  import UserForm from './components/user-form.vue';
  import UserAccount from './components/user-account.vue';
  const pagePath = '/user/profile';

  defineOptions({ name: 'UserProfile' });

  const route = useRoute();
  const { push } = useRouter();

  const userStore = useUserStore();

  /** 选项卡选中 */
  const active = ref('info');

  /** 登录用户信息 */
  const loginUser = computed(() => userStore.info ?? {});

  /** 修改登录用户信息 */
  const updateLoginUser = (data: User) => {
    userStore.setInfo({ ...loginUser.value, ...data });
  };

  /** 切换选项卡 */
  const handleUpdateModelValue = (modelValue: string) => {
    push({ path: pagePath, query: { type: modelValue } });
  };

  watch(
    () => route.query.type,
    (type) => {
      if (route.path === pagePath) {
        active.value = [type].flat()[0] || 'info';
      }
    },
    { immediate: true }
  );
</script>

<style lang="scss" scoped>
  .user-wrapper {
    display: flex;

    .user-side {
      width: 320px;
      margin: 0 16px 0 0;
      flex-shrink: 0;
    }

    .user-body {
      flex: 1;
    }
  }

  @media screen and (max-width: 928px) {
    .user-wrapper .user-side {
      width: 240px;
    }
  }

  @media screen and (max-width: 768px) {
    .user-wrapper {
      display: block;

      .user-side {
        width: auto;
        margin: 0 0 16px 0;
      }
    }
  }
</style>
