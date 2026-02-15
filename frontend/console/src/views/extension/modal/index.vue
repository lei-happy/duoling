<template>
  <ele-page>
    <demo-modal />
    <demo-multiple />
    <demo-drawer />
    <demo-message-box />
    <demo-popper />
    <demo-use-modal />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoModal from './components/demo-modal.vue';
  import DemoMultiple from './components/demo-multiple.vue';
  import DemoDrawer from './components/demo-drawer.vue';
  import DemoMessageBox from './components/demo-message-box.vue';
  import DemoPopper from './components/demo-popper.vue';
  import DemoUseModal from './components/demo-use-modal.vue';

  defineOptions({ name: 'ExtensionModal' });
</script>
