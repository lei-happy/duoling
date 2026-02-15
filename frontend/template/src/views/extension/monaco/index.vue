<template>
  <ele-page>
    <demo-basic />
    <demo-diff />
    <demo-run />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoBasic from './components/demo-basic.vue';
  import DemoDiff from './components/demo-diff.vue';
  import DemoRun from './components/demo-run.vue';

  defineOptions({ name: 'ExtensionMonaco' });
</script>
