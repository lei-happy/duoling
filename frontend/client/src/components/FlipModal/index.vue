<template>
  <teleport to="body">
    <div v-if="visible" class="flip-modal" :style="{ zIndex }">
      <div ref="overlayRef" class="flip-modal__mask" @click="onMaskClick"></div>
      <div ref="panelRef" class="flip-modal__panel" :style="panelStyle">
        <button
          v-if="showClose"
          type="button"
          class="flip-modal__close"
          aria-label="关闭"
          @click="close"
        >
          <el-icon :size="18"><Close /></el-icon>
        </button>
        <div ref="contentRef" class="flip-modal__content">
          <slot />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script lang="ts" setup>
  import { ref, computed, watch, onBeforeUnmount, type CSSProperties } from 'vue';
  import { Close } from '@element-plus/icons-vue';
  import { useFlipModal } from '@/utils/use-flip-modal';

  defineOptions({ name: 'FlipModal' });

  const props = withDefaults(
    defineProps<{
      /** 面板宽度 */
      width?: string;
      /** 面板最大高度 */
      maxHeight?: string;
      /** 动画时长（秒） */
      duration?: number;
      /** 缓动 */
      ease?: string;
      /** 透视距离 */
      perspective?: number;
      /** 点击遮罩是否关闭 */
      closeOnClickMask?: boolean;
      /** 是否监听 ESC 关闭 */
      closeOnPressEscape?: boolean;
      /** 是否显示右上角关闭按钮 */
      showClose?: boolean;
      /** 层级 */
      zIndex?: number;
    }>(),
    {
      width: '800px',
      maxHeight: '86vh',
      duration: 0.55,
      ease: 'power3.inOut',
      perspective: 1600,
      closeOnClickMask: true,
      closeOnPressEscape: true,
      showClose: true,
      zIndex: 3000
    }
  );

  const emit = defineEmits<{
    (e: 'opened'): void;
    (e: 'closed'): void;
  }>();

  const panelRef = ref<HTMLElement | null>(null);
  const overlayRef = ref<HTMLElement | null>(null);
  const contentRef = ref<HTMLElement | null>(null);

  const { visible, isAnimating, open, close } = useFlipModal({
    panelRef,
    overlayRef,
    contentRef,
    duration: props.duration,
    ease: props.ease,
    perspective: props.perspective,
    onOpened: () => emit('opened'),
    onClosed: () => emit('closed')
  });

  const panelStyle = computed<CSSProperties>(() => ({
    width: props.width,
    maxHeight: props.maxHeight
  }));

  const onMaskClick = () => {
    if (props.closeOnClickMask && !isAnimating.value) {
      close();
    }
  };

  const onKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.closeOnPressEscape && !isAnimating.value) {
      close();
    }
  };

  watch(visible, (val) => {
    if (val) {
      window.addEventListener('keydown', onKeydown);
    } else {
      window.removeEventListener('keydown', onKeydown);
    }
  });

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeydown);
  });

  defineExpose({ open, close, visible, isAnimating });
</script>

<style scoped>
  .flip-modal {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .flip-modal__mask {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    opacity: 0;
  }

  .flip-modal__panel {
    position: relative;
    box-sizing: border-box;
    max-width: 92vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--el-bg-color);
    border-radius: 12px;
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.24);
    opacity: 0;
    transform-origin: center center;
    backface-visibility: hidden;
    will-change: transform, opacity;
  }

  .flip-modal__content {
    flex: 1;
    min-height: 0;
    overflow: auto;
    opacity: 0;
  }

  .flip-modal__close {
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    padding: 0;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: var(--el-text-color-secondary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .flip-modal__close:hover {
    background: var(--el-fill-color);
    color: var(--el-text-color-primary);
  }
</style>
