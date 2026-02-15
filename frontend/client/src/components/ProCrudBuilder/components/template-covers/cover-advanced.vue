<template>
  <div
    class="ele-icon-border-color-base"
    :style="{
      borderStyle: 'solid',
      borderWidth: '1px',
      borderRadius: '4px',
      marginTop: '6px'
    }"
  >
    <div
      class="ele-icon-border-color-base ele-icon-bg-fill-extra-light"
      :style="{
        height: '40px',
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
          width: '50%',
          height: '100%',
          borderLeftStyle: 'solid',
          borderLeftWidth: '1px',
          borderRightStyle: 'solid',
          borderRightWidth: '1px',
          boxSizing: 'border-box'
        }"
      >
        <div
          class="ele-icon-border-color-base"
          :style="{
            height: '20px',
            display: 'flex',
            justifyContent: 'center',
            flexDirection: 'column',
            padding: '2px 8px',
            boxSizing: 'border-box',
            borderBottomStyle: 'solid',
            borderBottomWidth: '1px'
          }"
        >
          <IconSkeleton size="sm" style="width: 32px; margin: 0 auto" />
        </div>
        <div :style="{ height: '20px', display: 'flex', alignItems: 'center' }">
          <div
            :style="{
              height: '100%',
              width: '50%',
              padding: '0 8px',
              boxSizing: 'border-box',
              display: 'flex',
              justifyContent: 'center',
              flexDirection: 'column'
            }"
          >
            <IconSkeleton size="sm" />
          </div>
          <div
            class="ele-icon-border-color-base"
            :style="{
              height: '100%',
              width: '50%',
              padding: '0 8px',
              boxSizing: 'border-box',
              display: 'flex',
              justifyContent: 'center',
              flexDirection: 'column',
              borderLeftStyle: 'solid',
              borderLeftWidth: '1px'
            }"
          >
            <IconSkeleton size="sm" />
          </div>
        </div>
      </div>
      <div
        :style="{ width: '25%', padding: '2px 8px', boxSizing: 'border-box' }"
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
