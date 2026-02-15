<template>
  <div :style="{ display: 'flex', marginTop: '3px' }">
    <div
      class="ele-icon-border-color-base"
      :style="{
        flex: 1,
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '4px'
      }"
    >
      <div
        class="ele-icon-border-color-base"
        :style="{
          padding: '10px 12px',
          borderBottomStyle: 'solid',
          borderBottomWidth: '1px'
        }"
      >
        <IconSkeleton size="sm" :style="{ width: '60%' }" />
      </div>
      <div :style="{ padding: '14px 12px' }">
        <IconSkeleton />
        <IconSkeleton :style="{ marginTop: '16px' }" />
        <IconSkeleton :style="{ marginTop: '16px' }" />
      </div>
    </div>
    <div
      class="ele-icon-border-color-base"
      :style="{
        flex: 1,
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '4px',
        marginLeft: '12px'
      }"
    >
      <div
        class="ele-icon-border-color-base"
        :style="{
          padding: '10px 12px',
          borderBottomStyle: 'solid',
          borderBottomWidth: '1px'
        }"
      >
        <IconSkeleton size="sm" :style="{ width: '60%' }" />
      </div>
      <div :style="{ padding: '14px 12px' }">
        <IconSkeleton />
        <IconSkeleton :style="{ marginTop: '16px' }" />
        <IconSkeleton :style="{ marginTop: '16px' }" />
      </div>
    </div>
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
