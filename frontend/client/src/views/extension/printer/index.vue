<template>
  <ele-page>
    <print-basic />
    <print-contract />
    <print-more />
    <print-pdf />
  </ele-page>
</template>

<script lang="ts" setup>
  import PrintBasic from './components/print-basic.vue';
  import PrintContract from './components/print-contract.vue';
  import PrintMore from './components/print-more.vue';
  import PrintPdf from './components/print-pdf.vue';
</script>
