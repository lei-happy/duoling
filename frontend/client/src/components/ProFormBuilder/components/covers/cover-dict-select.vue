<template>
  <div>
    <IconInput
      size="sm"
      class="ele-icon-color-secondary"
      :style="{ fontSize: '12px', lineHeight: '18px', textAlign: 'center' }"
    >
      <div>女</div>
      <SvgIcon name="ArrowUp" size="sm" :style="{ margin: '0 0 0 auto' }" />
    </IconInput>
    <IconPanel size="sm">
      <IconSkeleton size="sm" />
      <IconSkeleton size="sm" :style="{ marginTop: '4px' }" />
      <IconSkeleton size="sm" :style="{ marginTop: '4px' }" />
    </IconPanel>
  </div>
</template>

<script lang="ts" setup>
  import {
    IconInput,
    IconSkeleton,
    SvgIcon,
    IconPanel
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
