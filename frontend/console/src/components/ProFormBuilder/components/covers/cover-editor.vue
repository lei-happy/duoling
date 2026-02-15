<template>
  <IconInput :style="{ height: 'auto', padding: '6px', display: 'block' }">
    <div :style="{ display: 'flex', alignItems: 'center' }">
      <IconImage size="sm" />
      <div :style="{ flex: 1, marginLeft: '6px' }">
        <IconSkeleton size="sm" />
        <IconSkeleton size="sm" :style="{ marginTop: '6px' }" />
      </div>
    </div>
    <IconSkeleton size="sm" :style="{ marginTop: '5px' }" />
    <div :style="{ display: 'flex', alignItems: 'center', marginTop: '3px' }">
      <IconSkeleton size="sm" :style="{ width: '50%' }" />
      <IconCursor />
    </div>
  </IconInput>
</template>

<script lang="ts" setup>
  import {
    IconInput,
    IconSkeleton,
    IconCursor,
    IconImage
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
