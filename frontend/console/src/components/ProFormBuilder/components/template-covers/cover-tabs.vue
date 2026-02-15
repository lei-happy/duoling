<template>
  <div
    :style="{
      display: 'flex',
      padding: '0 32px 0 0',
      marginTop: '6px'
    }"
  >
    <div
      v-for="i in 3"
      :key="i"
      class="ele-icon-border-color-base"
      :style="{
        flex: 1,
        borderTopLeftRadius: '4px',
        borderTopRightRadius: '4px',
        borderStyle: 'solid',
        borderWidth: '1px',
        borderBottom: 'none',
        padding: '8px 12px',
        marginRight: '8px'
      }"
    >
      <IconSkeleton size="sm" />
    </div>
  </div>
  <div
    class="ele-icon-border-color-base"
    :style="{
      padding: '14px 12px 18px 12px',
      borderStyle: 'solid',
      borderWidth: '1px'
    }"
  >
    <IconSkeleton />
    <IconSkeleton :style="{ marginTop: '14px' }" />
    <IconSkeleton :style="{ marginTop: '14px', width: '60%' }" />
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
