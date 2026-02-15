<template>
  <ele-page>
    <demo-basic />
    <demo-advanced />
    <demo-paper />
    <demo-map />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoBasic from './components/demo-basic.vue';
  import DemoAdvanced from './components/demo-advanced.vue';
  import DemoPaper from './components/demo-paper.vue';
  import DemoMap from './components/demo-map.vue';

  defineOptions({ name: 'ExtensionViewer' });
</script>
