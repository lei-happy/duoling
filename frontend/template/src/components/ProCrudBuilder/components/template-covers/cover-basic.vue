<template>
  <div
    class="ele-icon-border-color-base"
    :style="{
      borderStyle: 'solid',
      borderWidth: '1px',
      borderRadius: '4px',
      marginTop: '10px'
    }"
  >
    <div
      class="ele-icon-border-color-base ele-icon-bg-fill-extra-light"
      :style="{
        height: '20px',
        display: 'flex',
        alignItems: 'center',
        borderBottomStyle: 'solid',
        borderBottomWidth: '1px',
        borderRadius: '4px 4px 0 0'
      }"
    >
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          padding: '2px 8px',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          boxSizing: 'border-box'
        }"
      >
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          padding: '2px 8px',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          boxSizing: 'border-box'
        }"
      >
        <IconSkeleton size="sm" />
      </div>
      <div
        class="ele-icon-border-color-base"
        :style="{
          width: '25%',
          padding: '2px 8px',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          boxSizing: 'border-box'
        }"
      >
        <IconSkeleton size="sm" />
      </div>
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
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
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
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
    </div>
    <div :style="{ height: '20px', display: 'flex', alignItems: 'center' }">
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
      <div :style="{ width: '25%', padding: '0 8px', boxSizing: 'border-box' }">
        <IconSkeleton size="sm" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { IconSkeleton } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
