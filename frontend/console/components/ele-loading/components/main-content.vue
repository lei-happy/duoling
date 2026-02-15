<template>
  <div
    :style="{ height: contentHeight }"
    :class="{ 'ele-loading-show': isShowLoading }"
  >
    <slot v-bind="slotProps"></slot>
    <Teleport v-if="isShowLoading" :to="to">
      <LoadingSpinner
        style="top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%"
        v-bind="customProps"
      />
    </Teleport>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useContentSlot } from '../../utils/hook';

  defineOptions({ name: 'MainContent' });

  const props = defineProps({
    /** 内容高度 */
    wrapHeight: [String, Number]
  });

  /** 内容样式 */
  const contentHeight = computed<string | undefined>(() => {
    if (props.wrapHeight != null && typeof props.wrapHeight === 'number') {
      return `${props.wrapHeight}px`;
    }
    return props.wrapHeight;
  });

  /** 是否加载中 */
  const { show, slotProps, LoadingSpinner, customProps, to } = useContentSlot();
  const isShowLoading = computed(() => customProps.value && !show.value);
</script>
