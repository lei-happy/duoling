<!-- 新注册客户（最近30天） -->
<template>
  <ele-page>
    <customer-search
      :show-status="false"
      @search="(where) => tableRef?.reload?.({ where, page: 1 })"
    />
    <customer-table
      ref="tableRef"
      lifecycle="new"
      :show-add-button="true"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import CustomerSearch from '../components/customer-search.vue';
  import CustomerTable from '../components/customer-table.vue';

  defineOptions({ name: 'CustomerNew' });

  const tableRef = ref<InstanceType<typeof CustomerTable> | null>(null);
</script>
