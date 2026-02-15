<template>
  <div
    :style="{ display: 'flex', alignItems: 'flex-start', marginTop: '28px' }"
  >
    <div :style="{ flex: 1 }">
      <IconSkeleton />
      <IconSkeleton :style="{ marginTop: '22px' }" />
      <IconSkeleton :style="{ marginTop: '22px' }" />
    </div>
    <div :style="{ flex: 1, marginLeft: '10px' }">
      <IconSkeleton />
      <IconSkeleton :style="{ marginTop: '22px' }" />
      <IconSkeleton :style="{ marginTop: '22px' }" />
    </div>
    <div :style="{ flex: 1, marginLeft: '10px' }">
      <IconSkeleton />
      <IconSkeleton :style="{ marginTop: '22px' }" />
      <div
        :style="{ display: 'flex', alignItems: 'center', marginTop: '19px' }"
      >
        <IconButton
          type="primary"
          :hideSkeleton="true"
          :style="{ flex: 1, height: '16px' }"
        />
        <IconButton :style="{ flex: 1, height: '16px', marginLeft: '6px' }" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import {
    IconSkeleton,
    IconButton
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
