<template>
  <div :style="{ display: 'flex', marginTop: '10px' }">
    <div
      class="ele-icon-border-color-base"
      :style="{
        width: '46px',
        padding: '7px 6px',
        boxSizing: 'border-box',
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '4px',
        marginRight: '10px'
      }"
    >
      <div :style="{ display: 'flex', alignItems: 'center' }">
        <IconArrow
          size="sm"
          direction="down"
          color="primary"
          :style="{ marginRight: '1px', transform: 'translate(-2px, 1px)' }"
        />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div
        :style="{
          paddingLeft: '8px',
          display: 'flex',
          alignItems: 'center',
          marginTop: '8px'
        }"
      >
        <IconArrow size="sm" :style="{ marginRight: '1px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div
        :style="{
          paddingLeft: '8px',
          display: 'flex',
          alignItems: 'center',
          marginTop: '8px'
        }"
      >
        <IconArrow size="sm" :style="{ marginRight: '1px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '8px' }">
        <IconArrow size="sm" :style="{ marginRight: '1px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
      <div :style="{ display: 'flex', alignItems: 'center', marginTop: '8px' }">
        <IconArrow size="sm" :style="{ marginRight: '1px' }" />
        <IconSkeleton size="sm" :style="{ flex: 1 }" />
      </div>
    </div>
    <div
      class="ele-icon-border-color-base"
      :style="{
        flex: 1,
        borderStyle: 'solid',
        borderWidth: '1px',
        borderRadius: '4px'
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
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div
          class="ele-icon-border-color-base"
          :style="{
            flex: 1,
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
            flex: 1,
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
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
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
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
      </div>
      <div :style="{ height: '20px', display: 'flex', alignItems: 'center' }">
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
        <div :style="{ flex: 1, padding: '0 8px', boxSizing: 'border-box' }">
          <IconSkeleton size="sm" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import {
    IconSkeleton,
    IconArrow
  } from 'ele-admin-plus/es/ele-pro-form-builder/components/icons/index';
</script>
