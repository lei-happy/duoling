<template>
  <ele-page>
    <el-result title="404">
      <template #icon>
        <div style="width: 250px; height: 295px; margin: 20px 0 10px 0">
          <icon-svg />
        </div>
      </template>
      <template #sub-title>
        <ele-text type="placeholder">抱歉, 你访问的页面不存在.</ele-text>
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
  import IconSvg from './components/icon-svg.vue';

  defineOptions({ name: 'Exception404' });
</script>
