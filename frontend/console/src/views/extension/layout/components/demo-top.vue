<template>
  <ele-card header="用于前台网站" :body-style="{ padding: '12px' }">
    <frame-card>
      <div
        :style="{
          height: '520px',
          overflow: 'auto',
          background: 'var(--ele-layout-bg)'
        }"
      >
        <demo-top-layout :fixed-header="true" :mobile="mobile" />
      </div>
    </frame-card>
  </ele-card>
</template>

<script lang="ts" setup>
  import { useMobile } from '@/utils/use-mobile';
  import FrameCard from './frame-card.vue';
  import DemoTopLayout from './demo-top-layout.vue';

  /** 是否是移动端 */
  const { mobile } = useMobile();
</script>
