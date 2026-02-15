<template>
  <IconSkeleton
    size="sm"
    :style="{ width: '48px', margin: '2px auto 0 auto' }"
  />
  <div :style="{ display: 'flex', gap: '18px', marginTop: '12px' }">
    <div :style="{ flex: 1 }">
      <IconSkeleton size="sm" />
      <IconSkeleton size="sm" :style="{ marginTop: '8px' }" />
      <IconSkeleton size="sm" :style="{ marginTop: '8px' }" />
    </div>
    <div :style="{ flex: 1 }">
      <IconSkeleton size="sm" />
      <IconSkeleton size="sm" :style="{ marginTop: '8px' }" />
      <IconSkeleton size="sm" :style="{ marginTop: '8px' }" />
    </div>
    <div
      class="ele-icon-border-color-light"
      :style="{
        flexShrink: 0,
        width: '28px',
        height: '32px',
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '3px',
        overflow: 'hidden'
      }"
    >
      <IconSkeleton
        :style="{
          width: '14px',
          height: '14px',
          borderRadius: '50%',
          margin: '6px auto 0 auto'
        }"
      />
      <IconSkeleton
        :style="{
          width: '26px',
          height: '26px',
          borderRadius: '50%',
          margin: '2px auto 0 auto'
        }"
      />
    </div>
  </div>
  <IconSkeleton size="sm" :style="{ marginTop: '14px' }" />
  <IconSkeleton size="sm" :style="{ width: '50%', marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ marginTop: '10px' }" />
  <IconSkeleton size="sm" :style="{ width: '50%', marginTop: '10px' }" />
</template>

<script lang="ts" setup>
  import { IconSkeleton } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
