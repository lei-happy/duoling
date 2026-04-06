<template>
  <ele-page :multi-card="false">
    <div class="user-wrapper">
      <user-card :data="loginUser" @done="updateLoginUser" class="user-side" />
      <ele-card
        :body-style="{ padding: '0', minHeight: '462px' }"
        class="user-body"
      >
        <template #header>
          <ele-text size="md" style="font-weight: 500">基本信息</ele-text>
        </template>
        <user-form :data="loginUser" @done="updateLoginUser" />
      </ele-card>
    </div>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useUserStore } from '@/store/modules/user';
  import type { User } from '@/api/system/user/model';
  import UserCard from './components/user-card.vue';
  import UserForm from './components/user-form.vue';

  defineOptions({ name: 'UserProfile' });

  const userStore = useUserStore();

  const loginUser = computed(() => userStore.info ?? {});

  const updateLoginUser = (data: User) => {
    userStore.setInfo({ ...loginUser.value, ...data });
  };
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
