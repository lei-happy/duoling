<template>
  <div
    :style="{ display: 'flex', alignItems: 'center', justifyContent: 'center' }"
  >
    <div
      class="ele-icon-border-color-base"
      :style="{
        width: '40px',
        height: '40px',
        padding: '0 4px',
        boxSizing: 'border-box',
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column'
      }"
    >
      <IconImage size="sm" :style="{ width: '100%', height: '28px' }" />
    </div>
    <SvgIcon
      name="PlusOutlined"
      color="placeholder"
      class="ele-icon-border-color-base"
      :style="{
        width: '40px',
        height: '40px',
        marginLeft: '6px',
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '4px',
        fontSize: '20px'
      }"
      :iconStyle="{ strokeWidth: 3 }"
    />
  </div>
</template>

<script lang="ts" setup>
  import {
    IconImage,
    SvgIcon
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
