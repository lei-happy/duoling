<template>
  <ele-page>
    <el-result icon="info" title="功能开发中">
      <template #sub-title>
        <ele-text type="placeholder">
          {{ menuTitle ? `「${menuTitle}」` : '该模块' }}暂未上线，敬请期待
        </ele-text>
        <div
          v-if="route.path"
          style="
            margin-top: 12px;
            color: var(--el-text-color-secondary);
            font-size: 13px;
          "
        >
          路径：{{ route.path }}
        </div>
      </template>
      <template #extra>
        <router-link to="/" style="display: inline-flex; text-decoration: none">
          <el-button type="primary">返回首页</el-button>
        </router-link>
      </template>
    </el-result>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useRoute } from 'vue-router';

  defineOptions({ name: 'ExceptionPlaceholder' });

  const route = useRoute();

  const menuTitle = computed<string>(() => {
    const t = (route.meta as any)?.title;
    if (typeof t === 'string') return t;
    return '';
  });
</script>
