<template>
  <div :style="{ width: '120px', maxWidth: '100%', margin: '0 auto' }">
    <div
      class="ele-icon-border-color-base"
      :style="{
        padding: '4px 8px',
        borderRadius: '4px',
        borderStyle: 'solid',
        borderWidth: '1px',
        boxSizing: 'border-box'
      }"
    >
      <IconSkeleton size="xs" />
    </div>
    <div
      class="ele-icon-border-color-base"
      :style="{
        padding: '4px 8px',
        borderRadius: '4px',
        borderStyle: 'solid',
        borderWidth: '1px',
        boxSizing: 'border-box',
        marginTop: '4px'
      }"
    >
      <IconSkeleton size="xs" />
    </div>
    <div
      class="ele-icon-border-color-base"
      :style="{
        padding: '4px 8px',
        borderRadius: '4px',
        borderStyle: 'solid',
        borderWidth: '1px',
        boxSizing: 'border-box',
        marginTop: '4px'
      }"
    >
      <IconSkeleton size="xs" />
    </div>
    <SvgIcon
      name="PlusOutlined"
      :iconStyle="{ transform: 'scale(0.8)' }"
      color="placeholder"
      class="ele-icon-border-color-base"
      :style="{
        height: '14px',
        borderRadius: '4px',
        borderStyle: 'solid',
        borderWidth: '1px',
        boxSizing: 'border-box',
        marginTop: '4px',
        fontSize: '12px'
      }"
    />
  </div>
</template>

<script lang="ts" setup>
  import {
    IconSkeleton,
    SvgIcon
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
