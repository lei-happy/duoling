<template>
  <div>
    <IconInput size="sm">
      <IconSkeleton size="sm" :style="{ flex: 1, maxWidth: '32px' }" />
      <IconSkeleton
        size="sm"
        :style="{ flex: 1, maxWidth: '32px', margin: '0 0 0 6px' }"
      />
      <IconSkeleton
        size="sm"
        :style="{ flex: 1, maxWidth: '32px', margin: '0 6px 0 6px' }"
      />
      <SvgIcon
        name="EnvironmentOutlined"
        size="sm"
        :style="{ margin: '0 0 0 auto' }"
      />
    </IconInput>
    <IconPanel size="sm">
      <div :style="{ display: 'flex', alignItems: 'center' }">
        <IconCheckbox size="xs" :checked="true" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow
          size="sm"
          color="primary"
          :style="{ margin: '0 1px 0 4px' }"
        />
        <IconCheckbox size="xs" :checked="true" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow
          size="sm"
          color="primary"
          :style="{ margin: '0 1px 0 4px' }"
        />
        <IconCheckbox size="xs" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '4px' }">
        <IconCheckbox size="xs" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconCheckbox size="xs" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconCheckbox size="xs" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '4px' }">
        <IconCheckbox size="xs" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconCheckbox size="xs" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
        <IconArrow size="sm" :style="{ margin: '0 1px 0 4px' }" />
        <IconCheckbox size="xs" />
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
    IconCheckbox,
    SvgIcon
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
