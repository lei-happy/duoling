<template>
  <div :class="['option-item', { 'is-responsive': responsive }]">
    <div
      v-if="label"
      class="option-item-label"
      :style="[{ width: labelWidth }, labelStyle || {}]"
    >
      {{ label }}
    </div>
    <div class="option-item-body" :style="bodyStyle">
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import type { CSSProperties } from 'vue';

  withDefaults(
    defineProps<{
      label?: string;
      labelWidth?: string;
      labelStyle?: CSSProperties;
      bodyStyle?: CSSProperties;
      responsive?: boolean;
    }>(),
    { responsive: true }
  );
</script>

<style lang="scss" scoped>
  .option-item {
    display: flex;
    align-items: center;

    .option-item-label {
      text-align: right;

      &::after {
        content: ':';
      }

      & + .option-item-body {
        padding-left: 12px;
      }
    }

    .option-item-body {
      flex: 1;
      word-break: break-all;
    }

    & + .option-item {
      margin-top: 24px;
    }
  }

  @media screen and (max-width: 768px) {
    .option-item.is-responsive {
      display: block;

      .option-item-label {
        text-align: left;
        margin-bottom: 8px;

        & + .option-item-body {
          padding-left: 0;
        }
      }
    }
  }
</style>
