<template>
  <ele-page hide-footer :multi-card="false" class="doc-center-page">
    <div class="doc-center-shell">
      <div class="doc-center-tabs">
        <el-tabs v-model="activeTab" @tab-change="onTabChange">
          <el-tab-pane label="文档" name="docs" />
          <el-tab-pane label="设计对接" name="design" />
        </el-tabs>
      </div>
      <div class="doc-center-body">
        <doc-browser v-if="activeTab === 'docs'" />
        <design-board v-else />
      </div>
    </div>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import DocBrowser from './DocBrowser.vue';
  import DesignBoard from './design/DesignBoard.vue';

  defineOptions({ name: 'DocCenter' });

  const route = useRoute();
  const router = useRouter();

  const resolveTab = () =>
    route.query.tab === 'design' ? 'design' : 'docs';

  const activeTab = ref<'docs' | 'design'>(resolveTab());

  watch(
    () => route.query.tab,
    () => {
      activeTab.value = resolveTab();
    }
  );

  const onTabChange = (name: string | number) => {
    const tab = String(name) === 'design' ? 'design' : 'docs';
    activeTab.value = tab;
    router.replace({
      path: '/doc-center',
      query: tab === 'design' ? { tab: 'design' } : {}
    });
  };
</script>

<style lang="scss">
  .doc-center-page.ele-page {
    flex: 1 !important;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-sizing: border-box;
  }
</style>

<style lang="scss" scoped>
  .doc-center-shell {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .doc-center-tabs {
    flex-shrink: 0;
    margin-bottom: 4px;

    :deep(.el-tabs__header) {
      margin-bottom: 0;
    }

    :deep(.el-tabs__nav-wrap::after) {
      height: 1px;
    }
  }

  .doc-center-body {
    flex: 1;
    min-height: 0;
    display: flex;
    overflow: hidden;
  }
</style>
