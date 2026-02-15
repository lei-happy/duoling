<template>
  <div>
    <IconInput
      size="sm"
      class="ele-icon-color-secondary"
      :style="{
        fontSize: '12px',
        lineHeight: '14px',
        paddingLeft: '4px',
        textAlign: 'center'
      }"
    >
      <IconSkeleton :style="{ width: '22px', height: 'auto' }">
        <div :style="{ transform: 'scale(0.8)' }">男</div>
      </IconSkeleton>
      <IconSkeleton
        :style="{ width: '22px', height: 'auto', marginLeft: '4px' }"
      >
        <div :style="{ transform: 'scale(0.8)' }">女</div>
      </IconSkeleton>
      <SvgIcon name="ArrowUp" size="sm" :style="{ margin: '0 0 0 auto' }" />
    </IconInput>
    <IconPanel size="sm">
      <div
        :style="{ display: 'flex', alignItems: 'center', marginTop: '-2px' }"
      >
        <IconCheckbox size="sm" :checked="true" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '2px' }">
        <IconCheckbox size="sm" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div
        :style="{
          display: 'flex',
          alignItems: 'center',
          marginTop: '2px',
          marginBottom: '-2px'
        }"
      >
        <IconCheckbox size="sm" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
    </IconPanel>
  </div>
</template>

<script lang="ts" setup>
  import {
    IconInput,
    IconSkeleton,
    SvgIcon,
    IconPanel,
    IconCheckbox
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
