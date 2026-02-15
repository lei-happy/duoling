<template>
  <ele-page>
    <demo-basic />
    <demo-advanced />
    <demo-multiple />
    <demo-picker />
    <demo-cropper />
    <demo-form1 />
    <demo-form2 />
    <demo-customer />
    <demo-file />
    <demo-viewer />
  </ele-page>
</template>

<script lang="ts" setup>
  import DemoBasic from './components/demo-basic.vue';
  import DemoAdvanced from './components/demo-advanced.vue';
  import DemoMultiple from './components/demo-multiple.vue';
  import DemoPicker from './components/demo-picker.vue';
  import DemoForm1 from './components/demo-form1.vue';
  import DemoForm2 from './components/demo-form2.vue';
  import DemoCustomer from './components/demo-customer.vue';
  import DemoFile from './components/demo-file.vue';
  import DemoViewer from './components/demo-viewer.vue';
  import DemoCropper from './components/demo-cropper.vue';

  defineOptions({ name: 'ExtensionUpload' });
</script>
