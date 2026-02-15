<!-- 路由刷新页面 -->
<template>
  <div></div>
</template>

<script lang="ts" setup>
  import { useRouter, useRoute } from 'vue-router';
  import { storeToRefs } from 'pinia';
  import { useTabStore } from '@/store/modules/tab';

  defineOptions({ name: 'RedirectLayout' });

  const { replace } = useRouter();
  const { params, query } = useRoute();
  const tabStore = useTabStore();
  const { tabs } = storeToRefs(tabStore);

  const from = Array.isArray(params.path) ? params.path.join('/') : params.path;

  setTimeout(() => {
    tabs.value.forEach((t) => {
      if (t.refresh) {
        tabStore.tabSetItem({ key: t.key, refresh: false });
      }
    });
    replace({ path: `/${from}`, query });
  }, 100);
</script>
