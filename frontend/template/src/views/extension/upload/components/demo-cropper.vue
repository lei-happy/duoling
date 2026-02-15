<template>
  <ele-card header="选择图片后先裁剪">
    <div style="margin-bottom: 12px">
      与文件选择和图片裁剪一起三者结合使用。
    </div>
    <ele-upload-list
      :limit="8"
      :tools="true"
      v-model="images"
      :beforeUploadClick="beforeUploadClick"
      :beforeItemEdit="beforeItemEdit"
      @remove="handleRemove"
    />
    <file-picker
      title="图片选择"
      :limit="1"
      :fileLimit="2"
      accept="image/*"
      :params="{ contentType: 'image/' }"
      v-model="showFilePicker"
      @done="handleFilePickerDone"
      @close="handleFilePickerClose"
    />
    <ele-cropper-modal
      v-model="showCropperModal"
      :src="cropperSrc"
      :options="{
        aspectRatio: 1,
        autoCropArea: 1,
        viewMode: 1,
        dragMode: 'move'
      }"
      :modal-props="{ destroyOnClose: true }"
      :beforeUploadClick="cropperBeforeUploadClick"
      @done="handleCropperDone"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { UploadItem } from 'ele-admin-plus/es/ele-upload-list/types';
  import type { BeforeUploadOnResult } from 'ele-admin-plus/es/ele-cropper/types';
  import FilePicker from '@/components/FilePicker/index.vue';
  import type { UserFile } from '@/api/system/user-file/model';

  /** 已上传数据 */
  const images = ref<UploadItem[]>([]);

  /** 是否打开文件选择弹窗 */
  const showFilePicker = ref(false);

  /** 是否打开裁剪弹窗 */
  const showCropperModal = ref(false);

  /** 裁剪图片地址 */
  const cropperSrc = ref('');

  /** 裁剪弹窗上传按钮回调 */
  let currentCropperCallback: BeforeUploadOnResult | null = null;

  /** 当前修改的文件项 */
  let currentEditItem: UploadItem | null = null;

  /** 删除事件 */
  const handleRemove = () => {
    images.value = [];
  };

  /** 上传按钮点击打开文件选择弹窗 */
  const beforeUploadClick = () => {
    showFilePicker.value = true;
    currentEditItem = null;
    return false;
  };

  /** 修改按钮点击打开文件选择弹窗 */
  const beforeItemEdit = (item: UploadItem) => {
    showFilePicker.value = true;
    currentEditItem = item;
    return false;
  };

  /** 文件选择弹窗选择完成事件 */
  const handleFilePickerDone = (files: UserFile[]) => {
    showFilePicker.value = false;
    if (files.length && files[0].url) {
      if (currentCropperCallback != null) {
        currentCropperCallback(files[0].url, files[0].contentType);
        currentCropperCallback = null;
        return;
      }
      cropperSrc.value = files[0].url;
      showCropperModal.value = true;
    }
  };

  /** 裁剪完成事件 */
  const handleCropperDone = (data: string) => {
    showCropperModal.value = false;
    // 添加
    if (currentEditItem == null) {
      images.value.push({
        key: String(Date.now()),
        url: data,
        status: 'done'
      });
      return;
    }
    // 修改
    const oldItem = images.value.find((t) => t.key === currentEditItem?.key);
    if (oldItem) {
      oldItem.url = data;
      oldItem.status = 'done';
    }
  };

  /** 裁剪弹窗上传按钮点击打开文件选择弹窗 */
  const cropperBeforeUploadClick = (
    _e: MouseEvent,
    onResult: BeforeUploadOnResult
  ) => {
    currentCropperCallback = onResult;
    showFilePicker.value = true;
    return false;
  };

  /** 文件选择弹窗关闭事件 */
  const handleFilePickerClose = () => {
    currentCropperCallback = null;
  };
</script>
