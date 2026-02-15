<template>
  <ele-page>
    <demo-message />
    <demo-notice />
    <demo-tooltip />
    <demo-alert />
    <demo-loading />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoMessage from './components/demo-message.vue';
  import DemoNotice from './components/demo-notice.vue';
  import DemoTooltip from './components/demo-tooltip.vue';
  import DemoAlert from './components/demo-alert.vue';
  import DemoLoading from './components/demo-loading.vue';

  defineOptions({ name: 'ExtensionMessage' });
</script>
