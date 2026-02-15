<!-- 表头工具栏按钮 -->
<template>
  <div class="ele-tool" @click="handleClick" @mouseover="handleMouseover">
    <div class="ele-tool-body">
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { watch, inject } from 'vue';
  import type { EleTooltipProps } from '../ele-app/plus';
  import { useTimer } from '../utils/hook';
  import { TOOLBAR_KEY } from '../ele-toolbar/props';
  import { toolProps, toolEmits } from './props';

  defineOptions({ name: 'EleTool' });

  const props = defineProps(toolProps);

  const emit = defineEmits(toolEmits);

  const toolbarProvide = inject(TOOLBAR_KEY, {});
  const [startHideTipTimer, stopHideTipTimer] = useTimer(200);

  /** 显示提示 */
  const showTooltip = (
    text?: string,
    el?: HTMLElement,
    options?: EleTooltipProps
  ) => {
    if (toolbarProvide.showTooltip) {
      toolbarProvide.showTooltip(text, el, options);
    }
  };

  /** 关闭提示 */
  const hideTooltip = () => {
    toolbarProvide.hideTooltip && toolbarProvide.hideTooltip();
  };

  /** 点击事件 */
  const handleClick = (e: MouseEvent) => {
    if (props.clickHideTooltip) {
      startHideTipTimer(() => {
        hideTooltip();
      });
    }
    emit('click', e);
  };

  /** 鼠标移入事件 */
  const handleMouseover = (e: MouseEvent) => {
    if (props.title && !props.disabled) {
      stopHideTipTimer();
      showTooltip(props.title, e.currentTarget as HTMLElement, {
        placement: props.placement,
        offset: 10
      });
    }
  };

  /** 禁用提示文字 */
  watch([() => props.disabled, () => props.title], () => {
    if (!props.title || props.disabled) {
      hideTooltip();
    }
  });

  defineExpose({
    showTooltip,
    hideTooltip
  });
</script>
