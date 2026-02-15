<template>
  <ele-page>
    <demo-list />
    <demo-grid />
    <demo-table />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoList from './components/demo-list.vue';
  import DemoGrid from './components/demo-grid.vue';
  import DemoTable from './components/demo-table.vue';

  defineOptions({ name: 'ExtensionDragsort' });
</script>
