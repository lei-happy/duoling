<!-- 图片上传 -->
<template>
  <CommonUpload
    v-model="images"
    :fileLimit="fileLimit"
    :readonly="readonly"
    :disabled="disabled"
    :preview="preview"
    :limit="limit"
    :multiple="multiple"
    :drag="drag"
    :accept="accept"
    :itemStyle="itemStyle"
    :buttonStyle="buttonStyle"
    :sortable="sortable"
    :imageProps="imageProps"
    :progressProps="progressProps"
    :previewProps="previewProps"
    :tools="tools"
    :listType="listType"
    :beforeUploadClick="beforeUploadClick"
    :beforeItemEdit="beforeItemEdit"
    :locale="locale"
    :componentLang="componentLang"
    :scene="scene"
  />
</template>

<script lang="ts" setup>
  import type { CSSProperties } from 'vue';
  import { ref, watch } from 'vue';
  import type {
    ElProgressProps,
    ElImageProps
  } from 'ele-admin-plus/es/ele-app/el';
  import type { EleImageViewerProps } from 'ele-admin-plus/es/ele-app/plus';
  import type {
    UploadItem,
    ListType,
    BeforeUploadClick,
    BeforeItemEdit,
    UploadLocale
  } from 'ele-admin-plus/es/ele-upload-list/types';
  import type { CommonUploadLocale } from '@/components/CommonUpload/config';
  import CommonUpload from '@/components/CommonUpload/index.vue';

  defineOptions({ name: 'ImageUpload' });

  const props = withDefaults(
    defineProps<{
      /** 绑定值 */
      modelValue?: string;
      /** 文件大小限制, 单位MB */
      fileLimit?: number;
      /** 是否只读 */
      readonly?: boolean;
      /** 是否禁用 */
      disabled?: boolean;
      /** 是否支持点击预览 */
      preview?: boolean;
      /** 最大上传数量 */
      limit?: number;
      /** 是否支持多选文件 */
      multiple?: boolean;
      /** 是否启用拖拽上传 */
      drag?: boolean;
      /** 接受上传的文件类型 */
      accept?: string;
      /** 自定义样式 */
      itemStyle?: CSSProperties;
      /** 自定义上传按钮样式 */
      buttonStyle?: CSSProperties;
      /** 是否开启拖拽排序 */
      sortable?: boolean | Record<keyof any, any>;
      /** 自定义图片属性 */
      imageProps?: ElImageProps;
      /** 自定义进度条属性 */
      progressProps?: ElProgressProps;
      /** 自定义图片预览属性 */
      previewProps?: EleImageViewerProps;
      /** 是否开启底部预览和修改的操作按钮 */
      tools?: boolean;
      /** 列表显示样式 */
      listType?: ListType;
      /** 上传按钮点击前的钩子 */
      beforeUploadClick?: BeforeUploadClick;
      /** 修改按钮点击前的钩子 */
      beforeItemEdit?: BeforeItemEdit;
      /** 国际化 */
      locale?: Partial<UploadLocale>;
      /** 自定义文案 */
      componentLang?: CommonUploadLocale;
      /** 上传场景目录（与后端 ALLOWED_SCENES 一致，默认 avatar） */
      scene?: string;
    }>(),
    {
      fileLimit: 100,
      preview: true,
      drag: true,
      accept: 'image/*',
      sortable: () => ({ forceFallback: true }),
      tools: true
    }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: string): void;
    (e: 'change', value?: string): void;
  }>();

  /** 上传组件数据 */
  const images = ref<UploadItem[]>([]);

  /** 更新绑定值 */
  const updateModelValue = (value: string) => {
    const oldValue = props.modelValue ?? '';
    const newValue = value ?? '';
    if (oldValue !== newValue) {
      emit('update:modelValue', newValue);
      emit('change', value);
    }
  };

  /** 清空上传组件数据 */
  const clearData = () => {
    images.value = [];
  };

  /** 判断是否全部上传完成 */
  const isDone = () => {
    return !images.value.some((item) => item.status !== 'done');
  };

  /** 获取上传数据对应的值 */
  const getDataValue = (imagesValue: UploadItem[]) => {
    const urls: string[] = [];
    imagesValue.forEach((item) => {
      if (item.status === 'done' && item.url != null) {
        urls.push(item.url);
      }
    });
    return urls;
  };

  /** 获取值对应的上传数据 */
  const getImagesValue = (
    dataValue: string | undefined | null,
    imagesValue: UploadItem[]
  ) => {
    if (!dataValue) {
      return imagesValue.filter((item) => item.status !== 'done');
    }
    const result: UploadItem[] = [];
    if (props.limit === 1) {
      result.push({ key: `0-${dataValue}`, url: dataValue, status: 'done' });
      return result;
    }
    try {
      const urls: string[] = JSON.parse(dataValue);
      imagesValue.forEach((item) => {
        if ((item.url && urls.includes(item.url)) || item.status !== 'done') {
          result.push(item);
        }
      });
      urls.forEach((url: string, index: number) => {
        if (url && !result.some((item) => item.url === url)) {
          const key = `${index}-${url}`;
          const oldIndex = result.findIndex((item) => item.key === key);
          if (oldIndex !== -1) {
            result.splice(oldIndex, 1);
          }
          result.push({ key, url, status: 'done' });
        }
      });
      if (props.limit != null && result.length > props.limit) {
        const temp = result.filter((item) => item.status !== 'done');
        for (const t of temp) {
          const i = result.indexOf(t);
          result.splice(i, 1);
          if (result.length <= props.limit) {
            break;
          }
        }
      }
    } catch (e) {
      console.error(e);
      imagesValue.forEach((item) => {
        if (item.status !== 'done') {
          result.push(item);
        }
      });
    }
    return result;
  };

  /** 判断上传数据是否改变 */
  const imagesIsChanged = (
    newImages: UploadItem[],
    oldImages: UploadItem[]
  ) => {
    if (newImages.length !== oldImages.length) {
      return true;
    }
    for (let i = 0; i < newImages.length; i++) {
      const newItem = newImages[i];
      const oldItem = oldImages[i];
      if (
        newItem.key !== oldItem.key ||
        newItem.url !== oldItem.url ||
        newItem.status !== oldItem.status
      ) {
        return true;
      }
    }
    return false;
  };

  /** 同步绑定值 */
  watch(
    images,
    (imagesValue) => {
      const dataValue = getDataValue(imagesValue);
      if (props.limit === 1) {
        updateModelValue(dataValue.join());
        return;
      }
      updateModelValue(dataValue.length ? JSON.stringify(dataValue) : '');
    },
    { deep: true }
  );

  watch(
    () => props.modelValue,
    (dataValue) => {
      const imagesValue = getImagesValue(dataValue, images.value);
      if (imagesIsChanged(imagesValue, images.value)) {
        images.value = imagesValue;
      }
    },
    { immediate: true }
  );

  defineExpose({ clearData, isDone });
</script>
