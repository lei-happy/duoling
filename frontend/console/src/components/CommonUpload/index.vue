<!-- 文件上传 -->
<template>
  <EleUploadList
    v-model="images"
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
    :beforePreview="beforePreview"
    :locale="locale"
    @upload="handleItemUpload"
    @retry="(item) => handleItemUpload(item, true)"
    @remove="handleItemRemove"
    @editUpload="handleItemEditUpload"
    @itemClick="handleItemClick"
    @preview="handleItemPreview"
  >
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleUploadList>
</template>

<script lang="ts" setup>
  import type { CSSProperties } from 'vue';
  import type { AxiosProgressEvent } from 'axios';
  import { EleMessage } from 'ele-admin-plus';
  import type {
    ElProgressProps,
    ElImageProps
  } from 'ele-admin-plus/es/ele-app/el';
  import type { EleImageViewerProps } from 'ele-admin-plus/es/ele-app/plus';
  import type {
    UploadItem,
    EditUploadResult,
    ListType,
    BeforeUploadClick,
    BeforeItemEdit,
    BeforePreview,
    UploadLocale
  } from 'ele-admin-plus/es/ele-upload-list/types';
  import { useComponentLang } from '@/utils/use-component-lang';
  import type { CommonUploadLocale } from './config';
  import { uploadApi } from './config';

  defineOptions({ name: 'CommonUpload' });

  const props = withDefaults(
    defineProps<{
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
      /** 预览按钮点击前的钩子 */
      beforePreview?: BeforePreview;
      /** 国际化 */
      locale?: Partial<UploadLocale>;
      /** 自定义文案 */
      componentLang?: CommonUploadLocale;
    }>(),
    {
      fileLimit: 100,
      preview: true,
      drag: true,
      accept: '',
      sortable: () => ({ forceFallback: true }),
      tools: true
    }
  );

  const emit = defineEmits<{
    (e: 'itemClick', item: UploadItem): void;
    (e: 'preview', item: UploadItem): void;
  }>();

  const { lang } = useComponentLang<CommonUploadLocale>(
    {
      zh_CN: {
        imageError: '只能选择图片',
        excelError: '只能选择 excel 文件',
        limitError: '大小不能超过 {limit}MB'
      },
      zh_TW: {
        imageError: '只能選擇圖片',
        excelError: '只能選擇 Excel 檔案',
        limitError: '大小不能超過 {limit}MB'
      },
      en: {
        imageError: 'Can only select images',
        excelError: 'Can only select excel files',
        limitError: 'File size cannot exceed {limit}MB'
      }
    },
    props
  );

  /** 已上传数据 */
  const images = defineModel<UploadItem[]>({
    type: Array,
    default: () => []
  });

  /** 校验选择的文件 */
  const checkFile = (file?: File) => {
    if (!file) {
      return;
    }
    if (props.accept === 'image/*') {
      if (!file.type.startsWith('image')) {
        EleMessage.error({ message: lang.value.imageError, plain: true });
        return;
      }
    } else if (props.accept === '.xls,.xlsx') {
      if (
        ![
          'application/vnd.ms-excel',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ].includes(file.type)
      ) {
        EleMessage.error({ message: lang.value.excelError, plain: true });
        return;
      }
    }
    if (props.fileLimit && file.size / 1024 / 1024 > props.fileLimit) {
      EleMessage.error({
        message: lang.value.limitError.replace(
          /\{\s*limit\s*\}/g,
          String(props.fileLimit)
        ),
        plain: true
      });
      return;
    }
    return true;
  };

  /** 上传事件 */
  const handleItemUpload = (data: UploadItem, retry?: boolean) => {
    if (!data.file || !checkFile(data.file)) {
      return;
    }
    if (!retry) {
      images.value.push({ ...data });
    }
    const item = images.value.find((t) => t.key === data.key);
    if (!item) {
      return;
    }
    item.status = 'uploading';
    item.progress = 0;
    uploadApi(data.file, {
      onUploadProgress: (e: AxiosProgressEvent) => {
        if (e.total != null && item.status !== 'done') {
          item.progress = (e.loaded / e.total) * 100;
        }
      }
    })
      .then((res) => {
        item.progress = 100;
        item.status = 'done';
        item.url = res.url;
        item.response = res;
      })
      .catch((e) => {
        item.status = 'exception';
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  /** 修改事件 */
  const handleItemEditUpload = ({ item, newItem }: EditUploadResult) => {
    if (!checkFile(newItem.file)) {
      return;
    }
    const oldItem = images.value.find((t) => t.key === item.key);
    if (oldItem) {
      oldItem.url = void 0;
      oldItem.name = newItem.name;
      oldItem.file = newItem.file;
      oldItem.progress = 0;
      oldItem.status = void 0;
      handleItemUpload(oldItem, true);
    }
  };

  /** 删除事件 */
  const handleItemRemove = (item: UploadItem) => {
    images.value.splice(images.value.indexOf(item), 1);
  };

  /** 点击事件 */
  const handleItemClick = (item: UploadItem) => {
    emit('itemClick', item);
  };

  /** 预览事件 */
  const handleItemPreview = (item: UploadItem) => {
    emit('preview', item);
  };
</script>
