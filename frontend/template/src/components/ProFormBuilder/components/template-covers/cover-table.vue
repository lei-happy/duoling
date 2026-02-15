<template>
  <CoverTableView />
  <div
    :style="{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: '8px'
    }"
  >
    <IconButton
      size="sm"
      type="primary"
      :style="{ width: '52px', padding: '0 12px' }"
    />
    <IconButton size="sm" :style="{ width: '52px', marginLeft: '16px' }" />
  </div>
</template>

<script lang="ts" setup>
  import { IconButton } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
  import CoverTableView from './cover-table-view.vue';
</script>
