<template>
  <div :style="{ display: 'flex', alignItems: 'center', marginTop: '8px' }">
    <IconSkeleton :style="{ flex: 1 }" />
    <IconSkeleton :style="{ flex: 1, marginLeft: '16px' }" />
  </div>
  <div :style="{ display: 'flex', alignItems: 'center', marginTop: '16px' }">
    <IconSkeleton :style="{ flex: 1 }" />
    <IconSkeleton :style="{ flex: 1, marginLeft: '16px' }" />
  </div>
  <div :style="{ display: 'flex', alignItems: 'center', marginTop: '16px' }">
    <IconSkeleton :style="{ flex: 1 }" />
    <IconSkeleton :style="{ flex: 1, marginLeft: '16px' }" />
  </div>
  <IconSkeleton :style="{ marginTop: '16px' }" />
  <div :style="{ display: 'flex', alignItems: 'center', marginTop: '20px' }">
    <IconButton
      size="sm"
      type="primary"
      :style="{ width: '52px', padding: '0 12px' }"
    />
    <IconButton size="sm" :style="{ width: '52px', marginLeft: '16px' }" />
  </div>
</template>

<script lang="ts" setup>
  import {
    IconSkeleton,
    IconButton
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
