<template>
  <IconInput
    :style="{
      height: 'auto',
      padding: '6px',
      maxWidth: '52px',
      margin: '0 auto'
    }"
  >
    <SvgIcon name="UserOutlined" color="base" />
    <SvgIcon name="ArrowDown" size="sm" :style="{ margin: '0 0 0 auto' }" />
  </IconInput>
</template>

<script lang="ts" setup>
  import {
    IconInput,
    SvgIcon
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
