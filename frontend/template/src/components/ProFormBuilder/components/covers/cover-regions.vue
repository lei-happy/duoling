<template>
  <div>
    <IconInput size="sm">
      <IconSkeleton size="sm" :style="{ width: '50%' }" />
      <SvgIcon
        name="EnvironmentOutlined"
        size="sm"
        :style="{ margin: '0 0 0 auto' }"
      />
    </IconInput>
    <IconPanel size="sm">
      <div :style="{ display: 'flex', alignItems: 'center' }">
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow
          size="sm"
          color="primary"
          :style="{ margin: '0 1px 0 4px' }"
        />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow
          size="sm"
          color="primary"
          :style="{ margin: '0 1px 0 4px' }"
        />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '4px' }">
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '4px' }">
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
    </IconPanel>
  </div>
</template>

<script lang="ts" setup>
  import {
    IconInput,
    IconSkeleton,
    IconPanel,
    IconArrow,
    SvgIcon
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
