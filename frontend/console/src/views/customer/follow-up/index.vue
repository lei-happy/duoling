<!-- 跟进池 -->
<template>
  <ele-page>
    <customer-search
      @search="(where) => tableRef?.reload?.({ where, page: 1 })"
    />
    <customer-table
      ref="tableRef"
      lifecycle="follow_up"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import CustomerSearch from '../components/customer-search.vue';
  import CustomerTable from '../components/customer-table.vue';

  defineOptions({ name: 'CustomerFollowUp' });

  const tableRef = ref<InstanceType<typeof CustomerTable> | null>(null);
</script>
