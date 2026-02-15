<template>
  <IconSkeleton size="sm" :style="{ width: '30%', marginTop: '4px' }" />
  <IconSkeleton size="sm" :style="{ marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ width: '30%', margin: '16px 0 10px 0' }" />
  <div
    class="ele-icon-border-color-base"
    :style="{
      padding: '12px',
      borderStyle: 'solid',
      borderWidth: '1px',
      borderRadius: '4px'
    }"
  >
    <IconSkeleton size="sm" />
    <IconSkeleton size="sm" :style="{ marginTop: '10px', width: '60%' }" />
  </div>
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
  import {
    IconSkeleton,
    IconButton
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
