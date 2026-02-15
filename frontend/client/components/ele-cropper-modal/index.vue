<!-- 图片裁剪弹窗 -->
<template>
  <EleModal
    width="620px"
    :title="lang.title"
    v-bind="modalProps || {}"
    :modelValue="modelValue"
    @update:modelValue="updateModelValue"
  >
    <EleCropper
      :height="height"
      :src="src"
      :imageType="imageType"
      :accept="accept"
      :tools="tools"
      :preview="preview"
      :previewWidth="previewWidth"
      :toBlob="toBlob"
      :options="options"
      :croppedOptions="croppedOptions"
      :tooltip="tooltip"
      :tooltipProps="tooltipProps"
      :beforeUploadClick="beforeUploadClick"
      :responsive="responsive"
      :locale="locale"
      @done="handleDone"
    />
    <template v-if="$slots.header" #header="slotProps">
      <slot name="header" v-bind="slotProps || {}"></slot>
    </template>
    <template v-if="$slots.footer" #footer="slotProps">
      <slot name="footer" v-bind="slotProps || {}"></slot>
    </template>
    <template v-if="$slots.maxIcon" #maxIcon="slotProps">
      <slot name="maxIcon" v-bind="slotProps || {}"></slot>
    </template>
    <template v-if="$slots.closeIcon" #closeIcon="slotProps">
      <slot name="closeIcon" v-bind="slotProps || {}"></slot>
    </template>
  </EleModal>
</template>

<script lang="ts" setup>
  import { useLocale } from '../ele-config-provider/receiver';
  import EleModal from '../ele-modal/index.vue';
  import EleCropper from '../ele-cropper/index.vue';
  import { cropperModalProps, cropperModalEmits } from './props';

  defineOptions({ name: 'EleCropperModal' });

  const props = defineProps(cropperModalProps);

  const emit = defineEmits(cropperModalEmits);

  const { lang } = useLocale('cropper', props);

  /** 更新绑定值 */
  const updateModelValue = (value: boolean) => {
    emit('update:modelValue', value);
  };

  /** 裁剪完成 */
  const handleDone = (result: Blob | string | null) => {
    emit('done', result);
  };
</script>
