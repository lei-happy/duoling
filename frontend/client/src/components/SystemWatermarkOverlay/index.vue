<template>
  <div
    v-if="fixed && visible && overlayStyle"
    :key="patternKey"
    class="system-watermark__layer is-fixed"
    :style="overlayStyle"
  />
  <div
    v-else-if="!fixed"
    class="system-watermark"
    :style="hostStyle"
  >
    <slot />
    <div
      v-if="visible && overlayStyle"
      :key="patternKey"
      class="system-watermark__layer"
      :style="overlayStyle"
    />
  </div>
</template>

<script lang="ts" setup>
  import { computed, watchEffect, ref, type CSSProperties } from 'vue';
  import {
    createWatermarkPattern,
    type WatermarkFontStyle
  } from '@/utils/watermark';

  defineOptions({ name: 'SystemWatermarkOverlay' });

  const props = withDefaults(
    defineProps<{
      /** 是否显示水印层 */
      visible?: boolean;
      /** 水印文本（支持多行） */
      content?: string | string[];
      /** 文本样式 */
      font?: WatermarkFontStyle;
      /** 旋转角度 */
      rotate?: number;
      /** 平铺间距 */
      gap?: [number, number];
      /** 层级 */
      zIndex?: number;
      /** 是否固定覆盖视口 */
      fixed?: boolean;
      /** 容器高度（非 fixed 时） */
      height?: number | string;
    }>(),
    {
      visible: true,
      rotate: -22,
      gap: () => [200, 160],
      zIndex: 9999,
      fixed: false
    }
  );

  const pattern = ref<ReturnType<typeof createWatermarkPattern>>(null);

  const lines = computed(() => {
    if (Array.isArray(props.content)) {
      return props.content.map((line) => line.trim()).filter(Boolean);
    }
    return props.content?.trim() ? [props.content.trim()] : [];
  });

  const rotateValue = computed(() => Number(props.rotate ?? -22));

  const gapValue = computed<[number, number]>(() => [
    Number(props.gap?.[0] ?? 200),
    Number(props.gap?.[1] ?? 160)
  ]);

  watchEffect(() => {
    if (!props.visible || !lines.value.length || !props.font) {
      pattern.value = null;
      return;
    }
    pattern.value = createWatermarkPattern(
      lines.value,
      props.font,
      rotateValue.value,
      gapValue.value
    );
  });

  const patternKey = computed(() => {
    if (!pattern.value) {
      return 'empty';
    }
    return [
      lines.value.join('\n'),
      props.font?.color,
      props.font?.fontSize,
      rotateValue.value,
      gapValue.value.join(','),
      pattern.value.url.slice(-32)
    ].join('|');
  });

  const hostStyle = computed<CSSProperties>(() => {
    const height =
      typeof props.height === 'number' ? `${props.height}px` : props.height;
    return {
      position: 'relative',
      height: height || '220px',
      overflow: 'hidden'
    };
  });

  const overlayStyle = computed<CSSProperties | undefined>(() => {
    if (!pattern.value) {
      return undefined;
    }
    return {
      backgroundImage: `url("${pattern.value.url}")`,
      backgroundRepeat: 'repeat',
      backgroundSize: `${pattern.value.width}px ${pattern.value.height}px`,
      zIndex: props.zIndex
    };
  });
</script>

<style scoped>
  .system-watermark {
    position: relative;
  }

  .system-watermark__layer {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .system-watermark__layer.is-fixed {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
  }
</style>
