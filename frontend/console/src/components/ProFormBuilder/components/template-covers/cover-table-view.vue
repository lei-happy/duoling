<template>
  <div
    class="ele-icon-border-color-base"
    :style="{
      flex: 1,
      borderStyle: 'solid',
      borderWidth: '1px',
      borderRadius: '4px',
      marginTop: '3px'
    }"
  >
    <div
      class="ele-icon-border-color-base"
      :style="{
        height: '20px',
        display: 'flex',
        alignItems: 'center',
        borderBottomStyle: 'solid',
        borderBottomWidth: '1px'
      }"
    >
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          height: '100%',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          borderRightStyle: 'solid',
          borderRightWidth: '1px',
          boxSizing: 'border-box'
        }"
      ></div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          height: '100%',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          boxSizing: 'border-box'
        }"
      ></div>
    </div>
    <div
      class="ele-icon-border-color-base"
      :style="{
        height: '20px',
        display: 'flex',
        alignItems: 'center',
        borderBottomStyle: 'solid',
        borderBottomWidth: '1px'
      }"
    >
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          height: '100%',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          borderRightStyle: 'solid',
          borderRightWidth: '1px',
          boxSizing: 'border-box'
        }"
      ></div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          height: '100%',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          boxSizing: 'border-box'
        }"
      ></div>
    </div>
    <div
      class="ele-icon-border-color-base"
      :style="{
        height: '36px',
        display: 'flex',
        borderBottomStyle: 'solid',
        borderBottomWidth: '1px'
      }"
    >
      <div
        class="ele-icon-border-color-base"
        :style="{
          padding: '6px 10px',
          height: '100%',
          boxSizing: 'border-box',
          borderRightStyle: 'solid',
          borderRightWidth: '1px'
        }"
      >
        <IconSkeleton size="sm" :style="{ width: '6px', height: '100%' }" />
      </div>
    </div>
    <div :style="{ height: '22px', padding: '8px 10px' }">
      <IconSkeleton size="sm" />
      <IconSkeleton size="sm" :style="{ marginTop: '6px', width: '60%' }" />
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { IconSkeleton } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
