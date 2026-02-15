<template>
  <IconSkeleton
    size="sm"
    :style="{ width: '38%', margin: '4px auto 0 auto' }"
  />
  <IconSkeleton size="sm" :style="{ marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ width: '70%', marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ width: '50%', marginTop: '16px' }" />
  <IconSkeleton size="sm" :style="{ width: '90%', marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ width: '90%', marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ width: '50%', marginTop: '10px' }" />
  <div
    :style="{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: '14px'
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
