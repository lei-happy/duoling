<template>
  <div
    class="tabs"
    :role="isSwitch ? 'radiogroup' : 'tablist'"
    :aria-label="ariaLabel"
  >
    <button
      v-for="item in items"
      :key="item.key"
      ref="tabRefs"
      type="button"
      class="tab-btn"
      :class="{ 'is-on': item.key === modelValue }"
      :role="isSwitch ? 'radio' : 'tab'"
      :aria-selected="isSwitch ? undefined : item.key === modelValue"
      :aria-checked="isSwitch ? item.key === modelValue : undefined"
      :aria-controls="isSwitch ? undefined : panelId"
      :tabindex="item.key === modelValue ? 0 : -1"
      @click="emit('update:modelValue', item.key)"
      @keydown="onKeydown"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

export interface TabItem {
  key: string;
  label: string;
}

const props = withDefaults(
  defineProps<{
    items: TabItem[];
    modelValue: string;
    /** 供屏幕阅读器交代这组按钮在切什么 */
    ariaLabel?: string;
    /**
     * tabs 变体必须给出对应面板的 id，否则就是只说了一半的 ARIA：
     * 读屏会宣告「选项卡」，却找不到它控制的内容。
     */
    panelId?: string;
    /** switch 变体用于「月付/年付」这类同一份内容换口径的场景 */
    variant?: 'tabs' | 'switch';
  }>(),
  { ariaLabel: undefined, panelId: undefined, variant: 'tabs' }
);

const isSwitch = computed(() => props.variant === 'switch');

const emit = defineEmits<{ 'update:modelValue': [key: string] }>();

const tabRefs = ref<HTMLButtonElement[]>([]);

/** 左右方向键在标签之间移动，符合 tablist 的键盘约定 */
function onKeydown(event: KeyboardEvent) {
  const step =
    event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
  if (!step) {
    return;
  }
  event.preventDefault();

  const current = props.items.findIndex((i) => i.key === props.modelValue);
  const next = (current + step + props.items.length) % props.items.length;
  emit('update:modelValue', props.items[next].key);
  tabRefs.value[next]?.focus();
}
</script>

<style scoped lang="scss">
.tabs {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 3px;
  background: var(--bg-2);
  border-radius: var(--r);
}

.tab-btn {
  padding: 8px 16px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-2);
  cursor: pointer;
  transition:
    background var(--dur-hover) var(--ease),
    color var(--dur-hover) var(--ease);

  &[aria-selected='true'],
  &[aria-checked='true'],
  &.is-on {
    background: var(--paper);
    color: var(--brand);
    box-shadow: var(--shadow-sm);
  }
}

@media (hover: hover) and (pointer: fine) {
  .tab-btn:hover {
    color: var(--brand);
  }
}
</style>
