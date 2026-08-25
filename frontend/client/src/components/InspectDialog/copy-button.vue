<template>
  <button
    type="button"
    class="wbi-copy"
    :aria-label="ariaLabel"
    :title="ariaLabel"
    @click.stop="onClick"
  >
    <el-icon :size="14"><DocumentCopy /></el-icon>
  </button>
</template>

<script lang="ts" setup>
  import { DocumentCopy } from '@element-plus/icons-vue';
  import { copyTextWithToast } from './copy-text';

  defineOptions({ name: 'InspectCopyButton' });

  const props = withDefaults(
    defineProps<{
      text?: string | null;
      emptyTip?: string;
      successTip?: string;
      ariaLabel?: string;
    }>(),
    {
      text: '',
      emptyTip: '没有可复制的内容',
      successTip: '已复制',
      ariaLabel: '复制'
    }
  );

  const onClick = () =>
    copyTextWithToast(props.text, {
      emptyTip: props.emptyTip,
      successTip: props.successTip
    });
</script>

<style scoped>
  .wbi-copy {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    padding: 0;
    border: none;
    border-radius: 6px;
    color: var(--wbi-secondary, #6e6e73);
    background: transparent;
    cursor: pointer;
    transition:
      background 150ms ease,
      transform 100ms ease-out,
      color 150ms ease;
  }

  .wbi-copy:hover {
    color: var(--wbi-ink, #1c1c1e);
    background: rgba(120, 120, 128, 0.12);
  }

  .wbi-copy:active {
    transform: scale(0.94);
  }

  .wbi-copy:focus-visible {
    outline: 2px solid var(--el-color-primary);
    outline-offset: 2px;
  }

  @media (prefers-reduced-motion: reduce) {
    .wbi-copy {
      transition: none;
    }
  }
</style>
