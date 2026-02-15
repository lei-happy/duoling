<template>
  <div>
    <ele-card style="border-radius: 0">
      <ele-text type="heading" size="lg">修改用户</ele-text>
      <ele-text type="placeholder" style="margin-top: 6px">
        修改用户基本信息后点击保存按钮
      </ele-text>
    </ele-card>
    <ele-page>
      <ele-card>
        <ele-loading :loading="loading">
          <edit-form v-if="user" :data="user" />
        </ele-loading>
      </ele-card>
    </ele-page>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useRoute } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import { usePageTab } from '@/utils/use-page-tab';
  import EditForm from '../components/edit-form.vue';
  import { getUser } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';

  defineOptions({ name: 'ListBasicEdit' });

  const { setPageTabTitle } = usePageTab();
  const route = useRoute();
  const userId = Number(route.params.id);

  /** 查询状态 */
  const loading = ref(true);

  /** 用户信息 */
  const user = ref<User>();

  /** 查询用户信息 */
  const query = () => {
    if (!userId || isNaN(userId)) {
      return;
    }
    getUser(userId)
      .then((data) => {
        loading.value = false;
        user.value = data;
        // 修改页签标题
        setPageTabTitle(`修改用户[${user.value.nickname}]`);
      })
      .catch((e) => {
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  query();
</script>
