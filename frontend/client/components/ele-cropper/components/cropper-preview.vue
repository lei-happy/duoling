<template>
  <div
    ref="rootRef"
    class="ele-cropper-previews"
    :style="{ width: `${previewWidth + 14}px` }"
  >
    <div
      class="ele-cropper-preview"
      :style="{
        width: `${previewWidth}px`,
        height: `${previewWidth / (aspectRatio || 1)}px`,
        marginTop: '0px'
      }"
    >
    </div>
    <div
      v-if="aspectRatio === 1"
      class="ele-cropper-preview is-circle"
      :style="{
        width: `${previewWidth}px`,
        height: `${previewWidth / aspectRatio}px`
      }"
    >
    </div>
    <template v-else-if="aspectRatio">
      <div
        class="ele-cropper-preview"
        :style="{
          width: `${previewWidth}px`,
          height: `${((previewWidth / 3) * 2 - 10) / aspectRatio}px`
        }"
      >
      </div>
      <div
        class="ele-cropper-preview"
        :style="{
          width: `${previewWidth}px`,
          height: `${previewWidth / 3 / aspectRatio}px`,
          marginLeft: '10px'
        }"
      >
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';

  defineOptions({ name: 'CropperPreview' });

  defineProps({
    /** 组件宽度 */
    previewWidth: {
      type: Number,
      required: true
    },
    /** 裁剪比例 */
    aspectRatio: Number
  });

  /** 根节点 */
  const rootRef = ref<HTMLDivElement | null>(null);

  /** 获取所有预览节点 */
  const getPreviews = (): NodeListOf<HTMLElement> | undefined => {
    if (!rootRef.value) {
      return;
    }
    return rootRef.value.querySelectorAll('.ele-cropper-preview');
  };

  defineExpose({
    getPreviews
  });
</script>
