<template>
  <ele-page>
    <demo-badge />
    <demo-group />
    <demo-tab />
    <demo-component />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoBadge from './components/demo-badge.vue';
  import DemoGroup from './components/demo-group.vue';
  import DemoTab from './components/demo-tab.vue';
  import DemoComponent from './components/demo-component.vue';

  defineOptions({ name: 'Example' });
</script>
