<template>
  <teleport to="body">
    <AnimatePresence :on-exit-complete="onExitComplete">
      <Motion
        v-if="visible"
        :key="layoutId || 'flip-modal'"
        as="div"
        class="flip-modal"
        :style="{ zIndex }"
        :initial="{ opacity: 1 }"
        :animate="{ opacity: 1 }"
        :exit="{ opacity: 1 }"
      >
        <Motion
          as="div"
          class="flip-modal__mask"
          :initial="{ opacity: 0 }"
          :animate="{ opacity: 1 }"
          :exit="{ opacity: 0 }"
          :transition="maskTransition"
          @click="onMaskClick"
        />
        <Motion
          as="div"
          class="flip-modal__panel"
          :layout-id="layoutId || undefined"
          :style="panelStyle"
          :transition="layoutTransition"
          :crossfade="true"
        >
          <button
            v-if="showClose"
            type="button"
            class="flip-modal__close"
            aria-label="关闭"
            @click="close"
          >
            <el-icon :size="18"><Close /></el-icon>
          </button>
          <Motion
            as="div"
            class="flip-modal__content"
            :variants="contentVariants"
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            <slot />
          </Motion>
        </Motion>
      </Motion>
    </AnimatePresence>
  </teleport>
</template>

<script lang="ts" setup>
  import {
    ref,
    computed,
    watch,
    onBeforeUnmount,
    type CSSProperties
  } from 'vue';
  import { Close } from '@element-plus/icons-vue';
  import { Motion, AnimatePresence } from 'motion-v';

  defineOptions({ name: 'FlipModal' });

  const EASE_OUT = [0.23, 1, 0.32, 1] as const;

  const props = withDefaults(
    defineProps<{
      /** 面板宽度 */
      width?: string;
      /** 面板最大高度 */
      maxHeight?: string;
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

  const visible = ref(false);
  const layoutId = ref<string>('');

  const layoutTransition = {
    type: 'spring' as const,
    bounce: 0,
    duration: 0.32
  };

  const maskTransition = computed(() => ({
    duration: visible.value ? 0.18 : 0.14,
    ease: EASE_OUT
  }));

  const contentVariants = {
    hidden: {
      opacity: 0,
      y: 6,
      transition: { duration: 0.14, ease: EASE_OUT }
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.2, delay: 0.12, ease: EASE_OUT }
    }
  };

  const panelStyle = computed<CSSProperties>(() => ({
    width: props.width,
    maxHeight: props.maxHeight
  }));

  const lockScroll = (lock: boolean) => {
    if (typeof document === 'undefined') return;
    document.body.style.overflow = lock ? 'hidden' : '';
  };

  const open = (id: string | number) => {
    layoutId.value = `capacity-shell-${id}`;
    visible.value = true;
    lockScroll(true);
    emit('opened');
  };

  const close = () => {
    if (!visible.value) return;
    visible.value = false;
  };

  const onExitComplete = () => {
    lockScroll(false);
    layoutId.value = '';
    emit('closed');
  };

  const onMaskClick = () => {
    if (props.closeOnClickMask) {
      close();
    }
  };

  const onKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.closeOnPressEscape && visible.value) {
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
    lockScroll(false);
  });

  defineExpose({ open, close, visible, layoutId });
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
  }

  .flip-modal__panel {
    position: relative;
    z-index: 1;
    box-sizing: border-box;
    max-width: 92vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--el-bg-color);
    border-radius: 12px;
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.24);
  }

  .flip-modal__content {
    flex: 1;
    min-height: 0;
    overflow: auto;
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
    transition:
      background 0.16s cubic-bezier(0.23, 1, 0.32, 1),
      color 0.16s cubic-bezier(0.23, 1, 0.32, 1),
      transform 0.16s cubic-bezier(0.23, 1, 0.32, 1);
  }

  .flip-modal__close:hover {
    background: var(--el-fill-color);
    color: var(--el-text-color-primary);
  }

  .flip-modal__close:active {
    transform: scale(0.97);
  }
</style>
